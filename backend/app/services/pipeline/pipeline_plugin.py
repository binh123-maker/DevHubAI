"""
Pipeline Plugin Infrastructure — Phase 10.6

Architecture-only plugin registration system.
No plugin implementations yet — only the registry contract.

Future plugins:
    OCRPlugin, ImageParserPlugin, GithubParserPlugin,
    YoutubeParserPlugin, WebResourcePlugin
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


@dataclass
class PluginManifest:
    """Metadata declared by a plugin during registration."""
    name: str
    version: str = "1.0"
    description: str = ""
    stages: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    statistics: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)


class PipelinePlugin:
    """Abstract base every future plugin must extend."""

    def manifest(self) -> PluginManifest:
        raise NotImplementedError

    def on_load(self, registry: "PipelinePluginRegistry") -> None:
        """Called once when the plugin is loaded into the registry."""

    def on_unload(self) -> None:
        """Called when the plugin is removed."""


class PipelinePluginRegistry:
    """Central registry for pipeline plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, PipelinePlugin] = {}
        self._manifests: Dict[str, PluginManifest] = {}

    def register(self, plugin: PipelinePlugin) -> None:
        manifest = plugin.manifest()
        if manifest.name in self._plugins:
            logger.warning("Plugin %s already registered. Replacing.", manifest.name)
        self._plugins[manifest.name] = plugin
        self._manifests[manifest.name] = manifest
        try:
            plugin.on_load(self)
        except Exception as exc:
            logger.error("Plugin %s on_load failed: %s", manifest.name, exc)
        logger.info("Plugin registered: %s v%s", manifest.name, manifest.version)

    def unregister(self, name: str) -> None:
        plugin = self._plugins.pop(name, None)
        self._manifests.pop(name, None)
        if plugin:
            try:
                plugin.on_unload()
            except Exception as exc:
                logger.warning("Plugin %s on_unload failed: %s", name, exc)

    def get(self, name: str) -> Optional[PipelinePlugin]:
        return self._plugins.get(name)

    def list_plugins(self) -> List[PluginManifest]:
        return list(self._manifests.values())

    def plugin_count(self) -> int:
        return len(self._plugins)

    def is_registered(self, name: str) -> bool:
        return name in self._plugins

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_count": self.plugin_count(),
            "plugins": [
                {"name": m.name, "version": m.version, "stages": m.stages}
                for m in self._manifests.values()
            ],
        }

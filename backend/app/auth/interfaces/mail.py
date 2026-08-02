from abc import ABC, abstractmethod
from typing import Any


class IMailService(ABC):
    """Abstract Base Class for transactional mail delivery."""

    @abstractmethod
    async def send_mail(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_context: dict[str, Any],
    ) -> bool:
        """Dispatches an email asynchronously using a template and context parameters."""
        pass

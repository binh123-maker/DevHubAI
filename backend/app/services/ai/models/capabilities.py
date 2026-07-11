from pydantic import BaseModel

class ProviderCapabilities(BaseModel):
    supports_stream: bool = True
    supports_images: bool = False
    supports_tools: bool = False
    supports_function_calling: bool = False
    supports_json_mode: bool = False
    supports_embeddings: bool = False

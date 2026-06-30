import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class GenderType(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class OAuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"


class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class ChatMode(str, enum.Enum):
    GLOBAL = "global"
    WORKSPACE = "workspace"
    FOLDER = "folder"
    DOCUMENT = "document"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class CitationSourceType(str, enum.Enum):
    DOCUMENT = "document"
    WEBSITE = "website"
    NOTE = "note"

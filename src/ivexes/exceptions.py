"""Domain-specific exception classes for IVEXES."""


class IvexesError(Exception):
    """Base exception class for all IVEXES errors."""

    pass


class ConfigurationError(IvexesError):
    """Configuration validation failed."""

    pass


class SandboxError(IvexesError):
    """Sandbox operation failed."""

    pass


class CodeBrowserError(IvexesError):
    """Code browser operation failed."""

    pass


class VectorDatabaseError(IvexesError):
    """Vector database operation failed."""

    pass

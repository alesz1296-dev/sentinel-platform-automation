"""Domain invariant errors."""


class DomainValidationError(ValueError):
    """A supplied domain value cannot be accepted."""


class InvalidTransitionError(DomainValidationError):
    """An operation was requested from an invalid lifecycle state."""


class StaleFencingTokenError(DomainValidationError):
    """An obsolete worker attempted a platform operation."""

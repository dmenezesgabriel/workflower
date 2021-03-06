"""
Base exceptions module.
"""


class InvalidSchemaError(Exception):
    """Base class for invalid Schema exception"""

    pass


class InvalidTypeError(Exception):
    """Base class for invalid type error"""

    pass


class InvalidFilePathError(Exception):
    """Base class for invalid type error"""

    pass


class BusinessRuleValidationException(Exception):
    """A base class for all business rule validation exceptions"""

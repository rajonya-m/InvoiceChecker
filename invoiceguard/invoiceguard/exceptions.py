"""Our own exception classes (CONCEPT: custom exceptions, inheritance)."""


class InvoiceGuardError(Exception):
    """Base class for all errors raised by this project."""


class FileFormatError(InvoiceGuardError):
    """The input file is missing columns or is not what we expect."""


class InvoiceValidationError(InvoiceGuardError):
    """A single invoice row failed validation. Holds ALL its problems."""

    def __init__(self, errors):
        self.errors = errors                      # a list of messages
        super().__init__("; ".join(errors))


class InvoiceExistsError(InvoiceGuardError):
    """Tried to create an invoice whose number is already in the database."""

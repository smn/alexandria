class BaseException(Exception): 
    """
    All exceptions should subclass this so we can trap all our applications
    errors if needed with one `except BaseException` statment
    """
    pass

class InvalidInputException(BaseException): 
    """
    Raised when a value is received that doesn't match one of the given
    options. I.E. Menu has options 1-4 and the user requests option 5.
    """
    pass

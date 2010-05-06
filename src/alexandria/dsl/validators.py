from exceptions import InvalidInputException

def always_true(input, options):
    """
    A validator that will never fail. Used as the default validator.
    
    >>> always_true(False, ())
    True
    >>> always_true("", ())
    True
    >>> always_true([], ())
    True
    >>> always_true("grrrr", ())
    'grrrr'
    >>> always_true(1, ())
    1
    >>>
    
    """
    
    return input or True

def non_empty_string(input, options):
    """
    Fails when given an empty string
    
    >>> non_empty_string("foo",())
    'foo'
    >>> try: non_empty_string("",())
    ... except InvalidInputException, e: print e
    ... 
    empty string
    >>> 
    
    """
    if not input.strip(): 
        raise InvalidInputException, 'empty string'
    return input.strip()

def integer(input, options):
    """
    Fails when given non-digits
    
    >>> integer("1",())
    1
    >>> try: integer("foo",())
    ... except InvalidInputException, e: print e
    ... 
    contains not only digits
    >>> 
    
    """
    if not input.isdigit(): raise InvalidInputException, 'contains not only digits'
    return int(input)

def pick_one(input, options):
    """
    Fails unless one of the given inputs is actually available 
    in the given options. The option number or number value can be passed
    
    >>> pick_one("1",("a","b"))
    'a'
    >>> pick_one("b",("a","b"))
    'b'
    >>> try: pick_one("3",("a","b"))
    ... except InvalidInputException, e: print e
    ... 
    not one of the available options
    >>> try: pick_one("c",("a","b"))
    ... except InvalidInputException, e: print e
    ... 
    not one of the available options
    >>>
    
    """
    if not isinstance(input, str): raise InvalidInputException, 'not a string'
    if input.isdigit():
        return pick_one_by_digit(int(input), options)
    else:
        return pick_one_by_value(input, options)
    

def pick_one_by_digit(digit, options):
    for idx, entry in enumerate(options, start=1):
        if idx == digit:
            return entry
    raise InvalidInputException, 'not one of the available options'

def pick_one_by_value(input, options):
    for idx, entry in enumerate(options, start=1):
        if entry.lower() == input.lower():
            return entry
    raise InvalidInputException, 'not one of the available options'
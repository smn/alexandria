from exceptions import InvalidInputException

def always_true(input, options):
    return True

def non_empty_string(input, options):
    if not input.strip(): raise InvalidInputException, 'empty string'
    return input.strip()

def integer(input, options):
    if not input.isdigit(): raise InvalidInputException, 'contains not only digits'
    return int(input)

def pick_one(input, options):
    if input.isdigit():
        return pick_one_by_digit(int(input), options)
    else:
        return pick_one_by_value(input, options)
    

def pick_one_by_digit(digit, options):
    for idx, entry in enumerate(options, start=1):
        if idx == digit:
            return (digit, entry)
    raise InvalidInputException, 'not one of the available options'

def pick_one_by_value(input, options):
    for idx, entry in enumerate(options, start=1):
        if entry == input:
            return (idx, entry)
    raise InvalidInputException, 'not one of the available options'
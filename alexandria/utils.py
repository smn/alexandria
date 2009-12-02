import random
import operator

def msg(message, options):
    if options:
        message += '\n' + ol(options)
    return message

def ol(list):
    """return an ordered list"""
    return '\n'.join('%s: %s' % (idx, item) for idx,item in enumerate(list, start=1))

def shuffle(*items):
    items = list(items)
    random.shuffle(items)
    return items


def table(header, data):
    """print a pretty table for in the console"""
    column_widths = {}
    buffer = []
    # grab the first row to count the columns
    for idx in range(0, len(data[0])):
        all_column_widths = [len(str(row[idx])) for row in data]
        column_widths[idx] = max(all_column_widths)
    combined_width = reduce(operator.add, column_widths.values()) + (len(column_widths) - 1)

    buffer.append('+' + ('-' * combined_width) + '+')
    buffer.append('|' + header.center(combined_width) + '|')
    buffer.append('+' + ('-' * combined_width) + '+')
    for row in data:
        padded_columns = [str(column).ljust(column_widths[idx]) for idx, column in enumerate(row)]
        buffer.append('|' + '|'.join(padded_columns) + '|')
    buffer.append('+' + ('-' * combined_width) + '+')
    return '\n'.join(buffer)

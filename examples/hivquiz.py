from alexandria.core import MenuSystem, prompt
from alexandria.utils import shuffle, table
from alexandria.validators import pick_one
from alexandria.utils import msg
from generator_tools.copygenerators import copy_generator
import logging

# allow for lazy ugettext based translation like Django does it
_ = lambda s: s

# yes no options
yes_or_no = {
    'options': ('yes','no'),
    'validator': pick_one
}

def pick_first_unanswered(*prompts):
    """Returns the first prompt for which the storage doesn't have an
    answer stored yet."""
    cloned_prompts = map(copy_generator, prompts)
    while True:
        ms = yield
        while cloned_prompts:
            prompt = cloned_prompts.pop()
            prompt.next()
            question = prompt.send(ms)
            if not any([question.startswith(key) for key in ms.storage]):
                yield question
                answer = yield
                prompt.next()
                validated_answer = prompt.send(answer)
                yield validated_answer
            else:
                logging.debug('already handled question %s' % question)
        yield False
                


def case(*cases):
    """Returns the first prompt for which the test function returns True"""
    while True:
        ms = yield
        for test, prompt in cases:
            if test(ms):
                prompt = copy_generator(prompt)
                prompt.next()
                question = prompt.send(ms)
                yield question
                answer = yield
                prompt.next()
                validated_answer = prompt.send(answer)
                yield validated_answer
        yield False


def do(*callbacks):
    while True:
        ms = yield
        for callback in callbacks:
            callback(ms)
        yield False

def all_questions_answered(menu_system):
    return len(menu_system.storage) == 10

def more_questions_left(menu_system):
    return not all_questions_answered(menu_system)


def print_storage(ms):
    print table('ms.storage', ms.storage.items())

def check_question(ms):
    print ms.storage.keys()
    answer = ms.storage.get('Can traditional medicine cure HIV/AIDS?\n1: yes\n2: no', None)
    return answer == [(1, 'yes')]


def check_answer(question, answer):
    def _checker(ms):
        print ms.storage[question] == answer
        return ms.storage[question] == answer
    return _checker

def question(text, options):
    """
    
    Example:
    
        ms.append(
            *question('Can traditional medicine cure HIV/AIDS?', {
                'no': 'Correct! Press 1 to continue.',
                'yes': 'Incorrect! Please check your answer and press 1 to continue'
            })
        )
    
    Is the same as:
    
        ms.append(
            prompt(_('Can traditional medicine cure HIV/AIDS?'), {
                'options': ('yes','no'),
                'validator': pick_one
            }),
            case(
                (
                    lambda ms: ms.storage['Can traditional medicine cure HIV/AIDS?'] == ['1']),
                    prompt('Correct! Press 1 to continue.')
                ),
                (
                    lambda ms: ms.storage['Can traditional medicine cure HIV/AIDS?'] != ['1']),
                    prompt('Incorrect! Please check your answer and press 1 to continue.')
                ),
            )
        )
    
    
    """
    stack_list = []
    question_text = msg(text, options.keys())
    stack_list.append(prompt(text, options=options.keys()))
    case_list = []
    for idx, (option, answer) in enumerate(options.items(),start=1):
        case_list.append(
            (check_answer(question_text, [str(idx)]), prompt(answer))
        )
    stack_list.append(case(*case_list))

ms = MenuSystem(
    prompt('Thnx 4 taking the Quiz! Answer 3 questions and see how much you know. '
            'Pick your language:', options=(
        'English',
        'Zulu',
        'Afrikaans',
        'Sotho',
    ), validator=pick_one),
    prompt(_('You will be asked to answer 3 questions regarding HIV. '
        'Answer them correctly and stand a chance to win airtime! Press 1 to continue.'
    )),
    pick_first_unanswered(
        prompt(_('Can traditional medicine cure HIV/AIDS?'), **yes_or_no),
        prompt(_('Is an HIV test at any government clinic free of charge?'), **yes_or_no),
        prompt(_('Is it possible to test HIV-negative for up to 3-months after becoming HIV-infected?'), **yes_or_no),
    ),
    # do(print_storage),
    case(
            (check_question, prompt('Correct! Press 1 to continue.'))
    ),
    pick_first_unanswered(
        prompt(_('Can HIV be transmitted by sweat?'), **yes_or_no),
        prompt(_('Is there a herbal medication that can cure HIV/AIDS?'), **yes_or_no),
        prompt(_('Does a CD4-count reflect the strength of a person\'s immune system?'), **yes_or_no),
    ),
    pick_first_unanswered(
        prompt(_('Can HIV be transmitted through a mother\'s breast milk?'), **yes_or_no),
        prompt(_('Is it possible for an HIV positive woman to deliver an HIV negative baby?'), **yes_or_no)
    ),
    case(
        (all_questions_answered, prompt(_('Thank you you\'ve answered all questions! Press 1 to continue.'))),
        (more_questions_left, prompt(_('Dial in again to answer the remaining questions Press 1 to continue.'))),
    ),
    prompt(_('For more information about HIV/AIDS please phone the Aids '+
                'Helpline on 0800012322.  This is a free call from a landline. '+
                'Normal cell phone rates apply.'))
)

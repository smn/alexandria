from alexandria.dsl.core import MenuSystem, prompt, question, case, pick_first_unanswered
from alexandria.dsl.utils import shuffle, table
from alexandria.dsl.validators import pick_one
from alexandria.dsl.utils import msg
from generator_tools.copygenerators import copy_generator
import logging

# allow for lazy ugettext based translation like Django does it
_ = lambda s: s

# yes no options
yes_or_no = {
    'options': ('yes','no'),
    'validator': pick_one
}


def do(*callbacks):
    while True:
        ms, session = yield
        for callback in callbacks:
            callback(ms, session)
        yield False

def all_questions_answered(menu_system, session):
    return len(session) == 10

def more_questions_left(menu_system, session):
    return not all_questions_answered(menu_system, session)

def print_storage(ms, session):
    print table('session', session.items())

def check_question(ms, session):
    print session.keys()
    answer = session.get('Can traditional medicine cure HIV/AIDS?\n1: yes\n2: no', None)
    return answer == [(1, 'yes')]


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

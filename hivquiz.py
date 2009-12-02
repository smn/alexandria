from alexandria.client import ReallyDumbTerminal
from alexandria.core import MenuSystem, prompt, display, coroutine, delay
from alexandria.utils import shuffle, table
from alexandria.validators import non_empty_string, integer, pick_one

# fake translation function
_ = lambda s: s

# yes no options
yes_or_no = {
    'options': ('yes','no'),
    'validator': pick_one
}

@delay
@coroutine
def do_first_unanswered(*prompts):
    """
    Running into an interesting problem here, I need to be able to 
    introspect the questions here to see if they've been answered yet or not.
    
    Currently unable to do so.
    """
    prompts = list(prompts)
    while True:
        ms = (yield) # wait for menu system to be handed to us
        for prompt in prompts:
            # right now we're just doing the first one instead of intelligently
            # picking one that hasn't been answered yet
            yield prompt.invoke().send(ms)

ms = MenuSystem()
ms \
    .do(
        prompt('Thnx 4 taking the Quiz! Answer 3 questions and see how much you know'+
                '. Pick your language:', options=(
            'English',
            'Zulu',
            'Afrikaans',
            'Sotho',
        ), validator=pick_one),
        prompt(_('You will be asked to answer 3 questions regarding HIV. ' +
            'Answer them correctly and stand a chance to win airtime!'
        ))
    ) \
    .do(
        do_first_unanswered(
            prompt(_('Can traditional medicine cure HIV/AIDS?'), **yes_or_no),
            prompt(_('Is an HIV test at any government clinic free of charge?'), **yes_or_no),
            prompt(_('Is it possible to test HIV-negative for up to 3-months after becoming HIV-infected?'), **yes_or_no),
        )
    ) \
    .do(
        do_first_unanswered(
            prompt(_('Can HIV be transmitted by sweat?'), **yes_or_no),
            prompt(_('Is there a herbal medication that can cure HIV/AIDS?'), **yes_or_no),
            prompt(_('Does a CD4-count reflect the strength of a person\'s immune system?'), **yes_or_no),
        )
    ) \
    .do(
        do_first_unanswered(
            prompt(_('Can HIV be transmitted through a mother\'s breast milk?'), **yes_or_no),
            prompt(_('Is it possible for an HIV positive woman to deliver an HIV negative baby?'), **yes_or_no)
        )
    ) \
    .do(
        display(_('For more information about HIV/AIDS please phone the Aids '+
                    'Helpline on 0800012322.  This is a free call from a landline. '+
                    'Normal cell phone rates apply.'))
    )

for dc in ms.state:
    print dc

# run through the system
[(step, routine) for step, routine in ms.run(client=ReallyDumbTerminal("msisdn"))]

# print summary
print '\n\n' + table('Current state', ms.store.items()) + '\n\n'
from alexandria.client import ReallyDumbTerminal
from alexandria.core import MenuSystem, prompt
from alexandria.utils import shuffle, table
from alexandria.validators import non_empty_string, integer, pick_one

# fake translation function
_ = lambda s: s

# yes no options
yes_or_no = {
    'options': ('yes','no'),
    'validator': pick_one
}

ms = MenuSystem()
ms \
    .do(
        prompt('Choose your language',options=(
            'English',
            'Dutch'
        ), validator=pick_one)
    ) \
    .do(
        prompt(_('You will be asked to answer 3 questions regarding HIV. ' +
            'Answer them correctly and stand a chance to win airtime!'
        ))
    ) \
    .do(
        *shuffle(
            prompt('Can traditional medicine cure HIV/AIDS?', **yes_or_no),
            prompt('Is an HIV test at any government clinic free of charge?', **yes_or_no),
            prompt('Is it possible to test HIV-negative for up to 3-months after becoming HIV-infected?', **yes_or_no),
            prompt('Can HIV be transmitted by sweat?', **yes_or_no),
            prompt('Is there a herbal medication that can cure HIV/AIDS?', **yes_or_no),
            prompt('Does a CD4-count reflect the strength of a person\'s immune system? ', **yes_or_no),
            prompt('Can HIV be transmitted through a mother\'s breast milk?', **yes_or_no),
            prompt('Is it possible for an HIV positive woman to deliver an HIV negative baby?', **yes_or_no)
        )
    )

for step, routine in ms.run(client=ReallyDumbTerminal()):
    print '\n\n' + table('Current state', ms.store.items()) + '\n\n'
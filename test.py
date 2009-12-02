from alexandria.client import ReallyDumbTerminal
from alexandria.core import MenuSystem, prompt
from alexandria.utils import shuffle, table
from alexandria.validators import non_empty_string, integer, pick_one

# items can be grouped together and referred to on the fly
get_personal_info = [
    prompt('What is your name?', validator=non_empty_string),
    prompt('What is your age?', validator=integer), 
    prompt('Where do you live?', validator=non_empty_string)
]


ms = MenuSystem()
ms \
    .do(*get_personal_info) \
    .do(
        # items can be added as arguments to do
        prompt('This is your inbox:', options=(
            'Message 1',
            'Message 2',
            'Message 3',
        ), validator=pick_one)
    ) \
    .do(
        # present items in random order
        *shuffle(
            prompt('How old are you?', validator=integer),
            prompt('What is your favorite food?', validator=pick_one, options=(
                'Apples',
                'Oranges'
            )),
            prompt('What is your favorite colour?', validator=non_empty_string),
        )
    )
    
for step, routine in ms.run(start_at=0, client=ReallyDumbTerminal()):
    # ms is always available at every step, we can track the step we're
    # at with the client and also what state the client is at
    print table('Current state', ms.store.items())
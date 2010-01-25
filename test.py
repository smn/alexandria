from alexandria.client import FakeUSSDClient
from alexandria.core import MenuSystem, prompt, StateKeeper
from alexandria.utils import shuffle, table
from alexandria.validators import non_empty_string, integer, pick_one

# items can be grouped together and referred to on the fly
get_personal_info = [
    prompt('What is your name?', validator=non_empty_string),
    prompt('What is your age?', validator=integer), 
    prompt('Where do you live?', validator=non_empty_string)
]


menu_system = MenuSystem()
menu_system \
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
    

client = FakeUSSDClient('27764493806')
sk = StateKeeper(client, menu_system)
sk.fast_forward(0)
while sk.has_next():
    sk.next()

print table("Menu System state", menu_system.storage.items())

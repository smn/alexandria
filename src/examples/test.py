from alexandria.client import FakeUSSDClient
from alexandria.dsl.core import MenuSystem, prompt
from alexandria.dsl.exceptions import InvalidInputException
from alexandria.dsl.utils import shuffle, table
from alexandria.dsl.validators import non_empty_string, integer, pick_one
import logging

# items can be grouped together and referred to on the fly
get_personal_info = [
    prompt('What is your name?', validator=non_empty_string),
    prompt('What is your age?', validator=integer), 
    prompt('Where do you live?', validator=non_empty_string)
]

menu_system = MenuSystem()
menu_system \
    .append(*get_personal_info) \
    .append(
        # items can be added as arguments to do
        prompt('This is your inbox:', options=(
            'Message 1',
            'Message 2',
            'Message 3',
        ), validator=pick_one)
    ) \
    .append(
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
    

# if __name__ == '__main__':
#     idx = 0
#     for current_item, next_item in iter(menu_system):
#         print table('questions %s' % idx, {
#             'current': current_item.next().split('\n')[0] if current_item else None,
#             'next': next_item.next().split('\n')[0] if next_item else None,
#         }.items())
#         idx += 1

if __name__ == '__main__':
    logging.info(" " * 80)
    logging.info("*" * 80)
    logging.info("STARTING MENU")
    logging.info("*" * 80)
    logging.info(" " * 80)

    client = FakeUSSDClient('27764493806')
    client.process(menu_system)

    # fake the state
    # menu_system.fast_forward(3)
    # menu_system.store('What is your name?', 'smn')
    # menu_system.store('What is your age?', '29')
    # menu_system.store('Where do you live?', 'cpt')

    # for current_item, next_item in iter(menu_system):
    #     # receive answer and pass it to the last question that was asked
    #     answer = client.receive()
    #     logging.debug('received answer: %s' % answer)
    # 
    #     try:
    #         if current_item:
    #             question = current_item.next() # re-read question
    #             logging.debug('answer to "%s" is "%s"' % (question, answer))
    #             current_item.next() # proceed to answer feed manually?
    #             validated_answer = current_item.send(answer) # feed answer
    #             menu_system.store(question, validated_answer)
    #             logging.debug('validated_answer is %s' % str(validated_answer))
    #         else:
    #             logging.debug('no current item to answer to')
    # 
    #         if next_item:
    #             next_question = next_item.next() # read question
    #             logging.debug('getting next question: %s' % next_question)
    #             client.send(next_question)
    #         else:
    #             logging.debug('no next item to ask question, end of menu reached')
    #     except InvalidInputException, e:
    #         logging.exception(e)
    #         current_item = menu_system.repeat_current_item()
    #         repeated_question = current_item.next()
    #         logging.debug('repeating current question: %s' % repeated_question)
    #         client.send(repeated_question)

    print table("Menu System state", menu_system.storage.items())
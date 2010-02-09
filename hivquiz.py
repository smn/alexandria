from alexandria.client import FakeUSSDClient, NothingToDoException
from alexandria.exceptions import InvalidInputException
from alexandria.core import MenuSystem, prompt, coroutine
from alexandria.utils import shuffle, table
from alexandria.validators import non_empty_string, integer, pick_one
from generator_tools.copygenerators import copy_generator

# allow for lazy ugettext based translation like Django does it
_ = lambda s: s

# yes no options
yes_or_no = {
    'options': ('yes','no'),
    'validator': pick_one
}



# @coroutine
def pick_first_unanswered(*prompts):
    # wait for ms & yield question
    # wait for answer
    # yield validated answer or raise error
    prompts = list(prompts)
    cloned_prompts = map(copy_generator, prompts)
    while True:
        ms = yield
        print 'pick_first_unanswered: got menu system', ms
        while cloned_prompts:
            prompt = cloned_prompts.pop()
            prompt.next()
            question = prompt.send(ms)
            if question not in ms.storage:
                print 'pick_first_unanswered, yielding question'
                yield question
                answer = yield
                print 'pick_first_unanswered, got answer', answer
                prompt.next()
                validated_answer = prompt.send(answer)
                print 'validated answer', validated_answer
                yield validated_answer
                


# @coroutine
def test(test_fn, *prompts):
    prompts = map(copy_generator, prompts)
    while True:
        ms = yield
        print 'test: got ms', ms
        if test_fn(ms):
            print 'hmmmm'
            prompt = prompts.pop()
            print 'test: prompt', prompt
            prompt.next()
            question = prompt.send(ms)
            print 'test: question', question
            yield question
            answer = yield
            print 'test: answer', answer
            prompt.next()
            validated_answer = prompt.send(answer)
            print 'test: validated_answer', validated_answer
            yield validated_answer
        else:
            print 'test: %s failed!' % test_fn
            raise NothingToDoException
    


ms = MenuSystem()
ms \
    .do(
        prompt('Thnx 4 taking the Quiz! Answer 3 questions and see how much you know. '
                'Pick your language:', options=(
            'English',
            'Zulu',
            'Afrikaans',
            'Sotho',
        ), validator=pick_one),
        prompt(_('You will be asked to answer 3 questions regarding HIV. '
            'Answer them correctly and stand a chance to win airtime!'
        ))
    ) \
    .do(
        pick_first_unanswered(
            prompt(_('Can traditional medicine cure HIV/AIDS?'), **yes_or_no),
            prompt(_('Is an HIV test at any government clinic free of charge?'), **yes_or_no),
            prompt(_('Is it possible to test HIV-negative for up to 3-months after becoming HIV-infected?'), **yes_or_no),
        )
    ) \
    .do(
        pick_first_unanswered(
            prompt(_('Can HIV be transmitted by sweat?'), **yes_or_no),
            prompt(_('Is there a herbal medication that can cure HIV/AIDS?'), **yes_or_no),
            prompt(_('Does a CD4-count reflect the strength of a person\'s immune system?'), **yes_or_no),
        )
    ) \
    .do(
        pick_first_unanswered(
            prompt(_('Can HIV be transmitted through a mother\'s breast milk?'), **yes_or_no),
            prompt(_('Is it possible for an HIV positive woman to deliver an HIV negative baby?'), **yes_or_no)
        )
    ) \
    .do(
        test(lambda ms: len(ms.storage) == 10, prompt(_('Thank you you\'ve answered all questions!')))
    ) \
    .do(
        test(lambda ms: len(ms.storage) < 10, prompt(_('Dial in again to answer the remaining questions')))
    ) \
    .do(
        prompt(_('For more information about HIV/AIDS please phone the Aids '+
                    'Helpline on 0800012322.  This is a free call from a landline. '+
                    'Normal cell phone rates apply.'))
    )

# # prepopulate answers for testing
# ms.fast_forward()
# ms.storage['Can traditional medicine cure HIV/AIDS?'] = [(1, 'yes')]
# ms.storage['Is an HIV test at any government clinic free of charge?'] = [(1, 'yes')]
# ms.storage['Is it possible to test HIV-negative for up to 3-months after becoming HIV-infected?'] = [(1, 'yes')]
# ms.storage['Can HIV be transmitted by sweat?'] = [(1, 'yes')]
# ms.storage['Is there a herbal medication that can cure HIV/AIDS?'] = [(1, 'yes')]
# ms.storage['Does a CD4-count reflect the strength of a person\'s immune system?'] = [(1, 'yes')]
# ms.storage['Can HIV be transmitted through a mother\'s breast milk?'] = [(1, 'yes')]

if __name__ == '__main__':
    # run through the system
    client = FakeUSSDClient("msisdn")
    client.process(ms)
    
    # 
    # # gen = client.process(ms)
    # for args in client.process(ms):
    #     pass
    #     # print 'client got args', args
    #     # print args
    #     # print 'step: %s, coroutine: %s' % (step, coroutine)
    #     # print 'question: %s, answer: %s' % (question, answer)

    # print summary
    print '\n\n' + table('Current state', ms.storage.items()) + '\n\n'

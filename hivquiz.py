from alexandria.client import ReallyDumbTerminal
from alexandria.core import MenuSystem, prompt, display, coroutine, delay_call
from alexandria.utils import shuffle, table
from alexandria.validators import non_empty_string, integer, pick_one

# allow for lazy ugettext based translation like Django does it
_ = lambda s: s

# yes no options
yes_or_no = {
    'options': ('yes','no'),
    'validator': pick_one
}

@delay_call
@coroutine
def pick_first_unanswered(*prompts):
    prompts = list(prompts)
    while True:
        ms = (yield)
        # it is unanswered if the current prompts' key isn't available in
        # in the MenuSystem's key/value store
        unanswered_prompts = [p for p in prompts if (p.args[0] not in ms.store)]
        while unanswered_prompts:
            prompt = unanswered_prompts[0]
            result = prompt.invoke().send(ms)
            # make sure we get a result
            if result:
                # only remove the prompt if we've got a result, otherwise try again
                unanswered_prompts.remove(prompt)
                yield result
        # always yield True when there are no unanswered_prompts to 
        # prevent getting stuck in a neverending loop
        yield True
    


@delay_call
@coroutine
def test(test_fn, *prompts):
    prompts = list(prompts)
    while True:
        ms = (yield)
        print test_fn
        if test_fn(ms):
            print 'PASS'
            for prompt in prompts:
                yield prompt.invoke().send(ms)
        else:
            print 'FAIL'
        
    


def count_store_entries(ms):
    print len(ms.store)
    result = len(ms.store) == 10
    print 'returning', result
    return result
    

ms = MenuSystem()
ms \
    .do(
        prompt('Thnx 4 taking the Quiz! Answer 3 questions and see how much you know. '+
                'Pick your language:', options=(
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
        test(lambda ms: len(ms.store) == 10, display(_('Thank you you\'ve answered all questions!')))
    ) \
    .do(
        test(count_store_entries, display(_('Dial in again to answer the remaining questions')))
    ) \
    .do(
        display(_('For more information about HIV/AIDS please phone the Aids '+
                    'Helpline on 0800012322.  This is a free call from a landline. '+
                    'Normal cell phone rates apply.'))
    )

# # prepopulate answers for testing
# ms.store['Can traditional medicine cure HIV/AIDS?'] = [True]
# ms.store['Is an HIV test at any government clinic free of charge?'] = [True]
# ms.store['Is it possible to test HIV-negative for up to 3-months after becoming HIV-infected?'] = [True]
# ms.store['Can HIV be transmitted by sweat?'] = [True]
# ms.store['Is there a herbal medication that can cure HIV/AIDS?'] = [True]
# ms.store['Does a CD4-count reflect the strength of a person\'s immune system?'] = [True]
# ms.store['Can HIV be transmitted through a mother\'s breast milk?'] = [True]

if __name__ == '__main__':
    # run through the system
    client = ReallyDumbTerminal("msisdn")
    for args in client.process(ms):
        # print 'client got args', args
        continue
        # print 'step: %s, coroutine: %s' % (step, coroutine)
        # print 'question: %s, answer: %s' % (question, answer)

    # print summary
    print '\n\n' + table('Current state', ms.client.store.items()) + '\n\n'

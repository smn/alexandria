from unittest import TestCase

from alexandria.core import prompt, end, question
from alexandria.utils import msg
from alexandria.validators import pick_one


class MockMenuSystem(object): pass

class AlexandriaTestCase(TestCase):
    """
    Lots of work to be done here.
    """
    pass

class PromptTestCase(TestCase):
    
    def setUp(self):
        self.session_store = {}
        # question & multiple choice answers
        self.question_text = "What is your favorite color?"
        self.question_options = ("red", "white", "blue")
        
    
    def test_numeric_response(self):
        """
        prompt() with a pick_one validator should accept numeric input for the
        menu items
        """
        p = prompt(self.question_text, validator=pick_one, 
                    options=self.question_options)
        # advance coroutine to yield statement, FIXME use coroutine decorator
        p.next()
        question, end_of_session = p.send((MockMenuSystem(), self.session_store))
        
        self.assertEquals(question, msg(self.question_text, 
                            self.question_options))
        self.assertFalse(end_of_session)
        
        # advance again - FIXME this manual advancing is sloppy
        p.next()
        validated_answer = p.send("1")
        self.assertEquals(validated_answer, "red")
        
        # check session store
        self.assertEquals(self.session_store['What is your favorite color?'], 
                            "red")
        
    def test_character_response(self):
        """
        prompt() with a pick_one validator should accept character input 
        that match the menu values for the menu items
        """
        p = prompt(self.question_text, validator=pick_one, 
                    options=self.question_options)
        # advance coroutine to yield statement, FIXME use coroutine decorator
        p.next()
        question, end_of_session = p.send((MockMenuSystem(), self.session_store))
        
        self.assertEquals(question, msg(self.question_text, 
                            self.question_options))
        self.assertFalse(end_of_session)
        
        # advance again - FIXME this manual advancing is sloppy
        p.next()
        validated_answer = p.send("blue")
        self.assertEquals(validated_answer, "blue")
        
        # check session store
        self.assertEquals(self.session_store['What is your favorite color?'], 
                            "blue")

class EndTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def test_end_response(self):
        """
        end() closes off a session with a good bye message. The end_of_message
        boolean flag should be true.
        """
        
        e = end("So long, and thanks for all the fish")
        e.next()
        message, end_of_session = e.send((MockMenuSystem(), {}))
        self.assertEquals(message, "So long, and thanks for all the fish")
        self.assertTrue(end_of_session)

class QuestionTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def test_generated_stack(self):
        """
        The question statement isn't a coroutine, it just generates a bit
        of the stack on the fly for us. This test checks if the generated
        stack is somewhat sane.
        """
        
        question_stack = question('Is your right thumb on your left hand?', {
            'no': 'Please see a doctor and press 1 to continue.',
            'yes': 'Correct! Please press 1 to continue'
        })
        
        [prompt, case] = question_stack
        
        prompt.next() # advance coroutine
        question_text, end_of_session = prompt.send((MockMenuSystem(), {}))
        
        # check that the dictionary keys are correctly translated to options
        # for the prompt
        self.assertEquals(question_text, 
                            msg("Is your right thumb on your left hand?", 
                                options=("yes","no"))) # FIXME strange sorting issue
        
        # Fake the answer by manually setting it in the session
        
        # check that the case statements reflect the options
        case.next()
        response_text, end_of_session = case.send((MockMenuSystem(), {
            "Is your right thumb on your left hand?": "no"
        }))
        self.assertEquals(response_text, "Please see a doctor and press 1 "
                                            "to continue.")
        self.assertFalse(end_of_session)
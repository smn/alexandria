from unittest import TestCase

from alexandria.dsl.core import (MenuSystem, prompt, end, question, 
                                pick_first_unanswered, case)
from alexandria.dsl.utils import msg, coroutine
from alexandria.dsl.validators import pick_one, integer

from alexandria.sessions.manager import SessionManager
from alexandria.sessions.backend import DBBackend
from alexandria.client import Client


class MenuSystemTestCase(TestCase):
    
    def setUp(self):
        self.menu = MenuSystem(
            prompt("Prompt 1"),
            prompt("Prompt 2"),
            prompt("Prompt 3")
        )
    
    def test_cloning(self):
        """The menu system should be able to clone itself without any pass by 
        reference nastiness"""
        menu_clone = self.menu.clone()
        self.assertNotEquals(self.menu, menu_clone)
        self.assertNotEquals(self.menu.stack, menu_clone.stack)
    
    def test_appending(self):
        """
        append() should clone the menu system and append the given items
        """
        menu = self.menu.append(
            prompt("Prompt 4"),
            prompt("Prompt 5")
        )
        self.assertNotEquals(menu, self.menu)
        self.assertEquals(len(menu.stack), 5)
    
    def test_fast_forwarding(self):
        """The menu system should be able to fast forward to any point in the
        stack"""
        
        menu = self.menu.clone()
        self.assertEquals(menu.get_current_index(), 0)
        
        menu.fast_forward(1)
        index, next_prompt = menu.next()
        
        # fast forwarded
        self.assertEquals(index, 2)
        
        # advance
        next_prompt.next()
        
        session_store = {}
        prompt_2, end_of_session = next_prompt.send((menu, session_store))
        self.assertEquals(prompt_2, "Prompt 2")
        self.assertFalse(end_of_session)
    
    def test_repeat_current_item(self):
        """
        repeat_current_item() should repeat the current coroutine by 
        rewiding the stack by 1 and restarting
        """
        
        menu = self.menu.clone()
        
        def _test_repeated_coroutine(index, coroutine):
            # index is always 1 ahead
            self.assertEquals(index, 1)
            # advance
            coroutine.next()
            text, end_of_session = coroutine.send((MenuSystem(), {}))
            self.assertEquals(text, "Prompt 1")
            self.assertFalse(end_of_session)
        
        _test_repeated_coroutine(*menu.next())
        _test_repeated_coroutine(*menu.repeat_current_item())
        
    def test_next_after(self):
        """
        next_after() should return the next prompt coming after the given
        index
        """
        
        menu = self.menu.clone()
        index, prompt = menu.next_after(1)
        self.assertEquals(index, 2)
        
        def _test_coroutine(coroutine):
            # advance
            coroutine.next()
            text, end_of_session = coroutine.send((MenuSystem(), {}))
            self.assertEquals(text, "Prompt 2")
            self.assertFalse(end_of_session)
        
        _test_coroutine(prompt)         # these should both return the same text
        _test_coroutine(menu.stack[1])  # since they should be the same prompt
    
    def test_end_of_stack(self):
        """
        next() should return None for the next item if the end of the stack
        has been reached
        """
        
        menu = self.menu.clone()
        menu.fast_forward(3)
        index, none = menu.next()
        self.assertEquals(index, 4)
        self.assertEquals(none, None)
    
    def test_iteration(self):
        """
        the menu system should support the normal iterator pattern and 
        raise a StopIteration when the end of the stack has been reached
        
        Not sure if this is even useful.
        """
        
        for index, coroutine in iter(self.menu.clone()):
            a,b = index, coroutine
        

class TestingClient(Client):
    
    def __init__(self, id):
        self.outbox = []
        self.id = id
        self.session_manager = SessionManager(client=self, backend=DBBackend())
        self.session_manager.restore()
     
    def send(self, message, end_of_session):
        self.outbox.append((message, end_of_session))
        if end_of_session:
            self.deactivate()
    


class DumbClient(Client):
    
    def __init__(self):
        self.id = "test_client"
        self.session_manager = SessionManager(client=self, backend=DBBackend())
        self.session_manager.restore()
    

class ClientTestCase(TestCase):
    """Testing the generic Client for alexandria"""
    
    def setUp(self):
        pass
    
    def tearDown(self):
        from alexandria.sessions.db.models import Client
        [c.delete() for c in Client.objects.all()]
    
    def test_uuid(self):
        """
        the uuid() should return a dictionary with that can be used to look
        up the last session for the client in the backend. Using dictionary
        because we can then easily expand the key/values into kwargs for 
        Django's ORM.
        
        FIXME: this will probably bite us somewhere
        """
        client = TestingClient("test_client")
        self.assertTrue(isinstance(client.uuid(), dict))
    
    def test_stepping_through_system(self):
        """
        testing the perfect scenario
        """
        
        client = TestingClient("test_client")
        menu = MenuSystem(
            prompt("What is your name?"),
            prompt("What is your favorite color?", 
                validator=pick_one,
                options=(
                "red", "white", "blue"
            )),
            prompt("How old are you?", 
                validator=integer),
            end("Thanks & goodbye!")
        )
        
        
        client.answer("*120*USSD_SHORTCODE#", menu)
        client.answer("Simon de Haan", menu)
        client.answer("red", menu)
        client.answer("29", menu)
        
        self.assertEquals(client.outbox, [
            (msg("What is your name?", ()), False),
            (msg("What is your favorite color?", ("red","white","blue")), False),
            (msg("How old are you?", ()), False),
            (msg("Thanks & goodbye!", ()), True)
        ])
    
    def test_coroutines_returning_nothing(self):
        """
        the client should forward to the next coroutine if a given coroutine 
        does not return a message to return to the client
        """
        
        client = TestingClient("test_client")
        menu = MenuSystem(
            prompt("What is your age?", validator=integer),
            case(
                (lambda ms, session: False, prompt("This should never be displayed"))
            ),
            end("Goodbye!")
        )
        
        client.answer("*120*USSD_SHORTCODE#", menu)
        client.answer("29", menu)
        
        self.assertEquals(client.outbox, [
            ("What is your age?", False),
            ("Goodbye!", True)
        ])
    
    def test_validation(self):
        """
        the client should repeat the same coroutine if validation for the given
        input fails
        """
        client = TestingClient("test_client")
        menu = MenuSystem(
            prompt("What is your favorite color?", 
                validator=pick_one,
                options=(
                "red", "white", "blue"
            )),
            prompt("How old are you?", 
                validator=integer),
            end("Thanks & goodbye!")
        )
        
        client.answer("*120*USSD_SHORTCODE#", menu)
        client.answer("yellow", menu)
        client.answer("red", menu)
        client.answer("twenty nine", menu)
        client.answer("29", menu)
        
        self.assertEquals(client.outbox, [
            (msg("What is your favorite color?", ("red","white","blue")), False), # yellow => repeat
            (msg("What is your favorite color?", ("red","white","blue")), False), # red
            (msg("How old are you?", ()), False), # twenty nine => repeat
            (msg("How old are you?", ()), False), # 29
            (msg("Thanks & goodbye!", ()), True)
        ])
    
    def test_subclassing(self):
        """
        The client's send method must be subclassed
        """
        client = DumbClient()
        menu = MenuSystem(end("thanks!"))
        
        self.assertRaises(NotImplementedError, client.answer, "*120*USSD_SHORTCODE#", menu)
        
    def test_deactivation(self):
        """
        After completing a menu the client should deactivate the session, closing
        it from further use.
        """
        client = TestingClient("test_client")
        menu = MenuSystem(end("thanks!"))
        client.answer("*120*USSD_SHORTCODE#", menu)
        self.assertEquals(client.outbox, [
            ("thanks!", True)
        ])
        
        from alexandria.sessions.db.models import Client as BackendClient
        backend_client = BackendClient.objects.filter(**client.uuid())[0]
        self.assertFalse(backend_client.active)
        

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
        question, end_of_session = p.send((MenuSystem(), self.session_store))
        
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
        question, end_of_session = p.send((MenuSystem(), self.session_store))
        
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
        message, end_of_session = e.send((MenuSystem(), {}))
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
        question_text, end_of_session = prompt.send((MenuSystem(), {}))
        
        # check that the dictionary keys are correctly translated to options
        # for the prompt
        self.assertEquals(question_text, 
                            msg("Is your right thumb on your left hand?", 
                                options=("yes","no"))) # FIXME strange sorting issue
        
        # Fake the answer by manually setting it in the session
        
        # check that the case statements reflect the options
        case.next()
        response_text, end_of_session = case.send((MenuSystem(), {
            "Is your right thumb on your left hand?": "no"
        }))
        self.assertEquals(response_text, "Please see a doctor and press 1 "
                                            "to continue.")
        self.assertFalse(end_of_session)


class CombinedCoroutineTestCase(TestCase):
    """
    Where we test coroutines that are really a combination of other 
    coroutines.
    """
    
    def setUp(self):
        self.session_store = {}
    
    def test_pick_first_unanswered(self):
        """
        pick_first_unanswered() accepts a number of prompts and when called 
        fires off the first prompt() it finds for which the session store does
        not have an entry yet.
        """
        
        pfu = pick_first_unanswered(
                prompt("What is your name?"),
                prompt("What is your age?"),
                prompt("What is your gender?"))
        
        session_store = {
            "What is your name?": "Simon",
            "What is your gender?": "Male"
        }
        
        pfu.next()
        [question_text, end_of_session] = pfu.send((MenuSystem(), session_store))
        
        self.assertEquals(question_text, "What is your age?")
        self.assertFalse(end_of_session)
        
        # advance coroutine
        pfu.next()
        validated_answer = pfu.send("29")
        self.assertEquals(session_store['What is your age?'], '29')
        
        # advance coroutine
        pfu.next()
        empty_response = pfu.send((MenuSystem(), session_store))
        # all prompts have been answered, it should yield False
        self.assertFalse(empty_response)
        
    def test_case_statements(self):
        """
        case() accepts a list of (callback, coroutine) tuples. 
        The callback is given the instance of the menu system and the session 
        store return True or False. 
        """
        
        def test_one(menu_system, session_store):
            return "one" in session_store
        
        def test_two(menu_system, session_store):
            return "two" in session_store
        
        def test_three(menu_system, session_store):
            return "three" in session_store
        
        case_statement = case(
            (test_one, prompt("test one")),
            (test_two, prompt("test two")),
            (test_three, prompt("test three"))
        )
        
        # the first two prompts shouldn't respond with this session store
        session_store = {
            "three": "exists"
        }
        
        # advance
        case_statement.next()
        response_text, end_of_session = case_statement.send(
                                            (MenuSystem(), session_store))
        self.assertEquals(response_text, "test three")
        self.assertFalse(end_of_session)
        
        # advance
        case_statement.next()
        validated_answer = case_statement.send("ok")
        self.assertEquals(validated_answer, "ok")
    
    def test_case_statements_with_no_response(self):
        """
        case() should return False if none of the callbacks return True
        """
        
        case_statement = case(
            (lambda ms, session_store: False, prompt("1")),
            (lambda ms, session_store: False, prompt("2")),
            (lambda ms, session_store: False, prompt("3")),
        )
        
        # advance
        case_statement.next()
        self.assertFalse(any(case_statement.send((MenuSystem(), {}))))

class UtilsTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def test_coroutine_decorator(self):
        """
        the coroutine decorator should automatically advance coroutines
        to their first yield statement; avoiding the initial call to next()
        """
        
        @coroutine
        def test_coroutine():
            while True:
                a = (yield)
                yield "got %s" % a
        
        tc = test_coroutine()
        got_b = tc.send("b")
        
        self.assertEquals(got_b, "got b")
    

class SessionManagerTestCase(TestCase):
    
    def setUp(self):
        
        client = DumbClient()
        self.session = client.session_manager
        self.original_data = self.session.data = {
            "string": "bar",
            "int": "1",
            "list": [1,2,3,4,5],
            "dict": {"di":"ct"}
        }
    
    def test_save_and_restore(self):
        """
        restore() should retrieve the last session for a specific user.
        """
        self.session.save()
        self.session.restore()
        self.assertEquals(self.session.data, self.original_data)
    
    def test_save_and_deactivate_and_restore(self):
        """
        restore() should return an empty session after a save with deactivate=True
        """
        self.session.save(deactivate=True)
        self.session.restore()
        self.assertEquals(self.session.data, {})
    
    def test_save_and_overwrite_existing_key(self):
        """
        save() should overwrite keys that already exist in the database
        
        FIXME: this test is flakey, probably a tell-tale sign of a bad idea
                at a lower level
        """
        self.session.save()
        self.session.data = {
            "string": "foo"
        }
        self.session.save()
        self.assertEquals(self.session.data["string"], "foo")
    


from alexandria.loader.base import YAMLLoader
from alexandria.dsl.utils import dump_menu, msg

class YAMLLoaderTestCase(TestCase):
    
    def setUp(self):
        self.loader = YAMLLoader()
    
    def tearDown(self):
        pass
    
    def test_loading_of_yaml_file(self):
        """
        Just testing loading & getting of menu items, not the content
        of the file.
        """
        menu = self.loader.load_from_file(open('src/alexandria/examples/devquiz.yaml', 'r'))
        self.assertEquals(len(menu.stack), 4)
        self.assertEquals(dump_menu(menu), [
            (msg('What is your favorite programming language?', [
                    'java', 
                    'c', 
                    'python', 
                    'ruby', 
                    'javascript', 
                    'php', 
                    'other']), False),
            (msg('What is your favorite development operating system?', [
                    'windows', 
                    'apple', 
                    '*nix', 
                    'other']), False),
            (msg('What is your favorite development environment?', [
                    'netbeans', 
                    'eclipse', 
                    'vim', 
                    'emacs', 
                    'textmate', 
                    'notepad']), False),
            (msg('Thanks! You have completed the quiz.', []), True)
        ])
    
        
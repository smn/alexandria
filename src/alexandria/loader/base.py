from alexandria.dsl.core import MenuSystem, prompt, end
from alexandria.dsl.validators import pick_one

class Loader(object):
    pass

class Dispatcher(object):
    def create_prompt(self, *args, **kwargs):
        return prompt(*args, validator=pick_one, **kwargs)
    
    def create_end(self, *args, **kwargs):
        return end(*args)
    
    def dispatch(self, key, *args, **kwargs):
        mapping = {
            'question': self.create_prompt,
            'end': self.create_end
        }
        return mapping[key](*args, **kwargs)
    

class YAMLLoader(Loader):
    
    def __init__(self):
        self.dispatcher = Dispatcher()
    
    def load_file(self, fp):
        """Load a menu from the given file"""
        return self.load_string(''.join(fp.readlines()))
    
    def load_dict(self, item):
        """
        Depends on the order of keys, works for YAML but is flakely nontheless
        
        >>> loader = YAMLLoader()
        >>> item = loader.load_dict({
        ...     'question': 'What is your favorite color?',
        ...     'options': ['red','white','blue']
        ... })
        >>> item.next() # manually advance
        >>> item.send((None, {})) # fake feed of menu and session store
        ('What is your favorite color?\\n1: red\\n2: white\\n3: blue', False)
        >>> 
        
        """
        # the first key in the sequence is the key for the dispatcher
        menu_type = item.keys()[0]
        # all other keys are keys for the dispatcher kwargs
        menu_option_keys = item.keys()[1:]
        return self.dispatcher.dispatch(menu_type, item[menu_type], \
            **dict([(key, item[key]) for key in menu_option_keys]))
        
    
    def load_string(self, string):
        """
        Load a menu from a YAML description
        
        >>> loader = YAMLLoader()
        >>> menu = loader.load_string(\"\"\"
        ... - question: What is your favorite color?
        ...   options:
        ...     - red
        ...     - white
        ...     - blue
        ... \"\"\")
        >>> index, item = menu.next()
        >>> index # the index of the next menu
        1
        >>> item.next() # manually advance
        >>> item.send((None, {})) # fake feed of menu and session store
        ('What is your favorite color?\\n1: red\\n2: white\\n3: blue', False)
        >>> 
        
        """
        import yaml
        menu = MenuSystem()
        for item in yaml.safe_load(string):
            menu.append(self.load_dict(item))
        return menu

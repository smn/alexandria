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
        pass
    
    def load_file(self, fp):
        """Load a menu from the given file"""
        return self.load_string(''.join(fp.readlines()))
    
    def load_string(self, string):
        import yaml
        menu = MenuSystem()
        dispatcher = Dispatcher()
        for item in yaml.safe_load(string):
            menu_type = item.keys()[0]
            menu_option_keys = item.keys()[1:]
            menu.append(dispatcher.dispatch(menu_type, item[menu_type], \
                **dict([(key, item[key]) for key in menu_option_keys])))
        return menu

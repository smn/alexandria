class Loader(object):
    
    def load_dict(self, dict):
        pass


class YAMLLoader(Loader):
    
    def __init__(self):
        import yaml
    
    def load_file(self, fp):
        """Load a menu from the given file"""
        return self.load_string(''.join(fp.readlines()))
    
    def load_string(self, string):
        return yaml.safe_load(string)
    

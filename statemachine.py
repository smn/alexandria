class InitializationError(Exception): pass

class StateMachine:
    """A really simple state machine from
     http://www.ibm.com/developerworks/library/l-python-state.html"""
    def __init__(self):
        self.handlers = []
        self.startState = None
        self.endStates = []
    
    def add_state(self, handler, end_state=0):
        self.handlers.append(handler)
        if end_state:
            self.endStates.append(name)
    
    def set_start(self, handler):
        self.startState = handler
    
    def run(self, cargo=None):
        if not self.startState:
            raise InitializationError, "must call .set_start() before .run()"
        if not self.endStates:
            raise InitializationError, "at least one state must be an end_state"
        handler = self.startState
        while 1:
            (newState, cargo) = handler(cargo)
            if newState in self.endStates:
                newState(cargo)
                break
            elif newState not in self.handlers:
                raise RuntimeError, "Invalid target %s" % newState
            else:
                handler = newState

"""
Finite state machine class with the following functions:

- 'add_state', adds a state to the state machine
- 'set_start', sets the start state of the state machine
- 'run', run the state machine from the start state
"""

class StateMachine:

    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []

    def add_state(self, name, handler, end_state=0):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = name.upper()

    def run(self, cargo):
        try:
            handler = self.handlers[self.startState]
        except:
            raise "InitializationError", "must call .set_start() before .run()"
        if not self.endStates:
            raise "InitializationError", "at least one state must be an end_state"

        while True:
            (newState, cargo) = handler(cargo)
            if newState.upper() in self.endStates:
                #print("reached ", newState)
                break
            else:
                handler = self.handlers[newState.upper()]


#https://ai-boson.github.io/mcts/

from vars import *

class Node():
    def __init__(self, state, parent=None):
        self.state = state
        #self.parent_action = parent_action
        self.children = []

        self.value = 0
        self.descendants = 1

        self.parent = parent
        self.visited = False
        # self._results = defaultdict(int)
        # self._results[1] = 0
        # self._results[-1] = 0
        # self._untried_actions = None
        # self._untried_actions = self.untried_actions()
        return
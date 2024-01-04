#https://ai-boson.github.io/mcts/

from vars import *

class MonteCarloTreeSearchNode():
    def __init__(self, state):
        self.state = state
        #self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self.cValue = 0
        self.sValue = 0
        # self._results = defaultdict(int)
        # self._results[1] = 0
        # self._results[-1] = 0
        # self._untried_actions = None
        # self._untried_actions = self.untried_actions()
        return
    
    def getUCB1(self):
        return self.sValue + self.cValue/self.number_of_visits + 2*math.sqrt(math.log(self.parent.number_of_visits)/self._number_of_visits)
    
    def calculateSVALUE(self):



        return

    # def untried_actions(self):
    #     self._untried_actions = self.state.get_legal_actions()
    #     return self._untried_actions

    # def q(self):
    #     wins = self._results[1]
    #     loses = self._results[-1]
    #     return wins - loses

    # def n(self):
    #     return self._number_of_visits

    # def expand(self):
        
    #     action = self._untried_actions.pop()
    #     next_state = self.state.move(action)
    #     child_node = MonteCarloTreeSearchNode(
    #         next_state, parent=self, parent_action=action)

    #     self.children.append(child_node)
    #     return child_node 
    
    # def is_terminal_node(self):
    #     return self.state.is_game_over()
    
    # def rollout(self):
    #     current_rollout_state = self.state
        
    #     while not current_rollout_state.is_game_over():
            
    #         possible_moves = current_rollout_state.get_legal_actions()
            
    #         action = self.rollout_policy(possible_moves)
    #         current_rollout_state = current_rollout_state.move(action)
    #     return current_rollout_state.game_result()
    
    # def backpropagate(self, result):
    #     self._number_of_visits += 1.
    #     self._results[result] += 1.
    #     if self.parent:
    #         self.parent.backpropagate(result)

    # def is_fully_expanded(self):
    #     return len(self._untried_actions) == 0




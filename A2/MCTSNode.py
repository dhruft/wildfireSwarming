#https://ai-boson.github.io/mcts/

from vars import *

class MCTSNode():
    def __init__(self, state, parent=None):
        self.state = state
        #self.parent_action = parent_action
        self.children = []
        self.number_of_visits = 0

        #child value: value due to value of children
        self.cValue = 0

        #self value due to rollout and move to get to the node (don't divide by number of visit in ucb1)
        self.sValue = 0

        self.parent = parent
        self.visited = False
        # self._results = defaultdict(int)
        # self._results[1] = 0
        # self._results[-1] = 0
        # self._untried_actions = None
        # self._untried_actions = self.untried_actions()
        return
    
    def getUCB1(self):
        ## AVOID DIVIDE BY 0 FOR EXPLORATION
        if self.number_of_visits == 0:
                return 999999
        
        #this means that there are no moves from this node or that the UAV ran out of fuel 
        # if self.number_of_visits > 0 and len(self.children) == 0:
        #         return 0
        
        #formula from https://www.youtube.com/watch?v=UXW2yZndl7U
        return self.cValue/self.number_of_visits + 10*math.sqrt(math.log(self.parent.number_of_visits)/self.number_of_visits)

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




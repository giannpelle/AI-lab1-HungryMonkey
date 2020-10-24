import math
import random
from typing import Iterable
import sys

from queue import PriorityQueue

from wumpus import InformedPlayer
from wumpus.gridworld import Eater, EaterWorld, Food, Coordinate

from hungry_monkey_model import HungryMonkeyProblem, HungryMonkeyNode
from hungry_monkey_model import HungryMonkeyState, HungryMonkeyResult


class IDPlayer(InformedPlayer):
    """
    Iterative deepening player to resolve the problem with a IDS 
    """

    def _say(self, text: str):
        print(self.name + ' says: ' + text)
        
    def iterative_deepening_search(self, problem: HungryMonkeyProblem):
        """
        Implementation of the pseudocode found on: 
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Iterative-Deepening-Search.md
        
        cutoff flag is [-1] 
        no admissible solution flag is [-2]    
        """
        for depth in range((problem.map_size.x * problem.map_size.y) - len(problem.block_locations)):
            result = self.depth_limited_search(problem, depth)
            
            print(f"nodes explored: {self.counter}")
            self.counter = 0
            
            if result != [-1]: #-1 is cutoff
                return result
        else:
            return result

    def depth_limited_search(self, problem: HungryMonkeyProblem, depth):
        """
        Implementation of the pseudocode AIMA3e found on:
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Depth-Limited-Search.md
        """
        print("".join(["-" for i in range(40)]), f"Limit Depth ({depth})", "".join(["-" for i in range(40)]))
        
        #if depth == 0:
            #print(f"nodes explored: 0")
        #else:
            #print(f"nodes explored: {self.counter}")
        #self.counter = 0
        
        return self.recursive_dls(HungryMonkeyNode(problem.initial_location, problem.banana_locations), problem, depth, set([HungryMonkeyNode(problem.initial_location, problem.banana_locations)]))
    
    def recursive_dls(self, node: HungryMonkeyNode, problem: HungryMonkeyProblem, limit, explored_nodes):
        self.counter += 1
        self.total_counter += 1
        
        if problem.is_goal_state(node.state):
            return HungryMonkeyResult(problem.unwrap_solution(node), node.path_cost)
        elif limit == 0:
            return [-1]
        else:
            cutoff_occured = False
            childs = [problem.child_node(node, action) for action in problem.available_actions_for(node.state)]
            clean_childs = list(filter(lambda child: child not in explored_nodes, childs))
            
            new_explored_nodes = explored_nodes.copy()
            new_explored_nodes.add(node)
            
            for child in clean_childs:
                result = self.recursive_dls(child, problem, limit - 1, new_explored_nodes)
                
                if result == [-1]:
                    cutoff_occured = True
                elif result != [-2]:
                    return result
            
            if cutoff_occured:
                return [-1]
            else:
                return [-2]
        

    def start_episode(self, world: EaterWorld):
        """
        Print the description of the world before starting.
        """
        # keep track of the reward
        self.reward = 0

        self._say('Episode starting for player {}'.format(self.name))

        # inspect the objects in the world
        food_locations = []
        eater_location = None
        for o in world.objects:
            if isinstance(o, Eater):
                eater_location = Coordinate(o.location.x, o.location.y)
            elif isinstance(o, Food):
                food_locations.append(Coordinate(o.location.x, o.location.y))

        # get the list of blocks
        block_locations = sorted((bl.x, bl.y) for bl in world.blocks)

        # Print the description of the world
        self._say('World size: {}x{}'.format(world.size.x, world.size.y))
        self._say('Eater agent in {}'.format(eater_location))
        self._say('Food in {}'.format(sorted(food_locations)))
        self._say('Blocks in {}'.format(block_locations))

        self._say('Available actions: {}'.format({a.name: a.value for a in Eater.Actions}))
        print("")

        self.counter = 0
        self.total_counter = 0
        hungry_monkey_problem = HungryMonkeyProblem(world, Eater.Actions)
        
        result = self.iterative_deepening_search(hungry_monkey_problem)
        if result == [-1]:
            print("Cutoff occured, so there's no solution to the problem with the given maximum depth")
            return
        elif result == [-2]:
            print("There is no solution for the problem")
            return
        
        self.result_reward = result.total_reward
        self.result_sequence_actions = result.sequence_actions
        
        print("")
        print("".join(["*" for i in range(100)]))
        print(f"The counter of nodes explored is {self.total_counter} (counting from LIMIT = 0)")
        print(f"The action sequence to arrive at the banana is \n{self.result_sequence_actions}\n")
        print(f"The total reward of the search is {self.result_reward}")
        print("".join(["*" for i in range(100)]))
        print("")

    def end_episode(self, outcome: int, alive: bool, success: bool):
        """Method called at the when an episode is completed."""
        self._say('Episode completed, my reward is {}'.format(outcome))

    # random player
    def play(self, turn: int, percept: Eater.Percept, actions: Iterable[Eater.Actions]) -> Eater.Actions:
        return self.result_sequence_actions[turn]

    def feedback(self, action: Eater.Actions, reward: int, percept: Eater.Percept):
        """Receive in input the reward of the last action and the resulting state. The function is called right after the execution of the action."""
        self._say('Moved to {} with reward {}'.format(percept.position, reward))
        self.reward += reward


MAP_STR = """
################
#    #    #    #
#    #    #    #
#    #         #
#    #    #    #
###           ##
"""


def main(*args):
    """
    Play a random EaterWorld episode using the default player
    """

    player_class = IDPlayer

    world = EaterWorld.random(MAP_STR)
    player = player_class('Hungry.Monkey')

    world.run_episode(player, horizon=20)
    
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
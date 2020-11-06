import math
import random
from typing import Iterable
import sys

from queue import PriorityQueue

from wumpus import InformedPlayer
from wumpus.gridworld import Eater, EaterWorld, Food, Coordinate

from hungry_monkey_model import HungryMonkeyProblem, HungryMonkeyNode
from hungry_monkey_model import HungryMonkeyState, HungryMonkeyResult


class AStarPlayer(InformedPlayer):
    """
    AStar cost player to resolve the problem with a A*
    """

    def _say(self, text: str):
        print(self.name + ' says: ' + text)

    def astar_search(self, problem: HungryMonkeyProblem):
        """
        Implementation of the pseudocode UCS AIMA4e found on:
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Uniform-Cost-Search.md
        Added heuristic function and cost to optimize search algorithm
        """
        initial_node = HungryMonkeyNode(problem.initial_location, problem.banana_locations)
        
        if problem.is_goal_state(initial_node.state):
            self.counter+=1
            return HungryMonkeyResult([], 0)
        
        frontier = PriorityQueue()
        frontier.put(initial_node)
        reached = {}
        solution = math.inf
        solution_node = None
        
        while not frontier.empty() and (parent := frontier.get()).path_cost + parent.heuristic_cost < solution:
            successors = [problem.child_node(parent, action) for action in problem.available_actions_for(parent.state)]
            self.counter+=1
            for child in successors:
                child_total_cost = child.path_cost + child.heuristic_cost
                if child not in list(reached) or child_total_cost < reached[child]:
                    reached[child] = child_total_cost
                    frontier.put(child)
                    if problem.is_goal_state(child.state) and child_total_cost < solution:
                        solution = child_total_cost
                        solution_node = child 
        return HungryMonkeyResult(problem.unwrap_solution(solution_node), solution)

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

        def heuristic_func(node: HungryMonkeyNode):
            def manhattan_distance_between(start, destination):
                return abs(destination.x - start.x) + abs(destination.y - start.y)

            return min(goal_distances) if (goal_distances := [manhattan_distance_between(node.state.current_location, banana_location) for banana_location in node.state.remaining_bananas]) else 0

        hungry_monkey_problem = HungryMonkeyProblem(world, Eater.Actions, 1, -10, heuristic_func)
        self.counter = 0

        result = self.astar_search(hungry_monkey_problem)
        self.result_reward = result.total_reward
        self.result_sequence_actions = result.sequence_actions
        
        print("")
        print("".join(["*" for i in range(100)]))
        print(f"The counter of nodes explored is {self.counter}")
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

    player_class = AStarPlayer

    world = EaterWorld.random(MAP_STR)
    player = player_class('Hungry.Monkey')

    world.run_episode(player, horizon=20)
    
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))

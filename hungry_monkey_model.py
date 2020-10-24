from collections import namedtuple

from wumpus.gridworld import Eater, EaterWorld, Food, Coordinate

# (Coordinate, [Coordinate])
# Named tuple to define the state of the hungry monkey game
HungryMonkeyState = namedtuple("HungryMonkeyState", "current_location remaining_bananas")

# ([Eater.Action], number)
# Named tuple to define the end result of the search
HungryMonkeyResult = namedtuple("HungryMonkeyResult", "sequence_actions total_reward")

class HungryMonkeyNode(object):
    """
    Represent a node of the problem with: 
    - state: HungryMonkeyState -> (Coordinate, [Coordinate])
            represent the state of the node with the location of the agent (monkey) and the remaining goals (bananas)
    - path_cost: number 
            is the cost it takes to get to the node from the initial node applying previous_action, to all the parents
    - previous_action: Eater.Action
            action that has to be applied to get from parent to the actual node
    - parent: HungryMonkeyNode
            parent node of the actual node
    - heuristic_cost: number
            is the value of the heuristic function to reach the goal
    """

    def __init__(self, current_location: Coordinate, remaining_bananas, path_cost=0, previous_action=None, parent=None, heuristic_cost=0):
        self.state = HungryMonkeyState(Coordinate(current_location.x, current_location.y), remaining_bananas)
        self.path_cost = path_cost
        self.previous_action = previous_action
        self.parent = parent
        self.heuristic_cost = heuristic_cost

    def __hash__(self):
        """"
        Determines the uniqueness of an  HungryMonkeyNode object. 
        Nodes should have same hash if they represent same state, meanwhile other attributes can differ.
        """
        return hash((self.state.current_location.x, self.state.current_location.y, frozenset(self.state.remaining_bananas)))

    def __eq__(self, other):
        """
        It's been called every time there is the need to compare 2 objects of type HungryMonkeyNode. 
        It is used to prevent the search algorithm from exploring the nodes that have already been visited. 
        (To avoid infinite loops)
        """
        return self.state.current_location.x == other.state.current_location.x and \
               self.state.current_location.y == other.state.current_location.y and \
               self.state.remaining_bananas == other.state.remaining_bananas
    
    def __lt__(self, other):
        """
        It's been called to define an order between 2 objects of type HungryMonkeyNode like in the PriorityQueue.
        Order is determined by the sum of path cost and heuristic cost. In case of a tie we choose the state with 
        fewer remaining goals (bananas).
        """
        if self.path_cost + self.heuristic_cost == other.path_cost + other.heuristic_cost:
            return len(self.state.remaining_bananas) < len(other.state.remaining_bananas)
        return self.path_cost + self.heuristic_cost < other.path_cost + other.heuristic_cost
    

class HungryMonkeyProblem(object):
    """
    Is the formal representation of the hungry monkey problem in general:
    - map_size: Coordinate
            represents width (x) and heigth (y) of the world grid 
    - initial_location: Coordinate
            represent the initial location of the agent (monkey)
    - block_locations: [Coordinate]
            represent a list of all blocks in the world grid
    - banana_locations: set{Coordinate}
            represent a set of all goals (bananas) in the world grid
    - step_cost: number
            contains the cost of a single movement in the world grid
    - banana_reward: number
            contains the reward for reaching a goal (banana)
    - possible_actions: [Eater.Action]
            contains all possible actions in the world grid, like N, S, E, W
    - heuristic_func: function(HungryMonkeyNode) -> number
            a function that returns the value of the heuristic based on the node
    """
  
    def __init__(self, world: EaterWorld, possible_actions, step_cost = -1, banana_reward = 10, heuristic_func = lambda x: 0):
        """
        maps the EaterWorld to an instance of a problem
        """

        food_locations = []
        eater_location = None
        for o in world.objects:
            if isinstance(o, Eater):
                eater_location = Coordinate(o.location.x, o.location.y)
            elif isinstance(o, Food):
                food_locations.append(Coordinate(o.location.x, o.location.y))

        # get the list of blocks
        block_locations = sorted((bl.x, bl.y) for bl in world.blocks)
        
        self.map_size = world.size
        self.initial_location = eater_location
        self.block_locations = block_locations
        self.banana_locations = set(food_locations)
        self.step_cost = step_cost
        self.banana_reward = banana_reward
        self.possible_actions = list(possible_actions)
        self.heuristic_func = heuristic_func
        
        
    def is_inside_grid_map(self, location: Coordinate):
        """
        returns a boolean indicating if the given location is inside the grid world 
        """
        return (0 <= location.x and location.x < self.map_size.x) and (0 <= location.y and location.y < self.map_size.y)

    def available_actions_for(self, state):
        """
        filters out all illegal actions for given state (like moving out of grid or on to a block)
        from the possible actions defined in the problem and returns the list of legal actions
        """
        available_actions = []
        for action in self.possible_actions:
            future_location = Coordinate(state.current_location.x + action.value[0], state.current_location.y + action.value[1])
            if self.is_inside_grid_map(future_location) and future_location not in self.block_locations:
                available_actions.append(action)
        return available_actions
    
    def successor(self, state, action):
        """
        returns the successor HungryMonkeyState resulting from applying the given action on the given state
        """
        if action not in self.available_actions_for(state):
            return (state.current_location, state.remaining_bananas)

        new_location = Coordinate(state.current_location.x + action.value[0], state.current_location.y + action.value[1])
        
        new_remaining_bananas = []
        for banana in state.remaining_bananas:
            if not (banana.x == new_location.x and banana.y == new_location.y):
                new_remaining_bananas.append(banana)
        return HungryMonkeyState(new_location, new_remaining_bananas)

    def is_goal_state(self, state):
        """
        returns True if the list of goals (bananas) is empty
        """
        return not state.remaining_bananas

    def child_node(self, node: HungryMonkeyNode, action):
        """
        returns the child HungryMonkeyNode resulting from applying the given action on the given node
        """
        def path_cost(state, action, next_state): 
            """
            private function to calculate the path cost to go from state -> next_state with the given action
            """
            return self.step_cost if next_state.current_location not in state.remaining_bananas else self.step_cost + self.banana_reward
        
        next_state = self.successor(node.state, action)
        path_cost = path_cost(node.state, action, next_state) 
        
        return HungryMonkeyNode(next_state.current_location, next_state.remaining_bananas, node.path_cost + path_cost, action, node, self.heuristic_func(HungryMonkeyNode(next_state.current_location, next_state.remaining_bananas)))
    
    def unwrap_solution(self, node: HungryMonkeyNode):
        """
        returns all actions performed from the initial_node to the given node
        """
        result_actions = []
        current_parent = node
        
        while current_parent.previous_action != None:
            result_actions.append(current_parent.previous_action)
            current_parent = current_parent.parent
            
        result_actions.reverse()
        return result_actions
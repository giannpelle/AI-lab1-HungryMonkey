# AIMA 2020 Assignment 1 - Hungry Monkey

This repository contains the group work submitted for the Assignment 1 of the [AIMA 2020](https://ole.unibz.it/course/view.php?id=6841) course from the Free University of Bozen-Bolzano.

## Problem description

The problem introduced by the assignment is to find the **best sequence of actions** to make the *agent* (a monkey) reaching all *goals* (bananas) in the given environment: in this case it was a *grid map*, with some obstacles (blocks) inside the grid map.  
An example of the **world environment** is shown below:  

<img src="/images/hungry_monkey.gif"  width="300">

The *agent* can only move north, east, south or west (with the corresponding actions {N, E, S, W}) each costing 1. If you reach a banana you get a reward of 10, and if you bump into an obstable or the border of the map you just stay still.

## Technical description

The assignment requires the development of an **offline search** (in a known and fully visible world) to perform at the start of the game which has to return the sequence of actions to play the game in an optimal way.  
Three different types of search techniques are required:
* __Uninformed search__:
  1. Iterative Deepening Search (IDS)
  2. Uniform Cost Search (UCS)
* __Informed search__:
  1. A* search (with a custom heuristic function to be passed as input)
  
## Solution outputs

If you want to see the results (outputs) we got from running the different kind of search techniques just look at the [sample outputs](https://github.com/giannpelle/AI-lab1-HungryMonkey/tree/master/sample-outputs) directory.
Otherwise, if you want to run them yourself, go straight to the next section.

## Running requirements

To run the code you have to create an *anaconda* environment with the configuration file found in *environment.yml* and then activate it to run the code.  
The required commands to make it work are the following:
1. `conda create env -f environment.yml`
2. `conda activate aima_search`
3. `jupyter lab`

To run the sample code you just need to run the code cells in the files *IDS-sample.ipynb*, *UCS-sample.ipynb* and *AStar-sample.ipynb*.

## Development summary

We modeled the formal definition of the problem in the **HungryMonkeyProblem** class, including:

- initial state
- possible actions
- applicable actions (for the given state)
- transition model (with a successor function)
- a function to calculate the sequence of actions/nodes to reach the current state
- goal test
- path cost function to determine the cost of a given action

Then we defined a **HungryMonkeyNode** class to keep track of the state, path and cost of the node while performing the search.

Eventually, we made an **InformedPlayer** subclass for each search algorithm requested and we implemented the *pseudocode* of each of them correctly adding the appropriate checks whether a node had already been explored to avoid the algorithm from exploring circular loops over and over.  
That way we developed the *graph-state search*, which is way more efficient than the *tree-state search*. 

## Final Results

We measured the efficiency of each different search technique based on the total number of nodes explored until an optimal solution was found. 

Environment | IDS | UCS | A*(*)
------ | ------ | ------ | ------
world0 | 115 nodes | 37 nodes | 7 nodes
world1 | 874 nodes | 102 nodes | 14 nodes
world2 | 17'887 nodes | 192 nodes | 28 nodes
world3 | 171'692'518 nodes | 431 nodes | 94 nodes
world4 | unknown | 3'923 nodes | 878 nodes
world5 | unknown | 1'053 nodes | 240 nodes

(*) euristic function:  
manhattan distance between the agent and the closest goal among the remaining ones (\*\*)

(\*\*) EDIT 8 Nov 2020: we found out that the heuristic is actually not admissible, so the A* algorithm will not return an optimal solution to the problem


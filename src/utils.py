import time
import random
import heapq
from collections import namedtuple, deque

algorithm = namedtuple('Algorithm', ['name', 'func'])

class Board:
    @staticmethod
    def translate_to_2D(index):
        """Returns a tuple of 2D coordinate equivalent"""
        return index // 3, index % 3
    
    @staticmethod
    def manhattan_distance(x1, y1, x2, y2):
        """Returns a manhattan distance between two points"""
        return abs(x1 - x2) + abs(y1 - y2)
    
    @staticmethod
    def valid_actions(state):
        """Generates valid actions of a given state"""
        blank_index = state.index(0)
        if blank_index > 2:
            yield 'U'
        if blank_index < 6:
            yield 'D'
        if blank_index % 3 > 0:
            yield 'L'
        if blank_index % 3 < 2:
            yield 'R'
    
    @staticmethod
    def transform(state, action):
        """Returns a new instance of a state when an action is applied"""
        state = [*state]
        blank_index = state.index(0)
        match action:
            case 'U':
                state[blank_index], state[blank_index - 3] = state[blank_index - 3], state[blank_index]
            case 'D':
                state[blank_index], state[blank_index + 3] = state[blank_index + 3], state[blank_index]
            case 'L':
                state[blank_index], state[blank_index - 1] = state[blank_index - 1], state[blank_index]
            case 'R':
                state[blank_index], state[blank_index + 1] = state[blank_index + 1], state[blank_index]
        return tuple(state)
    
    @staticmethod
    def inversions(state):
        """Returns the inversion sum of a state"""
        inversion_sum = 0
        for i in range(9):
            for j in range(i + 1, 9):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inversion_sum += 1
        return inversion_sum
    
    @staticmethod
    def is_solvable(state):
        """Checks if a state is solvable or not"""
        return Board.inversions(state) % 2 == 0
    
    @staticmethod
    def create_solvable_state():
        """Returns a random solvable state"""
        state = [*range(9)]
        while True:
            random.shuffle(state)
            if Board.is_solvable(state):
                return tuple(state)
    
    @staticmethod
    def solve(state, func):
        """Returns the solution of a state given a search algorithm"""
        board_node = BoardNode(state)

        start_time = time.time()
        final_node, nodes_expanded, distance_traversee_max = func(board_node)
        final_time = time.time()

        path_to_goal = final_node.actions()
        time_elasped = final_time - start_time

        return path_to_goal, nodes_expanded, distance_traversee_max, time_elasped

    @staticmethod
    def draw(state):
        """affichage par chaines"""
        return '{} {} {}\n{} {} {}\n{} {} {}'.format(*state)

class Node:
    def __init__(self, parent=None, depth=0):
        self.parent = parent
        self.depth = depth
        self.nodes = []

    def ajouter_node(self, node):
        """ajouts des nodes au fils des nodes fils"""
        self.nodes.append(node)

    def iterer_precedeurs(self):
        """generation des precedents"""
        curr_node = self
        while curr_node:
            yield curr_node
            curr_node = curr_node.parent

class BoardNode(Node):
    def __init__(self, state, action=None, parent=None, depth=0):
        super().__init__(parent, depth)
        self.state = state
        self.action = action
        self.goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.fonct_heuristique = Board.manhattan_distance

    def cost(self):
        """calcul de h(n) et f(n)"""
        somme_heuristique = 0
        for index, item in enumerate(self.state):
            curr_x, curr_y = Board.translate_to_2D(index)
            goal_x, goal_y = Board.translate_to_2D(self.goal.index(item))
            somme_heuristique += self.fonct_heuristique(curr_x, curr_y, goal_x, goal_y)
        if Board.algo_utilisee == "F":
            return somme_heuristique + self.depth
        else:
            return somme_heuristique

    def expand(self):
        """Expantion"""
        if not self.nodes:
            for action in Board.valid_actions(self.state):
                self.ajouter_node(BoardNode(
                    Board.transform(self.state, action),
                    parent=self,
                    action=action,
                    depth=self.depth + 1
                    ))

    def actions(self):
        """retourner tout les etats"""
        return tuple(node.action for node in self.iterer_precedeurs())[-2::-1]

    def is_goal(self):
        return self.state == self.goal

    def __lt__(self, other):
        return self.cost() < other.cost()

    def __eq__(self, other):
        """verification du cout en utilisant cost"""
        return self.cost() == other.cost()

    def __str__(self):
        """representation de letat"""
        return Board.draw(self.state)

    def __repr__(self):
        return f'Board(state={self.state}, action={self.action}, depth={self.depth})'


def A_STAR(node_depart):
    Board.algo_utilisee = "F"
    ouvert = []
    explored_nodes = set()
    nodes_expanded = 0
    distance_traversee_max = 0

    heapq.heappush(ouvert, node_depart)

    while ouvert:
        node = heapq.heappop(ouvert)
        explored_nodes.add(node.state)

        if node.is_goal():
            return node, nodes_expanded, distance_traversee_max

        node.expand()
        nodes_expanded += 1

        for voisin in node.nodes:
            if voisin.state not in explored_nodes:
                heapq.heappush(ouvert, voisin)
                explored_nodes.add(voisin.state)

                if voisin.depth > distance_traversee_max:
                    distance_traversee_max = voisin.depth

    return None

def BEST_FIRST(node_depart):
    """Returns the goal node"""
    Board.algo_utilisee = "H"
    ouvert = []
    fermee = set()
    nodes_expanded = 0
    distance_traversee = 0

    heapq.heappush(ouvert, node_depart)

    while ouvert:
        node = heapq.heappop(ouvert)
        fermee.add(node.state)
        if node.is_goal():
            return node, nodes_expanded, distance_traversee
        node.expand()
        nodes_expanded += 1
        for voisin in node.nodes:
            if voisin.state not in fermee:
                heapq.heappush(ouvert, voisin)
                fermee.add(voisin.state)

                if voisin.depth > distance_traversee:
                    distance_traversee = voisin.depth
    return None



def HC(node_depart):
    Board.algo_utilisee = "H"
    ouvert = []
    fermee = set()
    nodes_expanded = 0
    distance_traversee = 0

    heapq.heappush(ouvert, node_depart)
    closest = 100
    while ouvert:
        node = heapq.heappop(ouvert)
        fermee.add(node.state)
        if node.is_goal() :
            print("FOUND")
            return node, nodes_expanded, distance_traversee
        node.expand()
        nodes_expanded += 1
    # Evaluate neighbors and add only the best one with the lowest cost
        best_neighbor = node
        best_neighbor_cost = 1000  # Initialize with positive infinity
        
        for voisin in node.nodes:
            if voisin.state not in fermee:
                neighbor_cost = voisin.cost()  # Evaluate neighbor's cost
                if neighbor_cost < best_neighbor_cost:  # Check for lower cost
                    best_neighbor = voisin
                    best_neighbor_cost = neighbor_cost
                    if closest> best_neighbor_cost:
                        closest = best_neighbor_cost
        if best_neighbor_cost == 1000:
            print("closest:",closest)
            return node, nodes_expanded, distance_traversee
        heapq.heappush(ouvert, best_neighbor)
        fermee.add(best_neighbor.state)


        if voisin.depth > distance_traversee:
            distance_traversee = best_neighbor.depth

    return None  # No solution found


if __name__ == '__main__':
    # start state
    start_state = Board.create_solvable_state()
    print('Start state:')
    print(Board.draw(start_state))

    # solved using HC
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elasped = Board.solve(start_state, BEST_FIRST)

    print(f'Done in {round(time_elasped, 4)} second(s) with {len(path_to_goal)} moves using BEST_FIRST')
    print(f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
    print('Actions:', *path_to_goal)

    # solved using A*
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elasped = Board.solve(start_state, A_STAR)

    print(f'Done in {round(time_elasped, 4)} second(s) with {len(path_to_goal)} moves using A*')
    print(f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
    print('Actions:', *path_to_goal)
    # solved using hc
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elasped = Board.solve(start_state, HC)
    print(f'Done in {round(time_elasped, 4)} second(s) with {len(path_to_goal)} moves using HCL')
    print(f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
    print('Actions:', *path_to_goal)

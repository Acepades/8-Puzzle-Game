import time
import random
import heapq
from collections import namedtuple, deque

algorithm = namedtuple('Algorithm', ['name', 'func'])

class Board:
    @staticmethod
    def translate_to_2D(index):
        return index // 3, index % 3
    
    @staticmethod
    def manhattan_distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    
    @staticmethod
    def valid_actions(state):
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
        inversion_sum = 0
        for i in range(9):
            for j in range(i + 1, 9):
                if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                    inversion_sum += 1
        return inversion_sum
    
    @staticmethod
    def is_solvable(state):
        return Board.inversions(state) % 2 == 0
    
    @staticmethod
    def create_solvable_state():
        state = [*range(9)]
        while True:
            random.shuffle(state)
            if Board.is_solvable(state):
                return tuple(state)
    
    @staticmethod
    def solve(state, func):
        board_node = BoardNode(state)
        
        start_time = time.time()
        final_node, nodes_expanded, max_search_depth = func(board_node)
        final_time = time.time()
        
        path_to_goal = final_node.actions()
        time_elasped = final_time - start_time
        
        return path_to_goal, nodes_expanded, max_search_depth, time_elasped
    
    @staticmethod
    def draw(state):
        return '{} {} {}\n{} {} {}\n{} {} {}'.format(*state)

class Node:
    def __init__(self, parent=None, depth=0):
        self.parent = parent
        self.depth = depth
        self.nodes = []
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def iterate_ancestors(self):
        curr_node = self
        while curr_node:
            yield curr_node
            curr_node = curr_node.parent

class BoardNode(Node):
    def __init__(self, state, action=None, parent=None, depth=0):
        super().__init__(parent, depth)
        self.state = state
        self.action = action
        self.goal = tuple(range(9)) #(1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.heuristic_func = Board.manhattan_distance
    
    def cost(self):
        heuristic_sum = 0
        for index, item in enumerate(self.state):
            curr_x, curr_y = Board.translate_to_2D(index)
            goal_x, goal_y = Board.translate_to_2D(self.goal.index(item))
            heuristic_sum += self.heuristic_func(curr_x, curr_y, goal_x, goal_y)
        return heuristic_sum + self.depth
    
    def expand(self):
        if not self.nodes:
            for action in Board.valid_actions(self.state):
                self.add_node(BoardNode(
                    Board.transform(self.state, action),
                    parent=self,
                    action=action,
                    depth=self.depth + 1
                    ))
    
    def actions(self):
        return tuple(node.action for node in self.iterate_ancestors())[-2::-1]
    
    def is_goal(self):
        return self.state == self.goal
    
    def __lt__(self, other):
        return self.cost() < other.cost()
    
    def __eq__(self, other):
        return self.cost() == other.cost()
    
    def __str__(self):
        return Board.draw(self.state)
    
    def __repr__(self):
        return f'Board(state={self.state}, action={self.action}, depth={self.depth})'

def A_STAR(start_node):
    frontier = []
    explored_nodes = set()
    nodes_expanded = 0
    max_search_depth = 0
    
    heapq.heappush(frontier, start_node)
    
    while frontier:
        node = heapq.heappop(frontier)
        explored_nodes.add(node.state)
        
        if node.is_goal():
            return node, nodes_expanded, max_search_depth
        
        node.expand()
        nodes_expanded += 1
        
        for neighbor in node.nodes:
            if neighbor.state not in explored_nodes:
                heapq.heappush(frontier, neighbor)
                explored_nodes.add(neighbor.state)
                
                if neighbor.depth > max_search_depth:
                    max_search_depth = neighbor.depth
    
    return None


def BFS(start_node):
    frontier = deque()
    explored_nodes = set()
    nodes_expanded = 0
    max_search_depth = 0
    
    frontier.append(start_node)
    
    while frontier:
        node = frontier.popleft()
        explored_nodes.add(node.state)
        
        if node.is_goal():
            return node, nodes_expanded, max_search_depth
        
        node.expand()
        nodes_expanded += 1
        
        for neighbor in node.nodes:
            if neighbor.state not in explored_nodes:
                frontier.append(neighbor)
                explored_nodes.add(neighbor.state)
                
                if neighbor.depth > max_search_depth:
                    max_search_depth = neighbor.depth
    
    return None

if __name__ == '__main__':
    # start state
    start_state = Board.create_solvable_state() #(8, 6, 7, 2, 5, 4, 3, 0, 1)
    print('Start state:')
    print(Board.draw(start_state))
    
    # solved using A*
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elasped = Board.solve(start_state, A_STAR)
    
    print(f'Done in {round(time_elasped, 4)} second(s) with {len(path_to_goal)} moves using A*')
    print(f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
    print('Actions:', *path_to_goal)
    
    # solved using BFS
    print('\nFinding solution...')
    path_to_goal, nodes_expanded, max_search_depth, time_elasped = Board.solve(start_state, BFS)
    
    print(f'Done in {round(time_elasped, 4)} second(s) with {len(path_to_goal)} moves using BFS')
    print(f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
    print('Actions:', *path_to_goal)

from collections import deque
from random import shuffle
from time import time

from config import UP, DOWN, LEFT, RIGHT

def get_transformed_state(state, action, empty_value=0):
    index = state.index(empty_value)
    new_state = state[:]
    
    if action == UP:
        new_state[index], new_state[index - 3] = new_state[index - 3], new_state[index]
    
    elif action == DOWN:
        new_state[index], new_state[index + 3] = new_state[index + 3], new_state[index]
    
    elif action == LEFT:
        new_state[index], new_state[index - 1] = new_state[index - 1], new_state[index]
    
    elif action == RIGHT:
        new_state[index], new_state[index + 1] = new_state[index + 1], new_state[index]
    
    return new_state

def get_possible_actions(state, empty_value=0):
    index = state.index(empty_value)
    
    if index >= 3:
        yield UP
    
    if index <= 5:
        yield DOWN
    
    if index % 3 > 0:
        yield LEFT
    
    if index % 3 < 2:
        yield RIGHT

def get_possible_states(state, empty_value=0):
    possible_actions = get_possible_actions(state)
    return (get_transformed_state(state, action, empty_value) for action in possible_actions)

def get_breadth_first_shortest_path(start_state, final_state, controller=None):
    initial_path = [start_state]
    
    if start_state == final_state:
        return initial_path
    
    visited_states = set()
    queue = deque()
    queue.append(initial_path)
    
    while queue:
        if controller:
            if controller.is_stopped:
                break
        
        path = queue.popleft()
        state = path[-1]
        
        if not str(state) in visited_states:
            visited_states.add(str(state))
            neighboring_states = get_possible_states(state)
            
            for neighbor in neighboring_states:
                new_path = path + [neighbor]
                
                if neighbor == final_state:
                    return new_path
                
                queue.append(new_path)
    
    return None

def get_inversion_count(state, empty_value=0):
	inversion_count = 0
	for i in range(9):
		for j in range(i + 1, 9):
			if state[i] != empty_value and state[j] != empty_value and state[i] > state[j]:
				inversion_count += 1
	return inversion_count

def is_solvable(state):
    inversion_count = get_inversion_count(state)
    return inversion_count % 2 == 0

def get_random_solvable_state():
    state = list(range(9))
    while True:
        shuffle(state)
        if is_solvable(state):
            return state

if __name__ == '__main__':
    start_state = [8, 6, 7, 2, 5, 4, 3, 0, 1]    # one of the most difficult puzzle instances with 31 moves
    final_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    
    start = time()
    solution = get_breadth_first_shortest_path(start_state, final_state)
    end = time()
     
    print('Solution:')
    for count, state in enumerate(solution, 1):
        print(f'{count:02d} {state}')
    
    print(f'Done in {round((end - start), 2)} second(s) with {len(solution) - 1} moves')

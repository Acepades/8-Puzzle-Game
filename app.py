import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from time import time, sleep
from threading import Thread
from config import *
from utils import *

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('8-Puzzle Game')
        self.geometry('750x750')
        self.resizable(False, False)
        self.iconbitmap('assets/images/app.ico')
        self.protocol('WM_DELETE_WINDOW', lambda: os._exit(0))
        
        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.show_frame(PuzzlePage, **BASIC_FRAME_PROPERTIES)
    
    def show_frame(self, page, *args, **kwargs):
        frame = page(self.container, self, *args, **kwargs)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.tkraise()

class PuzzlePage(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.controller = controller
        
        self.display_widgets()
    
    def display_widgets(self):
        self.frame_title = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_title.pack(pady=25)
        
        self.label_heading = tk.Label(self.frame_title, **HEADING_LABEL_PROPERTIES)
        self.label_heading.pack()
        
        self.label_subheading = tk.Label(self.frame_title, **SUBHEADING_LABEL_PROPERTIES)
        self.label_subheading.pack()
        
        self.frame_puzzle = Puzzle(self, **BASIC_FRAME_PROPERTIES)
        self.frame_puzzle.pack(padx=10, pady=10)
        
        self.frame_buttons = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_buttons.pack(pady=20)
        
        self.button_solve = tk.Button(self.frame_buttons, text='solve', command=lambda: self.frame_puzzle.solve_board(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_solve.grid(row=0, column=0, padx=10, pady=10)
        
        self.button_stop = tk.Button(self.frame_buttons, text='stop', command=lambda: self.frame_puzzle.stop_solution(), **SECONDARY_BUTTON_PROPERTIES)
        self.button_stop.grid(row=0, column=1, padx=10, pady=10)
        
        self.button_shuffle = tk.Button(self.frame_buttons, text='shuffle', command=lambda: self.frame_puzzle.shuffle_board(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_shuffle.grid(row=0, column=2, padx=10, pady=10)
        
        self.button_reset = tk.Button(self.frame_buttons, text='reset', command=lambda: self.frame_puzzle.reset_board(), **SECONDARY_BUTTON_PROPERTIES)
        self.button_reset.grid(row=0, column=3, padx=10, pady=10)

class Puzzle(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.moves = 0
        self.board = []
        self.saved_board_state = list(range(9))
        self.current_board_state = list(range(9))
        self.target_board_state = list(range(9))
        self.tile_images = [ImageTk.PhotoImage(Image.open(f'assets/images/tile_{n}.png')) for n in range(9)]
        
        self.is_stopped = False
        self.is_solving = False
        self.is_done = False
        
        self.display_widgets()
    
    def display_widgets(self):
        self.label_moves = tk.Label(self, text=f'Moves: {self.moves}', **TEXT_LABEL_PROPERTIES)
        self.label_moves.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.label_status = tk.Label(self, text=f'Playing...', **TEXT_LABEL_PROPERTIES)
        self.label_status.grid(row=0, column=1, sticky='e', padx=10, pady=5)
        
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=1, columnspan=2, sticky='ew', pady=10)
        
        self.frame_board = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_board.grid(row=2, columnspan=2)
        
        self.initialize_board()
        
        self.shuffle_board()
    
    def initialize_board(self):
        for index in range(9):
            self.board.append(tk.Button(self.frame_board, **TILE_BUTTON_PROPERTIES))
            self.board[index].grid(row=index // 3, column=index % 3, padx=10, pady=10)
    
    def populate_board(self, state, empty_value=0):
        for tile_index, tile_value in enumerate(state):
            self.board[tile_index].configure(
                    image=self.tile_images[tile_value],
                    text=tile_value,
                    state='normal',
                    command=lambda tile_index=tile_index: self.swap_click(tile_index, empty_value)
                )
            
            if tile_value == empty_value:
                self.board[tile_index].configure(state='disabled')
            
            self.current_board_state[tile_index] = tile_value
    
    def set_state(self, state, delay_time=0, empty_value=0):
        current_index = self.current_board_state.index(empty_value)
        new_index = state.index(empty_value)
        
        first_tile = self.board[current_index]
        second_tile = self.board[new_index]
        
        first_tile_properties = self.get_tile_property(first_tile)
        second_tile_properties = self.get_tile_property(second_tile)
        
        self.set_tile_property(first_tile, second_tile_properties)
        self.set_tile_property(second_tile, first_tile_properties)
        
        self.current_board_state = state[:]
        
        if not self.is_done:
            self.update_moves(self.moves + 1)
        
        sleep(delay_time)
    
    def get_tile_property(self, tile):
        return {
            'text': tile.cget('text'),
            'background': tile.cget('background'),
            'image': tile.cget('image'),
            'state': tile.cget('state')
        }
    
    def set_tile_property(self, tile, properties):
        tile.configure(**properties)
    
    def update_moves(self, moves):
        self.moves = moves
        self.label_moves.configure(text=f'Moves: {self.moves}')
    
    def update_status(self, status):
        self.label_status.configure(text=status)
    
    def reset_board(self):
        self.stop_solution()
        self.is_stopped = False
        self.is_done = False
        self.update_moves(0)
        self.update_status('Playing...')
        self.populate_board(state=self.saved_board_state)
    
    def shuffle_board(self):
        self.saved_board_state = get_random_solvable_state()
        self.reset_board()
    
    def solve_board(self):
        if not self.is_solving:
            self.reset_board()
            self.solution_thread = Thread(target=self.run_solution)
            self.solution_thread.start()
    
    def stop_solution(self):
        if self.is_solving and not self.is_stopped:
            self.is_stopped = True
            self.is_solving = False
            sleep(0.75)
    
    def run_solution(self):
        self.is_solving = True
        self.update_status('Solving...')
        
        print('\nFinding solution...')
        
        start = time()
        solution = get_breadth_first_shortest_path(self.current_board_state, self.target_board_state, self)
        end = time()
        
        if not self.is_stopped:
            print(f'Done in {round((end - start), 2)} second(s) with {len(solution) - 1} moves')
        else:
            print('Stopped')
        
        if solution != None and not self.is_stopped:
            print('\nMoving board...')
            self.update_status('Moving...')
            
            delay_time = 0.75
            sleep(delay_time)
            
            for move in solution[1:]:
                if self.is_stopped:
                    print('Stopped')
                    self.update_status('Playing...')
                    break
                else:
                    self.set_state(move, delay_time)
            else:
                print('Done animation')
                self.update_status('Solved!')
                self.is_done = True
            self.is_solving = False
        else:
            self.update_status('Playing...')
            self.is_solving = False
    
    def swap_click(self, tile_index, empty_value=0):
        possible_actions = get_possible_actions(self.current_board_state)
        empty_value_index = self.current_board_state.index(empty_value)
        tile_value = int(self.board[tile_index].cget('text'))
        
        for action in possible_actions:
            if not self.is_solving and not self.is_done:
                if action == UP and self.current_board_state[empty_value_index - 3] == tile_value:
                    self.set_state(get_transformed_state(self.current_board_state, UP))
                
                elif action == DOWN and self.current_board_state[empty_value_index + 3] == tile_value:
                    self.set_state(get_transformed_state(self.current_board_state, DOWN))
                
                elif action == LEFT and self.current_board_state[empty_value_index - 1] == tile_value:
                    self.set_state(get_transformed_state(self.current_board_state, LEFT))
                
                elif action == RIGHT and self.current_board_state[empty_value_index + 1] == tile_value:
                    self.set_state(get_transformed_state(self.current_board_state, RIGHT))
        
        if not self.is_done and self.current_board_state == self.target_board_state:
            self.update_status('Well done!')
            self.is_done = True

if __name__ == '__main__':
    app = App()
    app.mainloop()
    
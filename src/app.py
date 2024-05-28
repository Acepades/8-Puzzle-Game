import os
import tkinter as tk
import time
from tkinter import ttk
from PIL import Image, ImageTk
from threading import Thread

from src.config import *
from src.utils import algorithm, Board, A_STAR, HC, BEST_FIRST

class EightPuzzle(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('750x750')
        self.resizable(False, False)
        self.iconbitmap('src/assets/images/app.ico')
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
        
        self.depth = 0
        self.board = []
        
        self.available_algorithms = [
            algorithm('A* Search', A_STAR),
            algorithm('Hill Climbing (local)', HC),
            algorithm('Best First Search', BEST_FIRST)
        ]
        self.algorithm_index = 0
        self.algorithm = self.available_algorithms[0]

        self.current_board_state = tuple(range(9))
        self.goal_board_state = tuple(range(9))
        self.saved_board_state = tuple(range(9))

        self.tile_images = [ImageTk.PhotoImage(Image.open(f'src/assets/images/tile_{n}.png')) for n in range(9)]

        self.is_stopped = False
        self.is_solving = False
        self.is_done = False

        self.display_widgets()

    def display_widgets(self):

        self.frame_puzzle = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_puzzle.pack(padx=10, pady=10)

        #Button section
        self.frame_buttons = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_buttons.pack(pady=20)

        self.button_solve = tk.Button(self.frame_buttons, text='solve', command=lambda: self.solve_board(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_solve.grid(row=0, column=0, padx=10, pady=10)

        self.button_reset = tk.Button(self.frame_buttons, text='reset', command=lambda: self.reset_board(), **SECONDARY_BUTTON_PROPERTIES)
        self.button_reset.grid(row=0, column=1, padx=10, pady=10)

        self.button_new = tk.Button(self.frame_buttons, text='new', command=lambda: self.new_board(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_new.grid(row=0, column=2, padx=10, pady=10)

        self.button_change = tk.Button(self.frame_buttons, text='Strat', command=lambda: self.change_algorithm(), **TERTIARY_BUTTON_PROPERTIES)
        self.button_change.grid(row=0, column=3, padx=10, pady=10)

        self.label_depth = tk.Label(self.frame_puzzle, text=f'depths: {self.depth}', **TEXT_LABEL_PROPERTIES)
        self.label_depth.grid(row=0, column=0, sticky='w', padx=10, pady=5)

        self.label_status = tk.Label(self.frame_puzzle, text=f'', **TEXT_LABEL_PROPERTIES)
        self.label_status.grid(row=0, column=1, sticky='e', padx=10, pady=5)

        self.separator = ttk.Separator(self.frame_puzzle, orient='horizontal')
        self.separator.grid(row=1, columnspan=2, sticky='ew', pady=10)


        self.frame_title = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_title.pack(pady=25)
        self.label_subheading = tk.Label(self.frame_title, text=f'{self.algorithm.name} algorithm', **SUBHEADING_LABEL_PROPERTIES)
        self.label_subheading.pack()

        self.frame_board = tk.Frame(self.frame_puzzle, **BASIC_FRAME_PROPERTIES)
        self.frame_board.grid(row=2, columnspan=2)
 

        self.initialize_board()

        self.new_board()

        self.controller.bind('<Up>', lambda event: self.transform_keys('D'))
        self.controller.bind('<Down>', lambda event: self.transform_keys('U'))
        self.controller.bind('<Left>', lambda event: self.transform_keys('R'))
        self.controller.bind('<Right>', lambda event: self.transform_keys('L'))

    def initialize_board(self):
        for index in range(9):
            self.board.append(tk.Button(self.frame_board, **TILE_BUTTON_PROPERTIES))
            self.board[index].grid(row=index // 3, column=index % 3, padx=10, pady=10)

    def populate_board(self, state, delay_time=0):
        for tile_index, tile_value in enumerate(state):
            self.board[tile_index].configure(
                    image=self.tile_images[tile_value],
                    text=tile_value,
                    state='normal',
                    command=lambda tile_index=tile_index: self.transform_click(tile_index)
                )

            if tile_value == 0:
                self.board[tile_index].configure(state='disabled')

        self.current_board_state = state

        time.sleep(delay_time)

    def solve_board(self):
        if not self.is_solving:
            self.reset_board()
            self.solution_thread = Thread(target=self.run_solution)
            self.solution_thread.start()

    def run_solution(self):
        self.is_stopped = False
        self.is_solving = True
        self.is_done = False
        self.update_status('Solving...')

        print('\nFinding solution...')

        path_to_goal, nodes_expanded, max_search_depth, time_elasped = Board.solve(self.current_board_state, self.algorithm.func)

        if not self.is_stopped:
            print(f'Done in {round(time_elasped, 4)} second(s) with {len(path_to_goal)} depth using {self.algorithm.name}')
            print(f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
            print('Actions:', *path_to_goal)
        else:
            print('Stopped')

        if path_to_goal:
            print('\nMoving board...')
            self.update_status('Moving...')

            delay_time = 0.75
            time.sleep(delay_time)

            for action in path_to_goal:
                if self.is_stopped:
                    print('Stopped')
                    self.update_status('')
                    break
                else:
                    self.transform_state(action, delay_time=0.5)
            else:
                print('Done board animation')
                self.update_status('Done!')
                self.is_done = True

            self.is_solving = False

        else:
            self.is_solving = False
            self.update_status('')

    def reset_board(self):
        self.stop_solution()
        self.update_depth(0)
        self.update_status('')
        self.populate_board(state=self.saved_board_state)

    def new_board(self):
        self.saved_board_state = Board.create_solvable_state()
        self.reset_board()

    def stop_solution(self):
        if self.is_solving and not self.is_stopped:
            self.is_stopped = True
        self.is_done = False

    def change_algorithm(self):
        self.reset_board()
        self.algorithm_index = (self.algorithm_index + 1) % len(self.available_algorithms)
        self.algorithm = self.available_algorithms[self.algorithm_index]
        self.label_subheading.configure(text=f'{self.algorithm.name} algorithm')

    def transform_click(self, tile_index):
        possible_actions = Board.valid_actions(self.current_board_state)
        blank_index = self.current_board_state.index(0)
        tile_value = int(self.board[tile_index].cget('text'))

        for action in possible_actions:
            if not self.is_solving and not self.is_done:
                if action == 'U' and self.current_board_state[blank_index - 3] == tile_value:
                    self.transform_state(action)

                elif action == 'D' and self.current_board_state[blank_index + 3] == tile_value:
                     self.transform_state(action)

                elif action == 'L' and self.current_board_state[blank_index - 1] == tile_value:
                     self.transform_state(action)

                elif action == 'R' and self.current_board_state[blank_index + 1] == tile_value:
                     self.transform_state(action)

        if not self.is_done and self.current_board_state == self.goal_board_state:
            self.update_status('Well done!')
            self.is_done = True

    def transform_keys(self, action):
        if not self.is_solving and not self.is_done:
           if action in Board.valid_actions(self.current_board_state):
                self.transform_state(action)

        if not self.is_done and self.current_board_state == self.goal_board_state:
            self.update_status('Well done!')
            self.is_done = True

    def transform_state(self, action, delay_time=0):
        new_state = Board.transform(self.current_board_state, action)

        current_index = self.current_board_state.index(0)
        new_index = new_state.index(0)

        first_tile = self.board[current_index]
        second_tile = self.board[new_index]

        first_tile_properties = self.get_tile_property(first_tile)
        second_tile_properties = self.get_tile_property(second_tile)

        self.set_tile_property(first_tile, second_tile_properties)
        self.set_tile_property(second_tile, first_tile_properties)

        self.current_board_state = new_state

        if not self.is_done:
            self.update_depth(self.depth + 1)

        time.sleep(delay_time)

    def get_tile_property(self, tile):
        return {
            'text': tile.cget('text'),
            'background': tile.cget('background'),
            'image': tile.cget('image'),
            'state': tile.cget('state')
        }

    def set_tile_property(self, tile, properties):
        tile.configure(**properties)

    def update_depth(self, depth):
        self.depth = depth
        self.label_depth.configure(text=f'depth: {self.depth}')

    def update_status(self, status):
        self.label_status.configure(text=status)
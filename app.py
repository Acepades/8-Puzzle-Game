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
        self.board = [[], [], []]
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
        self.separator.grid(row=1, columnspan=2, sticky='we', pady=10)
        
        self.frame_board = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_board.grid(row=2, columnspan=2)
        
        for row in range(3):
            for column in range(3):
                self.board[row].append(tk.Button(self.frame_board, **TILES_BUTTON_PROPERTIES))
                self.board[row][column].grid(row=row, column=column, padx=10, pady=10)
        
        self.shuffle_board()
    
    def generate_board(self, state, empty_value=0):
        index = 0
        for i in range(3):
            for j in range(3):
                self.board[i][j].configure(
                    image=self.tile_images[state[index]],
                    text=state[index],
                    state='normal',
                    command=lambda x=i, y=j: self.swap_click(x, y)
                )
                
                if state[index] == empty_value:
                    self.board[i][j].configure(state='disabled')
                
                self.current_board_state[i*3 + j] = state[index]
                index += 1
    
    def set_state(self, state, delay_time):
        current_row, current_col = self.get_board_coordinate(self.current_board_state.index(0))
        new_row, new_col = self.get_board_coordinate(state.index(0))
        
        tile_1, tile_2 = self.board[current_row][current_col], self.board[new_row][new_col]
        tile_1_prop, tile_2_prop = self.get_tile_property(tile_1), self.get_tile_property(tile_2)
        self.set_tile_property(tile_2_prop, tile_1)
        self.set_tile_property(tile_1_prop, tile_2)
        
        self.current_board_state = state[:]
        
        if not self.is_done:
            self.update_moves(self.moves + 1)
        
        sleep(delay_time)
    
    def get_board_coordinate(self, index):
        return index // 3, index % 3
    
    def get_tile_property(self, tile):
        return tile.cget('text'), tile.cget('background'), tile.cget('state'), tile.cget('image')
    
    def set_tile_property(self, properties, tile):
        tile.configure(text=properties[0], background=properties[1], state=properties[2], image=properties[3])
    
    def update_moves(self, moves):
        self.moves = moves
        self.label_moves.configure(text=f'Moves: {self.moves}')
    
    def update_status(self, status):
        self.label_status.configure(text=status)
    
    def reset_board(self):
        self.stop_solution()
        self.is_stopped = False
        self.is_solving = False
        self.is_done = False
        self.update_moves(0)
        self.update_status('Playing...')
        self.generate_board(state=self.saved_board_state)
    
    def shuffle_board(self):
        self.saved_board_state = generate_random_solvable_puzzle()
        self.reset_board()
    
    def solve_board(self):
        if not self.is_solving:
            self.reset_board()
            self.solution_thread = Thread(target=self.run_solution)
            self.solution_thread.start()
    
    def stop_solution(self):
        self.is_stopped = True
        self.is_solving = False
        sleep(0.75)
    
    def run_solution(self):
        self.is_solving = True
        self.update_status('Solving...')
        
        print('Finding solution...')
        
        start = time()
        solution = breadth_first_shortest_path(self.current_board_state, self.target_board_state, self)
        end = time()
        
        if not self.is_stopped:
            print(f'Done in {round((end - start), 2)} second(s) with {len(solution) - 1} moves')
        else:
            print('Stopped')
        
        if solution != None and not self.is_stopped:
            print('Moving board...')
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
                self.update_status('Solved!')
                self.is_done = True
            self.is_solving = False
        else:
            self.update_status('Playing...')
            self.is_solving = False
    
    def swap_click(self, x, y):
        possible_actions = get_possible_actions(self.current_board_state)
        board_state_index = self.current_board_state.index(0)
        tile_number = int(self.board[x][y].cget('text'))
        
        for action in possible_actions:
            if not self.is_solving and not self.is_done:
                state = None
                
                if action == 'U' and self.current_board_state[board_state_index - 3] == tile_number:
                    state = change_state(self.current_board_state, 'U')
                elif action == 'D' and self.current_board_state[board_state_index + 3] == tile_number:
                    state = change_state(self.current_board_state, 'D')
                elif action == 'L' and self.current_board_state[board_state_index - 1] == tile_number:
                    state = change_state(self.current_board_state, 'L')
                elif action == 'R' and self.current_board_state[board_state_index + 1] == tile_number:
                    state = change_state(self.current_board_state, 'R')
                
                if state:
                    self.set_state(state, 0)
        
        if not self.is_done and self.current_board_state == self.target_board_state:
            self.update_status('Well done!')
            self.is_done = True

if __name__ == '__main__':
    app = App()
    app.mainloop()
    
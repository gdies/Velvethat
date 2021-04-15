# DEPENDENCIES
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.clock import Clock
import random
import numpy as np
import os
import math
import time
import itertools
import operator
from typing import List
import sys
print('recursion limit: ', sys.getrecursionlimit())

# CUSTOM MODULES
from globals import config_dict

# SUPPORT CLASSES
class TileButton(Button):
    """
    A button that represents a minesweeper tile.
    """
    config_dict = config_dict
    base_size = config_dict['Tasks']['Minesweeper']['base_size']

    def __init__(self, index_tuple:tuple, mine:bool, **kwargs):
        super(TileButton, self).__init__(**kwargs)
        self.index_tuple:tuple = index_tuple # identifies the button
        self.mine:bool = mine
        self.neighbor_list:List[tuple] = self.generate_neighbors() # from 3 up to 8 elements
        self.neighbor_mines:int = 0
        self.text = ''
        self.revealed:bool = False

    def generate_neighbors(self) -> list:
        """
        Generate a list of tuples that indicate the indices of neighboring elements in a matrix

        :return: A list of tuples with the indices of neighboring tiles.
        :rtype: list
        """
        operation_list = list(itertools.product([-1, 0, 1], repeat=2)) # all pairwise combinations of -1, 0, 1
        neighbor_list = []
        for operation in operation_list:
            if operation != (0,0):
                neighbor = tuple(map(operator.add, self.index_tuple, operation)) # add operator tuples to index tuple
                if self.validate_neighbor(neighbor = neighbor): # check if generated indices are out of range
                    neighbor_list.append(neighbor)
        return neighbor_list

    def validate_neighbor(self, neighbor:tuple):
        """
        Take tuple containing indices, if out of range, return False, else True

        :return: False, if input indices are out of range (of the game tile matrix), else True
        :rtype: bool
        """
        return False if (-1 in neighbor or self.base_size in neighbor) else True

    def reveal(self):
        """
        Set button property to revealed
        """
        self.revealed = True
        self.disabled = True # disable button
        if not self.mine:
            self.text = str(self.neighbor_mines) if self.neighbor_mines > 0 else '' # set text when revealed
        else:
            self.color = [1,0,0,1]
            self.text = '×' # if its a mine, display this

    def use_button_left(self):
        """
        Trigger, when button is clicked with left click
        """
        if self.mine: # end of game
            self.background_color = [1,0,0,1] # red
            self.parent.parent.end_game(win = False)
        else:
            self.parent.parent.update_tiles(next_tile = self.index_tuple) # start with itself
            if self.parent.parent.check_win_conditions(): # check win conditions
                self.parent.parent.end_game(win = True)

    def use_button_right(self):
        """
        Trigger, when button is clicked with right click
        """
        if not self.text:
            self.color = [0,0,1,1] # blue Flag
            self.text = 'F'
        else:
            self.color = [1,1,1,1]
            self.text = ''

    def use_button(self, instance, touch):
        """
        Trigger, when the button receives interaction (right or left click)
        """
        if not self.revealed:
            if self.collide_point(*touch.pos): # check if touch position collides with button
                if touch.button == 'right':
                    self.use_button_right()
                elif touch.button == 'left':
                    self.use_button_left()


# MAIN WIDGET
class Minesweeper(GridLayout):
    config_dict = config_dict
    task_id = config_dict['Tasks']['Minesweeper']['task_id']
    base_size = config_dict['Tasks']['Minesweeper']['base_size']
    mine_ratio = config_dict['Tasks']['Minesweeper']['mine_ratio']
    tile_layout = ObjectProperty()
    info_label = ObjectProperty()
    time_label = ObjectProperty()

    def __init__(self, **kwargs):
        super(Minesweeper, self).__init__(**kwargs)
        self.mine_matrix = self.generate_mine_matrix() # a boolean matrix
        self.start_time = time.time()
        self.add_tiles()
        self.update_neighbor_mine_count()
        self.time_update_event = self.schedule_time_update()

    def stop_task(self, instance):
        """ GENERAL TASK METHOD (called by velvethat.py game screen manager)
        Remove updating thread from Clock.
        """
        Clock.unschedule(self.time_update_event)

    def end_game(self, win:bool):
        """
        Reveal everything, a mine is clicked
        """
        Clock.unschedule(self.time_update_event)
        [tile.reveal() for tile in self.tile_layout.children]
        if not win:
            self.info_label.text = 'Booomm!'
        else:
            self.info_label.text = 'Well done!'
            for tile in self.tile_layout.children:
                if tile.mine:
                    tile.color = [0,1,0,1] # green when winning

    def update_tiles(self, next_tile:tuple):
        """ THE METOD CONTAINS RECURSION
        Called when a tile is clicked that is NOT A MINE. Calls itself recursively, until all tiles are done
        """
        current_tile = [tile for tile in self.tile_layout.children if tile.index_tuple == next_tile][0]
        if not current_tile.revealed: # otherwise the tile is revealed already, no need to do anything
            current_tile.reveal() # reveal tile
            if current_tile.neighbor_mines == 0: # only check neighbors if the current tile has no neighboring mine
                for neighbor in current_tile.neighbor_list:
                    self.update_tiles(next_tile = neighbor) # RECURSION
        else: # when the tile is revealed already
            pass

    def add_tiles(self):
        """
        Add buttons representing tiles to the tile layout
        """
        side_indices = list(range(self.base_size))
        index_list = list(itertools.product(side_indices, repeat=2)) # generate matrix indices pairing elements in range, # organized row first, column second
        mine_list = list(self.mine_matrix.flatten())
        i = 0
        for ind_tuple in index_list:
            button = TileButton(index_tuple = ind_tuple, mine = mine_list[i])
            button.bind(on_touch_down = button.use_button)
            self.tile_layout.add_widget(button)
            i += 1

    def generate_mine_matrix(self):
        """
        Generate a boolean matrix, that has True where there is a mine
        """
        return np.random.choice(a=[True, False], size=(self.base_size, self.base_size), p=[self.mine_ratio, 1-self.mine_ratio])

    def update_neighbor_mine_count(self):
        """
        For each tile, update the neighbor_mines count
        """
        for tile in self.tile_layout.children:
            for neighbor_tuple in tile.neighbor_list:
                if self.mine_matrix[neighbor_tuple]: # True if there is a mine at the given index
                    tile.neighbor_mines += 1 # starts with 0, increment by 1 if neighbor mine found

    def check_win_conditions(self):
        """
        Check if all non-mines are revealed
        """
        for tile in self.tile_layout.children:
            if (not tile.mine and not tile.revealed):
                return False
        return True

    def schedule_time_update(self):
        """
        Schedule time label text update
        """
        return Clock.schedule_interval(self.update_time, 1) # every second

    def update_time(self, instance):
        """
        Update time label every second
        """
        time_elapsed = '{:.0f}'.format(time.time()-self.start_time)
        self.time_label.text = 'Elapsed time: ' + time_elapsed + ' s'

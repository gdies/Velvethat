# DEPENDENCIES
import random
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import numpy as np
import itertools

# CUSTOM MODULES
from globals import config_dict

# SUPPORT FUNCTIONS
def get_text_dict(max_number:int=config_dict['Tasks']['Sudoku']['base_size']**2):
    """
    Define button text dictionary with a maximum number.
    """
    text_dict = {str(i):str(i+1) for i in range(1,max_number)}
    text_dict.update({'-':'1', str(max_number):'-'})
    return text_dict

# SUPPORT CLASSES
class NumberButton(Button):
    """
    A button that changes its label when pressed.
    """
    config_dict = config_dict
    text_dict = get_text_dict(max_number=config_dict['Tasks']['Sudoku']['base_size']**2)

    def __init__(self, row:int, column:int, number:int, **kwargs):
        super(NumberButton, self).__init__(**kwargs)
        self.row = row
        self.column = column
        self.number = number
        self.text = str(self.number)

    def use_button(self, instance):
        """
        Trigger when button is pressed. Button changes its own text.
        """
        self.text = self.text_dict[self.text]

    def disable_button(self):
        """
        Disable interactability.
        """
        self.disabled = True


# MAIN WIDGET
class Sudoku(GridLayout):
    config_dict = config_dict
    empty_rate = config_dict['Tasks']['Sudoku']['empty_rate']
    board = ObjectProperty(None)
    widget_board = ObjectProperty(None)
    task_id = config_dict['Tasks']['Sudoku']['task_id']

    def __init__(self, base_size:int=config_dict['Tasks']['Sudoku']['base_size'], **kwargs):
        super(Sudoku, self).__init__(**kwargs)
        self.base_size = base_size
        self.side_size = self.base_size**2
        self.generate_board()
        self.add_number_buttons()
        self.clear_some()
        self.disable_rest()

    def building_pattern(self, r:int, c:int):
        """
        Pattern for a baseline valid solution
        """
        return (self.base_size*(r%self.base_size)+r//self.base_size+c)%self.side_size

    def shuffle(self, s:list):
        """
        # randomize rows, columns and numbers (of valid base pattern)
        """
        return random.sample(s,len(s))

    def generate_board(self):
        """
        Generate a list of lists where each sublist is a row of the game matrix.
        """
        r_base = range(self.base_size)
        rows = [g*self.base_size + r for g in self.shuffle(r_base) for r in self.shuffle(r_base)]
        cols = [g*self.base_size + c for g in self.shuffle(r_base) for c in self.shuffle(r_base)]
        nums = self.shuffle(s=range(1, self.base_size**2 + 1))

        self.board = [[nums[self.building_pattern(r=r,c=c)] for c in cols] for r in rows] # build board using randomised building pattern

    def add_number_buttons(self):
        """
        Add Number button to game board GridLayout.
        """
        add_rowspace, add_colspace = False, False
        for i in range(len(self.board)): # for each row i of the board
            add_rowspace = ((i+1)%self.base_size == 1 and i != 0)
            if add_rowspace:
                [self.widget_board.add_widget(Label(text='')) for _ in range(self.side_size + self.base_size - 1)] # add sudoku row spacing
            for j in range(len(self.board[i])): # for each index j in row i of the board
                add_colspace = ((j+1)%self.base_size == 1 and j != 0)
                if add_colspace:
                    self.widget_board.add_widget(Label(text='')) # add sudoku spacing
                button = NumberButton(row=i, column=j, number=self.board[i][j])
                button.bind(on_release=button.use_button)
                self.widget_board.add_widget(button)

    def clear_some(self):
        """
        Sets some of the widget texts to '-'
        """
        squares = self.side_size**2
        empties = round(squares * self.empty_rate)
        for p in random.sample(range(squares),empties):
            r, c = p//self.side_size, p%self.side_size
            buttons = [w for w in self.widget_board.children if isinstance(w, NumberButton)]
            button = [b for b in buttons if (b.row == r and b.column == c)][0] # find button in row r and column c
            button.text = '-'

    def disable_rest(self):
        """
        Disable buttons that are not modifiable. Also make them look different.
        """
        button_list = [w for w in self.widget_board.children if isinstance(w, NumberButton)]
        short_button_list = [b for b in button_list if b.text != '-']
        for button in short_button_list:
            button.disabled = True

    def check_solution(self):
        """
        Look at board widgets, check if the solution is valid or not. Could be different from generated board but still valid.
        Empty field treated as 0.

        :return: 'Correct' if solution is correct, else return 'Incorrect'
        :rtype: str
        """
        button_list = [w for w in self.widget_board.children if isinstance(w, NumberButton)]
        solution_board = [[int(b.text) if b.text != '-' else 0 for b in button_list if b.row == i] for i in range(self.side_size)] # a nested list of integers
        rows = [set(row) for row in solution_board] # rows as sets
        columns =  [set(row) for row in list(np.transpose(np.asarray(solution_board)))] # columns as sets
        block_indices = [[i for i in range(self.side_size) if i//self.base_size==j] for j in range(self.base_size)] # define block index groups
        blocks = list(itertools.permutations(block_indices, 2)) + [(i,i) for i in block_indices]
        blocks = [set.union(*[set([solution_board[i][j] for j in t[1]]) for i in t[0]]) for t in blocks] # through tuples through lists, construct sets of block elements
        val = self.validate_solution(rows=rows, columns=columns, blocks=blocks)
        if val:
            self.disable_buttons()
            return 'Correct'
        else:
            return 'Incorrect, check again when done.'

    def validate_solution(self, rows:list, columns:list, blocks:list):
        """
        Compare columns, rows and blocks to reference_set.

        :param rows: A list of sets of row elements.
        :type rows: list
        :param columns: A list of sets of column elements.
        :type columns: list
        :param blocks: A list of sets of block elements.
        :type blocks: list

        :return: True if solution is corect, False otherwise.
        :rtype: bool
        """
        reference_set = set(list(range(1,self.side_size+1))) # a set of numbers a row, column and block has to contain
        for i in range(self.side_size): # go through rows, columns and blocks and compare elements with
            if (rows[i] != reference_set or columns[i] != reference_set or blocks[i] != reference_set):
                return False
        return True

    def disable_buttons(self):
        """
        Disable all buttons.
        """
        [w.disable_button() for w in self.widget_board.children if isinstance(w, NumberButton)]

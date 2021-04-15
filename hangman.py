# DEPENDENCIES
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
import os
import re
import random
import string

# CUSTOM MODULES
import support
from globals import config_dict, data_dir, text_file

# SUPPORT CLASSES
class SymbolButton(Button):
    """
    A button that has a letter associated with it.
    """
    config_dict = config_dict

    def __init__(self, symbol:str, symbol_pos_list:list, **kwargs):
        super(SymbolButton, self).__init__(**kwargs)
        self.text = symbol
        self.symbol_pos_list = symbol_pos_list

    def use_button(self, instance):
        """
        Trigger when button is pressed.
        """
        riddle_char_list = list(self.parent.parent.riddle)
        if self.symbol_pos_list:
            self.background_color = (0,1,0,1) # green if correct guess
            for i in self.symbol_pos_list: # update riddle
                riddle_char_list[i] = self.text # reveal matching characters
            self.parent.parent.riddle = ''.join(riddle_char_list)
            self.parent.parent.riddle_label.text = ' '.join(riddle_char_list)
        else:
            self.background_color = (1,0,0,1) # red if incorrect guess
        self.disabled = True # button is used
        self.parent.parent.check_solution()

# MAIN WIDGET
class Hangman(GridLayout):
    config_dict = config_dict
    data_dir = data_dir
    text_file = text_file
    task_id = config_dict['Tasks']['Hangman']['task_id']
    riddle_label = ObjectProperty(None)
    symbol_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Hangman, self).__init__(**kwargs)
        self.abc = string.ascii_lowercase[:26] # a-z string
        self.text:str = self.load_text()
        self.solution:str = self.sample_text()
        self.riddle:str = self.prepare_text()
        self.index_dict:dict = self.symbol_indices()
        self.add_buttons()
        self.add_riddle()

    def load_text(self):
        """
        load text file into str
        """
        with open(os.path.join(self.data_dir, self.text_file), 'r') as file:
            text = file.read() #.replace('\n', ' ')
        return text

    def sample_text(self) -> str:
        """
        Use regex pattern to create a list of sentences. Sample the sentences

        :return: A randomly chosen sentence
        :rtype: str
        """
        pattern = r'(?i)(?<=[?!\.(\s")][\s\n(\n")])([a-z\s,;\-(\'?s)]+)(?=[\.?!("\s)])'
        sample_list = [match for match in re.findall(pattern, self.text) if len(match) > 5] # filter out very short matches
        return random.choice(sample_list)

    def prepare_text(self):
        """
        Take in text, create riddle form.
        """
        riddle = self.solution
        for c in self.abc:
            riddle = riddle.replace(c, '_')
        return  riddle

    def symbol_indices(self):
        """
        for each letter in self.abc, create a list of indices pointing at positions in self.riddle.
        """
        index_dict = {c:[] for c in self.abc}
        index = 0
        for i in list(self.solution):
            if i in index_dict.keys():
                index_dict[i].append(index)
            index += 1
        return index_dict

    def add_buttons(self):
        """
        Add button widgets for each letter to guess.
        """
        for c in self.abc:
            button = SymbolButton(symbol = c, symbol_pos_list = self.index_dict[c])
            button.bind(on_release = button.use_button)
            self.symbol_layout.add_widget(button)

    def add_riddle(self):
        """
        Set riddle_label text to riddle.
        """
        self.riddle_label.text = ' '.join(list(self.riddle))

    def check_solution(self):
        """
        Check if the riddle is resolved, change color if yes.
        """
        if self.riddle_label.text == ' '.join(list(self.solution)):
            self.riddle_label.color = (0,1,0,1)
            if [1,0,0,1] not in [child.background_color for child in self.symbol_layout.children if isinstance(child, Button)]:
                self.symbol_layout.add_widget(Label(text = 'perfect', color = (0,1,0,.3)))

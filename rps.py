# DEPENDENCIES
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
import random
import numpy as np
from fractions import Fraction

# CUSTOM MODULES
from globals import config_dict

# SUPPORT CLASSES

# MAIN WIDGET
class RPS(GridLayout):
    config_dict = config_dict
    task_id = config_dict['Tasks']['RPS']['task_id']
    min_games = config_dict['Tasks']['RPS']['min_games']
    win_rate = Fraction(config_dict['Tasks']['RPS']['win_rate']).limit_denominator()
    game_history = ObjectProperty(None)
    result_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RPS, self).__init__(**kwargs)
        self.play_dict:dict = {0:'Rock', 1:'Paper', 2:'Scissors'}
        self.rule_dict = {'Rock':'Scissors', 'Paper':'Rock', 'Scissors':'Paper'} # A dictionary containing what beats what: {Rock:Scissors, Paper:Rock,...}
        self.probabilities:dict = {'Rock':1/3, 'Paper':1/3, 'Scissors':1/3}
        self.n_games:int = 0 # start with 0 games
        self.games_won:int = 0 # start with 0 won games
        self.generate_strategy() # update self.probabilities, same strategy stands for a game

    def generate_strategy(self):
        """
        Generate opponent strategy, not necessarily uniform probabilities
        """
        # the play probabilities
        r = random.uniform(0, 1)
        p = random.uniform(0, 1-r)
        s = 1 - (r+p)
        self.probabilities = {'Rock':r, 'Paper':p, 'Scissors':s}

    def opponent_play(self) -> str:
        """
        Generate opponent play

        :return: Played symbol as string
        :rtype: str
        """
        return self.play_dict[np.random.choice(np.arange(0, 3), p=list(self.probabilities.values()))]

    def check_requirements(self) -> bool:
        """
        Check if min_games and win_rate are satisfied at the same time
        """
        if (self.n_games >= self.min_games and self.games_won/self.n_games >= self.win_rate):
            return True
        else:
            return False

    def play(self, symbol:str) -> None:
        """
        Play RPS. Take symbol selected by the player, draw symbol for opponent, then compare & update widget
        """
        self.n_games += 1 # add 1 to played games
        opponent_symbol = self.opponent_play()
        label_text = symbol + '/' + opponent_symbol
        if self.rule_dict[symbol] == opponent_symbol: # win
            self.games_won += 1
            self.game_history.add_widget(Label(text=label_text, color=(0,1,0,1), font_size=10))
        elif self.rule_dict[opponent_symbol] == symbol: # lose
            self.game_history.add_widget(Label(text=label_text, color=(1,0,0,1), font_size=10))
        else: # tie
            self.game_history.add_widget(Label(text=label_text, color=(0,0,1,1), font_size=10))

        # check if enough games had been won
        result_text = f'{self.games_won}/{self.n_games} win rate with {self.n_games} games played.'
        if self.check_requirements():
            result_text = result_text + '\nCongratulations, you are the champion!'
        self.result_label.text = result_text

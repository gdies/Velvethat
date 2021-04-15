# DEPENDENCIES
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import random

# CUSTOM MODULES
from globals import config_dict

# SUPPORT CLASSES

# MAIN WIDGET
class Arithmetics(GridLayout):
    config_dict = config_dict
    task_id = config_dict['Tasks']['Arithmetics']['task_id']
    digits = config_dict['Tasks']['Arithmetics']['digits']
    hint_label = ObjectProperty(None)
    problem_label = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Arithmetics, self).__init__(**kwargs)
        self.solution:int = None # the solution of current problem
        #self.problem_text:str = '' # a str representation of the problem
        self.generate_problem(digits = self.digits)

    def generate_problem(self, digits:int=1) -> None:
        """
        Generate problem to solve: (a + b) x c, where: a,b,c are integers, set self.problem string, self.solution

        :param digits: Character lenght of problem components (a,b,c)
        :type digits: int
        """
        max_number = 10**digits
        a, b, c = random.randrange(max_number), random.randrange(max_number), random.randrange(max_number)
        self.problem_label.text = f'({a} + {b}) × {c} = '
        self.solution = (a + b) * c

    def check_solution(self, attempt:int):
        """
        Compare attempt and self.solution

        :param attempt: The guess for the solution
        :type attempt: int
        """
        if attempt == self.solution:
            self.hint_label.text = 'Correct'
        else:
            self.hint_label.text = 'Incorrect'

    def focus_on_text_input(self, instance):
        """
        Set focus on the TextInput widget.
        """
        self.text_input.focus = True

    def schedule_focus(self):
        """
        Schedule focus_on_text_input method.
        """
        Clock.schedule_once(self.focus_on_text_input)

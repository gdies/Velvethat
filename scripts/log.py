# DEPENDENCIES
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.clock import Clock
import random

# CUSTOM MODULES
from globals import config_dict

# SUPPORT CLASSES
class AnswerButton(Button):
    """
    A button that has a number.
    """
    config_dict = config_dict

    def __init__(self, number:int, **kwargs):
        super(AnswerButton, self).__init__(**kwargs)
        self.number:int = number
        self.text = str(number)

    def use_button(self, instance):
        """
        Trigger when button is pressed.
        """
        if self.parent.parent.check_solution(solution=self.number):
            self.background_color = (0,1,0,1) # green if correct guess
            self.text = f'Yes, {self.number} is the right answer.'
        else:
            self.background_color = (1,0,0,1) # red if incorrect guess
            self.text = f'No, {self.number} is not the right answer.'
        self.disabled = True # button is used

# MAIN WIDGET
class Log(GridLayout):
    config_dict = config_dict
    task_id = config_dict['Tasks']['Log']['task_id']
    max_base = config_dict['Tasks']['Log']['max_base']
    max_exponent = config_dict['Tasks']['Log']['max_exponent']
    n_answers = config_dict['Tasks']['Log']['n_answers']
    problem_label = ObjectProperty(None)
    answer_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Log, self).__init__(**kwargs)
        self.base:int = None
        self.exponent:int = None
        self.result:int = None
        self.masked:int = None
        self.components:tuple = self.draw_components()
        self.generate_problem()
        self.add_buttons()

    def draw_components(self) -> tuple:
        """
        Generate random base and exponent, return components and an index, which one to mask

        :return: A tuple with a list of components, and a random index, that is to be masked
        :rtype: tuple  - fx: ([a,b,c],0)
        """
        a = random.randrange(2, self.max_base + 1) # between 2 and max_base (included both)
        c = random.randrange(1, self.max_exponent + 1) # between 1 and max power (both included)
        b = int(a**c)
        return ([a,b,c], random.randrange(3))

    def generate_problem(self):
        """
        Generate a problem of the form log_a b = c
        """
        self.base, self.exponent, self.result = self.components[0] # unpack list
        self.masked = self.components[1]
        str_components = [str(i) for i in self.components[0]]
        str_components[self.masked] = 'x' # mask one
        self.problem_label.text = 'log[sub] ' + str_components[0] + '[/sub] ' + str_components[1] + ' = ' + str_components[2]

    def check_solution(self, solution:int) -> bool:
        """
        Check if solution equals to the masked component

        :param solution: The guessed number
        :type solution: int

        :return: True if the guessed number is correct, False otherwise
        :rtype: bool
        """
        if solution == self.components[0][self.masked]:
            return True
        else:
            return False

    def add_buttons(self):
        """
        Add answer buttons
        """
        button_list = [AnswerButton(number=self.draw_components()[0][self.masked]) for _ in range(self.n_answers-1)] # generate alternative answer buttons
        button_list.append(AnswerButton(number=self.components[0][self.masked])) # add right answer button
        random.shuffle(button_list) # shuffle list
        for button in button_list:
            button.bind(on_release = button.use_button)
            self.answer_layout.add_widget(button)

    @staticmethod
    def to_subscript(sequence:str): # not used here
        """
        Take sequence, return subscript version of numeric characters in the sequence.
        """
        sub = str.maketrans("0123456789x", "₀₁₂₃₄₅₆₇₈₉ₓ")
        return sequence.translate(sub)

# DEPENDENCIES
import random
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

# CUSTOM MODULES
from globals import config_dict
# SUPPORT FUNCTIONS
# SUPPORT CLASSES

# MAIN WIDGET
class NumberGuess(GridLayout):
    number = NumericProperty()
    hint = ObjectProperty()
    guess_counter = ObjectProperty()
    guess_count = NumericProperty(0)
    text_input = ObjectProperty()
    task_id = config_dict['Tasks']['NumberGuess']['task_id']

    def __init__(self, **kwargs):
        super(NumberGuess, self).__init__(**kwargs)
        self.generate_number()

    def generate_number(self, max:int=config_dict['Tasks']['NumberGuess']['max_number']):
        """
        Generate a random integer between 0 and max. Both included. Assign it to self.number NumericProperty.

        :param max: The function returns an integer between 0 and max.
        :type max: int
        """
        self.number =  random.randrange(max+1)

    def check_input(self, input:int) -> bool:
        """
        Check if input is equal to the generated number.

        :param input: An input integer, that is the current guess.
        :type input: int

        :return: True if the guess is correct, False if incorrect
        :rtype: bool
        """
        return True if input == self.number else False

    def hint_text(self, input:int):
        """
        The text that helps the guessing by telling the player if the random number is larger or smaller than the guessed number.

        :param input: An input integer, that is the current guess.
        :type input: int

        :return: The hint text.
        :rtype: str
        """
        text = ''
        if self.check_input(input=input):
            text = f'Correct guess, the number is {self.number}'
        elif input > self.number:
            text = f'{input} is too high.'
        else:
            text = f'{input} is too low.'
        return text

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

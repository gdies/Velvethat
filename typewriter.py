# DEPENDENCIES
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.animation import Animation
import random
import re
import os
import math
import time

# CUSTOM MODULES
from globals import config_dict, data_dir, text_file

# SUPPORT CLASSES
class WordLabel(Label):
    """
    A button that has a number.
    """
    config_dict = config_dict
    base_velocity = config_dict['Tasks']['Typewriter']['base_velocity']
    max_speed = config_dict['Tasks']['Typewriter']['max_speed']

    def __init__(self, word:str, **kwargs):
        super(WordLabel, self).__init__(**kwargs)
        self.word:str = word
        self.text = word
        self.size_hint = self.texture_size # set size to text size + padding
        self.eliminated:bool = False # keep track if eliminated or not
        self.speed:float = random.uniform(a = 0, b = self.max_speed)

    def move(self):
        """
        Update position
        """
        self.pos = Vector(*[v*self.speed for v in self.base_velocity]) + self.pos

    def eliminate(self):
        """
        Set self.eliminated to True
        """
        self.eliminated = True
        duration = random.uniform(a = 0.5, b = 1)
        Animation(opacity = 0, duration = duration).start(self)
        Clock.schedule_once(self.hide_label, duration)

    def hide_label(self, instance):
        """
        set hidden to True
        """
        self.hidden = True

# MAIN WIDGET
class Typewriter(GridLayout):
    config_dict, data_dir, text_file = config_dict, data_dir, text_file
    task_id = config_dict['Tasks']['Typewriter']['task_id']
    n_words = config_dict['Tasks']['Typewriter']['n_words']
    sample_length = config_dict['Tasks']['Typewriter']['sample_length']
    base_delay = config_dict['Tasks']['Typewriter']['min_delay']
    min_delay = config_dict['Tasks']['Typewriter']['min_delay']
    max_delay = config_dict['Tasks']['Typewriter']['max_delay']
    delay_coefficient = config_dict['Tasks']['Typewriter']['delay_coefficient']
    update_frequency = config_dict['Tasks']['Typewriter']['update_frequency']
    word_input = ObjectProperty(None)
    word_layout = ObjectProperty(None)
    result_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Typewriter, self).__init__(**kwargs)
        self.n_eliminated:int = 0
        self.n_missed:int = 0
        self.n_words:int = 0
        self.words = self.sample_text()
        self.start_time = time.time()
        self.word_fall_event = self.schedule_word_fall()
        self.word_status_event = self.schedule_status_update()
        self.result_update_event = self.schedule_result_update()

    def stop_task(self, instance):
        """ GENERAL TASK METHOD (called by velvethat.py game screen manager)
        Remove updating thread from Clock.
        """
        Clock.unschedule(self.word_fall_event)
        Clock.unschedule(self.word_status_event)
        Clock.unschedule(self.result_update_event)

    def focus_on_text_input(self, instance):
        """
        Set focus on the TextInput widget.
        """
        self.word_input.focus = True

    def schedule_focus(self):
        """
        Schedule focus_on_text_input method.
        """
        Clock.schedule_once(self.focus_on_text_input)

    def schedule_word_fall(self):
        """
        schedule word fall
        """
        return Clock.schedule_interval(self.schedule_word_label, self.base_delay)

    def schedule_word_label(self, instance):
        """
        Schedule self.add_word_label, adding the next label
        """
        delay = random.uniform(a = self.min_delay, b = self.max_delay) * self.get_delay_multiplier() # a random (uniform) delay between minimum delay and maximum delay
        self.n_words += 1
        Clock.schedule_once(self.add_word_label, delay)

    def get_delay_multiplier(self) -> float:
        """
        Generate delay multiplier for word scheduling intervals

        :return: A number between self.delay_coefficient + 1 and 1
        :rtype: float
        """
        return self.delay_coefficient * math.sqrt(self.n_words) # the function derivative (timedelta between words appearing (roughly)) is decreasing

    def add_word_label(self, instance):
        """
        Add new random word widget to self.word_layout
        """
        pos_x = random.uniform(a = self.word_layout.x + 50, b = self.right - 50) # padding
        label = WordLabel(word = random.choice(self.words), pos = (pos_x, self.word_layout.top)) # choose random word
        self.word_layout.add_widget(label)

    def schedule_status_update(self):
        """
        Create position update event, refresh displayed widgets
        """
        return Clock.schedule_interval(self.update_word_status, 1/self.update_frequency)

    def update_word_status(self, instance):
        """
        update word positions based on their velocity
        """
        for word in self.word_layout.children:
            word.move()
            if word.pos[1] < self.word_layout.y: # touching the bottom (pos[1] is the y coordinate)
                #print(f'Typewriter/update_word_status - delete word: ({word.text})')
                if word.eliminated:
                    self.n_eliminated += 1
                else:
                    self.n_missed += 1
                self.word_layout.remove_widget(word) # as the word touched the bottom, it has to go

    def check_input(self, input_word:str):
        """
        Check if input word is valid, call word.eliminate if yes
        """
        for word in self.word_layout.children:
            if word.text == input_word:
                word.eliminate()

    def schedule_result_update(self):
        """
        create result label update event
        """
        return Clock.schedule_interval(self.update_result_label, 1)

    def update_result_label(self, instance):
        """
        Set result label text according to current standings
        """
        elapsed_time = '{:.0f}'.format(time.time() - self.start_time)
        self.result_label.text = f'Eliminated: {self.n_eliminated}    Missed: {self.n_missed}    Time elapsed: ' + elapsed_time + ' s'

    def load_text(self) -> str:
        """
        load text file into str

        :return: A text as string
        :rtype: str
        """
        with open(os.path.join(self.data_dir, self.text_file), 'r') as file:
            text = file.read()
        return text

    def sample_text(self) -> list:
        """
        Load text and sample self.n_words from it after pattern match

        :return: A list of sampled words
        :rtype: list
        """
        text = self.load_text()
        pattern = r'(?i)(?<=[\s])([a-z]+)(?=[,;\.?!("\s)])'
        sample_list = list(set(re.findall(pattern, text)))
        return random.choices(population = sample_list, k = self.sample_length)

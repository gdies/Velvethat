# DEPENDENCIES
import os
import time
from typing import List
import numpy as np

# CUSTOM MODULES
import support
from globals import config_dict

# MAIN
class Task(object):
    """
    A task object to store task related administrative information.

    :param id: The task identifier.
    :type id: int
    """
    # parameters
    min_wage:float = config_dict['Task']['minimum_wage']
    wage_decay_factor:float = config_dict['Task']['wage_decay_factor']

    def __init__(self, id:int):
        self.id:int = id
        self.open:bool = False
        self.start_time = None # time of start
        self.end_time = None # time of finishing
        self.total_duration:float = 0.0 # total time spent on the task
        self.last_task_duration:float = 0.0 # length of last session
        self.payment:float = 0.0 # the amount earned, to be put into wallet

    def start_task(self):
        """
        Set self.open to True.
        """
        self.start_time = time.time()
        self.open = True

    def end_task(self):
        """
        Set self.open = False. If it was open, log update the start_time and end_time
        """
        if self.open:
            self.end_time = time.time()
            self.last_task_duration = (self.end_time-self.start_time) / 60.0 # measure time in minutes
            self.update_payment() # calculate wage
            self.total_duration += self.last_task_duration
        self.open = False

    def wage(self, min_wage:float, decay_factor:float, start_time:float, end_time:float):
        """
        Define diminishing function. The minimum wage and a decay factor defines how high the starting wage is.

        :param min_wage: The wage does not decrease below this with time.
        :type min_wage: float
        :param decay_factor: A multiplier for the exponentially decreasing wage/time.
        :type decay_factor: float
        :param start_time: The total time in seconds spent on a task already before starting again. The first evaluation point of the wage function.
        :type start_time: float
        :param end_time: The total time in seconds spent on a task when finishing.
        :type end_time: float

        :return: The area below the wage function between start_time and end_time. That is the calculated wage
        :rtype: float
        """
        # implement wage function
        # wage function f(x) = d*e^(-x)+m
        # d: decay factor, m: min wage
        # The wage is the area under the wage function between x_1 = start_time and x_2 = end_time
        return decay_factor*(-np.sinh(start_time)+np.cosh(start_time)+np.sinh(end_time)-np.cosh(end_time)) + (end_time-start_time)*min_wage

    def update_payment(self):
        """
        Set self.payment to wage earned
        """
        self.payment = self.wage(min_wage=self.min_wage, decay_factor=self.wage_decay_factor, start_time=self.total_duration, end_time=self.total_duration+self.last_task_duration)

    def zero_payment(self):
        """
        Set payment to 0.
        """
        self.payment = 0.0


class TaskManager(object):
    """
    The object holding and administering the task times, wages.

    :param n: The number of tasks to be generated.
    :type n: int
    """
    def __init__(self, n:int):
        self.tasks:List = []
        self.create_tasks(n=n)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self) -> Task:
        if self.index < len(self.tasks):
            task = self.tasks[self.index]
            self.index += 1
            return task
        else:
            raise StopIteration

    def create_tasks(self, n:int=9):
        """
        Fill self.tasks with tasks.

        :param n: The number of tasks to be generated.
        :type n: int
        """
        for i in range(n):
            self.tasks.append(Task(id = i))

    def open_task(self, id:int):
        """
        Set a task active.

        :param id: Task id.
        :type id: int
        """
        self.tasks[id].start_task()

    def close_task(self, id:int):
        """
        Set a task inactive.

        :param id: Task id.
        :type id: int
        """
        self.tasks[id].end_task()

    def close_tasks(self):
        """
        Close all tasks. Advantage that it is input free
        """
        for task in self.tasks:
            task.end_task()

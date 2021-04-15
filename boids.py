# DEPENDENCIES
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (NumericProperty, ReferenceListProperty, ObjectProperty)
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from typing import List
import numpy as np
import time

# CUSTOM MODULES
from globals import config_dict

# SUPPORT FUNCTIONS

# SUPPORT CLASSES
class Boid(Widget):
    config_dict = config_dict
    velocity_x = NumericProperty(0.0)
    velocity_y = NumericProperty(0.0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    # there is a .pos attribute as it is a widget
    def __init__(self, id:int, pos_x, pos_y, **kwargs):
        self.id = id
        self.pos = Vector(pos_x, pos_y)
        super(Boid, self).__init__(**kwargs)
    pass


class Flock(object):
    """
    An object describing the boids behaviour, implementing the boid algorithm.

    :param n_boids: Number of boids to simulate
    :type n_boids: int
    """
    config_dict = config_dict
    min_v_x, min_v_y = config_dict['Tasks']['Boids']['velocity_limits'][0], config_dict['Tasks']['Boids']['velocity_limits'][1]
    max_v_x, max_v_y = config_dict['Tasks']['Boids']['velocity_limits'][2], config_dict['Tasks']['Boids']['velocity_limits'][3]
    # Boid algorithm parameters
    move_to_goal_strength = config_dict['Tasks']['Boids']['goal_strength'] # moving towards cursor
    move_to_middle_strength = config_dict['Tasks']['Boids']['cohesion_strength'] # staying with the flock parameter
    alert_distance = config_dict['Tasks']['Boids']['alert_distance'] # collision avoidance parameter
    formation_flying_distance = config_dict['Tasks']['Boids']['formation_distance'] # velocity matching parameter
    formation_flying_strength = config_dict['Tasks']['Boids']['formation_strength'] # velocity matching parameter
    # other params
    velocity_coefficient = config_dict['Tasks']['Boids']['velocity_coefficient'] # overall velocity regulation


    def __init__(self, n_boids:int=10, pos_x_range:list=[150,200], pos_y_range:list=[100,200]):
        self.n_boids = n_boids
        self.positions = self.generate_vectors(n_boids = self.n_boids, lower_limits = np.array([pos_x_range[0], pos_y_range[0]]), upper_limits = np.array([pos_x_range[1], pos_y_range[1]]))
        self.velocities = self.generate_vectors(n_boids = self.n_boids, lower_limits = np.array([self.min_v_x, self.min_v_y]), upper_limits = np.array([self.max_v_x, self.max_v_y]))

    def generate_vectors(self, n_boids:int, lower_limits:np.ndarray, upper_limits:np.ndarray):
        """
        Generate x and y component of n_boids' position or velocity vectors. Return an array with two vectors of length n_boids.
        """
        range = upper_limits - lower_limits
        return (lower_limits[:, np.newaxis] + np.random.rand(2, n_boids) * range[:, np.newaxis])

    def update_positions(self, goal_pos:np.ndarray=None):
        """
        Implement the Boid algorithm
        """
        self.towards_middle()
        self.keep_distance()
        self.match_velocity()
        if goal_pos.size != 0:
            self.towards_goal(goal_pos=goal_pos)
        self.positions += self.velocities * self.velocity_coefficient # position update

    def towards_middle(self):
        """
        Implement cohesion
        """
        middle = np.mean(self.positions, 1) # move towards middle
        direction_to_middle = self.positions - middle[:, np.newaxis]
        self.velocities -= direction_to_middle * self.move_to_middle_strength

    def keep_distance(self):
        """
        Implement distance keeping - collision avoidance
        """
        # keep destance / avoid collision
        separations = self.positions[:, np.newaxis, :] - self.positions[:, :, np.newaxis]
        squared_displacements = separations * separations
        square_distances = np.sum(squared_displacements, 0)
        far_away = square_distances > self.alert_distance
        separations_if_close = np.copy(separations)
        separations_if_close[0, :, :][far_away] = 0
        separations_if_close[1, :, :][far_away] = 0
        self.velocities += np.sum(separations_if_close, 1)

    def match_velocity(self):
        """
        Implement velocity matching
        """
        # match velocity
        separations = self.positions[:, np.newaxis, :] - self.positions[:, :, np.newaxis] # duplicate line (also in keep distance)
        squared_displacements = separations * separations # duplicate line (also in keep distance)
        square_distances = np.sum(squared_displacements, 0) # duplicate line (also in keep distance)

        velocity_differences = self.velocities[:, np.newaxis, :] - self.velocities[:, :, np.newaxis]
        very_far = square_distances > self.formation_flying_distance
        velocity_differences_if_close = np.copy(velocity_differences)
        velocity_differences_if_close[0, :, :][very_far] = 0
        velocity_differences_if_close[1, :, :][very_far] = 0
        self.velocities -= np.mean(velocity_differences_if_close, 1) * self.formation_flying_strength

    def towards_goal(self, goal_pos:np.ndarray):
        """
        implement moving towards a goal.
        """
        direction_to_goal = self.positions - goal_pos[:, np.newaxis]
        self.velocities -= direction_to_goal * self.move_to_middle_strength

    def bounce(self, x_limits:list, y_limits:list):
        """
        Bounce boids that are crossing the limits of the space. When a boid is crossing an axis limit, flip the corresponding velocity component's sign.

        :param x_limits: The lowest and highest x values to keep the boid within.
        :type x_limits: list
        :param y_limits: The lowest and highett y values to keep the boid within.
        :type y_limits: list
        """
        pos_x, pos_y = self.positions[0,:], self.positions[1,:]
        outside_x = np.where(np.logical_or(pos_x < x_limits[0], pos_x > x_limits[1]), -1, 1) # -1 if outside space, 1 otherwise
        outside_y = np.where(np.logical_or(pos_y < y_limits[0], pos_y > y_limits[1]), -1, 1) # -1 if outside space, 1 otherwise
        outside_limits = np.stack((outside_x, outside_y), axis = 0)
        np.multiply(self.velocities, outside_limits, out = self.velocities) # the vector element signs are flipped where the boid is over the limit


# MAIN WIDGET
class Boids(FloatLayout):
    config_dict = config_dict
    task_id = config_dict['Tasks']['Boids']['task_id']
    max_boids = config_dict['Tasks']['Boids']['max_boids']
    update_event = None
    goal_pos = np.array([])

    def __init__(self, **kwargs):
        super(Boids, self).__init__(**kwargs)
        app = App.get_running_app()
        self.n_boids = np.random.randint(low = 2, high = self.max_boids)
        self.flock = Flock(n_boids = self.n_boids, pos_x_range=[app.root.center_x-50, app.root.center_x+50], pos_y_range=[app.root.center_y-50, app.root.center_y+50])
        self.add_boids()
        self.schedule_update()

    def stop_task(self, instance):
        """ GENERAL TASK METHOD (called by velvethat.py game screen manager)
        Remove updating thread from Clock.
        """
        Clock.unschedule(self.update_event)

    def add_boids(self):
        """
        Add boids to widget.
        """
        [self.add_widget(Boid(id = i, pos_x = self.flock.positions[0,i].item(), pos_y = self.flock.positions[1,i].item())) for i in range(self.n_boids)]

    def update_boids(self):
        """
        Set boid velocity and position generated by the flock behaviour
        """
        for boid in self.children:
            boid.pos = Vector(*[i.item() for i in self.flock.positions[:,boid.id]]) # unpack position coordinates into Vector

    def schedule_update(self):
        """
        Schedules updating process by adding it to the Clock
        """
        self.update_event = Clock.schedule_interval(self.update, 1.0 / self.config_dict['Tasks']['Boids']['update_frequency'])

    def deschedule_update(self):
        """
        Stop updating process
        """
        Clock.unschedule(self.update_event)

    def update(self, instance):
        """
        Call flock update methods
        """
        self.flock.update_positions(goal_pos=self.goal_pos)
        self.update_boids()
        self.bounce() # the bouncing works better like this than together with the flock.update_positions

    def bounce(self):
        """
        When a boid meets a side, change the velocity's respective component's sign
        """
        self.flock.bounce(x_limits=[self.x, self.right], y_limits=[self.y, self.top]) # bounce off bottom or top

    def on_touch_down(self, touch):
        """
        Register mouse click
        """
        print('touch pos: ', touch.x, touch.y)
        self.goal_pos = np.array([touch.x, touch.y])

    def on_touch_move(self, touch):
        """
        when mouse is held down, boids try to follow the cursor
        """
        self.goal_pos = np.array([touch.x, touch.y])

    def on_touch_up(self, touch):
        """
        Erase goal coordinates
        """
        self.goal_pos = np.array([])



# TESTING

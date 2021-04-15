# DEPENDENCIES
import time
import os
import threading
import numpy as np

# CUSTOM MODULES
import support
from globals import config_dict


class Exchange(object):
    """
    The Exchange class keeps track of the prices
    """
    def __init__(self):
        self.price_vector:np.ndarray = np.array([config_dict['Exchange']['price_1'], config_dict['Exchange']['price_2'], config_dict['Exchange']['price_3']])
        self.price_history:np.ndarray = np.tile(self.price_vector, reps=(config_dict['Exchange']['price_history_length'],1)) # price history matrix with prices being column vectors (each row is a timestep)
        self.covariance_matrix:np.ndarray = self.generate_covariance_matrix()
        self.rates = self.quick_rates()
        self.update_prices()

    def current_prices(self) -> tuple:
        """
        Return the current prices as a tuple of floats
        """
        return self.price_vector[0], self.price_vector[1], self.price_vector[2]

    def generate_covariance_matrix(self) -> np.ndarray:
        """
        Generate a small random integer sample of 3 variables, calculate the covariance matrix, return it.
        """
        n_vars = self.price_vector.shape[0]
        samples = np.random.uniform(low=0, high=config_dict['Exchange']['max_variance_factor'], size=(n_vars,10))
        return np.cov(samples, bias=True)

    def update_prices(self) -> None:
        """
        A thread that constantly updates the asset prices
        """
        t = threading.Thread(target=self.update_prices_thread, args=[], daemon=True)
        t.start()
        pass

    def update_prices_thread(self) -> None:
        """
        A loop that constantly updates the prices.
        Draw multivariate normal errors, add them to the prices
        to create a random walk process.
        """
        while True:
            print('prices: ', self.price_vector)
            time.sleep(config_dict['Exchange']['update_delay']) # delay between each price update
            eps = np.random.multivariate_normal(np.zeros(3), self.covariance_matrix, size=1, check_valid='warn', tol=1e-8) # draw increment
            self.price_vector = np.abs(np.add(self.price_vector, eps, casting='unsafe'))[0] # update prices
            self.price_history = np.concatenate((self.price_history[1:,:], np.reshape(self.price_vector, newshape=(-1,3))), axis=0) # (t x k) array, with t included timesteps and k prices
            self.rates = self.quick_rates() # calculate currency/currency_1 rates
        pass

    def get_price_history(self):
        """
        Converts price history array to a list of price lists - [[p11, p12, ...], [p21, ...], ...]
        List i in the returned list is the price history list of price i.
        """
        return [list(self.exchange.price_history[:,i]) for i in range(self.exchange.price_history.shape[1])]

    def quick_rates(self):
        """
        Return a list of rates - each price divided by the first one.
        """
        return [p/self.price_vector[0] for p in self.price_vector]

    def get_rate(self, c1:int, c2:int):
        """
        Get rate of two currencies, c1/c2, so the rate is in label_2/label_1.

        :param c1: Numerator of the exchange rate.
        :type c1: int
        :param c2: Denominator of the exchange rate.
        :type c2: int

        :return: The rate c1/c2 where c1 and c2 are prices
        :rtype: float
        """
        return self.price_vector[c1]/self.price_vector[c2]

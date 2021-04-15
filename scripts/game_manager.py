# DEPENDENCIES
import os

# CUSTOM MODULES
import support
from wallet import Wallet
from exchange import Exchange
from task_manager import TaskManager
from globals import save_file, save_dir




class Game(object):
    """
    The class that brings together the background mechanics: The TaskManager, Wallet and Exchange.
    """
    save_file = save_file

    def __init__(self):
        self.wallet = Wallet()
        self.task_manager = TaskManager(n=9)
        self.exchange = Exchange()
        self.load_game()

    def earn_wage(self) -> None:
        """
        Add calculated wages from tasks to Wallet
        """
        payment = 0 # start with 0 payment
        for task in self.task_manager:
            payment += task.payment
            task.zero_payment() # reset payment value
        self.wallet.currency_dict[1] += payment # add payment to wallet (1 is the key for the first currency)
        print('[game_manager/Game/earn_wage]: - earned wage: ', payment)
        self.save_game()

    def convert_currency(self, from_currency:int, to_currency:int, buy_amount:float) -> None:
        """
        Convert one currency to another in the wallet after looking at the conversion rate at the exchange.

        :param from_currency: The currency id to pay with.
        :type from_currency: int
        :param to_currency: The currency id to buy.
        :type to_currency: int
        :param buy_amount: The amount of to_currency to buy.
        :type buy_amount: float
        """
        prices = self.exchange.current_prices() # a tuple of all prices
        # popup ('Do you want to convert x to y at r?')
        rate = prices[to_currency]/prices[from_currency]
        self.wallet.convert(from_currency=from_currency, to_currency=to_currency, buy_amount=buy_amount, rate=rate)
        self.save_game()

    def get_price_history(self):
        """
        Converts price history array to a list of price lists - [[p11, p12, ...], [p21, ...], ...]
        List i in the returned list is the price history list of price i.
        """
        return [list(self.exchange.price_history[:,i]) for i in range(self.exchange.price_history.shape[1])]

    def save_game(self):
        """
        Write wallet state to file
        """
        support.saveJson(obj = self.wallet.currency_dict, file_path = os.path.join(save_dir, save_file))
        print('[game_manager/Game/save_game]: Game saved')

    def load_game(self):
        """
        Load wallet state from file
        """
        try:
            wallet_state = support.loadJson(file_path = os.path.join(save_dir, save_file))
            self.wallet.currency_dict = {int(key):val for key,val in wallet_state.items()}
        except:
            print('[game_manager/Game/load_game]: Could not find saved game')

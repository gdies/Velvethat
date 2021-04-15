# DEPENDENCIES
from typing import List, Dict

# CUSTOM MODULES
from globals import config_dict
from option import Option

class Wallet(object):
    """
    An instance of this class keeps track of the amount of money
    """
    def __init__(self):
        self.currency_dict:Dict = {1:config_dict['Wallet']['currency_1'], 2:config_dict['Wallet']['currency_2'], 3:config_dict['Wallet']['currency_3']}
        self.options:List = []

    def update_wallet(self, currency:int, amount:float) -> None:
        """
        Add or subtract funds of a specified currency type.
        """
        self.currency_dict[currency] += amount

    def convert(self, from_currency:int, to_currency:int, buy_amount:float, rate:float) -> bool:
        """
        Convert from one currency to another, given the price (the second currency denominated in the first currency)

        :param from_currency: The identifier of the currency to convert to another.
        :type from_currency: int
        :param to_currency: The identifier of the currency to purchase.
        :type to_currency: int
        :param buy_amount: Amount of to_currency.
        :type buy_amount: float
        :param rate: Conversion rate. The from_currency/to_currency = sell_currency/buy_currency = buy_amount/sell_amount.
        :type rate: float

        :return: True if conversion happens, False otherwise
        :rtype: bool
        """
        sell_amount = buy_amount*rate
        conv_enabled = self.check_funds(currency=from_currency, amount=sell_amount)
        if conv_enabled: # the actual conversion
            self.update_wallet(currency=from_currency, amount=-sell_amount)
            self.update_wallet(currency=to_currency, amount=buy_amount)
        else:    # raise red button error (in the UI)
            pass
        return conv_enabled


    def check_funds(self, currency:int, amount:float) -> bool:
        """
        Check if the amount of a specific currency held in wallet is larger or equal to a target amount.

        :param currency: Identifier of the currency to chech the amount of.
        :type currency: int
        :param amount: Amount of currency to check.
        :type amount: float

        :return: True if the held amount of specified currency is larger than specified amount, else False.
        :rtype: bool
        """
        enable = True if self.currency_dict[currency] >= amount else False
        if not enable: print('wallet/check_funds: Requested transfer not possible.')
        return enable

    def add_option(self, currency:int, rate:float, amount:float) -> None:
        """
        Add option to self.options.

        :param currency: Identifier of the currency to buy or sell for base currency.
        :type currency: int
        :param price: Price of currency to buy or sell at.
        :type price: float
        :param amount: Amount of the currency to buy or sell.
        :type amount: float
        """
        try:
            id = max([opt.id for opt in self.options]) + 1
        except:
            id = 0
        opt = Option(id=id, currency=currency, rate=rate, amount=amount)
        self.options.append(opt)

    def remove_option(self, id:int) -> None:
        """
        Remove Option from self.options with given id.

        :param id: Identifier of Option to remove from self.options.
        :type id: int
        """
        self.options = [opt for opt in self.options if opt.id!=id] # keep options that are not the one to drop

    def use_option(self, id:int) -> bool:
        """
        Use option with given id.

        :param id: Identifier of Option to use from self.options.
        :type id: int

        :return: True if option is succesfully used, else False
        :rtype: bool
        """
        opt = [o for o in self.options if o.id==id][0] # the option to use
        if opt.amount >= 0: # buy option
            from_currency, to_currency = 1, opt.currency
            rate = opt.rate
            buy_amount = opt.amount
        else: # sell option
            from_currency, to_currency = opt.currency, 1
            rate = 1/opt.rate
            buy_amount = -opt.amount*opt.rate

        # do the conversion
        conversion_success = self.convert(from_currency=from_currency, to_currency=to_currency, buy_amount=buy_amount, rate=rate)
        if conversion_success: # attempt the conversion as the condition
            self.remove_option(id=id) # drop used option
        print('wallet/Wallet/use_option - option id list', [o.id for o in self.options])
        return conversion_success

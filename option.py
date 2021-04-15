# DEPENDENCIES

# CUSTOM MODULES


# MAIN
class Option(object):
    """
    A class holding properties of the option.
    """
    def __init__(self, id:int, currency:int, rate:float, amount:float):
        self.id:int = id
        self.currency:int = currency
        self.rate:float = rate # currency/currency_1
        self.amount:float = amount # positive or negative
        self.option_type = 'buy' if amount >= 0 else 'sell' # not used attribute but makes the code more readable

    def __repr__(self):
        """
        This is how the object is printed
        """
        return "<%s: %s>" % (self.__class__.__name__, self.__dict__)

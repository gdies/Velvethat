# DEPENDENCIES
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') # otherwise, right click generates red circle
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy_garden.graph import Graph, LinePlot
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import numpy as np

# CUSTOM MODULES
from game_manager import Game
from globals import config_dict
from option import Option
from number_guess import NumberGuess
from sudoku import Sudoku
from boids import Boids
from arithmetics import Arithmetics
from rps import RPS
from hangman import Hangman
from log import Log
from typewriter import Typewriter
from minesweeper import Minesweeper

# SUPPORT FUNCTIONS

# SUPPORT CLASSES
class ExchangeGraph(Graph):
    config_dict = config_dict
    plot_1 = ObjectProperty()
    plot_2 = ObjectProperty()
    make_plots: ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(ExchangeGraph, self).__init__(*args, **kwargs)

    def make_plot(self, prices):
        """
        Make plot area of the graph.

        :param prices: A (t x k) price matrix with t timesteps and k prices.
        :type prices: numpy.ndarray
        """
        self.plot_1 = LinePlot(line_width=2, color=[1, 0, 0, 1])
        self.plot_1.points = [(x,y) for x,y in enumerate(list(prices[:,1]/prices[:,0]))]
        self.add_plot(self.plot_1)

        self.plot_2 = LinePlot(line_width=2, color=[0, 1, 0, 1])
        self.plot_2.points = [(x,y) for x,y in enumerate(list(prices[:,2]/prices[:,0]))]
        self.add_plot(self.plot_2)

    def update_plot(self, prices):
        """
        Update plot area of the graph.

        :param prices: A (t x k) price matrix with t timesteps and k prices.
        :type prices: numpy.ndarray
        """
        rates_21, rates_31 = list(prices[:,1]/prices[:,0]), list(prices[:,2]/prices[:,0])
        self.ymax = int(max(rates_21 + rates_31)) + 1 # adjust plot focus according to max price
        self.plot_1.points = [(x,y) for x,y in enumerate(rates_21)]
        self.plot_2.points = [(x,y) for x,y in enumerate(rates_31)]


class OptionButton(Button):
    """
    A button that has a corresponding option in the wallet. They share id.
    """
    config_dict = config_dict

    def __init__(self, option:Option, **kwargs):
        super(OptionButton, self).__init__(**kwargs)
        self.option = option
        self.option_id = option.id
        self.text = self.button_text()

    def button_text(self):
        """
        Adds text to button, inherited from the corresponding Option object.
        """
        currency_dict = {self.config_dict['Main_Screen']['Currencies'][key][1]:key for key in self.config_dict['Main_Screen']['Currencies'].keys()} # keys: currncy id, vals: currency abbreviation
        currency_abbr = currency_dict[self.option.currency]
        rate_text = currency_dict[1] + '/' + currency_dict[self.option.currency]
        rate_number = '{:.3f}'.format(self.option.rate)
        if self.option.option_type == 'buy':
            text = f'Option {self.option_id}: Buy {self.option.amount} {currency_abbr} \nat rate {rate_number} {rate_text}.'
        else:
            text = f'Option {self.option_id}: Sell {-self.option.amount} {currency_abbr} \nat rate {rate_number} {rate_text}.'
        return text

    def use_button(self, instance):
        """
        Trigger when button is pressed. Calls the wallet.use_option method.
        """
        app = App.get_running_app()
        if app.root.game.wallet.use_option(id=self.option_id): # if conversion successful
            app.root.game.save_game()
            app.root.get_screen('Main_Screen').update_assets()
            self.parent.remove_widget(self) # button removes itself
        else:
            self.background_color = [1,0,0,1]
            Clock.schedule_once(self.reset_color, 0.1)

    def reset_color(self, instance):
        """
        Set color to default
        """
        self.background_color = [1,1,1,1]


class RewardButton(Button):
    """
    Button for rewards
    """
    config_dict = config_dict
    price_dict = {int(key):{int(k):v for k,v in value_dict.items()} for key,value_dict in config_dict['Rewards']['reward_price_dict'].items()}
    reward_dict = {int(key):value for key,value in config_dict['Rewards']['reward_dict'].items()}
    reward_text_dict = {key:{{val[1]:key for key,val in config_dict['Main_Screen']['Currencies'].items()}[k]:v for k,v in val_dict.items()} for key,val_dict in price_dict.items()}

    def __init__(self, **kwargs):
        super(RewardButton, self).__init__(**kwargs)
        self.prize_id:int = None

    def give_reward(self):
        """
        Execute reward giving
        """
        if self.check_requirements():
            app = App.get_running_app()
            if self.prize_id != 3: # for reward button 1 and 2
                [app.root.game.wallet.add_option(currency=self.prize_id+1, rate=app.root.game.exchange.rates[self.prize_id], amount=self.reward_dict[self.prize_id][2]) for _ in range(self.reward_dict[self.prize_id][0])] # buy options
                [app.root.game.wallet.add_option(currency=self.prize_id+1, rate=app.root.game.exchange.rates[self.prize_id], amount=-self.reward_dict[self.prize_id][2]) for _ in range(self.reward_dict[self.prize_id][1])] # sell options
                app.root.get_screen('Market_Screen').update_option_list()
                print('RewardButton/give_reward - options: ', app.root.game.wallet.options)
            else:
                print('RewardButton/give_reward - Fair Game')
            app.root.get_screen('Main_Screen').show_prize(prize_id = self.prize_id)

    def deduct_funds(self):
        """
        Deduct funds from wallet
        """
        app = App.get_running_app()
        [app.root.game.wallet.update_wallet(currency = currency, amount = -price) for currency,price in self.price_dict[self.prize_id].items()] # deduct funds from wallet
        app.root.get_screen('Main_Screen').update_assets() # update displayed funds too
        app.root.game.save_game()

    def check_requirements(self) -> bool:
        """
        Check if player has the eligible funds to buy the reward

        :return: True, if price requirements are met, False otherwise
        :rtype: bool
        """
        app = App.get_running_app()
        bool_list = [app.root.game.wallet.check_funds(currency = key, amount = val) for key,val in self.price_dict[self.prize_id].items()] # go through requirements
        if all(bool_list): # if all fund requirements are met (True and True and True)
            self.deduct_funds() # if requirements met, pay the price
            return True
        # else
        self.background_color = [1,0,0,1] # red flash
        Clock.schedule_once(self.reset_color, 0.2)
        return False

    def reset_color(self, instance):
        """
        Set color to default
        """
        self.background_color = [1,1,1,1]

    @staticmethod
    def clean_string(text:str, characters:str):
        """
        Takes in a string, replaces given characters with ''

        :return: The cleaned string
        :rtype: str
        """
        for c in characters:
            text = text.replace(c, '')
        return text


class ConvertButton(Button):
    """
    Button for Conversion
    """
    config_dict = config_dict

    def __init__(self, **kwargs):
        super(ConvertButton, self).__init__(**kwargs)

    def use_button(self):
        """
        Calls conversion
        """
        app = App.get_running_app()
        market = app.root.get_screen('Market_Screen')
        conversion_success = False
        if market.buy_amount.text: # if none of them is empty
            conversion_success = market.manager.game.wallet.convert(from_currency=self.config_dict['Main_Screen']['Currencies'][market.sell_currency.text][1], to_currency=self.config_dict['Main_Screen']['Currencies'][market.buy_currency.text][1], buy_amount=float(market.buy_amount.text), rate=market.manager.game.exchange.get_rate(c1=self.config_dict['Main_Screen']['Currencies'][market.buy_currency.text][1]-1, c2=self.config_dict['Main_Screen']['Currencies'][market.sell_currency.text][1]-1))
            if conversion_success:
                market.update_converted_amount(buy_sell = 'sell') # update sell text, so textinput values are more informative
                market.manager.get_screen('Main_Screen').update_assets()
        else: print('velvethat/ConvertButton/use_button - conversion fail (no buy amount given)')
        if not (market.buy_amount.text and conversion_success): # if
            self.background_color = [1,0,0,1] # change color
            Clock.schedule_once(self.reset_color, 0.2)

    def reset_color(self, instance):
        """
        Set color to default
        """
        self.background_color = [1,1,1,1]


# POPUPS
class RewardPopup(FloatLayout):
    config_dict = config_dict

    def __init__(self, prize_id:int, **kwargs):
        super(RewardPopup, self).__init__(**kwargs)
        self.prize_id = prize_id
        self.prize_text = self.get_prize_text()
        self.add_widget(Label(text=self.prize_text, size_hint=(1, 1), pos_hint={'x':0, 'top':1}))

    def get_prize_text(self) -> dict:
        t1,t2,t3 = config_dict['Rewards']['Reward 1'][0], config_dict['Rewards']['Reward 1'][1], config_dict['Rewards']['Reward 1'][2]
        t4,t5,t6 = config_dict['Rewards']['Reward 2'][0], config_dict['Rewards']['Reward 2'][1], config_dict['Rewards']['Reward 2'][2]
        t7 = config_dict['Rewards']['Reward 3']
        text_dict = {
            1:f'You get {t1} options to buy \n and {t2} options to sell {t3} HHS \n for BW at current price.',
            2:f'You get {t4} options to buy \n and {t5} options to sell {t6} JDF \n for BW at current price.',
            3:f'Congratulations, now you deserve to know the code: \n {t7}'}
        return text_dict[self.prize_id]
    pass


class PaymentPopup(FloatLayout):
    config_dict = config_dict

    def __init__(self, payment:float=0.0, **kwargs):
        super(PaymentPopup, self).__init__(**kwargs)
        self.payment_text = 'With your hard work, you have earned: ' + '{:.3f}'.format(payment) + ' BW'
        self.add_widget(Label(text = self.payment_text, size_hint=(1, 1), pos_hint={'x':0, 'top':1}))
    pass


# SCREENS
class Main_Screen(Screen):
    """
    The starting screen.
    """
    currency_1 = ObjectProperty(None)
    currency_2 = ObjectProperty(None)
    currency_3 = ObjectProperty(None)

    def payment(self, instance):
        """
        Call payment methods:
            Show payment on popup
            Add payment to wallet
            Update displayed assets on screen
        """
        payment = 0
        for task in self.manager.game.task_manager:
            payment += task.payment # obtain payment amount
        self.show_payment(payment=payment)
        self.manager.game.earn_wage()
        self.update_assets()

    def show_prize(self, prize_id:int):
        show_popup = RewardPopup(prize_id=prize_id) # content
        popup_window = Popup(title='Reward', content=show_popup,  size_hint=(None, None), size=(400, 150), auto_dismiss=True)
        popup_window.open()

    def show_payment(self, payment:float=0.0):
        """
        PaymentPopup window, showing earned wage
        """
        show_popup = PaymentPopup(payment=payment) # popup content
        popup_window = Popup(title='Payment', content=show_popup, size_hint=(None, None), size=(400, 150), auto_dismiss=True)
        popup_window.open()

    def schedule_payment(self):
        """
        Schedule self.update_assets method on the clock once
        """
        Clock.schedule_once(self.payment, .1)

    def update_assets(self):
        """
        Update main screen - when it is
        """
        self.currency_1.text = '{:.3f}'.format(self.manager.game.wallet.currency_dict[1])
        self.currency_2.text = '{:.3f}'.format(self.manager.game.wallet.currency_dict[2])
        self.currency_3.text = '{:.3f}'.format(self.manager.game.wallet.currency_dict[3])

    pass

class Market_Screen(Screen):
    """
    The screen showing the stock market activity.
    """
    config_dict = config_dict
    market_state = ObjectProperty(int)
    market_update_event = None
    option_list = ObjectProperty()
    buy_amount = ObjectProperty()
    sell_amount = ObjectProperty()
    buy_currency = ObjectProperty()
    sell_currency = ObjectProperty()
    currency_conversion_dict = dict(zip(list(config_dict['Main_Screen']['Currencies'].keys()), list(config_dict['Main_Screen']['Currencies'].keys())[1:] + [list(config_dict['Main_Screen']['Currencies'].keys())[0]]))

    def update_on(self, on:bool=True):
        """
        A Function that schedules a market_state ObjectProperty changer callback.

        :param on: If True, schedule price update, else unschedule.
        :type on: bool
        """
        if on:
            self.market_update_event = Clock.schedule_interval(self.update_market, 1/self.manager.config_dict['Market_Screen']['checking_frequency'])
        else:
            Clock.unschedule(self.market_update_event)

    def update_market(self, instance):
        """
        Changes the market_state ObjectProperty.
        """
        self.market_state = np.random.randint(low=0, high=100) # change market state (to trigger things)

    def on_market_state(self, instance, other):
        pass

    def add_option_button(self, option_id:int):
        """
        Add option button to option list.
        """
        option = [opt for opt in self.manager.game.wallet.options if opt.id == option_id][0] # find option
        button = OptionButton(option=option)
        button.bind(on_release=button.use_button)
        self.option_list.add_widget(button)

    def update_option_list(self):
        """
        A method that updates the option list with options existing in Wallet.
        """
        opt_ids = set([opt.id for opt in self.manager.game.wallet.options]) # list option id-s
        button_ids = set([button.option_id for button in [widg for widg in self.option_list.children if isinstance(widg, OptionButton)]]) # list button id-s
        diff_set = opt_ids-button_ids # diff option ids and button id-s
        print('velvethat/Market_Screen/update_option_list - diff_set: ', diff_set)
        for id in diff_set: # add buttons for the difference
            self.add_option_button(option_id=id)

    def update_converted_amount(self, buy_sell:str):
        """
        When conversion happens, it only considers the buy amount to be the true amount, the sell amount has to set accordingly so the textinput texts are informative about the spent amount
        """
        if buy_sell == 'sell':
            self.sell_amount.text = '{:.3f}'.format(float(self.buy_amount.text)*self.manager.game.exchange.get_rate(c1=self.config_dict['Main_Screen']['Currencies'][self.buy_currency.text][1]-1, c2=self.config_dict['Main_Screen']['Currencies'][self.sell_currency.text][1]-1)) if self.buy_amount.text else '0'
        elif buy_sell == 'buy':
            self.buy_amount.text = '{:.3f}'.format(float(self.sell_amount.text)*self.manager.game.exchange.get_rate(c1=self.config_dict['Main_Screen']['Currencies'][self.sell_currency.text][1]-1, c2=self.config_dict['Main_Screen']['Currencies'][self.buy_currency.text][1]-1)) if self.sell_amount.text else '0'
        else: print('velvethat/Market_Screen/update_converted_amount - wrongly specified arguments')

    pass

class Game_Screen(Screen):
    """
    The screen that shows the current game widgets.
    """
    task_dict = {config_dict['Tasks'][key]['task_id']:eval(key) for key in config_dict['Tasks'].keys()} # using eval()
    task = ObjectProperty(None)

    def remove_task(self):
        """
        Remove all task widgets from the Layout self.task.
        """
        # stop game
        if self.task.children:
            current_task = self.task.children[0] # the first child should be the game widget
            print('current_task: ', current_task)
            stop_task = getattr(current_task, 'stop_task', None) # if there is a stop_game method implemented by the game, call it
            if callable(stop_task):
                stop_task(current_task)
        self.task.clear_widgets() # remove widgets

    def start_task(self, task_id:int):
        """
        Add task with id task_id.

        :param task_id: The identifier of the task to initialize.
        :type task_id: int
        """
        print('Game_Screen/start_task')
        self.remove_task()
        self.task.add_widget(self.task_dict[task_id]())
    pass

class VelvetHat_ScreenManager(ScreenManager):
    config_dict = config_dict
    game = Game()
    pass


# kv file
#kv_file = Builder.load_file('velvethat.kv')
#Builder.load_file('number_guess.kv')

class VelvetHat(App):
    def build(self):
        return # kv_file

if __name__ == '__main__':
    VelvetHat().run()

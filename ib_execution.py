import datetime, time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message

from event import FillEvent, OrderEvent
from execution import ExecutionHandler
import queue as Queue

class IBExecutionHandler(ExecutionHandler):
    # Handles order execution via the IB API

    def __init__(self, event, order_routing = "SMART", currency = "USD"):
        self.event = event
        self.order_routing = order_routing
        self.currency = currency
        self.fill_dict = {}

        self.tws_conn = self.create_tws_connection()
        self.order_id = self.create_initial_order_id()
        self.register_handlers()

    def _error_handler(self, msg):
        # handles error messages
        # currently DNE
            print("Server Error: {}".format(msg))

    def _reply_handler(self,msg):
        # handles server replies

        # handle open order orderID processing
        if msg.typeName == "openOrder" and msg.orderID == self.order_id and not msg.orderID in self.fill_dict:
            self.create_fill_dict_entry(msg)

        # handle Fills
        if msg.typeName == "orderStatus" and msg.status == "Filled" and self.fill_dict[msg.orderID]["filled"] == False:
            self.create_fill(msg)

        print("Server Response: {}, {}".format(msg.typeName, msg))

    def create_tws_connection(self):
        # connect to Trader Workstation (TWS) running on port 7496, with clientId of 10
        tws_conn = ibConnection()
        tws_conn.connect()
        return tws_conn

    def create_initial_order_id(self):
        # create initial order ID used for IB to keep track of submitted orders
        # default set to one, but in future will be an ID that is set by us or by IB's TWS
        return 1

    def register_handlers(self):
        # simply registers the error and reply handler methods
        # being def _error_handler(self, msg): AND def _reply_handler(self,msg):
        self.tws_conn.register(self._error_handler, 'Error')
        self.tws_conn.registerAll(self._reply_handler)

    def create_contract(self, symbol, sec_type, exch, prim_exch, curr):
        # creates a Contract object defining what will be purchased (what exchange and what currency)

        contract = Contract()
        contract.m_symbol = symbol              # ticker for the contract
        contract.m_secType = sec_type           # security type ('STK' or 'stock')
        contract.m_exchange = exch              # exchange
        contract.m_primaryExch = prim_exch      # primary exchange
        contract.m_currency = curr              # currency
        return contract

    def create_order(self, order_type, quantity, action):
        # creates an Order object (market or limit) to go long or short

        order = Order()
        order.m_orderType = order_type          # 'MKT' or 'LMT' for market or limit
        order.m_totalQuantity = quantity        # number of assets to order
        order.m_action = action                 # 'BUY' or 'SELL'
        return order

    def create_fill_dict_entry(self, msg):
        # to avoid duplicating FillEvent instances for a particular order ID, we utilise a dictionary
        # dictionary is called the fill_dict to store keys that match particular order IDs.
        # When a fill has been generated the "filled" key of an entry for a particular order ID is set to True.

        self.fill_dict[msg.orderID] = {
            "symbol": msg.contract.m_symbol,
            "exchange": msg.contract.m_exchange,
            "direction": msg.order.m_action,
            "filled": False
        }

    def create_fill(self, msg):
        # creates the FillEvent instance and places it onto the events queue
        # fd = fill data
        fd = self.fill_dict[msg.orderID]

        # prep the fill data
        symbol = fd["symbol"]
        exchange = fd["exchange"]
        filled = msg.filled
        direction = fd["direction"]
        fill_cost = msg.avgFillPrice

        # create a fill event object
        fill = FillEvent(
            datetime.datetime.utcnow(), symbol, exchange, filled, direction, fill_cost
        )

        # ensures that multiple messages don't create more fills
        self.fill_dict[msg.orderID]['filled'] = True

        # place the fill event onto the event queue
        self.event.put(fill)

    def execute_order(self, event):
        # creates the necessary InteractiveBrokers order object and submits it to IB via their API
        # results are then queried in order to generate a corresponding Fill object which is placed back on the event queue

        if event.type == "ORDER":
            # prep parameters for the asset order
            asset = event.symbol
            asset_type = "STK"
            order_type = event.order_type
            quantity = event.quantity
            direction = event.direction

            # create IB contract via the passed Order event
            ib_contract = self.create_contract(asset, asset_type, self.order_routing, self.order_routing, self.currency)

            # create IB order via the passed Order event
            ib_order = self.create_order(order_type, quantity, direction)

            # send order to IB via connection
            self.tws_conn.placeOrder(self.order_id, ib_contract, ib_order)

            time.sleep(5)

            # updates orderID for session
            self.order_id+=1
import MetaTrader5 as mt5
from IAccount import Account

DEVIATION = 20
MAGIC = 234000

class RequestInfo:
    def __init__(self, symbol, volume, open_price, type, stop_loss, take_profit):
        self.symbol = symbol
        self.volume = volume
        self.price = open_price
        self.order_type = type
        self.stop_loss = stop_loss
        self.take_profit = take_profit


def mt5_request(request_info: RequestInfo):
    symbol = request_info.symbol
    volume = request_info.volume
    open_price = request_info.price
    order_type = request_info.order_type
    stop_loss = request_info.stop_loss
    take_profit = request_info.take_profit

    # Create a new order
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": open_price,
        "sl": stop_loss,
        "deviation": DEVIATION,
        "magic": MAGIC,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if take_profit:
        request["tp"] = take_profit

    return request


def send_order(request, account: Account):
    # Send the order request
    try:
        # Connect to MetaTrader 5
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        mt5.login(login=account.login, password=account.password, server=account.server)

        order_result = mt5.order_send(request)
        if order_result is None:
            # Get the last error information
            error = mt5.last_error()

            print("Order placement failed.")
            print(f"Error: {error}")
            return
        else:
            if order_result.comment == "Invalid volume":
                request["volume"] = round(request["volume"], 1)
                new_order_result = mt5.order_send(request)
                print(f'Order {request["symbol"]} filled in MT5 '
                      f'with response: {new_order_result.comment}')
            else:
                print(f'Order {request["symbol"]} filled in MT5 '
                      f'with response: {order_result.comment}')
    except Exception as e:
        print(f'Error filling order {request["symbol"]}: {str(e)}'
              f'with request: {request}')

    # Disconnect from MetaTrader 5
    mt5.shutdown()


def close_all_positions():
    # Connect to MetaTrader 5
    mt5.initialize()

    # Get the list of open positions
    positions = mt5.positions_get()

    if positions:
        for position in positions:
            # Create an order to close each open position
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "type": mt5.ORDER_TYPE_BUY if position.type == mt5.ORDER_SELL else mt5.ORDER_SELL,
                "volume": position.volume,
                "price": position.price_current,
                "deviation": DEVIATION,
                "magic": MAGIC,
                "comment": "Close all from Python",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }

            # Send the order request
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to close position: {result.comment}")
            else:
                print(f"Position closed successfully: {position.symbol}, {position.volume:.2f} lots")
    else:
        print("No open positions to close.")

    # Disconnect from MetaTrader 5
    mt5.shutdown()
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

    if not positions:
        print(f"No open trades for account: {mt5_account.login}")

        # iterate over the positions and close each one
    for position in positions:
        # determine the action type based on the position direction
        if position.type == mt5.ORDER_TYPE_BUY:
            type_f = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(position.symbol).bid
        elif position.type == mt5.ORDER_TYPE_SELL:
            type_f = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).ask

        # close the position using mt5.order_send()
        result = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": type_f,
            "position": position.ticket,
            "price": price,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        })

        # check if the order was closed successfully
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Order {result.request.symbol} closed: {result.comment}")
        else:
            print(f"Failed to close order {position.ticket}, error: {result.comment}")

    # Disconnect from MetaTrader 5
    mt5.shutdown()

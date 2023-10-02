import MetaTrader5 as mt5
from IAccount import available_accounts, Account

selected_account: Account = available_accounts[
    input("select the account [vantage_demo, vantage_live, ftmo_demo, ftmo_challenge]: ")]


def get_current_price(symbol: str):
    prices = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
    return prices[0].close


def get_open_trade(symbol: str):
    position = mt5.positions_get(symbol=symbol)
    # Return the first position tuple (and the only one)
    return position[0]


def mt5_request_stoploss(open_trade, action: int = mt5.TRADE_ACTION_SLTP):
    request = {
        "action": action,
        "symbol": open_trade.symbol,
        "type": open_trade.type,
        "position": open_trade.ticket,
        "sl": open_trade.sl,
        "tp": open_trade.tp,
        "magic": open_trade.magic,
        "comment": open_trade.comment,
    }

    return request


def update_stoploss_mt5(open_trade):
    symbol = open_trade.symbol
    break_even_ratio = 1

    # Get the current market price
    current_price = open_trade.price_current

    # Calculate the current risk reward ratio
    entry_price = float(open_trade.price_open)
    stop_loss = float(open_trade.sl)
    risk = entry_price - stop_loss
    reward = current_price - entry_price
    if risk == 0:  # Avoid division by zero
        return
    else:
        risk_reward_ratio = reward / risk

    new_request = mt5_request_stoploss(open_trade)

    # Update the stop loss if necessary
    if risk_reward_ratio >= break_even_ratio and stop_loss != entry_price:
        new_request["sl"] = entry_price
        mt5.order_send(new_request)
        print(f"Position secured for: {symbol}")


if __name__ == "__main__":
    print("Manage Stop_loss MT5 Algorithm started...")

    while True:

        try:
            mt5.initialize()
            mt5.login(login=selected_account.login, password=selected_account.password, server=selected_account.server)
            open_trades = mt5.positions_get()
            for open_trade in open_trades:
                update_stoploss_mt5(open_trade)

        except Exception as error:
            print("An error occurred:", error)

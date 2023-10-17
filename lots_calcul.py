from typing import List
import MetaTrader5 as mt5


def is_currency_pair(symbol: str) -> bool:
    # Connect to MetaTrader 5
    mt5.initialize()

    # Get symbol information
    symbol_info = mt5.symbol_info(symbol)

    # Check if the symbol's path starts with "Forex"
    is_currency = symbol_info.path.startswith("Forex")

    # Disconnect from MetaTrader 5
    mt5.shutdown()

    return is_currency


def calculate_forex_pips(stop_loss: float, open_price, symbol: str, decimal_places: int = 4) -> float:
    """
    Calculates the number of pips between the stop loss and open price for any currency pair.

    Parameters:
    open_price (float): The open price of the trade.
    stop_loss (float): The stop loss price of the trade.
    decimal_places (int): The number of decimal places to round the pip value to. Defaults to 4.

    Returns:
    float: The number of pips between the stop loss and open price.
    """
    pip_multiplier = 10 ** decimal_places

    # Calculate the pip value based on the currency pair's decimal places
    if "JPY" in symbol:  # Japanese Yen currency pairs have 2 decimal places
        pip_reference = 0.01
    elif "XAU" in symbol:  # Gold (XAU) has 2 decimal places
        pip_reference = 0.01
    elif "XAG" in symbol:  # Silver (XAG) has 3 decimal places
        pip_reference = 0.001
    else:  # All other currency pairs have 4 decimal places
        pip_reference = 0.0001

    # Calculate the number of pips based on the pip value and decimal places
    pips = round(abs(stop_loss - open_price) / pip_reference * pip_multiplier) / pip_multiplier

    # Return the number of pips rounded to the specified decimal places
    return round(pips, decimal_places)


def calculate_indices_pips(stop_loss, open_price, decimal_places: int = 2) -> float:
    """
    Calculates the number of pips between the stop loss and open price for indices like SP500, NASDAQ100, etc.

    Parameters:
    open_price (float): The open price of the trade.
    stop_loss (float): The stop loss price of the trade.
    decimal_places (int): The number of decimal places to round the pip value to. Defaults to 2.
    pip_value (float): The pip value of the instrument. Defaults to 1.

    Returns:
    float: The number of pips between the stop loss and open price.
    """

    pip_multiplier = 10 ** decimal_places

    # Calculate the number of pips based on the pip value and decimal places
    pips = round(abs(stop_loss - open_price), decimal_places)

    # Return the number of pips rounded to the specified decimal places
    return pips


def calculate_pips(stop_loss, open_price, symbol, is_currency: bool) -> float:
    if is_currency:
        decimal_place = 4
        pips = calculate_forex_pips(stop_loss, open_price, symbol, decimal_place)
        return pips
    else:
        decimal_place = 2
        pips = calculate_indices_pips(stop_loss, open_price, decimal_place)
        return pips


def calculate_pip_value(pips, risk_percentage, account_balance, is_currency) -> float:
    risk_value = account_balance * (risk_percentage / 100)
    pip_value = risk_value / pips
    mini_lots = 10000

    if is_currency:
        return pip_value * mini_lots
    else:
        return pip_value


def calculate_volume(pip_value: float, is_currency: bool, type, factor: int = 100000) -> float:
    if not is_currency:
        factor = 1

    volume = round(pip_value / factor, 2)
    volume = 0.01 if abs(volume) == 0.0 else volume

    if is_currency:
        volume = 50.00 if abs(volume) > 50 else volume

    return volume


def correct_volume(symbol: str, volume: float) -> float:
    # Connect to MetaTrader 5
    mt5.initialize()

    currency_base = "CHF"
    second_currency = mt5.symbol_info(symbol).currency_profit

    # Check if the symbol's path starts with "Forex"
    if mt5.symbol_info(currency_base + second_currency):
        exchange = mt5.symbol_info(currency_base + second_currency).bid
        return round(volume * exchange, 2)
    elif mt5.symbol_info(second_currency + currency_base):
        exchange = mt5.symbol_info(second_currency + currency_base).bid
        return round(volume * (1 / exchange), 2)
    else:
        return volume

    # Disconnect from MetaTrader 5
    mt5.shutdown()

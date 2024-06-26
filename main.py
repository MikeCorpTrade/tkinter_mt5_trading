import tkinter as tk
from tkinter import font
import MetaTrader5 as mt5
from lots_calcul import *
from mt5_request import *
from IAccount import available_accounts, Account

selected_account = available_accounts[input("select the account [ftmo_demo, ftmo_challenge]: ")]


def collect_request_info(order_type, account: Account):
    # Connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    mt5.login(login=account.login, password=account.password, server=account.server)

    # Get the account balance
    account_info = mt5.account_info()
    account_balance = account_info.balance
    symbol = symbol_entry.get()
    stop_loss = float(stop_loss_entry.get())
    risk_percentage = float(risk_percentage_entry.get())
    symbol_info = mt5.symbol_info(symbol)

    # Get all needed infos
    open_price = mt5.symbol_info_tick(symbol).ask if order_type == "Buy" else mt5.symbol_info_tick(symbol).bid
    is_currency = is_currency_pair(symbol)
    pips = calculate_pips(stop_loss, open_price, symbol, is_currency)
    pip_value = calculate_pip_value(pips, risk_percentage, account_balance, is_currency)
    type = mt5.ORDER_TYPE_BUY if order_type == "Buy" else mt5.ORDER_TYPE_SELL
    new_volume = mt5_volume(pip_value, is_currency, type, symbol)

    # Check if Take Profit field has input
    take_profit_input = take_profit_entry.get()
    if take_profit_input:
        if percentage_radio.get() == 1:  # Percentage selected
            percentage_value = float(take_profit_input)
            take_profit = open_price + abs(open_price - stop_loss) * percentage_value if order_type == "Buy" else \
                open_price - abs(open_price - stop_loss) * percentage_value
            take_profit = round(take_profit, 5)
        else:  # Price target selected
            take_profit = float(take_profit_input)
            take_profit = round(take_profit, 5)
    else:
        take_profit = 0

    # Check the strategy wanted
    if strategy_var.get() == "Scalping":
        scalping_pips = pip_reference(is_currency, symbol)
        sl_target = 3 * scalping_pips
        tp_target = 5 * scalping_pips
        scalping_pip_value = calculate_pip_value(sl_target, risk_percentage, account_balance, is_currency)
        new_volume = mt5_volume(scalping_pip_value, is_currency, type, symbol)

        max_mt5_volume_currency = 50.00
        max_mt5_volume_indice = 1000.00

        if new_volume > max_mt5_volume_currency and is_currency:
            new_volume = max_mt5_volume_currency
        elif new_volume > max_mt5_volume_indice and not is_currency:
            new_volume = max_mt5_volume_indice

        stop_loss = open_price - sl_target if order_type == "Buy" else open_price + sl_target
        take_profit = open_price + tp_target if order_type == "Buy" else open_price - tp_target

    return RequestInfo(symbol, new_volume, open_price, type, stop_loss, take_profit)


def update_mt5_volume() -> None:
    mt5.initialize()

    # Get the account balance
    account_info = mt5.account_info()
    account_balance = account_info.balance

    symbol = symbol_entry.get()
    stop_loss = float(stop_loss_entry.get())
    risk_percentage = float(risk_percentage_entry.get())

    symbol_info = mt5.symbol_info(symbol)

    # Get all needed infos
    open_price = (mt5.symbol_info_tick(symbol).ask + mt5.symbol_info_tick(symbol).bid) / 2
    is_curreny = is_currency_pair(symbol)
    pips = calculate_pips(stop_loss, open_price, symbol, is_curreny)
    pip_value = calculate_pip_value(pips, risk_percentage, account_balance, is_curreny)
    volume = calculate_volume(pip_value, is_curreny, type=type)
    new_volume = correct_volume(symbol, volume)

    mt5_volume_label.config(text=f"MT5 Volume: {new_volume:.2f} lots")


# Function to calculate and display the MT5 volume
def calculate_and_show_volume():
    update_mt5_volume()


# Create the GUI
root = tk.Tk()
root.title("MetaTrader 5 Order Placement")
root.geometry("400x300")

# Radio Buttons for Strategy
strategy_var = tk.StringVar(value="Intraday")

intraday_radio = tk.Radiobutton(root, text="Intraday", variable=strategy_var, value="Intraday")
intraday_radio.pack(side=tk.TOP)

scalping_radio = tk.Radiobutton(root, text="Scalping", variable=strategy_var, value="Scalping")
scalping_radio.pack(side=tk.TOP)

# Symbol
symbol_label = tk.Label(root, text="Symbol")
symbol_label.pack()
symbol_entry = tk.Entry(root)
symbol_entry.pack()

# Create a bold font
button_font = font.Font(weight="bold")
text_color = "white"

# Buy Button
buy_button = tk.Button(root, text="Buy",
                       command=lambda: send_order(mt5_request(collect_request_info("Buy", account=selected_account)),
                                                  account=selected_account),
                       bg="blue", fg="white", font=button_font)
buy_button.pack(side='left')

# Sell Button
sell_button = tk.Button(root, text="Sell",
                        command=lambda: send_order(mt5_request(collect_request_info("Sell", account=selected_account)),
                                                   account=selected_account),
                        bg="red", fg="white", font=button_font)
sell_button.pack(side='right')

# Close All Button
close_all_button = tk.Button(root, text="Close All", command=close_all_positions, bg="red", fg="white",
                             font=("Arial", 16, "bold"))
close_all_button.pack(side=tk.BOTTOM, expand=False)

# Stop Loss
stop_loss_label = tk.Label(root, text="Stop Loss")
stop_loss_label.pack()
stop_loss_entry = tk.Entry(root)
stop_loss_entry.pack()

# Take Profit
percentage_radio = tk.IntVar()
percentage_radio.set(1)  # Set default value to percentage option

percentage_radio_button = tk.Radiobutton(root, text="Percentage", variable=percentage_radio, value=1)
percentage_radio_button.pack()

price_target_radio_button = tk.Radiobutton(root, text="Price Target", variable=percentage_radio, value=2)
price_target_radio_button.pack()

take_profit_label = tk.Label(root, text="Take Profit")
take_profit_label.pack()
take_profit_entry = tk.Entry(root)
take_profit_entry.pack()

# Risk Percentage
risk_percentage_label = tk.Label(root, text="Risk Percentage")
risk_percentage_label.pack()
risk_percentage_entry = tk.Entry(root)
risk_percentage_entry.pack()

# MT5 Volume Label
mt5_volume_label = tk.Label(root, text="MT5 Volume: 0.00 lots")
mt5_volume_label.pack()

# Calculate Volume Button
calculate_volume_button = tk.Button(root, text="Calculate Volume", command=calculate_and_show_volume)
calculate_volume_button.pack()

# Start the GUI event loop
root.mainloop()

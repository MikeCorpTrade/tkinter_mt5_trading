import tkinter as tk
from tkinter import font
import MetaTrader5 as mt5
from lots_calcul import *
from mt5_request import *
from IAccount import available_accounts, Account


selected_account = available_accounts[input("select the account [vantage_demo, vantage_live, ftmo_demo, ftmo_challenge]: ")]

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
    is_curreny = is_currency_pair(symbol)
    pips = calculate_pips(stop_loss, open_price, symbol, is_curreny)
    pip_value = calculate_pip_value(pips, risk_percentage, account_balance, is_curreny)
    type = mt5.ORDER_TYPE_BUY if order_type == "Buy" else mt5.ORDER_TYPE_SELL
    volume = calculate_volume(pip_value, is_curreny, type=type)

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

    return RequestInfo(symbol, volume, open_price, type, stop_loss, take_profit)


# Create the GUI
root = tk.Tk()
root.title("MetaTrader 5 Order Placement")
root.geometry("400x300")

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

# Start the GUI event loop
root.mainloop()

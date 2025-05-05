import tkinter as tk
from tkinter import font, ttk
import MetaTrader5 as mt5
from lots_calcul import *
from mt5_request import *
from IAccount import available_accounts, Account

selected_account = available_accounts[input("select the account [ftmo_demo, ftmo_challenge]: ")]
# Available assets
symbols_list = ["GER40.cash", "US500.cash", "US100.cash","US2000.cash", "US30.cash", "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "USDJPY"]


def collect_request_info(order_type, account: Account):
    # Connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    mt5.login(login=account.login, password=account.password, server=account.server)

    # Get the account balance
    account_info = mt5.account_info()
    account_balance = account_info.balance
    symbol = symbol_var.get()
    stop_loss = float(stop_loss_entry.get())
    risk_percentage = float(risk_percentage_entry.get())

    # Get all needed infos
    if order_type_var.get() == "Market":
        open_price = mt5.symbol_info_tick(symbol).ask if order_type == "Buy" else mt5.symbol_info_tick(symbol).bid
        type = mt5.ORDER_TYPE_BUY if order_type == "Buy" else mt5.ORDER_TYPE_SELL
        action = mt5.TRADE_ACTION_DEAL
    elif order_type_var.get() == "Limit":
        open_price = float(entry_price_entry.get())
        type = mt5.ORDER_TYPE_BUY_LIMIT if order_type == "Buy" else mt5.ORDER_TYPE_SELL_LIMIT
        action = mt5.TRADE_ACTION_PENDING

    is_currency = is_currency_pair(symbol)
    pips = calculate_pips(stop_loss, open_price, symbol, is_currency)
    pip_value = calculate_pip_value(pips, risk_percentage, account_balance, is_currency)

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

    return RequestInfo(action, symbol, new_volume, open_price, type, stop_loss, take_profit)

# Activate the entry price field
def on_order_type_change():
    if order_type_var.get() == "Market":
        entry_price_entry.config(state='disabled')
    else:
        entry_price_entry.config(state='normal')


# Create the GUI
root = tk.Tk()
root.title("MetaTrader 5 Order Placement")
root.geometry("400x300")

# Type d'ordre : Market ou Limit
order_type_var = tk.StringVar(value="Market")
tk.Label(root, text="Type d'ordre:").pack()
market_radio = tk.Radiobutton(root, text="Market", variable=order_type_var, value="Market", command=on_order_type_change)
limit_radio = tk.Radiobutton(root, text="Limit", variable=order_type_var, value="Limit", command=on_order_type_change)
market_radio.pack()
limit_radio.pack()

# Symbol
symbol_label = tk.Label(root, text="Symbol")
symbol_var = tk.StringVar()
symbol_combobox = ttk.Combobox(root, textvariable=symbol_var, values=symbols_list, state="readonly")
symbol_combobox.current(0)  # sélectionne le premier symbole par défaut
symbol_combobox.pack()

# Create a bold font
button_font = font.Font(weight="bold")
text_color = "white"

# Prix d'entrée (pour ordre limite)
entry_price_label = tk.Label(root, text="Prix d'exécution (Limit only):")
entry_price_label.pack()
entry_price_entry = tk.Entry(root, state='disabled')
entry_price_entry.pack()

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

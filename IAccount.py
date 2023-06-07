from login_info import *

class Account:
    def __init__(self, login, password, server):
        self.login = login
        self.password = password
        self.server = server


ftmo_demo = Account(login=FTMO_DEMO_LOGIN, password=FTMO_DEMO_PASS, server=FTMO_DEMO_SERVER)
ftmo_challenge = Account(login=FTMO_CHALLENGE_LOGIN, password=FTMO_CHALLENGE_PASS, server=FTMO_CHALLENGE_SERVER)
vantage_demo = Account(login=VANTAGE_DEMO_LOGIN, password=VANTAGE_DEMO_PASS, server=VANTAGE_DEMO_SERVER)
vantage_live = Account(login=VANTAGE_LIVE_LOGIN, password=VANTAGE_LIVE_PASS, server=VANTAGE_LIVE_SERVER)
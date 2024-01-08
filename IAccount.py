from login_info import *

class Account:
    def __init__(self, login, password, server):
        self.login = login
        self.password = password
        self.server = server


ftmo_demo = Account(login=FTMO_DEMO_LOGIN, password=FTMO_DEMO_PASS, server=FTMO_DEMO_SERVER)
ftmo_challenge = Account(login=FTMO_CHALLENGE_LOGIN, password=FTMO_CHALLENGE_PASS, server=FTMO_CHALLENGE_SERVER)
ftmo_swing = Account(login=FTMO_SWING_LOGIN, password=FTMO_SWING_PASS, server=FTMO_SWING_SERVER)


available_accounts = {
    "ftmo_demo": ftmo_demo,
    "ftmo_challenge": ftmo_challenge,
    "ftmo_swing": ftmo_swing
}
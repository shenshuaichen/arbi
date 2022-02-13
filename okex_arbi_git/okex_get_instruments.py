import ccxt
import pandas as pd


# import openpyxl

class ChooseInstruments:

    def __init__(self, currency: str):
        self.currency = currency
        self.spot_name = currency + '/USDT'
        self.swap_name = currency + '/USDT:USDT'

    def get_inst(self):
        wb_inst = pd.read_excel('okex_instruments.xlsx')
        wb_inst = wb_inst[wb_inst['instId'] == self.currency+'-USDT-SWAP']
        val_inst = wb_inst['ctVal']
        ccy_inst = wb_inst['ctValCcy']
        minsz_inst = wb_inst['minSz']
        a = [list(val_inst)[0], list(ccy_inst)[0], list(minsz_inst)[0]]
        return a


if __name__ == '__main__':
    api_key = "a31494df-b48d-41f7-ba62-52e0454e4134"
    secret_key = "71C106D8D08A8CF58FA87FE862440CA0"
    passphrase = "okexsim2"

    # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
    flag = '1'  # 模拟盘 demo trading
    # flag = '0'  # 实盘 real trading
    account = ccxt.okex({'apiKey': api_key,
                         'secret': secret_key,
                         'password': passphrase})
    account.set_sandbox_mode(flag)
    instruments = account.public_get_public_instruments(params={'instType': 'SWAP'}).get('data')
    frame = pd.read_excel('okex_instruments.xlsx')

    pd_inst = pd.DataFrame(instruments)
    pd_inst.to_excel('okex_instruments.xlsx')
    print(frame)

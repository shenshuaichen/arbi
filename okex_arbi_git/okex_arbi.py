import ccxt
import okex_account_info as AccInfo
import time
import decimal
from okex_risk_control import risk_control as rc
from okex_get_instruments import ChooseInstruments
# test

time_limit_on = ccxt.bitfinex({'enableRateLimit': True})
okexsimm = ccxt.okex({'apiKey': AccInfo.okexsim2.get('api_key'),
                      'secret': AccInfo.okexsim2.get('secret_key'),
                      'password': AccInfo.okexsim2.get('passphrase')})
okexsimm.set_sandbox_mode(AccInfo.okexsim2.get('flag'))
markets = okexsimm.load_markets(reload=True)
risk = rc(AccInfo.okexsim2.get('api_key'),
          AccInfo.okexsim2.get('secret_key'),
          AccInfo.okexsim2.get('passphrase'),
          AccInfo.okexsim2.get('flag'))
# print(markets.get('BTC/USDT'))  # BTC-USDT
# {'percentage': True, 'taker': 0.0015, 'maker': 0.001, 'precision': {'amount': 1e-08, 'price': 0.1},
# 'limits': {'amount': {'min': 0.001, 'max': None}, 'price': {'min': 0.1, 'max': None},
# 'cost': {'min': 0.0001, 'max': None}, 'leverage': {'max': 10.0}}, 'id': 'BTC-USDT', 'symbol': 'BTC/USDT',
# 'base': 'BTC', 'quote': 'USDT', 'baseId': 'BTC', 'quoteId': 'USDT', 'settleId': '', 'settle': '',
# 'info': {'alias': '', 'baseCcy': 'BTC', 'category': '1', 'ctMult': '', 'ctType': '', 'ctVal': '', 'ctValCcy': '',
# 'expTime': '', 'instId': 'BTC-USDT', 'instType': 'SPOT', 'lever': '10', 'listTime': '1606468572000',
# 'lotSz': '0.00000001', 'minSz': '0.001', 'optType': '', 'quoteCcy': 'USDT', 'settleCcy': '',
# 'state': 'live', 'stk': '', 'tickSz': '0.1', 'uly': ''}, 'type': 'spot', 'spot': True, 'futures': False,
# 'swap': False, 'contract': False, 'option': False, 'linear': False, 'inverse': False, 'active': True,
# 'contractSize': None, 'expiry': None, 'expiryDatetime': None}

# print(markets.get('BTC/USDT:USDT')) # BTC-USDT-SWAP
# {'percentage': True, 'taker': 0.0005, 'maker': 0.0002, 'precision': {'amount': 1.0, 'price': 0.1},
# 'limits': {'amount': {'min': 1.0, 'max': None}, 'price': {'min': 0.1, 'max': None}, 'cost': {'min': 0.1, 'max': None},
# 'leverage': {'max': 125.0}}, 'id': 'BTC-USDT-SWAP', 'symbol': 'BTC/USDT:USDT', 'base': 'BTC', 'quote': 'USDT',
# 'baseId': 'BTC', 'quoteId': 'USDT', 'settleId': 'USDT', 'settle': 'USDT', 'info': {'alias': '', 'baseCcy': '',
# 'category': '1', 'ctMult': '1', 'ctType': 'linear', 'ctVal': '0.01', 'ctValCcy': 'BTC', 'expTime': '',
# 'instId': 'BTC-USDT-SWAP', 'instType': 'SWAP', 'lever': '125', 'listTime': '1606468568000', 'lotSz': '1','minSz': '1',
# 'optType': '', 'quoteCcy': '', 'settleCcy': 'USDT', 'state': 'live', 'stk': '', 'tickSz': '0.1', 'uly': 'BTC-USDT'},
# 'type': 'swap', 'spot': False, 'futures': False, 'swap': True, 'contract': True, 'option': False, 'linear': True,
# 'inverse': False, 'active': True, 'contractSize': '0.01', 'expiry': None, 'expiryDatetime': None}'''

ccy = 'LTC'
swap_lever = 2
tolerance = 0


ccy1 = ChooseInstruments(ccy)
ccy_list = ccy1.get_inst()
spot_inst_id = ccy1.spot_name
swap_inst_id = ccy1.swap_name
okexsimm.set_leverage(swap_lever, swap_inst_id, params={'mgnMode': 'cross'})
loop_sum = 0

while True:
    while okexsimm.fetch_status().get('status') == 'ok':
        break
    #  check balance
    account_details = okexsimm.fetch_balance().get('info').get('data')[0]
    totalEq = float(account_details.get('totalEq'))
    account_details = account_details.get('details')
    #  print(account_details)
    print(totalEq)
    usdt_bal = 0
    btc_bal = 0
    for i in account_details:
        if i.get('ccy') == 'USDT':
            usdt_bal = float(i.get('availEq'))
            print(usdt_bal)
        elif i.get('ccy') == ccy:
            btc_bal = float(i.get('availEq'))
            print(btc_bal)

    account_positions = okexsimm.fetch_positions()
    #  print(account_positions)
    swap_amount = 0
    spot_amount = 0
    liq_Px = 9999999
    if account_positions:
        liq_Px = account_positions[0].get('info').get('liqPx')
        swap_amount = float(account_positions[0].get('info').get('pos'))  # 合约张数
        swap_amount = abs(swap_amount) * float(ccy_list[0])  # 合约对应的货币数量
        spot_amount = btc_bal  # 现货对应的货币数量，无杠杆
    #  check price

    spot_price = okexsimm.fetch_order_book(spot_inst_id).get('bids')[0][0]
    swap_price = okexsimm.fetch_order_book(swap_inst_id).get('asks')[0][0]
    percentage_rate = float(okexsimm.fetch_funding_rate(swap_inst_id).get('info').get('fundingRate'))
    print(spot_price)
    print(swap_price)
    print(percentage_rate)

    #trade
    cash_left = totalEq * 0.01
    order_list = okexsimm.fetch_open_orders()
    if usdt_bal > cash_left:
        if not order_list:
            if percentage_rate > 0:
                Deci = abs(decimal.Decimal(ccy_list[0]).as_tuple().exponent)
                spot_balance = (float(usdt_bal) - cash_left) * 0.5  # 账户的spot分配的部分
                swap_balance = (float(usdt_bal) - cash_left) * 0.5  # 账户的swap分配的部分
                amount_buy_spot = spot_balance / float(spot_price)  # spot最多可购买的数量
                amount_buy_swap = round(amount_buy_spot / swap_lever, Deci)  # swap购买的数量
                amount_buy_spot = amount_buy_swap / (1 - risk.commission().get('comm_c2c')[1])  # spot购买的数量
                if amount_buy_swap >= float(ccy_list[2]):
                    buy_order = okexsimm.create_limit_buy_order(spot_inst_id, str(amount_buy_spot), spot_price,
                                                                params={'tdMode': 'cash'})
                    sell_order = okexsimm.create_limit_sell_order(swap_inst_id,
                                                                  str(int(amount_buy_swap / float(ccy_list[0]))),
                                                                  swap_price, params={'tdMode': 'cross'})
                    print({'buy_order':buy_order,
                           'sell_order':sell_order})
    #  risk control
    risk.downside_risk(percentage_rate, swap_amount, spot_amount, int(swap_lever), swap_price,
                       spot_price, order_list, ccy_list, spot_inst_id, swap_inst_id, tolerance=tolerance)
    risk.upside_risk(liq_Px, swap_amount, swap_price, spot_price,
                     order_list, ccy_list, spot_inst_id, swap_inst_id, position='short')
    time.sleep(1)
    loop_sum = loop_sum +1
    print('第'+str(loop_sum)+'轮循环结束')
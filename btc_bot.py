import pandas as pd
from binance.client import Client
from datetime import datetime
import time
import yfinance as yf
import talib
import requests


start_time = time.time()

btc = yf.Ticker("BTC-USD")
btc_data = btc.history(period="max")
btc_data['ema_100'] = talib.EMA(btc_data['Close'].values, timeperiod=100)
btc_data = btc_data.drop(columns = ['Dividends','Stock Splits'], axis = 1)
btc_data['CPR'] = None

for i in range(1,len(btc_data)):
    if i == 0:
        btc_data.iloc[0,6] = 0
    else:
        btc_data.iloc[i,6] = (btc_data.iloc[i-1,1]+btc_data.iloc[i-1,2]+btc_data.iloc[i-1,3])/3
        
cpr = btc_data.iloc[-1,6]
sma100 = btc_data.iloc[-1,5]
open = btc_data.iloc[-1,0]

def telegram_bot(text_message):
    token = '5846641193:AAG5X9vFKV2e4QYZnLGkWARY-e7VIZ8SX0w'
    chat_id = '842155342'
    url_req = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&text=' + str(text_message)
    response = requests.get(url_req)
    return response.json()


# Replace with your Binance API key and secret
api_key = 'ydWF2ZZvEJMhzXMxxBcwOakR7gHdogecUqcUGluRPrxmiCndUyMBFpRFZo84Fev6'
secret_key = 'QDMSJu4XwfkRdUDiZf7PV8UhAlWQXhJAi3Y3neffHdpgsPZaZH18umo963fLVgkU'

# Initialize the Binance client
client = Client(api_key, secret_key)

# Get the available balance for the futures account
usdt_balance = client.futures_account_balance(asset = 'USDT')[6]['balance']
message = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": Available USDT balance for futures account: " + str(usdt_balance))
print(message)
telegram_bot(message)


#Buy and sell functions
def buy_btc():

    buy_response = client.futures_create_order(
        symbol='BTCUSDT',
        side='BUY',
        Quantity = round(buy_quantity*leverage,3),
        type='MARKET'
    )
    global sell_quantity
    sell_quantity = buy_response['origQty']
    message = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+': BTC bought = ' +  str(round(buy_quantity,5))
                + ' ' + '@ ' + str(price) + ' ,' + 'SL:' + str(stoploss) + ' ,' + 'Lev:' + str(leverage)
                )
    print(message)
    telegram_bot(message)
    stop_response = client.futures_create_order(
        symbol = 'BTCUSDT',
        side = 'SELL',
        Quantity = round(float(sell_quantity),3),
        type='STOP_MARKET',
        stopPrice = stoploss,
        closePosition = True,
        timeInForce = 'GTE_GTC',
    )
    
def sell_btc():
    global sell_quantity
    sell_response = client.futures_create_order(
        symbol='BTCUSDT',
        side='SELL',
        Quantity = round(float(sell_quantity),3),
        reduceOnly = True,
        type='MARKET'
    )
    profit = (sell_price - buy_price)*sell_quantity
    message = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':BTC sold = ' + str(round(float(sell_quantity),5)) + ', ' 
    + '@ ' + str(sell_price) + ', ' + 'Profit: ' + str(profit))
    print(message)
    telegram_bot(message)
    buy_quantity = 0


def buy_exec(buy_time, buy_slip, lev, sl):
    if now >= buy_time:
        if now <= buy_slip:
            x = 0
            btc_price = client.get_symbol_ticker(symbol="BTCUSDT")['price']
            global price
            price = round(float(btc_price),2)
            amount = float(usdt_balance) - 1
            global buy_quantity
            buy_quantity = round(amount/ float(btc_price),5) - 0.01*round(amount/ float(btc_price),5)
            global leverage
            leverage = lev
            global stoploss
            stoploss = round((price - sl*price),0)
            while True:
                if x == 0: 
                    buy_btc()
                    to_save = [float(sell_quantity), float(price)]
                    s = pd.Series(to_save)
                    s.to_csv('D:/Work/Projects/Python/430 to 430/bot2/BTC bot/data.txt', header=False, index=False)
                    time.sleep(1)
                    x = 1
                    continue          
                else:
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':buy order executed')
                    time.sleep(0.5)
                    break
        else: 
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':order not placed before buy slip')
            time.sleep(0.5)
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':some more time to buy')
        time.sleep(0.5)


def sell_exec():
    ss = pd.read_csv('D:/Work/Projects/Python/430 to 430/bot2/BTC bot/data.txt',sep='\t', header=None)
    global sell_quantity
    sell_quantity = ss.iloc[0,0]
    global buy_price
    buy_price = ss.iloc[1,0]
    global sell_price
    sell_price = round(float(client.get_symbol_ticker(symbol="BTCUSDT")['price']),2)
    sell_btc()
    time.sleep(1)

while True:
    now = datetime.now().time()
    time1_buy = datetime.now().time().replace(hour=1, minute=29, second=58, microsecond=0)
    time1_bslip = datetime.now().time().replace(hour=1, minute=30, second=3, microsecond=0)
    time1_sell = datetime.now().time().replace(hour=6, minute=29, second=58, microsecond=0)
    time1_sslip = datetime.now().time().replace(hour=6, minute=30, second=3, microsecond=0)

    time2_buy = datetime.now().time().replace(hour=18, minute=29, second=58, microsecond=0)
    time2_bslip = datetime.now().time().replace(hour=18, minute=30, second=5, microsecond=0)
    time2_sell = datetime.now().time().replace(hour=19, minute=29, second=58, microsecond=0)
    time2_sslip = datetime.now().time().replace(hour=19, minute=30, second=3, microsecond=0)

    time3_buy = datetime.now().time().replace(hour=20, minute=29, second=58, microsecond=0)
    time3_bslip = datetime.now().time().replace(hour=20, minute=30, second=3, microsecond=0)
    time3_sell = datetime.now().time().replace(hour=21, minute=29, second=58, microsecond=0)
    time3_sslip = datetime.now().time().replace(hour=21, minute=30, second=3, microsecond=0)

    
    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")['price']
    price = round(float(btc_price),2)
    if price<cpr and price<sma100:
        message = str(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+": CPR and SMA100 condition not met")
        print(message)
        time.sleep(1)
    else:
        buy_exec(buy_time = time1_buy, buy_slip = time1_bslip, lev = 5, sl = 0.16)
        buy_exec(buy_time = time2_buy, buy_slip = time2_bslip, lev = 11, sl = 0.06)
        buy_exec(buy_time = time3_buy, buy_slip = time3_bslip, lev = 9, sl = 0.1)

    if now >= time1_sell:
        if now <= time1_sslip:
            sell_exec()
            break

    if now >= time2_sell:
        if now <= time2_sslip:
            sell_exec()
            break

    if now >= time3_sell:
        if now <= time3_sslip:
            sell_exec()
            break
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':some more time to sell')
        time.sleep(0.5)    

    end_time = time.time()
    elapsed_time = end_time - start_time

    if elapsed_time > 60:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':Timeout')
        break


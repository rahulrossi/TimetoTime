import pandas as pd
from binance.client import Client
from datetime import datetime
import time

start_time = time.time()

logs = pd.read_excel('logs.xlsx')

# Replace with your Binance API key and secret
api_key = 'ydWF2ZZvEJMhzXMxxBcwOakR7gHdogecUqcUGluRPrxmiCndUyMBFpRFZo84Fev6'
secret_key = 'QDMSJu4XwfkRdUDiZf7PV8UhAlWQXhJAi3Y3neffHdpgsPZaZH18umo963fLVgkU'

# Initialize the Binance client
client = Client(api_key, secret_key)

# Get the available balance for the futures account
btc_balance = client.futures_account_balance(asset = 'USDT')[6]['balance']
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")['price']
price = round(float(btc_price),2)
print("Available BTC balance for futures account: ", btc_balance)

# Calculate the amount to sell
amount = float(btc_balance) - 1
buy_quantity = round(amount/ float(btc_price),5) - 0.01*round(amount/ float(btc_price),5)

#Buy and sell functions
def buy_btc():

    buy_response = client.futures_create_order(
        symbol='BTCUSDT',
        side='BUY',
        Quantity = round(buy_quantity,3),
        type='MARKET',
    )
    global sell_quantity
    sell_quantity = buy_response['origQty']
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+': BTC bought =', round(buy_quantity,5))
    
    
def sell_btc():
    global sell_quantity
    sell_response = client.futures_create_order(
        symbol='BTCUSDT',
        side='SELL',
        Quantity = round(float(sell_quantity),3),
        reduceOnly = True,
        type='MARKET'
    )
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':BTC sold =', round(float(sell_quantity),5)) 
    buy_quantity = 0
    
x = 0
lis = []

while True:
    now = datetime.now().time()
    buy_time = datetime.now().time().replace(hour=13, minute=58, second=1, microsecond=0)
    buy_slip = datetime.now().time().replace(hour=13, minute=58, second=3, microsecond=0)
    sell_time = datetime.now().time().replace(hour=13, minute=58, second=10, microsecond=0)   
    sell_slip = datetime.now().time().replace(hour=13, minute=58
, second=13, microsecond=0)
    
    
    if now >= buy_time:
        if now <= buy_slip:
            if x == 0: 
                buy_btc()
                s = pd.Series(float(sell_quantity))
                s.to_csv('data.txt', header=False, index=False)
                time.sleep(1)
                x = 1
                t_side = 'Buy'
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                close_balance = client.futures_account_balance(asset = 'USDT')[6]['balance']
                value = {'timestamp':timestamp,'open_bal':btc_balance,'side': t_side, 'price':price, 'qty': buy_quantity, 'close_bal': close_balance}
                logs = logs.append(value, ignore_index = True)
                #logs.index = pd.DatetimeIndex(logs['timestamp'])
                logs = logs.drop(columns=['timestamp'])
                logs.to_excel('logs.xlsx')
                continue           
            else:
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':buy order executed')
                time.sleep(0.5)      
        else: 
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':order not placed before buy slip')
            time.sleep(0.5)
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':some more time to buy')
        time.sleep(0.5)
        
    if now >= sell_time:
        if now <= sell_slip: 
            ss = pd.read_csv('data.txt',sep='\t', header=None)
            sell_quantity = ss.iloc[0,0]
            sell_btc()
            time.sleep(1)
            t_side = 'Sell'
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            close_balance = client.futures_account_balance(asset = 'USDT')[6]['balance']
            value = {'timestamp':timestamp,'open_bal':btc_balance,'side': t_side, 'price':price, 'qty': buy_quantity, 'close_bal': close_balance}
            logs = logs.append(value, ignore_index = True)
            logs.index = pd.DatetimeIndex(logs['timestamp'])
            logs = logs.drop(columns=['timestamp'])
            logs.to_excel('logs.xlsx')
            break    
        else:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':not sold before sell slip')
            time.sleep(0.5)
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':some more time to sell')
        time.sleep(0.5)

    end_time = time.time()
    elapsed_time = end_time - start_time

    if elapsed_time > 60:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':Timeout')
        break
    





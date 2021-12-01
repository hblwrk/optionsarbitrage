from ib_insync import *
from yahoo_fin import stock_info
from datetime import datetime, timedelta

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
ib.reqMarketDataType(3) #1 Live, 2 Frozen, 3 Delayed, 4 Delayed Frozen

exchangeName = 'SMART'
currencyName = 'USD'
rights = ['P','C']

for ticker in sorted(stock_info.tickers_sp500()):
    stock = Stock(ticker,exchangeName,currencyName) 
    ib.qualifyContracts(stock)
    optionChains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType,
            stock.conId)
    optionChains = [ c for c in optionChains
            if c.exchange==stock.exchange and
            c.underlyingConId==str(stock.conId)]
    optionChain = optionChains[0]
    expirations = [exp for exp in optionChain.expirations]
    strikes = [strike for strike in optionChain.strikes]
    optionContracts = [Option(ticker,expiration,strike,right,optionChain.exchange,tradingClass=optionChain.tradingClass)
           for right in rights
           for expiration in expirations
           for strike in strikes
            ]
    try:
        optionContracts = ib.qualifyContracts(*optionContracts)
    except Exception:
        pass
    optionContractsPrices = ib.reqTickers(*optionContracts)
    print(optionContractsPrices)

#TODO: Implement logic for comparing option pricing

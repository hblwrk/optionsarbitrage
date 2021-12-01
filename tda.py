#!/usr/bin/env python
#%%
from datetime import datetime, timedelta
from time import sleep

from yahoo_fin import stock_info
from td.client import TDClient
from td.option_chain import OptionChain
from td.exceptions import ExdLmtError

start_time = datetime.now()
session = TDClient(
    client_id="XXXXXX",
    redirect_uri="http://localhost",
    credentials_path="credentials"
)
session.login()
dte = 60
# %%
while True:
    try:
        print(f"***** {datetime.now()} *****")
        print(f"Ticker\tStrike\tMark\tSpread\tFront\t\tBack")
        for ticker in sorted(stock_info.tickers_sp500()):
            oc_args = OptionChain(ticker, to_date=datetime.today() + timedelta(days=dte), option_type="s", strike_count=1)
            while True:
                try:
                    chain = session.get_options_chain(oc_args)
                    dates = list(chain["putExpDateMap"].keys())
                    if not dates:
                        break
                    strikes = list(chain["putExpDateMap"][dates[0]].keys())
                    for strike in strikes:
                        res = []
                        for left in range(len(dates) - 1):
                            for right in range(left + 1, len(dates)):
                                if strike in chain["putExpDateMap"][dates[left]] and strike in chain["putExpDateMap"][dates[right]]:
                                    left_put = chain["putExpDateMap"][dates[left]][strike][0]
                                    right_put = chain["putExpDateMap"][dates[right]][strike][0]
                                    left_call = chain["callExpDateMap"][dates[left]][strike][0]
                                    right_call = chain["callExpDateMap"][dates[right]][strike][0]
                                    marks = [opt["mark"] for opt in [left_put, right_put, left_call, right_call]]
                                    spread_width = sum(opt["ask"] - opt["bid"] for opt in [left_put, right_put, left_call, right_call])
                                    res.append((marks[0] - marks[1] - marks[2] + marks[3], strike, spread_width, dates[left], dates[right]))
                    mark, strike, spread, left, right = min(res or [(0, 0, 0, "", "")])
                    if mark < -1 and spread / chain["underlyingPrice"] < .015:
                        print(f"{ticker}\t{strike}\t{round(mark, 2)}\t{round(spread, 2)}\t{left}\t{right}")
                    break
                except ExdLmtError:
                    sleep(.5)
    except Exception as e:
        print(e)
        pass
# %%

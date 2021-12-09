from datetime import datetime, timedelta
from time import sleep
from yahoo_fin import stock_info
import requests

from config import TD_API_KEY

start_time = datetime.now()
API_KEY = TD_API_KEY
TD_API = "https://api.tdameritrade.com/v1/marketdata/chains"


def construct_params(apikey=API_KEY, symbol="AAPL", contractType="ALL", strikeCount=1,
                     includeQuotes=True, strategy="SINGLE", range="ALL", dte=60):
    return (
        ("apikey", apikey),
        ("symbol", symbol),
        ("contractType", contractType),
        ("strikeCount", strikeCount),
        ("includeQuotes", includeQuotes),
        ("strategy", strategy),
        ("range", range),
        ("toDate", datetime.today() + timedelta(days=dte))
    )


def get_chain(symbol):
    response = requests.get(
        TD_API,
        params=construct_params(symbol=symbol),
        headers={"Cache-Control": "no-cache"}
    )
    sleep(0.51)
    return response.json()


if __name__ == "__main__":
    while True:
        print(f"***** {datetime.now()} *****")
        print(f"Ticker\tStrike\tMark\tSpread\tFront\t\tBack")
        for ticker in sorted(stock_info.tickers_sp500()):
            while True:
                chain = get_chain(ticker)
                dates = list(chain["putExpDateMap"].keys())
                if not dates:
                    break
                strikes = list(chain["putExpDateMap"][dates[0]].keys())
                for strike in strikes:
                    arbs = []
                    for left in range(len(dates) - 1):
                        for right in range(left + 1, len(dates)):
                            if strike in chain["putExpDateMap"][dates[left]] and strike in chain["putExpDateMap"][
                                dates[right]]:
                                left_put = chain["putExpDateMap"][dates[left]][strike][0]
                                right_put = chain["putExpDateMap"][dates[right]][strike][0]
                                left_call = chain["callExpDateMap"][dates[left]][strike][0]
                                right_call = chain["callExpDateMap"][dates[right]][strike][0]
                                marks = [opt["mark"] for opt in [left_put, right_put, left_call, right_call]]
                                spread_width = sum(
                                    opt["ask"] - opt["bid"] for opt in [left_put, right_put, left_call, right_call])
                                arbs.append((marks[0] - marks[1] - marks[2] + marks[3], strike, spread_width,
                                             dates[left], dates[right]))
                mark, strike, spread, left, right = min(arbs or [(0, 0, 0, "", "")])
                if mark < -1 and spread / chain["underlyingPrice"] < .015:
                    print(f"{ticker}\t{strike}\t{round(mark, 2)}\t{round(spread, 2)}\t{left}\t{right}")
                break

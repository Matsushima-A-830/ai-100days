import json
import pandas as pd

with open("btcusdt_1h.json") as f:
    raw = json.load(f)

cols = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "num_trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]
df = pd.DataFrame(raw, columns=cols)
for c in ["open", "high", "low", "close", "volume", "quote_volume"]:
    df[c] = df[c].astype(float)

df["timestamps"] = pd.to_datetime(df["open_time"], unit="ms")
df["amount"] = df["quote_volume"]
df = df[["timestamps", "open", "high", "low", "close", "volume", "amount"]]
df.to_csv("btcusdt_1h.csv", index=False)
print(df.shape)
print(df.head(2))
print(df.tail(2))

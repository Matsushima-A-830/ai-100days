import time

import pandas as pd
from model import Kronos, KronosTokenizer, KronosPredictor

t0 = time.time()
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-2k")
model = Kronos.from_pretrained("NeoQuasar/Kronos-mini")
t1 = time.time()
print(f"Load time: {t1 - t0:.1f}s")

predictor = KronosPredictor(model, tokenizer, device="cpu", max_context=2048)

df = pd.read_csv("btcusdt_1h.csv")
df["timestamps"] = pd.to_datetime(df["timestamps"])

lookback = 200
pred_len = 24

x_df = df.loc[: lookback - 1, ["open", "high", "low", "close", "volume", "amount"]]
x_timestamp = df.loc[: lookback - 1, "timestamps"]
y_timestamp = df.loc[lookback : lookback + pred_len - 1, "timestamps"]

t2 = time.time()
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9,
    sample_count=1,
    verbose=True,
)
t3 = time.time()
print(f"CPU predict time (Kronos-mini, lookback={lookback}, pred_len={pred_len}): {t3 - t2:.1f}s")
print(pred_df.head())

import time
import json
import argparse

import pandas as pd
import numpy as np
from model import Kronos, KronosTokenizer, KronosPredictor

parser = argparse.ArgumentParser()
parser.add_argument("--device", default=None)
parser.add_argument("--out", required=True)
args = parser.parse_args()

tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")

predictor = KronosPredictor(model, tokenizer, device=args.device, max_context=512)
print("ACTUAL_DEVICE:", predictor.device)

df = pd.read_csv("btcusdt_1h.csv")
df["timestamps"] = pd.to_datetime(df["timestamps"])

lookback = 400
pred_len = 120

x_df = df.loc[: lookback - 1, ["open", "high", "low", "close", "volume", "amount"]]
x_timestamp = df.loc[: lookback - 1, "timestamps"]
y_timestamp = df.loc[lookback : lookback + pred_len - 1, "timestamps"]

t0 = time.time()
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
t1 = time.time()
elapsed = t1 - t0
print(f"PREDICT_TIME: {elapsed:.2f}s")

actual = df.loc[lookback : lookback + pred_len - 1, ["close"]].reset_index(drop=True)
pred = pred_df[["close"]].reset_index(drop=True)

mae = float(np.mean(np.abs(actual["close"].values - pred["close"].values)))
mape = float(np.mean(np.abs((actual["close"].values - pred["close"].values) / actual["close"].values)) * 100)

actual_diff = np.diff(df.loc[lookback - 1 : lookback + pred_len - 1, "close"].values)
pred_diff = np.diff(np.concatenate([[df.loc[lookback - 1, "close"]], pred["close"].values]))
directional_hits = int(np.sum(np.sign(actual_diff) == np.sign(pred_diff)))
directional_total = len(actual_diff)
corr = float(np.corrcoef(actual_diff, pred_diff)[0, 1])

metrics = {
    "device": str(predictor.device),
    "predict_time_sec": elapsed,
    "mae_usd": mae,
    "mape_pct": mape,
    "directional_hits": directional_hits,
    "directional_total": directional_total,
    "directional_accuracy": directional_hits / directional_total,
    "diff_correlation": corr,
}
print("METRICS:", json.dumps(metrics, indent=2))

pred_df.to_csv(f"{args.out}_pred.csv")
with open(f"{args.out}_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

kline_df = df.loc[: lookback + pred_len - 1]
kline_df.to_csv(f"{args.out}_kline.csv", index=False)

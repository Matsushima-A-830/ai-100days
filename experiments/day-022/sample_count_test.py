import time, json
import pandas as pd
import numpy as np
from model import Kronos, KronosTokenizer, KronosPredictor

tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, device="cuda:0", max_context=512)

df = pd.read_csv("btcusdt_1h.csv")
df["timestamps"] = pd.to_datetime(df["timestamps"])
lookback, pred_len = 400, 120
x_df = df.loc[:lookback-1, ["open","high","low","close","volume","amount"]]
x_timestamp = df.loc[:lookback-1, "timestamps"]
y_timestamp = df.loc[lookback:lookback+pred_len-1, "timestamps"]

t0=time.time()
pred_df = predictor.predict(df=x_df, x_timestamp=x_timestamp, y_timestamp=y_timestamp,
    pred_len=pred_len, T=1.0, top_p=0.9, sample_count=10, verbose=True)
t1=time.time()

actual = df.loc[lookback:lookback+pred_len-1, "close"].values
pred = pred_df["close"].values
mae = float(np.mean(np.abs(actual-pred)))
mape = float(np.mean(np.abs((actual-pred)/actual))*100)
actual_diff = np.diff(df.loc[lookback-1:lookback+pred_len-1, "close"].values)
pred_diff = np.diff(np.concatenate([[df.loc[lookback-1,"close"]], pred]))
hits = int(np.sum(np.sign(actual_diff)==np.sign(pred_diff)))
corr = float(np.corrcoef(actual_diff, pred_diff)[0,1])
print(json.dumps({"predict_time_sec": t1-t0, "mae_usd": mae, "mape_pct": mape,
  "directional_accuracy": hits/len(actual_diff), "diff_correlation": corr}, indent=2))
pred_df.to_csv("gpu_sc10_pred.csv")

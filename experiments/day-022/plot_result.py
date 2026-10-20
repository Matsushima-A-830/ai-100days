import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

kline_df = pd.read_csv("gpu_kline.csv")
kline_df["timestamps"] = pd.to_datetime(kline_df["timestamps"])
kline_df = kline_df.set_index("timestamps")

pred_df = pd.read_csv("gpu_pred.csv", index_col=0)
pred_df.index = pd.to_datetime(pred_df.index)

lookback = 400

sr_close = kline_df["close"]
sr_pred_close = pred_df["close"]
sr_close.name = "Ground Truth"
sr_pred_close.name = "Kronos-small Prediction"

close_df = pd.concat([sr_close, sr_pred_close], axis=1)

fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))
ax1.plot(close_df.index[: lookback + 1], close_df["Ground Truth"][: lookback + 1], label="Ground Truth (lookback)", color="#2a78d6", linewidth=1.3)
ax1.plot(close_df.index[lookback - 1 :], close_df["Ground Truth"][lookback - 1 :], label="Ground Truth (future, actual)", color="#0a7a3d", linewidth=1.6)
ax1.plot(close_df.index[lookback - 1 :], close_df["Kronos-small Prediction"].reindex(close_df.index[lookback - 1 :]), label="Kronos-small Prediction", color="#d15a25", linewidth=1.6, linestyle="--")
ax1.axvline(close_df.index[lookback - 1], color="gray", linestyle=":", linewidth=1)
ax1.set_ylabel("BTC/USDT Close (USD)", fontsize=12)
ax1.set_title("Kronos-small: BTC/USDT 1h close, 400h lookback -> 120h forecast vs actual", fontsize=12)
ax1.legend(loc="best", fontsize=10)
ax1.grid(True, alpha=0.3)
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig("after.png", dpi=130)
print("saved after.png")

fig2, ax2 = plt.subplots(1, 1, figsize=(10, 5))
ax2.plot(close_df.index[: lookback + 1], close_df["Ground Truth"][: lookback + 1], label="Ground Truth (lookback, 400h)", color="#2a78d6", linewidth=1.3)
ax2.axvline(close_df.index[lookback - 1], color="gray", linestyle=":", linewidth=1)
ax2.set_ylabel("BTC/USDT Close (USD)", fontsize=12)
ax2.set_title("Before: 400h of lookback data fed to Kronos-small (no forecast yet)", fontsize=12)
ax2.legend(loc="best", fontsize=10)
ax2.grid(True, alpha=0.3)
fig2.autofmt_xdate()
plt.tight_layout()
plt.savefig("before.png", dpi=130)
print("saved before.png")

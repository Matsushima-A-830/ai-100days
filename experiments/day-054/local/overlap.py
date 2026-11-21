import json,sys,numpy as np,soundfile as sf
wav,js=sys.argv[1],sys.argv[2]
d,sr=sf.read(wav); d=d.mean(1) if d.ndim>1 else d; fr=int(sr*0.133)
rows=[json.loads(l) for l in open(js) if l.strip()]
talk=quiet=0;out=[]
for i,r in enumerate(rows):
    seg=d[i*fr:(i+1)*fr]; rms=float(np.sqrt(np.mean(seg**2))) if len(seg) else 0.0
    if r["text"].strip():
        st="talk" if rms>0.01 else "quiet"; talk+=st=="talk"; quiet+=st=="quiet"
        out.append(f"{r['time']:.2f}s {rms:.4f} {st} {r['text']!r}")
print(f"== {js}: text frames={len(out)} during-user-talk={talk} user-quiet={quiet}")
print("\n".join(out))

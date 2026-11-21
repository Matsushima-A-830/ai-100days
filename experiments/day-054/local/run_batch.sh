#!/bin/bash
cd ~/haru-verify
H=.venv/bin/haru-inference
run(){ name=$1; shift; echo "### $name: $*" > logs/$name.log; /usr/bin/time -f "wall=%es maxrss=%MKB" $H "$@" >> logs/$name.log 2>&1; grep -E "per frame|wall=" logs/$name.log | tr '\n' ' '; echo " [$name] text=$(tail -n 3 logs/$name.log | grep -v -E 'per frame|wall=' | tail -1)"; }
for s in 1 7 123; do run gpu-en-card-seed$s assets/en_seg.wav out/en_gpu_card_s$s.wav --reference assets/en_ref.wav --device cuda --transcript out/en_gpu_card_s$s.jsonl --system-prompt-file card_en.txt --seed $s; done
for s in 1 7 123; do run gpu-ja-padded-seed$s assets/ja_seg_padded.wav out/ja_gpu_padded_s$s.wav --reference assets/ja_ref.wav --device cuda --transcript out/ja_gpu_padded_s$s.jsonl --system-prompt-file card_ja.txt --seed $s; done
run gpu-en-card-triton assets/en_seg.wav out/en_gpu_card_triton.wav --reference assets/en_ref.wav --device cuda --transcript out/en_gpu_card_triton.jsonl --system-prompt-file card_en.txt --seed 1 --codec-backend triton
run cpu-en-card-seed1 assets/en_seg.wav out/en_cpu_card_s1.wav --reference assets/en_ref.wav --device cpu --transcript out/en_cpu_card_s1.jsonl --system-prompt-file card_en.txt --seed 1
echo BATCH_DONE

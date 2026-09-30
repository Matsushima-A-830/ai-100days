/*
 * rle_decode.c
 *
 * 極小のRun-Length Encoding(RLE)デコーダ。GIFのLZWデコーダにあった
 * 「入力が指す展開後サイズが出力バッファの実サイズを超えていても
 * チェックせずに書き込んでしまう」というクラスのバグ
 * (実例: giflibのDGifSlurp/DGifDecompressLine系のヒープ書き込み脆弱性)
 * を単純化して再現するために書いたもの。実運用コードではない。
 *
 * フォーマット(独自の単純フォーマット):
 *   入力バイト列は [count(1byte), value(1byte)] の繰り返し。
 *   countバイトだけvalueをoutputに書き込む。
 *
 * 意図的なバグ: out_capを受け取っているが、書き込み位置 out_pos が
 * out_cap を超えないかのチェックを一切していない。
 */
#include <stddef.h>
#include <stdint.h>

/* 戻り値: 書き込んだバイト数。out_cap を超えて書き込んでもチェックしない(意図的なバグ)。 */
size_t rle_decode(const uint8_t *in, size_t in_len, uint8_t *out, size_t out_cap) {
    size_t in_pos = 0;
    size_t out_pos = 0;

    while (in_pos + 1 < in_len) {
        uint8_t count = in[in_pos];
        uint8_t value = in[in_pos + 1];
        in_pos += 2;

        for (uint8_t i = 0; i < count; i++) {
            /* バグ: out_pos < out_cap のチェックが無いため、
             * countの合計がout_capを超えるとヒープバッファオーバーフローする */
            out[out_pos] = value;
            out_pos++;
        }
    }

    return out_pos;
}

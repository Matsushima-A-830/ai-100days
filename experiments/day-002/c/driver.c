/*
 * driver.c
 * rle_decode() を実行するだけの最小CLI。
 * 使い方: ./driver <out_cap> <hex_input>
 *   hex_input は "count,value" ペアを16進2桁ずつ並べた文字列(例: "0341" は count=3,value=0x41)
 * 出力: "OUT_POS <n>" の後に、書き込まれたバイト数(out_cap上限まで)を16進で出力する。
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

size_t rle_decode(const uint8_t *in, size_t in_len, uint8_t *out, size_t out_cap);

static size_t hex_decode(const char *hex, uint8_t *out) {
    size_t len = strlen(hex);
    size_t n = 0;
    for (size_t i = 0; i + 2 <= len; i += 2) {
        unsigned int byte;
        sscanf(hex + i, "%2x", &byte);
        out[n++] = (uint8_t)byte;
    }
    return n;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s <out_cap> <hex_input>\n", argv[0]);
        return 2;
    }

    size_t out_cap = (size_t)strtoul(argv[1], NULL, 10);
    const char *hex = argv[2];

    uint8_t in_buf[4096];
    size_t in_len = hex_decode(hex, in_buf);

    uint8_t *out = malloc(out_cap);
    if (!out) {
        fprintf(stderr, "malloc failed\n");
        return 1;
    }

    size_t out_pos = rle_decode(in_buf, in_len, out, out_cap);

    printf("OUT_POS %zu\n", out_pos);
    size_t print_n = out_pos < out_cap ? out_pos : out_cap;
    for (size_t i = 0; i < print_n; i++) {
        printf("%02x", out[i]);
    }
    printf("\n");

    free(out);
    return 0;
}

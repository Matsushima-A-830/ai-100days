//! rle_decode.c (giflib風のRLE展開処理の縮小版) をClaude Codeで
//! Rustへ書き換えたもの。元のCコードは `out_cap` を超えて書き込んでも
//! チェックしないバグ(CWE-787, ヒープバッファオーバーフロー)を持つが、
//! Rustではキャパシティ超過を`Err`として返し、決して`out_cap`を超えて
//! メモリへ書き込まない。

#[derive(Debug, PartialEq, Eq)]
pub struct CapacityExceeded {
    pub needed_at_least: usize,
    pub out_cap: usize,
}

/// C版のrle_decodeと同じ入力フォーマット([count, value]の繰り返し)を
/// out_cap バイトまでの Vec<u8> として安全に展開する。
/// out_cap を超えて書き込む必要が生じた時点で即座にエラーを返す
/// (Cの脆弱版と違い、書き込みそのものが起きない)。
pub fn rle_decode(input: &[u8], out_cap: usize) -> Result<Vec<u8>, CapacityExceeded> {
    let mut out = Vec::with_capacity(out_cap.min(1 << 20));
    let mut pairs = input.chunks_exact(2);

    for pair in &mut pairs {
        let count = pair[0];
        let value = pair[1];
        for _ in 0..count {
            if out.len() >= out_cap {
                return Err(CapacityExceeded {
                    needed_at_least: out.len() + 1,
                    out_cap,
                });
            }
            out.push(value);
        }
    }

    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decodes_valid_input_within_capacity() {
        // 03 41 02 42 -> "AAA" + "BB"
        let input = [0x03, 0x41, 0x02, 0x42];
        let out = rle_decode(&input, 10).unwrap();
        assert_eq!(out, b"AAABB");
    }

    #[test]
    fn rejects_input_that_would_overflow_capacity() {
        // 14(=20) 41 00 00 -> 20バイト要求だがcapは4
        let input = [0x14, 0x41, 0x00, 0x00];
        let err = rle_decode(&input, 4).unwrap_err();
        assert_eq!(err.out_cap, 4);
        assert!(err.needed_at_least > 4);
    }

    #[test]
    fn odd_trailing_byte_is_ignored_like_c_version() {
        // Cのdriver/rle_decodeも in_pos+1 < in_len の条件で末尾の1バイト単独は無視する
        let input = [0x02, 0x41, 0x99];
        let out = rle_decode(&input, 10).unwrap();
        assert_eq!(out, b"AA");
    }
}

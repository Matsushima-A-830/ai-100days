use rle_decode::rle_decode;
use std::env;
use std::process::ExitCode;

fn hex_decode(hex: &str) -> Vec<u8> {
    let bytes = hex.as_bytes();
    let mut out = Vec::with_capacity(bytes.len() / 2);
    let mut i = 0;
    while i + 2 <= bytes.len() {
        let s = std::str::from_utf8(&bytes[i..i + 2]).unwrap();
        out.push(u8::from_str_radix(s, 16).unwrap());
        i += 2;
    }
    out
}

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: {} <out_cap> <hex_input>", args[0]);
        return ExitCode::from(2);
    }

    let out_cap: usize = args[1].parse().expect("out_cap must be a number");
    let input = hex_decode(&args[2]);

    match rle_decode(&input, out_cap) {
        Ok(out) => {
            println!("OUT_POS {}", out.len());
            println!("{}", out.iter().map(|b| format!("{:02x}", b)).collect::<String>());
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!(
                "ERROR: capacity exceeded (needed >= {}, out_cap = {}) — write prevented, no memory corruption",
                e.needed_at_least, e.out_cap
            );
            ExitCode::from(1)
        }
    }
}

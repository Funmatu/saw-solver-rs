// src/lib.rs

// ============================================================================
// Core Logic (Pure Rust)
// ============================================================================

// N=20に対応するため、十分なサイズを確保 (64x64)
// スタックオーバーフローを避けるギリギリだが、bool配列なら4KB程度なので安全
const GRID_SIZE: usize = 64;
const CENTER: usize = 32;

fn core_solve(n: usize) -> u64 {
    // n=0の例外処理
    if n == 0 { return 1; }
    
    // NがGRID_SIZEの半径を超えないかチェック
    if n > CENTER {
        panic!("N is too large for the current GRID_SIZE");
    }

    // スタック上に確保（高速・ゼロアロケーション）
    let mut visited = [[false; GRID_SIZE]; GRID_SIZE];
    
    // 中心からスタート
    visited[CENTER][CENTER] = true;
    
    // 対称性を利用して4倍する
    // (0, 1) つまり x=CENTER, y=CENTER+1 へ移動
    // 戻り値をu64にして、N=20などの巨大な数に対応
    dfs(CENTER, CENTER + 1, 1, n, &mut visited) * 4
}

// 深さ優先探索
fn dfs(x: usize, y: usize, step: usize, target_step: usize, visited: &mut [[bool; GRID_SIZE]; GRID_SIZE]) -> u64 {
    if step == target_step {
        return 1;
    }

    visited[y][x] = true;
    let mut count: u64 = 0;

    // 上下左右の移動定義
    // ループ展開やイテレータを使わず、直接インデックス操作を行うのが最速だが、
    // Rustのコンパイラ最適化を信じて可読性の高いループを使用
    let moves = [(0, 1), (0, -1), (1, 0), (-1, 0)];

    for (dx, dy) in moves {
        // usizeへのキャスト。
        // GRID_SIZEが十分大きいため、負の値になるチェックは不要（CENTER=32, max N=20なら絶対安全）
        let nx = (x as isize + dx) as usize;
        let ny = (y as isize + dy) as usize;

        if !visited[ny][nx] {
            count += dfs(nx, ny, step + 1, target_step, visited);
        }
    }

    // バックトラック
    visited[y][x] = false;
    
    count
}


// ============================================================================
// Feature: Python (PyO3)
// ============================================================================
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pyfunction]
fn solve(n: usize) -> PyResult<u64> {
    // Python側へはu64を返す（Pythonのintは自動的に多倍長になるのでOK）
    Ok(core_solve(n))
}

#[cfg(feature = "python")]
#[pymodule]
fn saw_solver_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve, m)?)?;
    Ok(())
}


// ============================================================================
// Feature: WebAssembly (wasm-bindgen)
// ============================================================================
#[cfg(feature = "wasm")]
use wasm_bindgen::prelude::*;

#[cfg(feature = "wasm")]
#[wasm_bindgen]
pub fn solve_js(n: usize) -> u64 {
    // JSのNumber型(double)は2^53まで正確。
    // N=12程度なら問題ないが、Nが大きいと精度が落ちる可能性があるため、
    // 必要ならBigIntを使うべきだが、ここでは利便性のためu64を返す。
    // (wasm-bindgenが自動的にBigIntとして扱ってくれる設定になる場合がある)
    core_solve(n)
}
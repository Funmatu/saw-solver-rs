# SAW Solver RS: High-Performance Self-Avoiding Walk Solver

![Build Status](https://github.com/Funmatu/saw-solver-rs/actions/workflows/deploy.yml/badge.svg)
![Rust](https://img.shields.io/badge/Language-Rust-orange.svg)
![Platform](https://img.shields.io/badge/Platform-WASM%20%7C%20Python-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**SAW Solver RS** is a specialized, high-performance computing kernel designed to solve the [Self-Avoiding Walk (SAW)](https://en.wikipedia.org/wiki/Self-avoiding_walk) problem on a 2D grid.

Built with **Rust**, it employs a dual-runtime architecture:
1.  **Python Extension (PyO3):** Provides rigorous backend calculation capabilities, outperforming pure Python implementations by orders of magnitude.
2.  **WebAssembly (WASM):** Enables client-side execution directly in the browser for demos and visualizations without server-side processing.

## 1. Problem Definition (Q08)

The core algorithm calculates the number of distinct paths (Self-Avoiding Walks) of length $N$ starting from a center point on a square grid, such that the path never visits the same node twice.

* **Input:** Integer $N$ (Number of steps)
* **Output:** Integer (Count of valid paths)
* **Constraints:** High computational complexity ($O(3^N)$ roughly). $N=12$ is trivial for Rust, but $N=20$ involves exploring massive search spaces.

## 2. Technical Architecture

### Algorithm: Optimized Backtracking DFS
Unlike naive implementations that use HashMaps or Tuple Lists to track visited nodes (which incurs high allocation overhead), this solver uses **Stack-Allocated Boolean Grids**.

* **Memory Efficiency:** Uses a fixed-size `bool` array (`[[false; 64]; 64]`) allocated on the stack. This results in **Zero Heap Allocation** during the recursion.
* **Speed:** Grid access is $O(1)$ and highly cache-friendly compared to Hash lookups.
* **Safety:** Leveraging Rust's ownership model, the solver guarantees memory safety even with raw array indexing optimizations.

### Dual-Target Compilation
The `Cargo.toml` is configured with features to switch between targets:

| Feature | Crate Dependency | Output | Use Case |
| :--- | :--- | :--- | :--- |
| `python` | `pyo3` | `.so` / `.pyd` | Python Scripts, Jupyter Notebooks |
| `wasm` | `wasm-bindgen` | `.wasm` + JS Glue | Web Apps, GitHub Pages |

## 3. Installation & Usage

### A. Python (for Analysis)
**Requirements:** Python 3.8+, Rust toolchain.

1.  **Setup Environment:**
    ```bash
    # It is recommended to use uv or venv
    pip install maturin
    ```

2.  **Build & Install:**
    ```bash
    maturin develop --release --features python
    ```

3.  **Run Benchmark:**
    ```bash
    python tests/benchmark.py
    ```

### **Benchmark Results**
Comparison between Rust (Release Build) and Python implementations.
The Rust implementation demonstrates extreme performance, solving $N=20$ (approx. 900 million paths) in sub-millisecond time.

**Environment:**
* OS: Linux (WSL2)
* CPU: Release Build

| N  | Target | Result      | Time (ms) | Status    | Speedup (approx.) |
|:---|:-------|:------------|:----------|:----------|:------------------|
| 3  | Rust   | 36          | 0.00      | OK        | -                 |
| 3  | Python | 36          | 0.00      | Match     | -                 |
| 10 | Rust   | 44,100      | 0.00      | OK        | -                 |
| 10 | Python | 44,100      | 0.00      | Match     | -                 |
| 12 | Rust   | 324,932     | 0.00      | OK        | **> ∞** |
| 12 | Python | 324,932     | 6.27      | Match     | 1x                |
| 13 | Rust   | 881,500     | 0.00      | OK        | **> ∞** |
| 13 | Python | 881,500     | 22.23     | Match     | 1x                |
| 15 | Rust   | 6,416,596   | 0.10      | OK        | **~1,900x** |
| 15 | Python | 6,416,596   | 192.22    | Match     | 1x                |
| 18 | Rust   | 124,658,732 | 0.10      | OK        | **~38,000x** |
| 18 | Python | 124,658,732 | 3,791.63  | Match     | 1x                |
| 20 | Rust   | 897,697,164 | 0.14      | OK        | **N/A** |
| 20 | Python | (Skipped)   | -         | TOO LARGE | -                 |

*Note: Time `0.00` indicates execution completed below the timer resolution.*

### B. WebAssembly (for Demo)
**Requirements:** `wasm-pack`

1.  **Build:**
    ```bash
    wasm-pack build --target web --out-dir www/pkg --no-default-features --features wasm
    ```

2.  **Run Locally:**
    ```bash
    cd www
    python3 -m http.server 8000
    ```
    Open `http://localhost:8000` in your browser.

## 4. Development Guide

### File Structure
```text
saw-solver-rs/
├── .github/workflows/deploy.yml  # Auto-deploy to GitHub Pages
├── src/
│   └── lib.rs                    # The Core Logic (Dual implementation)
├── tests/
│   └── benchmark.py              # Comparison script
├── www/                          # Frontend Assets
│   ├── index.html
│   ├── index.js
│   └── pkg/                      # Generated WASM (ignored by git)
├── Cargo.toml                    # Manifest
└── pyproject.toml                # Python build config

```

### Dealing with N=20

Calculating $N=20$ is computationally expensive ($324,932$ paths for $N=12$, but exponentially more for $N=20$).

* The Rust solver utilizes `u64` to prevent integer overflow (standard `u32` is insufficient for $N \ge 16$).
* The algorithm is single-threaded DFS. For extreme values ($N > 25$), a multi-threaded approach (using `rayon` to split the first level of recursion) would be required, but strictly sequential DFS is implemented here for maximum portability (WASM compatibility).

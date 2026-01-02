# SAW Solver RS: High-Performance Self-Avoiding Walk Solver

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

    **Example Output (Apple M1):**
    ```text
    N    | Target   | Result          | Time (ms)  | Status    
    ------------------------------------------------------------
    12   | Rust     | 324932          | 2.50       | OK        
    12   | Python   | 324932          | 450.10     | (Match)   
    ------------------------------------------------------------
    ```
    *Note: Rust is approximately 150x - 200x faster than the optimized Python version.*

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

Calculating  is computationally expensive ( paths for , but exponentially more for ).

* The Rust solver utilizes `u64` to prevent integer overflow (standard `u32` is insufficient for ).
* The algorithm is single-threaded DFS. For extreme values (), a multi-threaded approach (using `rayon` to split the first level of recursion) would be required, but strictly sequential DFS is implemented here for maximum portability (WASM compatibility).
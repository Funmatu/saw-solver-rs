import init, { solve_js } from './pkg/saw_solver_rs.js';

async function run() {
    await init(); // Initialize WASM
    
    const btn = document.getElementById('run-btn');
    const input = document.getElementById('n-input');
    const output = document.getElementById('output');
    
    btn.innerText = "Calculate Paths";
    btn.disabled = false;

    btn.addEventListener('click', () => {
        const n = parseInt(input.value);
        if (isNaN(n) || n < 1) {
            output.innerText = "Please enter a valid number > 0";
            return;
        }

        output.innerText = `Computing N=${n}...`;
        btn.disabled = true;
        
        // UI描画更新のためsetTimeoutを使用
        setTimeout(() => {
            try {
                const start = performance.now();
                
                // Rust関数呼び出し
                const result = solve_js(n);
                
                const end = performance.now();
                const time = (end - start).toFixed(2);
                
                // BigIntの場合は 'n' サフィックスが付くことがあるのでString化
                output.innerText = `N = ${n}\nPaths: ${result.toString()}\nTime: ${time} ms`;
            } catch (e) {
                output.innerText = `Error: ${e}`;
            } finally {
                btn.disabled = false;
            }
        }, 10);
    });
}

run();
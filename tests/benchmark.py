import sys
import time
import concurrent.futures
import saw_solver_rs  # maturin develop でインストール済みと仮定


# Python実装（先ほどの最適化版）
def solve_python(n):
    sys.setrecursionlimit(max(2000, n * 100))
    grid_size = n * 2 + 1
    center = n
    visited = [[False] * grid_size for _ in range(grid_size)]
    visited[center][center] = True
    return _dfs(center, center + 1, 1, n, visited) * 4


def _dfs(x, y, step, limit, visited):
    if step == limit:
        return 1
    visited[y][x] = True
    c = 0
    if not visited[y + 1][x]:
        c += _dfs(x, y + 1, step + 1, limit, visited)
    if not visited[y - 1][x]:
        c += _dfs(x, y - 1, step + 1, limit, visited)
    if not visited[y][x + 1]:
        c += _dfs(x + 1, y, step + 1, limit, visited)
    if not visited[y][x - 1]:
        c += _dfs(x - 1, y, step + 1, limit, visited)
    visited[y][x] = False
    return c


def run_with_timeout(func, args, timeout_sec):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args)
        try:
            start = time.time()
            result = future.result(timeout=timeout_sec)
            end = time.time()
            return result, (end - start) * 1000
        except concurrent.futures.TimeoutError:
            return None, None


def benchmark():
    test_cases = [3, 10, 12, 13, 15, 18, 20]
    timeout = 5.0  # 秒

    print(
        f"{'N':<4} | {'Target':<8} | {'Result':<15} | {'Time (ms)':<10} | {'Status':<10}"
    )
    print("-" * 60)

    for n in test_cases:
        # 1. Rust Test
        res, t = run_with_timeout(saw_solver_rs.solve, (n,), timeout)
        if res is not None:
            print(f"{n:<4} | {'Rust':<8} | {res:<15} | {t:<10.2f} | {'OK':<10}")
        else:
            print(
                f"{n:<4} | {'Rust':<8} | {'-':<15} | {'> 5000':<10} | {'TIMEOUT':<10}"
            )

        # 2. Python Test (Nが大きい場合はスキップまたはタイムアウト前提)
        if n <= 18:  # Pythonは遅いので
            res_py, t_py = run_with_timeout(solve_python, (n,), timeout)
            if res_py is not None:
                match_mark = (
                    "(Match)" if res is not None and res == res_py else "(DIFF!)"
                )
                print(
                    f"{n:<4} | {'Python':<8} | {res_py:<15} | {t_py:<10.2f} | {match_mark:<10}"
                )
            else:
                print(
                    f"{n:<4} | {'Python':<8} | {'-':<15} | {'> 5000':<10} | {'TIMEOUT':<10}"
                )
        else:
            print(
                f"{n:<4} | {'Python':<8} | {'(Skipped)':<15} | {'-':<10} | {'TOO LARGE':<10}"
            )

        print("-" * 60)


if __name__ == "__main__":
    benchmark()

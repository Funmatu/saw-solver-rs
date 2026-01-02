import sys

# 再帰制限の緩和
sys.setrecursionlimit(10000)


def solve_q08_python(n):
    # 中心(n)から最大n歩進むため、グリッドサイズは 2n+1 必要
    grid_size = n * 2 + 1
    center = n

    # 高速化のため、クラスを使わずプリミティブなリストで管理
    # Falseで初期化されたグリッド
    visited = [[False] * grid_size for _ in range(grid_size)]

    # スタート地点
    visited[center][center] = True

    # 対称性を利用: 最初の1歩を(0, 1)に固定し、結果を4倍する
    return _dfs(center, center + 1, 1, n, visited) * 4


def _dfs(x, y, step, limit, visited):
    if step == limit:
        return 1

    visited[y][x] = True
    count = 0

    # 上下左右 (インライン展開的に記述したほうがPythonでは速い場合があるが、可読性維持)
    # 境界チェックは、配列サイズを十分にとっているため省略可能（これが高速化の肝）

    # Up
    if not visited[y + 1][x]:
        count += _dfs(x, y + 1, step + 1, limit, visited)
    # Down
    if not visited[y - 1][x]:
        count += _dfs(x, y - 1, step + 1, limit, visited)
    # Right
    if not visited[y][x + 1]:
        count += _dfs(x + 1, y, step + 1, limit, visited)
    # Left
    if not visited[y][x - 1]:
        count += _dfs(x - 1, y, step + 1, limit, visited)

    # Backtrack
    visited[y][x] = False
    return count

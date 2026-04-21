import random
import string
import time
import tracemalloc
import matplotlib.pyplot as plt
from datetime import datetime

from solver import solve


def generate_case(rows, cols, num_points):
    grid = [['0' for _ in range(cols)] for _ in range(rows)]

    # Start point
    start = (random.randint(0, rows-1), random.randint(0, cols-1))
    grid[start[0]][start[1]] = 'R'

    delivery = {}

    letters = list(string.ascii_uppercase)
    for i in range(num_points):
        while True:
            r, c = random.randint(0, rows-1), random.randint(0, cols-1)
            if grid[r][c] == '0':
                grid[r][c] = letters[i]
                delivery[letters[i]] = (r, c)
                break

    return delivery, start


def run_once(delivery, start):
    tracemalloc.start()

    t0 = time.perf_counter()
    solve(delivery, start)
    t1 = time.perf_counter()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return (t1 - t0), peak / 1024  # segundos, KB


def benchmark():
    sizes = list(range(2, 12))  # 12 pontos foi o max que rodou na minha maquina
    times = []
    memories = []

    for n in sizes:
        print(f"Testando com {n} pontos de entrega...")

        delivery, start = generate_case(6, 6, n)

        t, mem = run_once(delivery, start)

        print(f"  Tempo: {t:.4f}s | Uso maximo de memoria: {mem:.2f} KB")

        times.append(t)
        memories.append(mem)

    return sizes, times, memories


def plot_results(sizes, times, memories):
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Tempo
    ax1.set_xlabel("Número de Pontos")
    ax1.set_ylabel("Tempo (Segundos)", color="tab:blue")
    ax1.plot(sizes, times, marker='o', color="tab:blue")
    ax1.tick_params(axis='y', labelcolor="tab:blue")

    # Memoria
    ax2 = ax1.twinx()
    ax2.set_ylabel("Uso máximo de memória (KB)", color="tab:red")
    ax2.plot(sizes, memories, marker='s', linestyle='--', color="tab:red")
    ax2.tick_params(axis='y', labelcolor="tab:red")

    plt.title("Benchmark: Tempo vs Memória (Força Bruta TSP)")
    fig.tight_layout()
    plt.grid(True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_{timestamp}.png"

    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {filename}")


if __name__ == "__main__":
    random.seed(42)
    sizes, times, memories = benchmark()
    plot_results(sizes, times, memories)
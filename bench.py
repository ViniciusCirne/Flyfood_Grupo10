import random
import string
import time
import tracemalloc
import matplotlib.pyplot as plt
from datetime import datetime

from solver import solve


# ==========================================
# GERA CASOS ALEATÓRIOS
# ==========================================

def generate_case(rows, cols, num_points):

    grid = [['0' for _ in range(cols)] for _ in range(rows)]

    # Ponto inicial
    start = (
        random.randint(0, rows - 1),
        random.randint(0, cols - 1)
    )

    grid[start[0]][start[1]] = 'R'

    delivery = {}

    letters = list(string.ascii_uppercase)

    for i in range(num_points):

        while True:

            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)

            if grid[r][c] == '0':

                grid[r][c] = letters[i]

                delivery[letters[i]] = (r, c)

                break

    return delivery, start, grid


# ==========================================
# PRINTA MATRIZ
# ==========================================

def print_grid(grid):

    print("Matriz gerada:\n")

    for row in grid:

        print(' '.join(row))

    print()


# ==========================================
# EXECUTA UMA INSTÂNCIA
# ==========================================

def run_once(delivery, start):

    tracemalloc.start()

    t0 = time.perf_counter()

    # ======================================
    # CHAMA O ALGORITMO GENÉTICO
    # ======================================

    best_route, best_cost = solve(delivery, start)

    t1 = time.perf_counter()

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    return (
        best_route,
        best_cost,
        (t1 - t0),
        peak / 1024
    )


# ==========================================
# BENCHMARK
# ==========================================

def benchmark():

    sizes = list(range(2, 20))

    times = []
    memories = []

    for n in sizes:

        print("=" * 50)
        print(f"Testando com {n} pontos de entrega...")
        print("=" * 50)

        delivery, start, grid = generate_case(6, 6, n)

        # ======================================
        # PRINTA A MATRIZ COMPLETA
        # ======================================

        print_grid(grid)

        # ======================================
        # EXECUÇÃO
        # ======================================

        best_route, best_cost, t, mem = run_once(
            delivery,
            start
        )

        # ======================================
        # RESULTADOS
        # ======================================

        print(f"Melhor rota encontrada: {best_route}")

        print(f"Custo total: {best_cost}")

        print(
            f"Tempo: {t:.4f}s | "
            f"Uso máximo de memória: {mem:.2f} KB"
        )

        print()

        times.append(t)
        memories.append(mem)

    return sizes, times, memories


# ==========================================
# PLOT DOS RESULTADOS
# ==========================================

def plot_results(sizes, times, memories):

    fig, ax1 = plt.subplots(figsize=(8, 5))

    # ======================================
    # TEMPO
    # ======================================

    ax1.set_xlabel("Número de Pontos")

    ax1.set_ylabel(
        "Tempo (Segundos)",
        color="tab:blue"
    )

    ax1.plot(
        sizes,
        times,
        marker='o',
        color="tab:blue"
    )

    ax1.tick_params(
        axis='y',
        labelcolor="tab:blue"
    )

    # ======================================
    # MEMÓRIA
    # ======================================

    ax2 = ax1.twinx()

    ax2.set_ylabel(
        "Uso máximo de memória (KB)",
        color="tab:red"
    )

    ax2.plot(
        sizes,
        memories,
        marker='s',
        linestyle='--',
        color="tab:red"
    )

    ax2.tick_params(
        axis='y',
        labelcolor="tab:red"
    )

    # ======================================
    # TÍTULO
    # ======================================

    plt.title(
        "Benchmark: Algoritmo Genético "
        "(Tempo vs Memória)"
    )

    fig.tight_layout()

    plt.grid(True)

    # ======================================
    # SALVA O GRÁFICO
    # ======================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"benchmark_{timestamp}.png"

    plt.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    print(f"\nPlot salvo em: {filename}")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    random.seed(42)

    sizes, times, memories = benchmark()

    plot_results(
        sizes,
        times,
        memories
    )
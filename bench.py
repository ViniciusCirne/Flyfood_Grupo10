import random
import time
import tracemalloc
import csv
import math
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from solver import (
    solve as bf_solve,
    solve_dfs_pruning as dfs_solve,
    solve_mst_pruning as mst_solve,
    solve_genetic as gen_solve
)


# Configurações dos testes
GRID_ROWS = 50
GRID_COLS = 50
RANDOM_SEED = 46

EXACT_SOLVER = ("MST + Pruning", mst_solve)

SOLVERS = [
    ("Força Bruta", bf_solve),
    ("DFS com Poda", dfs_solve),
    ("MST + Poda", mst_solve),
    ("Algoritmo Genético", gen_solve)
]

SOLVER_SIZES = {
    "Força Bruta": list(range(2, 11)),
    "DFS com Poda": list(range(2, 13)),
    "MST + Poda": list(range(2, 22)),
    "Algoritmo Genético": list(range(2, 22)),
}

COLORS = {
    "Força Bruta": "#e05c5c",
    "DFS com Poda": "#5c9ee0",
    "MST + Poda": "#5cba7d",
    "Algoritmo Genético": "#03fca5",
}


# Funções auxiliares
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def route_cost(route, start, delivery):
    if not route:
        return 0

    points = [start] + [delivery[p] for p in route]

    cost = sum(
        manhattan(points[i], points[i + 1])
        for i in range(len(points) - 1)
    )

    return cost + manhattan(points[-1], start)


def normalize_route(route):
    if isinstance(route, tuple):
        route = route[0]

    if isinstance(route, str):
        return route.split()

    return route


# Execução de uma instância
def run_once(solver_fn, delivery, start):
    tracemalloc.start()
    t0 = time.perf_counter()

    try:
        route = solver_fn(delivery, start)
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()

        return t1 - t0, peak / 1024, route

    finally:
        tracemalloc.stop()


# Geração dos casos aleatórios
def generate_case(rows, cols, num_points):
    grid = [["0"] * cols for _ in range(rows)]

    start = (
        random.randint(0, rows - 1),
        random.randint(0, cols - 1)
    )

    grid[start[0]][start[1]] = "R"
    delivery = {}

    for i in range(num_points):
        while True:
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)

            if grid[r][c] == "0":
                label = f"P{i + 1}"
                grid[r][c] = label
                delivery[label] = (r, c)
                break

    return delivery, start


def build_cases():
    sizes = sorted(set().union(*SOLVER_SIZES.values()))
    cases = {}

    for n in sizes:
        random.seed(RANDOM_SEED + n)
        cases[n] = generate_case(GRID_ROWS, GRID_COLS, n)

    return cases


# Compara o algoritmo genético com o algoritmo exato
def verify_optimality(ga_results, exact_results):
    exact_name, _ = EXACT_SOLVER
    print(f"\nVerificação de qualidade: Gen Algo vs {exact_name}")

    exact_by_n = dict(zip(exact_results["sizes"], exact_results["costs"]))
    rows = []

    for i, n in enumerate(ga_results["sizes"]):
        if n not in exact_by_n:
            print(f"  n={n:2d} exact não disponível")
            continue

        ga_cost = ga_results["costs"][i]
        exact_cost = exact_by_n[n]
        gap = (ga_cost - exact_cost) / exact_cost * 100
        is_optimal = ga_cost == exact_cost

        status = "ótimo" if is_optimal else f"gap={gap:+.2f}%"

        print(
            f"  n={n:2d} "
            f"GA={ga_cost} "
            f"Exato={exact_cost} "
            f"{status}"
        )

        rows.append({
            "n": n,
            "ga_cost": ga_cost,
            "exact_cost": exact_cost,
            "gap_pct": gap,
            "optimal": is_optimal
        })

    if rows:
        optimal_count = sum(row["optimal"] for row in rows)
        avg_gap = sum(row["gap_pct"] for row in rows) / len(rows)

        print(f"\nÓtimo encontrado: {optimal_count}/{len(rows)}")
        print(f"Gap médio: {avg_gap:+.3f}%")

    return rows


# Benchmark principal
def benchmark():
    results = {}
    cases = build_cases()

    for name, solver_fn in SOLVERS:
        print(f"\n{name}")

        res = {
            "sizes": [],
            "times": [],
            "memories": [],
            "costs": [],
            "routes": []
        }

        for n in SOLVER_SIZES[name]:
            delivery, start = cases[n]

            t, mem, route = run_once(solver_fn, delivery, start)

            route = normalize_route(route)
            cost = route_cost(route, start, delivery)

            res["sizes"].append(n)
            res["times"].append(t)
            res["memories"].append(mem)
            res["costs"].append(cost)
            res["routes"].append(route)

            print(f"  n={n}  t={t:.3f}s  mem={mem:.1f}KB  cost={cost}")

        results[name] = res

    exact_name, _ = EXACT_SOLVER

    if "Gen Algo" in results and exact_name in results:
        verify_optimality(results["Gen Algo"], results[exact_name])

    return results


# Exporta os dados para CSV
def export_csv(results, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "solver",
            "n",
            "time_seconds",
            "memory_kb",
            "cost",
            "route"
        ])

        for name, res in results.items():
            for i, n in enumerate(res["sizes"]):
                writer.writerow([
                    name,
                    n,
                    res["times"][i],
                    res["memories"][i],
                    res["costs"][i],
                    " ".join(res["routes"][i])
                ])


# Gera o gráfico principal
def plot_performance(results, ts):
    fig, ax = plt.subplots(figsize=(10, 6))

    for name, res in results.items():
        ax.plot(
            res["sizes"],
            res["times"],
            marker="o",
            label=name,
            color=COLORS.get(name)
        )

    ax.set_title("Tempo de Execução por Número de Entregas")
    ax.set_xlabel("Número de entregas")
    ax.set_ylabel("Tempo (s)")
    ax.grid(True)
    ax.legend()

    filename = f"perf_{ts}.png"

    plt.savefig(filename)
    plt.close()

    return filename


# Lê o CSV para gerar análise complementar
def read_csv_results(csv_file):
    data = {}

    with open(csv_file, "r", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            solver = row["solver"]

            if solver not in data:
                data[solver] = {
                    "n": [],
                    "time": []
                }

            data[solver]["n"].append(int(row["n"]))
            data[solver]["time"].append(float(row["time_seconds"]))

    return data


def linear_fit(xs, ys):
    n = len(xs)

    if n < 2:
        return 0, ys[0] if ys else 0

    avg_x = sum(xs) / n
    avg_y = sum(ys) / n

    numerator = sum((xs[i] - avg_x) * (ys[i] - avg_y) for i in range(n))
    denominator = sum((x - avg_x) ** 2 for x in xs)

    if denominator == 0:
        return 0, avg_y

    a = numerator / denominator
    b = avg_y - a * avg_x

    return a, b


def analyze(csv_file, ts):
    data = read_csv_results(csv_file)

    plt.figure()

    for solver, values in data.items():
        ordered = sorted(zip(values["n"], values["time"]))
        xs = [item[0] for item in ordered]
        ys = [item[1] for item in ordered]

        plt.plot(
            xs,
            ys,
            label=solver,
            color=COLORS.get(solver)
        )

    # plt.yscale("log")
    plt.legend()

    analysis_file = f"analysis_runtime_{ts}.png"

    plt.savefig(analysis_file)
    plt.close()

    for solver, values in data.items():
        ordered = sorted(zip(values["n"], values["time"]))
        xs = [item[0] for item in ordered]
        ys = [math.log(max(item[1], 1e-12)) for item in ordered]

        a, b = linear_fit(xs, ys)

        print(f"{solver}: log(time) ≈ {a:.3f} * n + {b:.3f}")

    return analysis_file


# Main
if __name__ == "__main__":
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = benchmark()

    csv_file = f"results_{ts}.csv"
    export_csv(results, csv_file)

    perf_plot = plot_performance(results, ts)
    analysis_plot = analyze(csv_file, ts)

    print("\nArquivos salvos:")
    print(csv_file)
    print(perf_plot)
    print(analysis_plot)
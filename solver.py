import sys
import random


# ==========================================
# LEITURA DO INPUT
# ==========================================

def read_input():

    rows, cols = map(int, sys.stdin.readline().split())

    delivery = {}
    start = None

    for row in range(rows):

        line = sys.stdin.readline().strip().split()

        for col, char in enumerate(line):

            if char == 'R':
                start = (row, col)

            elif char != '0':
                delivery[char] = (row, col)

    return delivery, start


# ==========================================
# MATRIZ TRIANGULAR SUPERIOR
# ==========================================

def build_distance_matrix(delivery, start):

    points = ['R'] + sorted(delivery.keys())

    point_index = {
        point: i
        for i, point in enumerate(points)
    }

    coordinates = {'R': start}
    coordinates.update(delivery)

    n = len(points)

    dist_matrix = []

    for i in range(n):

        row = []

        for j in range(i + 1, n):

            x1, y1 = coordinates[points[i]]
            x2, y2 = coordinates[points[j]]

            # Distância Manhattan
            dist = abs(x1 - x2) + abs(y1 - y2)

            row.append(dist)

        dist_matrix.append(row)

    return points, point_index, dist_matrix


# ==========================================
# ACESSO À DISTÂNCIA
# ==========================================

def get_distance(a, b, point_index, dist_matrix):

    i = point_index[a]
    j = point_index[b]

    if i == j:
        return 0

    if i > j:
        i, j = j, i

    return dist_matrix[i][j - i - 1]


# ==========================================
# FITNESS
# ==========================================

def calculate_cost(route, point_index, dist_matrix):

    total = 0

    # R -> primeiro ponto
    total += get_distance(
        'R',
        route[0],
        point_index,
        dist_matrix
    )

    # Entre pontos
    for i in range(len(route) - 1):

        total += get_distance(
            route[i],
            route[i + 1],
            point_index,
            dist_matrix
        )

    # Último -> R
    total += get_distance(
        route[-1],
        'R',
        point_index,
        dist_matrix
    )

    return total


# ==========================================
# POPULAÇÃO INICIAL
# ==========================================

def generate_population(points, population_size):

    population = []

    for _ in range(population_size):

        chromosome = points[:]

        random.shuffle(chromosome)

        population.append(chromosome)

    return population


# ==========================================
# TORNEIO BINÁRIO (k=2)
# ==========================================

def tournament_selection(
    population,
    point_index,
    dist_matrix
):

    a = random.choice(population)
    b = random.choice(population)

    cost_a = calculate_cost(
        a,
        point_index,
        dist_matrix
    )

    cost_b = calculate_cost(
        b,
        point_index,
        dist_matrix
    )

    if cost_a < cost_b:
        return a[:]

    return b[:]


# ==========================================
# CROSSOVER OX
# ==========================================

def crossover(parent1, parent2):

    size = len(parent1)

    start, end = sorted(
        random.sample(range(size), 2)
    )

    child = [None] * size

    # Copia trecho do pai 1
    child[start:end + 1] = parent1[start:end + 1]

    # Completa usando pai 2
    p2_index = 0

    for i in range(size):

        if child[i] is None:

            while parent2[p2_index] in child:
                p2_index += 1

            child[i] = parent2[p2_index]

    return child


# ==========================================
# MUTAÇÃO SWAP
# ==========================================

def mutate(route, mutation_rate):

    if random.random() < mutation_rate:

        i, j = random.sample(
            range(len(route)),
            2
        )

        route[i], route[j] = route[j], route[i]


# ==========================================
# ALGORITMO GENÉTICO
# ==========================================

def solve(
    delivery,
    start,
    population_size=100,
    generations=500,
    mutation_rate=0.1
):

    if not delivery:
        return "", 0

    points, point_index, dist_matrix = build_distance_matrix(
        delivery,
        start
    )

    delivery_points = sorted(delivery.keys())

    # População inicial
    population = generate_population(
        delivery_points,
        population_size
    )

    best_solution = None
    best_cost = float('inf')

    # ======================================
    # EVOLUÇÃO
    # ======================================

    for generation in range(generations):

        # Seleção de pais
        parent1 = tournament_selection(
            population,
            point_index,
            dist_matrix
        )

        parent2 = tournament_selection(
            population,
            point_index,
            dist_matrix
        )

        # Crossover
        child = crossover(parent1, parent2)

        # Mutação
        mutate(child, mutation_rate)

        child_cost = calculate_cost(
            child,
            point_index,
            dist_matrix
        )

        # ==================================
        # SOBREVIVENTES (não geracional)
        # ==================================

        worst_index = 0

        worst_cost = calculate_cost(
            population[0],
            point_index,
            dist_matrix
        )

        for i in range(1, len(population)):

            current_cost = calculate_cost(
                population[i],
                point_index,
                dist_matrix
            )

            if current_cost > worst_cost:

                worst_cost = current_cost
                worst_index = i

        # Substitui apenas se filho for melhor
        if child_cost < worst_cost:
            population[worst_index] = child

        # Atualiza melhor solução global
        if child_cost < best_cost:

            best_cost = child_cost
            best_solution = child[:]

    return ' '.join(best_solution), best_cost


# ==========================================
# MAIN
# ==========================================

def main():

    delivery, start = read_input()

    best_route, best_cost = solve(
        delivery,
        start
    )

    print(best_route)
    print(f"Custo: {best_cost}")


if __name__ == "__main__":
    main()
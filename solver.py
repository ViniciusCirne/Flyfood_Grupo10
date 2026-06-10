import sys
import random

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

def permutations(elements):
    if len(elements) <= 1:
        yield elements
    else:
        for p in permutations(elements[1:]):
            for i in range(len(elements)):
                yield p[:i] + elements[0:1] + p[i:]


def solve_dfs_pruning(delivery, start):
    if not delivery:
        return ""

    points = set(delivery.keys())
    distance_cache = {}

    def get_distance(a, b):
        if (a, b) in distance_cache:
            return distance_cache[(a, b)]

        p1 = start if a == 'R' else delivery[a]
        p2 = start if b == 'R' else delivery[b]

        dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        distance_cache[(a, b)] = dist
        distance_cache[(b, a)] = dist
        return dist

    best_cost = float("inf")
    best_path = []

    def dfs(current, remaining, cost, path):
        nonlocal best_cost, best_path

        if cost >= best_cost:
            return

        if not remaining:
            total = cost + get_distance(current, 'R')

            if total < best_cost:
                best_cost = total
                best_path = path[:]

            return

        for nxt in remaining:
            dfs(
                nxt,
                remaining - {nxt},
                cost + get_distance(current, nxt),
                path + [nxt]
            )

    dfs('R', points, 0, [])
    return ' '.join(best_path)

def solve_greedy_pruning(delivery, start):
    if not delivery:
        return ""

    points = set(delivery.keys())
    distance_cache = {}

    def get_distance(a, b):
        if (a, b) in distance_cache:
            return distance_cache[(a, b)]

        p1 = start if a == 'R' else delivery[a]
        p2 = start if b == 'R' else delivery[b]

        dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        distance_cache[(a, b)] = dist
        distance_cache[(b, a)] = dist
        return dist

    def greedy():
        remaining = set(points)
        current = 'R'
        route = []
        cost = 0

        while remaining:
            nxt = min(remaining, key=lambda p: get_distance(current, p))

            cost += get_distance(current, nxt)
            route.append(nxt)

            remaining.remove(nxt)
            current = nxt

        cost += get_distance(current, 'R')
        return route, cost

    best_path, best_cost = greedy()

    def dfs(current, remaining, cost, path):
        nonlocal best_cost, best_path

        if cost >= best_cost:
            return

        if not remaining:
            total = cost + get_distance(current, 'R')

            if total < best_cost:
                best_cost = total
                best_path = path[:]

            return

        ordered = sorted(
            remaining,
            key=lambda p: get_distance(current, p)
        )

        for nxt in ordered:
            dfs(
                nxt,
                remaining - {nxt},
                cost + get_distance(current, nxt),
                path + [nxt]
            )

    dfs('R', points, 0, [])
    return ' '.join(best_path)

def solve_mst_pruning(delivery, start):
    if not delivery:
        return ""

    points = set(delivery.keys())
    distance_cache = {}

    def get_distance(a, b):
        # Calcula a distância Manhattan entre dois pontos
        # e reutiliza o valor caso ele já tenha sido calculado
        if (a, b) in distance_cache:
            return distance_cache[(a, b)]

        p1 = start if a == 'R' else delivery[a]
        p2 = start if b == 'R' else delivery[b]

        dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        distance_cache[(a, b)] = dist
        distance_cache[(b, a)] = dist
        return dist

    def greedy():
        # Gera uma solução inicial usando o ponto mais próximo
        # Essa solução serve como limite superior para as podas
        remaining = set(points)
        current = 'R'
        route = []
        cost = 0

        while remaining:
            nxt = min(remaining, key=lambda p: get_distance(current, p))

            cost += get_distance(current, nxt)
            route.append(nxt)

            remaining.remove(nxt)
            current = nxt

        cost += get_distance(current, 'R')
        return route, cost

    best_path, best_cost = greedy()
    mst_cache = {}

    def mst_cost(nodes):
        # Calcula o custo da árvore geradora mínima dos pontos restantes
        # O frozenset é usado porque a ordem dos nós não altera a MST
        key = frozenset(nodes)

        if key in mst_cache:
            return mst_cache[key]

        if len(nodes) <= 1:
            return 0

        nodes = list(nodes)
        visited = {nodes[0]}
        total = 0

        # Implementação simples do algoritmo de Prim
        while len(visited) < len(nodes):
            best_edge = float("inf")
            best_node = None

            for u in visited:
                for v in nodes:
                    if v in visited:
                        continue

                    d = get_distance(u, v)

                    if d < best_edge:
                        best_edge = d
                        best_node = v

            visited.add(best_node)
            total += best_edge

        mst_cache[key] = total
        return total

    def lower_bound(current, remaining, cost):
        # Estima o menor custo possível para completar a rota atual
        # Se essa estimativa já for pior que a melhor solução, o ramo é podado
        if not remaining:
            return cost + get_distance(current, 'R')

        mst = mst_cost(remaining)

        # Conecta o ponto atual aos pontos restantes
        connect_current = min(get_distance(current, p) for p in remaining)

        # Garante uma conexão de volta para o ponto inicial
        connect_home = min(get_distance('R', p) for p in remaining)

        return cost + mst + connect_current + connect_home

    def dfs(current, remaining, cost, path):
        nonlocal best_cost, best_path

        # Poda: não continua se nem a melhor estimativa supera a solução atual
        if lower_bound(current, remaining, cost) >= best_cost:
            return

        # Caso base: todos os pontos foram visitados
        if not remaining:
            total = cost + get_distance(current, 'R')

            if total < best_cost:
                best_cost = total
                best_path = path[:]

            return

        # Visita primeiro os pontos mais próximos para encontrar boas soluções cedo
        ordered = sorted(
            remaining,
            key=lambda p: get_distance(current, p)
        )

        for nxt in ordered:
            dfs(
                nxt,
                remaining - {nxt},
                cost + get_distance(current, nxt),
                path + [nxt]
            )

    dfs('R', points, 0, [])
    return ' '.join(best_path)

def solve_genetic(
    delivery,
    start,
    population_size=100,
    generations=500,
    mutation_rate=0.10
):
    if not delivery:
        return ""

    points = list(delivery.keys())
    distance_cache = {}

    def get_distance(a, b):
        # Calcula a distância Manhattan entre dois pontos e guarda em cache
        if (a, b) in distance_cache:
            return distance_cache[(a, b)]

        p1 = start if a == 'R' else delivery[a]
        p2 = start if b == 'R' else delivery[b]

        dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        distance_cache[(a, b)] = dist
        distance_cache[(b, a)] = dist

        return dist

    def route_cost(route):
        total = get_distance('R', route[0])

        for i in range(len(route) - 1):
            total += get_distance(route[i], route[i + 1])

        return total + get_distance(route[-1], 'R')

    def create_population():
        # Gera a população inicial com rotas aleatórias
        population = []

        for _ in range(population_size):
            chromosome = points[:]
            random.shuffle(chromosome)
            population.append(chromosome)

        return population

    def tournament_selection(population):
        # Torneio binário: escolhe dois indivíduos e retorna o de menor custo
        a = random.choice(population)
        b = random.choice(population)

        if route_cost(a) <= route_cost(b):
            return a[:]

        return b[:]

    def crossover(parent1, parent2):
        # Crossover OX: mantém um trecho do primeiro pai e completa com o segundo
        size = len(parent1)
        left, right = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[left:right + 1] = parent1[left:right + 1]

        remaining = [gene for gene in parent2 if gene not in child]
        idx = 0

        for i in range(size):
            if child[i] is None:
                child[i] = remaining[idx]
                idx += 1

        return child

    def mutate(route):
        # Mutação simples: troca dois pontos da rota
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(route)), 2)
            route[i], route[j] = route[j], route[i]

    population = create_population()

    best_solution = None
    best_cost = float('inf')

    for _ in range(generations):
        parent1 = tournament_selection(population)
        parent2 = tournament_selection(population)

        child = crossover(parent1, parent2)
        mutate(child)

        child_cost = route_cost(child)

        # Seleção de sobreviventes não geracional:
        # substitui apenas o pior indivíduo caso o filho seja melhor
        worst_idx = max(
            range(len(population)),
            key=lambda i: route_cost(population[i])
        )

        worst_cost = route_cost(population[worst_idx])

        if child_cost < worst_cost:
            population[worst_idx] = child

        if child_cost < best_cost:
            best_cost = child_cost
            best_solution = child[:]

    return ' '.join(best_solution)

def solve(delivery, start):
    if not delivery:
        return ""

    points = list(delivery.keys())
    distance_cache = {}

    def get_distance(a, b):
        if (a, b) in distance_cache:
            return distance_cache[(a, b)]

        if a == 'R':
            x1, y1 = start
        else:
            x1, y1 = delivery[a]

        if b == 'R':
            x2, y2 = start
        else:
            x2, y2 = delivery[b]

        dist = abs(x1 - x2) + abs(y1 - y2)

        distance_cache[(a, b)] = dist
        distance_cache[(b, a)] = dist
        return dist

    min_total = float('inf')
    best_path = None

    for perm in permutations(points):
        total = get_distance('R', perm[0])

        if total >= min_total:
            continue

        for i in range(len(perm) - 1):
            total += get_distance(perm[i], perm[i + 1])
            if total >= min_total:
                break

        total += get_distance(perm[-1], 'R')

        if total < min_total:
            min_total = total
            best_path = perm
        elif total == min_total and best_path is None:
            best_path = perm

    return ' '.join(best_path)


def main():
    delivery, start = read_input()

    # result = solve(delivery, start)
    result = solve_genetic(delivery, start)
    # result = solve_dfs_pruning(delivery, start)
    # result = solve_greedy_pruning(delivery, start)
    # result = solve_mst_pruning(delivery, start)

    print(result)


if __name__ == "__main__":
    main()

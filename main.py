import sys

def read_input():
    rows, cols = map(int, sys.stdin.readline().split()) # Input do grid

    # Dict para armazenar os pontos de entrega (chave: caractere, valor: coordenadas)
    delivery = {}
    start = None

    for row in range(rows):
        line = sys.stdin.readline().strip().split()
        for col, char in enumerate(line):
            if char == 'R':
                start = (row, col)
            elif char != '0':  # Ignora células com '0'
                delivery[char] = (row, col)
    return delivery, start


def permutations(elements):
    # Permutação feita recursivamente, usa o yield para ter um uso menor de memória
    if len(elements) <= 1:
        yield elements
    else:
        for p in permutations(elements[1:]):
            for i in range(len(elements)):
                yield p[:i] + elements[0:1] + p[i:]


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
            total += get_distance(perm[i], perm[i+1])
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
    # Lê o input
    delivery, start = read_input()
    result = solve(delivery, start)
    print(result)
    

if __name__ == "__main__":
    main()
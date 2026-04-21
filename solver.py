import sys

def read_input():
    rows, cols = map(int, sys.stdin.readline().split()) # Input do grid

    # Dicionário para armazenar os pontos de entrega (chave: caractere, valor: coordenadas)
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
    """Função principal que calcula o caminho ótimo para as entregas."""
    
    # Caso não haja pontos de entrega, imprime string vazia e retorna
    if not delivery:
        return ""
    
    # Define a lista com a chave todos os pontos no grid (ex: ['A', 'B', 'C'])
    points = list(delivery.keys())
    
    distance_cache = {}

    def get_distance(a, b):
        """Calcula a distância entre dois pontos (com cache)."""

        # Verifica se a distância já foi calculada anteriormente
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
        
        # Calcula a distância(soma das diferenças absolutas)
        dist = abs(x1 - x2) + abs(y1 - y2)

        # Armazena a distância no cache para ambas as direções (a->b e b->a)
        distance_cache[(a, b)] = dist
        distance_cache[(b, a)] = dist
        return dist


    min_total = float('inf')
    best_path = None

     # Gera todas as permutações possíveis dos pontos de entrega
    for perm in permutations(points):
        total = get_distance('R', perm[0])

        if total >= min_total:
            continue

        for i in range(len(perm) - 1):
            total += get_distance(perm[i], perm[i+1])
            if total >= min_total:
                break

        total += get_distance(perm[-1], 'R')
        
        # Atualiza o melhor caminho se encontrar uma distância menor
        if total < min_total:
            min_total = total
            best_path = perm
        # Em caso de empate, considera a primeira permutação encontrada
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
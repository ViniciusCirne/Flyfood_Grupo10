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


def main():
    # Lê o input
    delivery, start = read_input()
    
    # Caso não haja pontos de entrega, imprime string vazia e retorna
    if not delivery:
        print("")
        return
    
import random
import time
import tracemalloc


# ==========================================
# LEITURA DO ARQUIVO
# ==========================================

def ler_distancias(caminho_arquivo="edgesbrasil58.tsp"):

    objArq = open(caminho_arquivo)

    distancias = {}

    for i in range(1, 58):

        linha = objArq.readline()
        lista = linha.split()

        for j in range(i+1, 59):

            if len(lista) > 0:
                peso = int(lista.pop(0))
            else:
                print(f"Erro! linha {i} não possui elementos suficientes")
                exit()

            distancias[(i, j)] = peso
            distancias[(j, i)] = peso

    objArq.close()

    return distancias


# ==========================================
# CUSTO DO CAMINHO (ciclo completo)
# ==========================================

def custo_caminho(permutacao, distancias):

    soma = 0

    for i in range(len(permutacao)-1):
        soma += distancias[(permutacao[i], permutacao[i + 1])]

    # última cidade > primeira
    soma += distancias[(permutacao[-1], permutacao[0])]

    return soma


# ==========================================
# POPULAÇÃO INICIAL: vizinho mais próximo (NN) + aleatorios
# ==========================================

def vizinho_mais_proximo(inicio, qtde_cidades, distancias):

    visitados = {inicio}
    rota = [inicio]
    atual = inicio

    while len(rota) < qtde_cidades:
        melhor_viz = min(
            (c for c in range(1, qtde_cidades + 1) if c not in visitados),
            key=lambda c: distancias[(atual, c)]
        )
        rota.append(melhor_viz)
        visitados.add(melhor_viz)
        atual = melhor_viz

    return rota

def inicializa_populacao(tamanho, qtde_cidades, distancias, fracao_nn=0.2):

    populacao = []
    n_nn = max(1, int(tamanho * fracao_nn))

    # Soluções NN com diferentes cidades iniciais
    for i in range(n_nn):
        inicio = (i % qtde_cidades) + 1
        populacao.append(vizinho_mais_proximo(inicio, qtde_cidades, distancias))

    # Restante aleatório
    for _ in range(tamanho - n_nn):
        individuo = list(range(1, qtde_cidades + 1))
        random.shuffle(individuo)
        populacao.append(individuo)

    return populacao


# ==========================================
# CACHE DE APTIDÃO
# ==========================================

def chave_individuo(individuo):
    return tuple(individuo)

def calcula_aptidao_cache(populacao, distancias, cache):

    aptidoes = []

    for ind in populacao:
        k = chave_individuo(ind)
        if k not in cache:
            cache[k] = custo_caminho(ind, distancias)
        aptidoes.append(cache[k])

    return aptidoes


# ==========================================
# SELEÇÃO POR TORNEIO BINÁRIO (k=2)
# ==========================================

def selecao_torneio(populacao, aptidoes):

    i, j = random.sample(range(len(populacao)), 2)

    if aptidoes[i] <= aptidoes[j]:
        return populacao[i][:]

    return populacao[j][:]


# ==========================================
# CROSSOVER OX
# ==========================================

def crossover_ox(pai1, pai2):

    tamanho = len(pai1)
    inicio, fim = sorted(random.sample(range(tamanho), 2))

    filho = [None] * tamanho
    filho[inicio:fim + 1] = pai1[inicio:fim + 1]

    idx_pai2 = 0

    for i in range(tamanho):

        if filho[i] is None:

            while pai2[idx_pai2] in filho:
                idx_pai2 += 1

            filho[i] = pai2[idx_pai2]

    return filho


# ==========================================
# MUTAÇÃO POR INVERSÃO
# ==========================================

def mutacao_inversao(individuo, taxa_mutacao):

    # Inverte um segmento aleatório
    if random.random() < taxa_mutacao:
        i, j = sorted(random.sample(range(len(individuo)), 2))
        individuo[i:j + 1] = individuo[i:j + 1][::-1]


# ==========================================
# BUSCA LOCAL 2-OPT
# ==========================================

def dois_opt(rota, distancias, max_iter=50):

    # Melhora a rota trocando pares de arestas (2-opt)

    n = len(rota)
    melhorou = True
    iteracao = 0

    while melhorou and iteracao < max_iter:
        melhorou = False
        iteracao += 1

        for i in range(1, n - 1):
            for j in range(i + 1, n):

                # Custo das arestas atuais
                a, b = rota[i - 1], rota[i]
                c, d = rota[j], rota[(j + 1) % n]

                delta = (distancias[(a, c)] + distancias[(b, d)]
                         - distancias[(a, b)] - distancias[(c, d)])

                if delta < 0:
                    rota[i:j + 1] = rota[i:j + 1][::-1]
                    melhorou = True

    return rota


# ==========================================
# ALGORITMO GENÉTICO
# ==========================================

def algoritmo_genetico(
    distancias,
    qtde_cidades=58,
    tamanho_populacao=200,
    geracoes=1000,
    taxa_mutacao=0.1,
    elitismo=2
):

    cache = {}

    populacao = inicializa_populacao(tamanho_populacao, qtde_cidades, distancias)

    melhor_solucao = None
    melhor_custo = float('inf')

    aptidoes = calcula_aptidao_cache(populacao, distancias, cache)

    for i, custo in enumerate(aptidoes):
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = populacao[i][:]

    historico_custos = [melhor_custo]

    for _ in range(geracoes):

        # Elitismo: preserva os N melhores
        elite_idx = sorted(range(len(aptidoes)), key=lambda i: aptidoes[i])[:elitismo]
        elite = [populacao[i][:] for i in elite_idx]

        # Nova geração
        nova_populacao = []

        while len(nova_populacao) < tamanho_populacao - elitismo:

            pai1 = selecao_torneio(populacao, aptidoes)
            pai2 = selecao_torneio(populacao, aptidoes)

            filho = crossover_ox(pai1, pai2)

            mutacao_inversao(filho, taxa_mutacao)

            nova_populacao.append(filho)

        # Coloca a elite sem mudar nada
        nova_populacao.extend(elite)
        populacao = nova_populacao

        aptidoes = calcula_aptidao_cache(populacao, distancias, cache)

        # Atualiza melhor solução global
        for i, custo in enumerate(aptidoes):
            if custo < melhor_custo:
                melhor_custo = custo
                melhor_solucao = populacao[i][:]

        historico_custos.append(melhor_custo)

    # 2-opt na melhor solução final
    melhor_solucao = dois_opt(melhor_solucao, distancias)
    melhor_custo = custo_caminho(melhor_solucao, distancias)
    historico_custos[-1] = melhor_custo

    return melhor_solucao, melhor_custo, historico_custos


def executar_com_benchmark(distancias, **kwargs):

    tracemalloc.start()
    t0 = time.perf_counter()

    melhor_rota, melhor_custo, historico = algoritmo_genetico(
        distancias,
        **kwargs
    )

    t1 = time.perf_counter()
    current, pico_memoria = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tempo = t1 - t0
    memoria_kb = pico_memoria / 1024

    return melhor_rota, melhor_custo, historico, tempo, memoria_kb


# ==========================================
# EXIBE OS RESULTADOS
# ==========================================

def exibir_resultados(melhor_rota, melhor_custo, historico, tempo, memoria_kb):

    print("=" * 55)
    print("        RESULTADO - ALGORITMO GENÉTICO")
    print("=" * 55)

    print(f"\nMelhor rota encontrada:")
    print(" -> ".join(str(c) for c in melhor_rota))
    print(f"  (retorna à cidade {melhor_rota[0]})")

    print(f"\nCusto total       : {melhor_custo}")
    print(f"Tempo de execução : {tempo:.4f}s")
    print(f"Pico de memória   : {memoria_kb:.2f} KB")

    print(f"\nEvolução do melhor custo:")
    print(f"  Geração    0 : {historico[0]}")
    print(f"  Geração  250 : {historico[min(250, len(historico)-1)]}")
    print(f"  Geração  500 : {historico[min(500, len(historico)-1)]}")
    print(f"  Geração  750 : {historico[min(750, len(historico)-1)]}")
    print(f"  Geração 1000 : {historico[-1]}")
    print(f"  Melhoria total: {historico[0] - historico[-1]}")

    print("=" * 55)


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    random.seed(42)

    print("Lendo arquivo de distâncias...")
    distancias = ler_distancias("edgesbrasil58.tsp")
    print(f"Matriz carregada: 58 cidades, {len(distancias)} arestas.\n")

    print("Executando Algoritmo Genético...")

    melhor_rota, melhor_custo, historico, tempo, memoria_kb = executar_com_benchmark(
        distancias,
        qtde_cidades=58,
        tamanho_populacao=50,
        geracoes=1000,
        taxa_mutacao=0.15,
        elitismo=2
    )

    exibir_resultados(melhor_rota, melhor_custo, historico, tempo, memoria_kb)
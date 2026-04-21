# Projeto FlyFood - Otimização de Rotas para Entregas com Drones

## Descrição do Projeto

O **FlyFood** é um projeto desenvolvido para a disciplina de Projetos Interdisciplinares para Sistemas de Informação 2 (PISI2 - UFRPE). O objetivo é solucionar o problema de logística de uma empresa de entregas via drones, focando na economia de bateria através da otimização de trajetos.

O problema é modelado como uma variação do **Problema do Caixeiro Viajante (TSP)**. O drone deve partir de um ponto de origem (**R**), visitar todos os pontos de entrega (letras de **A-Z**) uma única vez e retornar à base pelo caminho mais curto possível, utilizando a **distância de Manhattan** para o cálculo de custos em uma malha urbana quadriculada.

---

## Funcionalidades e Diferenciais Técnicos

O projeto foi dividido em dois módulos principais para separar a lógica de negócio da análise de performance.

### 1. Otimizador (`solver.py`)
* **Leitura de Matriz Estática:** Processa a entrada de dados via terminal ou arquivo, mapeando coordenadas para cada ponto de interesse.
* **Permutação com Geradores (`yield`):** Em vez de armazenar todas as rotas possíveis na memória RAM (o que causaria travamentos em instâncias maiores), o algoritmo gera e avalia uma rota por vez.
* **Cache de Distâncias:** Utiliza um dicionário para memorizar cálculos de distância entre pontos já visitados, evitando processamento redundante.
* **Poda (Branch and Bound):** Implementa uma verificação em tempo real que descarta rotas parciais caso o custo atual já tenha superado o menor custo encontrado até o momento.

### 2. Módulo de Benchmark (`bench.py`)
* **Geração de Casos Aleatórios:** Cria matrizes de teste com diferentes números de pontos de entrega para validar a escalabilidade do algoritmo.
* **Análise de Recursos:** Monitora o tempo de execução (via `perf_counter`) e o consumo de memória RAM (via `tracemalloc`).
* **Visualização de Dados:** Gera gráficos automáticos (`matplotlib`) comparando o número de pontos de entrega com o tempo de processamento e o uso de memória.

---

## Estrutura do Código

### solver.py
1.  **`read_input`**: Converte a matriz de entrada em um dicionário de coordenadas.
2.  **`permutations`**: Função recursiva eficiente para gerar as combinações de entrega.
3.  **`get_distance`**: Calcula a distância ortogonal entre dois pontos e gerencia o cache.
4.  **`solve`**: O orquestrador que realiza a busca exaustiva (força bruta) com as otimizações de poda.

### bench.py
1.  **`generate_case`**: Gera cenários de teste aleatórios.
2.  **`run_once`**: Isola uma execução do solver para medir métricas de hardware.
3.  **`benchmark`**: Executa testes sequenciais de 2 a 11 pontos (limite computacional para força bruta).
4.  **`plot_results`**: Exporta um gráfico em formato `.png` com o comportamento da complexidade do algoritmo.

---

## Tecnologias Utilizadas

* **Python 3.x**
* **Matplotlib:** Para geração de gráficos de performance.
* **Tracemalloc:** Para perfilamento de memória.
* **Bibliotecas Nativas:** `sys`, `time`, `random`, `string`.

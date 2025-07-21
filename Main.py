from collections import defaultdict, deque
from itertools import combinations

# Conversão AFN -> AFD (com conjuntos como strings)
def transformar_afn_para_afd(estados, estado_inicial, transicoes, estados_finais, alfabeto):
    afd_transicoes = {}
    novos_estados = []
    estados_afd_finais = set()

    estado_inicial_str = ",".join(sorted([estado_inicial]))
    fila = deque([estado_inicial_str])
    visitados = set()

    while fila:
        atual_str = fila.popleft()
        if atual_str in visitados:
            continue
        visitados.add(atual_str)
        novos_estados.append(atual_str)

        atual = atual_str.split(",")
        for simbolo in alfabeto:
            destino = set()
            for estado in atual:
                destino.update(transicoes.get((estado, simbolo), []))
            if destino:
                destino_str = ",".join(sorted(destino))
                afd_transicoes[(atual_str, simbolo)] = destino_str
                if destino_str not in visitados:
                    fila.append(destino_str)

    for estado_str in novos_estados:
        subconjunto = estado_str.split(",")
        if any(e in estados_finais for e in subconjunto):
            estados_afd_finais.add(estado_str)

    return novos_estados, estado_inicial_str, afd_transicoes, estados_afd_finais

# Algoritmo de minimização de AFD (tabela de distinção)
def minimizar_afd(estados, transicoes, estado_inicial, estados_finais, alfabeto):
    estados = sorted(estados)
    distincoes = set()
    pares = list(combinations(estados, 2))
    tabela = {}

    for a, b in pares:
        marcado = ((a in estados_finais) != (b in estados_finais))
        tabela[(a, b)] = marcado
        if marcado:
            distincoes.add((a, b))

    alterado = True
    while alterado:
        alterado = False
        for a, b in pares:
            if tabela[(a, b)]:
                continue
            for simbolo in alfabeto:
                a_dest = transicoes.get((a, simbolo), "-")
                b_dest = transicoes.get((b, simbolo), "-")
                if a_dest == b_dest:
                    continue
                par = tuple(sorted((a_dest, b_dest)))
                if par in distincoes:
                    tabela[(a, b)] = True
                    distincoes.add((a, b))
                    alterado = True
                    break

    grupos = []
    usados = set()
    for estado in estados:
        if estado in usados:
            continue
        grupo = {estado}
        for outro in estados:
            if outro != estado and not tabela.get(tuple(sorted((estado, outro))), False):
                grupo.add(outro)
                usados.add(outro)
        usados.add(estado)
        grupos.append(grupo)

    estado_para_grupo = {}
    for grupo in grupos:
        nome = ",".join(sorted(grupo))
        for estado in grupo:
            estado_para_grupo[estado] = nome

    novo_estado_inicial = estado_para_grupo[estado_inicial]
    novo_estados_finais = {estado_para_grupo[e] for e in estados_finais}
    novo_estados = set(estado_para_grupo.values())
    novo_transicoes = {}

    for (origem, simbolo), destino in transicoes.items():
        novo_origem = estado_para_grupo[origem]
        novo_destino = estado_para_grupo.get(destino, destino)
        novo_transicoes[(novo_origem, simbolo)] = novo_destino

    return sorted(novo_estados), novo_estado_inicial, novo_transicoes, sorted(novo_estados_finais)

def exibir_tabela_transicao(estados, alfabeto, transicoes):
    max_estado_len = max(len(e) for e in estados)
    max_destino_len = 20

    header = f"{'Estado':<{max_estado_len}} | " + " | ".join(f"{s:^{max_destino_len}}" for s in sorted(alfabeto))
    print("\nTabela de Transição:")
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for estado in estados:
        row = f"{estado:<{max_estado_len}} | "
        for simbolo in sorted(alfabeto):
            destino = transicoes.get((estado, simbolo), "-")
            row += f"{destino:^{max_destino_len}} | "
        print(row)
    print("-" * len(header))

def main():
    estados = [e.strip() for e in input("Informe os estados do autômato: ").split(',')]
    estado_inicial = input("Informe o estado inicial: ").strip()

    print("Informe a função programa:")
    transicoes = defaultdict(list)
    alfabeto = set()

    while True:
        entrada = input().strip()
        if not entrada:
            break
        if len(entrada) >= 3:
            origem = entrada[0]
            simbolo = entrada[1]
            destino = entrada[2]
            transicoes[(origem, simbolo)].append(destino)
            alfabeto.add(simbolo)
        elif len(entrada) == 2:
            origem = entrada[0]
            destino = entrada[1]
            transicoes[(origem, 'ε')].append(destino)

    estados_finais = [e.strip() for e in input("Informe os estados finais: ").split(',')]

    afd_estados, afd_inicial, afd_transicoes, afd_finais = transformar_afn_para_afd(
        estados, estado_inicial, transicoes, estados_finais, alfabeto
    )

    print("\nAFD gerado (antes da minimização):")
    print("Estados:", ", ".join(afd_estados))
    print("Estado inicial:", afd_inicial)
    print("Estados finais:", ", ".join(afd_finais))
    exibir_tabela_transicao(afd_estados, alfabeto, afd_transicoes)

    min_estados, min_inicial, min_transicoes, min_finais = minimizar_afd(
        afd_estados, afd_transicoes, afd_inicial, afd_finais, alfabeto
    )

    print("\nAFD Mínimo resultante:")
    print("Estados:", ", ".join(min_estados))
    print("Estado inicial:", min_inicial)
    print("Estados finais:", ", ".join(min_finais))
    exibir_tabela_transicao(min_estados, alfabeto, min_transicoes)

    print("\nTransições do AFD Mínimo:")
    for (estado, simbolo), destino in sorted(min_transicoes.items()):
        print(f"{estado}{simbolo}{destino}")

if __name__ == "__main__":
    main()
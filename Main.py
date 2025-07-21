from collections import defaultdict, deque
from itertools import combinations

# Conversão AFN -> AFD (com inserção de estado‑morto '∅')
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
            for e in atual:
                destino.update(transicoes.get((e, simbolo), []))
            destino_str = ",".join(sorted(destino)) if destino else "∅"
            afd_transicoes[(atual_str, simbolo)] = destino_str
            if destino_str not in visitados and destino_str not in novos_estados:
                fila.append(destino_str)

    for estado_str in novos_estados:
        if any(e in estados_finais for e in estado_str.split(",")):
            estados_afd_finais.add(estado_str)

    # garante inclusão do estado‑morto e suas transições de laço
    if "∅" not in novos_estados:
        novos_estados.append("∅")
    for simbolo in alfabeto:
        afd_transicoes[("∅", simbolo)] = "∅"

    return novos_estados, estado_inicial_str, afd_transicoes, estados_afd_finais


# Minimização de AFD (tabela de distinção)
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
            if tabela[(a, b)]: continue
            for simbolo in alfabeto:
                a_dest = transicoes.get((a, simbolo), "∅")
                b_dest = transicoes.get((b, simbolo), "∅")
                if a_dest != b_dest and tuple(sorted((a_dest, b_dest))) in distincoes:
                    tabela[(a, b)] = True
                    distincoes.add((a, b))
                    alterado = True
                    break

    grupos = []
    usados = set()
    for estado in estados:
        if estado in usados: continue
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
        for e in grupo:
            estado_para_grupo[e] = nome

    novo_estado_inicial = estado_para_grupo[estado_inicial]
    novo_estados_finais = {estado_para_grupo[e] for e in estados_finais}
    novo_estados = list(sorted(set(estado_para_grupo.values())))
    novo_transicoes = {}
    for (origem, simbolo), destino in transicoes.items():
        novo_origem = estado_para_grupo[origem]
        novo_destino = estado_para_grupo.get(destino, destino)
        novo_transicoes[(novo_origem, simbolo)] = novo_destino

    return novo_estados, novo_estado_inicial, novo_transicoes, sorted(novo_estados_finais)

# Exibição com colchetes só para estados normais e ∅ sem colchetes
def exibir_tabela_transicao(estados, alfabeto, transicoes):
    # ordena, deixando '∅' por último
    if "∅" in estados:
        estados_ord = sorted(e for e in estados if e != "∅")
        estados_ord.append("∅")
    else:
        estados_ord = sorted(estados)

    # comprimento máximo (não conta colchetes do ∅)
    max_len = max(len(e) + (2 if e != "∅" else 0) for e in estados_ord)
    largura = 12

    header = f"{'Estado':<{max_len}} | " + " | ".join(f"{s:^{largura}}" for s in sorted(alfabeto))
    print("\nTabela de Transição:")
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for estado in estados_ord:
        # só coloca colchetes se não for o morto
        est_fmt = f"({estado})" if estado != "∅" else estado
        row = f"{est_fmt:<{max_len}} | "

        for simbolo in sorted(alfabeto):
            destino = transicoes.get((estado, simbolo), "-")
            if destino == "∅":
                dest_fmt = destino        # morto sem colchetes
            elif destino == "-":
                dest_fmt = "-"            # sem transição
            else:
                dest_fmt = f"({destino})" # colchetes nos demais
            row += f"{dest_fmt:^{largura}} | "
        print(row)

    print("-" * len(header))


def exibir_transicoes(transicoes):
    print("\nTransições:")
    for (e, s), d in sorted(transicoes.items()):
        e_fmt = f"({e})" if e != "∅" else e
        d_fmt = f"({d})" if d not in ("∅", "-") else d
        print(f"{e_fmt} --{s}--> {d_fmt}")


def main():
    estados = [e.strip() for e in input("Informe os estados do autômato: ").split(',')]
    estado_inicial = input("Informe o estado inicial: ").strip()

    print("Informe a função programa (linha em branco para terminar):")
    trans_afn = defaultdict(list)
    alfabeto = set()
    while True:
        linha = input().strip()
        if not linha: break
        origem, simbolo, destino = linha[0], linha[1], linha[2]
        trans_afn[(origem, simbolo)].append(destino)
        alfabeto.add(simbolo)

    estados_finais = [e.strip() for e in input("Informe os estados finais: ").split(',')]

    # AFN → AFD
    afd_est, afd_ini, afd_trans, afd_fin = transformar_afn_para_afd(
        estados, estado_inicial, trans_afn, estados_finais, alfabeto
    )
    print("\n========== AFD ==========")
    print("Estados:", ", ".join(afd_est))
    print("Inicial:", afd_ini)
    print("Finais:", ", ".join(sorted(afd_fin)))
    exibir_tabela_transicao(afd_est, alfabeto, afd_trans)
    exibir_transicoes(afd_trans)

    # Minimização
    min_est, min_ini, min_trans, min_fin = minimizar_afd(
        afd_est, afd_trans, afd_ini, afd_fin, alfabeto
    )
    print("\n========== AFD Minimizado ==========")
    print("Estados:", ", ".join(min_est))
    print("Inicial:", min_ini)
    print("Finais:", ", ".join(min_fin))
    exibir_tabela_transicao(min_est, alfabeto, min_trans)
    exibir_transicoes(min_trans)


if __name__ == "__main__":
    main()

"""Experimento A3: demonstração do sigilo perfeito.

Parte 1. Com p = 17, k = 3 e as partes (1, 8) e (2, 6) da Seção 2.5, percorre os
17^3 = 4913 polinômios de grau no máximo 2 e conta, para cada candidato D', quantos
passam pelas duas partes. Esperado: exatamente um por candidato.

Parte 2. Executa a divisão muitas vezes para D = 0 e D = 13 e registra o par (D_1, D_2).
Esperado: os 289 pares aparecem com frequência aproximadamente uniforme e igual para
os dois segredos, ou seja, a distribuição de k - 1 partes não depende de D.
"""

import itertools
import sys

import shamir
from comum import Relatorio, caminho, pyplot, qui_quadrado_critico, salvar_csv

P, K = 17, 3
CONHECIDAS = [(1, 8), (2, 6)]
rel = Relatorio("a3_sigilo")

# Parte 1: busca exaustiva ---------------------------------------------------------------
rel("=== A3.1 Busca exaustiva sobre todos os polinômios de grau <= 2 em Z_17 ===")
contagem = {d: [] for d in range(P)}
avaliados = 0
for coeficientes in itertools.product(range(P), repeat=K):
    avaliados += 1
    if all(shamir.avaliar(coeficientes, x, P) == y for x, y in CONHECIDAS):
        contagem[coeficientes[0]].append(coeficientes[1:])
rel(f"polinômios avaliados: {avaliados}")
rel("candidato D' | polinômios compatíveis | (a_1, a_2)")
for d in range(P):
    rel(f"{d:11d} | {len(contagem[d]):21d} | {contagem[d]}")
rel(f"todos os candidatos com exatamente um polinômio: "
    f"{all(len(v) == 1 for v in contagem.values())}")
salvar_csv("a3_busca_exaustiva.csv", ["candidato", "polinomios", "a1", "a2"],
           [(d, len(v), v[0][0], v[0][1]) for d, v in contagem.items()])

# Parte 2: distribuição das partes ----------------------------------------------------------
repeticoes = 30000 if "--rapido" in sys.argv else 300000
rel(f"\n=== A3.2 Distribuição de (D_1, D_2) em {repeticoes} divisões, k = 3, p = 17 ===")
histogramas = {}
for segredo in (0, 13):
    h = [[0] * P for _ in range(P)]
    for _ in range(repeticoes):
        partes = shamir.dividir(segredo, K, 3, P)
        h[partes[0][1]][partes[1][1]] += 1
    histogramas[segredo] = h

esperado = repeticoes / P**2
critico = qui_quadrado_critico(P**2 - 1)
rel(f"frequência esperada por par: {esperado:.1f}")
for segredo, h in histogramas.items():
    valores = [c for linha in h for c in linha]
    qui2 = sum((c - esperado) ** 2 / esperado for c in valores)
    rel(f"D = {segredo:2d}: pares observados {sum(c > 0 for c in valores)} de 289, "
        f"mínimo {min(valores)}, máximo {max(valores)}, qui-quadrado {qui2:.1f} "
        f"(valor crítico a 5% com 288 g.l.: {critico:.1f}) -> "
        f"{'compatível' if qui2 < critico else 'NÃO compatível'} com distribuição uniforme")

# Teste de homogeneidade: as duas distribuições são iguais?
a = [c for linha in histogramas[0] for c in linha]
b = [c for linha in histogramas[13] for c in linha]
qui2 = sum((x - y) ** 2 / (x + y) for x, y in zip(a, b) if x + y > 0)
rel(f"homogeneidade entre D = 0 e D = 13: qui-quadrado {qui2:.1f} (crítico {critico:.1f}) -> "
    f"{'distribuições indistinguíveis' if qui2 < critico else 'distribuições diferentes'}")
salvar_csv("a3_distribuicao_partes.csv", ["D1", "D2", "contagem_D0", "contagem_D13"],
           [(i, j, histogramas[0][i][j], histogramas[13][i][j])
            for i in range(P) for j in range(P)])

plt = pyplot()
if plt:
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(range(P), [len(contagem[d]) for d in range(P)], color="#3b6ea5")
    ax.set_xticks(range(P))
    ax.set_ylim(0, 2)
    ax.set_xlabel("candidato $D'$")
    ax.set_ylabel("polinômios compatíveis")
    ax.set_title("Partes conhecidas (1, 8) e (2, 6), $p = 17$")
    fig.tight_layout()
    fig.savefig(caminho("a3_busca_exaustiva.png"), dpi=200)

    fig, eixos = plt.subplots(1, 2, figsize=(9, 4.6), constrained_layout=True)
    maximo = max(max(a), max(b))
    for ax, segredo in zip(eixos, (0, 13)):
        im = ax.imshow(histogramas[segredo], origin="lower", cmap="viridis", vmin=0, vmax=maximo)
        ax.set_title(f"$D = {segredo}$")
        ax.set_xlabel("$D_2$")
        ax.set_ylabel("$D_1$")
        ax.set_xticks(range(0, P, 4))
        ax.set_yticks(range(0, P, 4))
    fig.colorbar(im, ax=eixos, label="ocorrências", shrink=0.85)
    fig.suptitle(f"Frequência dos pares $(D_1, D_2)$ em {repeticoes} divisões")
    fig.savefig(caminho("a3_distribuicao_partes.png"), dpi=200)
rel.fechar()

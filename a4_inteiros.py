"""Experimento A4: aritmética inteira contra corpo finito.

A divisão é repetida sem redução módulo p, com coeficientes inteiros sorteados em [0, M).
Sem o módulo, D_i = q(i) é congruente a D módulo i, e cada parte é um limitante superior
de D. Para segredos de 16 bits e k = 3, o experimento conta quantos candidatos D'
continuam compatíveis com k - 1 = 2 partes conhecidas. Para cada candidato, o sistema
linear que determina a_1, ..., a_{k-1} é resolvido em números racionais, e o candidato
é compatível se a solução for inteira e estiver em [0, M). A mesma contagem em Z_p,
com p = 65537, mantém todos os candidatos.
"""

import math
import secrets
import statistics
import sys
from fractions import Fraction
from functools import reduce

from comum import Relatorio, caminho, pyplot, salvar_csv

BITS = 16
K = 3
P_CORPO = 65537  # primo maior que 2^16
CANDIDATOS = range(2**BITS)
rel = Relatorio("a4_inteiros")


def q_inteiro(coeficientes, x):
    return sum(a * x**j for j, a in enumerate(coeficientes))


def resolver_racional(indices, valores):
    """Resolve V a = b em racionais, com V[i][j] = x_i^(j+1), por eliminação de Gauss."""
    t = len(indices)
    m = [[Fraction(x ** (j + 1)) for j in range(t)] + [Fraction(b)]
         for x, b in zip(indices, valores)]
    for c in range(t):
        piv = next(r for r in range(c, t) if m[r][c] != 0)
        m[c], m[piv] = m[piv], m[c]
        for r in range(t):
            if r != c and m[r][c] != 0:
                f = m[r][c] / m[c][c]
                m[r] = [a - f * b for a, b in zip(m[r], m[c])]
    return [m[r][t] / m[r][r] for r in range(t)]


def candidatos_compativeis_inteiros(partes, M):
    """Conta os D' em [0, 2^16) para os quais existe a_1..a_{k-1} inteiro em [0, M).

    Como o sistema é linear em D', a solução tem a forma a(D') = u - D' w, com
    u = V^-1 y e w = V^-1 (1, ..., 1). Os dois vetores são calculados uma vez em
    racionais e depois escritos com denominador comum L para testar cada candidato.
    """
    indices = [x for x, _ in partes]
    u = resolver_racional(indices, [y for _, y in partes])
    w = resolver_racional(indices, [1] * len(partes))
    L = reduce(math.lcm, [f.denominator for f in u + w])
    U = [int(f * L) for f in u]
    W = [int(f * L) for f in w]
    total = 0
    for d in CANDIDATOS:
        ok = True
        for uj, wj in zip(U, W):
            num = uj - d * wj  # a_j * L
            if num % L or not (0 <= num < M * L):
                ok = False
                break
        total += ok
    return total


def candidatos_compativeis_corpo(partes, p):
    """Mesma contagem em Z_p: para cada D', resolve o sistema módulo p e confere a solução."""
    indices = [x for x, _ in partes]
    u = resolver_racional(indices, [y for _, y in partes])
    w = resolver_racional(indices, [1] * len(partes))
    um = [f.numerator * pow(f.denominator, -1, p) % p for f in u]
    wm = [f.numerator * pow(f.denominator, -1, p) % p for f in w]
    total = 0
    for d in CANDIDATOS:
        a = [d] + [(uj - d * wj) % p for uj, wj in zip(um, wm)]
        total += all(sum(c * x**j for j, c in enumerate(a)) % p == y for x, y in partes)
    return total


# 1. Vazamentos diretos ---------------------------------------------------------------------
rel("=== A4.1 Vazamentos diretos sem redução modular (k = 3, n = 5, M = 2^16) ===")
D = secrets.randbelow(2**BITS)
coef = [D] + [secrets.randbelow(2**16) for _ in range(K - 1)]
partes = [(i, q_inteiro(coef, i)) for i in range(1, 6)]
rel(f"segredo D = {D}, partes = {partes}")
for i, y in partes:
    rel(f"  participante {i}: D_{i} mod {i} = {y % i}  (D mod {i} = {D % i})")
y2, y3 = partes[1][1], partes[2][1]
d_mod_6 = next(r for r in range(6) if r % 2 == y2 % 2 and r % 3 == y3 % 3)
rel(f"participantes 2 e 3 juntos (k - 1 partes): D mod 6 = {d_mod_6}  (real: {D % 6})")
rel(f"limitante superior dado pela parte 1: D <= {partes[0][1]}  (real: {D})")

# 2. Contagem de candidatos -----------------------------------------------------------------
rapido = "--rapido" in sys.argv
ensaios = 5 if rapido else 30
conjuntos = [(1, 2), (2, 3), (4, 5)]
limites = [2**8, 2**16, 2**32]
rel(f"\n=== A4.2 Candidatos D' compatíveis com 2 partes, segredos de {BITS} bits, "
    f"{ensaios} ensaios por configuração ===")
rel(f"total de candidatos: {2**BITS}")
linhas = []
medias = {}
for indices in conjuntos:
    for M in limites:
        contagens = []
        for _ in range(ensaios):
            D = secrets.randbelow(2**BITS)
            coef = [D] + [secrets.randbelow(M) for _ in range(K - 1)]
            conhecidas = [(i, q_inteiro(coef, i)) for i in indices]
            c = candidatos_compativeis_inteiros(conhecidas, M)
            assert c >= 1  # o segredo verdadeiro sempre é compatível
            contagens.append(c)
            linhas.append(("inteiros", f"{indices}", M, D, c))
        media = statistics.mean(contagens)
        medias[(indices, f"M = 2^{int(math.log2(M))}")] = media
        rel(f"inteiros, partes {indices}, M = 2^{int(math.log2(M)):2d}: média {media:9.1f} "
            f"candidatos (mín {min(contagens)}, máx {max(contagens)}), "
            f"restam {math.log2(media):5.2f} de {BITS} bits de incerteza")
    contagens = []
    for _ in range(ensaios):
        D = secrets.randbelow(2**BITS)
        coef = [D] + [secrets.randbelow(P_CORPO) for _ in range(K - 1)]
        conhecidas = [(i, sum(a * i**j for j, a in enumerate(coef)) % P_CORPO) for i in indices]
        c = candidatos_compativeis_corpo(conhecidas, P_CORPO)
        contagens.append(c)
        linhas.append((f"Z_{P_CORPO}", f"{indices}", P_CORPO, D, c))
    medias[(indices, f"$Z_{{{P_CORPO}}}$")] = statistics.mean(contagens)
    rel(f"Z_{P_CORPO},  partes {indices}:            {min(contagens)} a {max(contagens)} "
        f"candidatos em todos os ensaios (nenhuma informação)")
salvar_csv("a4_candidatos.csv", ["aritmetica", "partes", "limite_coeficientes", "segredo",
                                 "candidatos_compativeis"], linhas)

plt = pyplot()
if plt:
    rotulos = ["M = 2^8", "M = 2^16", "M = 2^32", f"$Z_{{{P_CORPO}}}$"]
    fig, ax = plt.subplots(figsize=(8, 4))
    largura = 0.2
    for desloc, rotulo in enumerate(rotulos):
        alturas = [medias[(c, rotulo)] for c in conjuntos]
        rotulo_legenda = (rotulo.replace("M = 2^", "inteiros, $M = 2^{") + "}$"
                          if rotulo.startswith("M") else rotulo)
        ax.bar([i + (desloc - 1.5) * largura for i in range(len(conjuntos))], alturas,
               largura, label=rotulo_legenda)
    ax.axhline(2**BITS, color="gray", linestyle="--", linewidth=1)
    ax.set_yscale("log", base=2)
    ax.set_ylim(1, 2**18)
    ax.set_xticks(range(len(conjuntos)))
    ax.set_xticklabels([f"partes {c[0]} e {c[1]}" for c in conjuntos])
    ax.set_ylabel("candidatos compatíveis (média)")
    ax.set_title(f"Candidatos restantes para um segredo de {BITS} bits com 2 partes ($k = 3$)")
    ax.legend(fontsize=8, loc="upper center", ncol=4)
    fig.tight_layout()
    fig.savefig(caminho("a4_candidatos.png"), dpi=200)
rel.fechar()

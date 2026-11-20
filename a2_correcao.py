"""Experimento A2: teste de correção.

1. Reproduz o exemplo da Seção 2.5 (coeficientes fixos a_1 = 2 e a_2 = 10).
2. Para n <= 10, testa todos os C(n, k) subconjuntos de k partes com p = 2^127 - 1.
3. Testa segredos e parâmetros sorteados com p = 2^127 - 1.
4. Mede com que frequência k - 1 partes "acertam" o segredo por coincidência
   (esperado 1/p, ou seja, 1/17 com p = 17 e nenhuma vez com p = 2^127 - 1).
"""

import itertools
import random
import secrets
import sys

import shamir
from comum import Relatorio, salvar_csv
from shamir import P127

rel = Relatorio("a2_correcao")
gerador = random.Random(2026)  # escolhe apenas parâmetros; os coeficientes vêm de secrets
rapido = "--rapido" in sys.argv

# 1. Exemplo do relatório ---------------------------------------------------------
rel("=== A2.1 Exemplo da Seção 2.5: q(x) = 13 + 2x + 10x^2 mod 17 ===")
partes = shamir.partes_do_polinomio([13, 2, 10], 5, 17)
rel(f"partes geradas: {partes}")
esperado = [(1, 8), (2, 6), (3, 7), (4, 11), (5, 1)]
rel(f"iguais à Tabela 1: {partes == esperado}")
trios_ok = 0
for trio in itertools.combinations(partes, 3):
    d = shamir.reconstruir(list(trio), 17)
    rel(f"  participantes {[x for x, _ in trio]} -> D = {d}")
    trios_ok += d == 13
rel(f"trios que reconstroem D = 13: {trios_ok} de 10")

# 2. Todos os subconjuntos para n <= 10 ----------------------------------------------
rel("\n=== A2.2 Todos os subconjuntos de k partes, n <= 10, p = 2^127 - 1 ===")
repeticoes = 3 if rapido else 20
total = falhas = 0
linhas = []
for n in range(1, 11):
    for k in range(1, n + 1):
        testados = erros = 0
        for _ in range(repeticoes):
            segredo = secrets.randbelow(P127)
            partes = shamir.dividir(segredo, k, n)
            for sub in itertools.combinations(partes, k):
                testados += 1
                erros += shamir.reconstruir(list(sub)) != segredo
        total += testados
        falhas += erros
        linhas.append((n, k, testados, erros))
salvar_csv("a2_subconjuntos.csv", ["n", "k", "reconstrucoes", "falhas"], linhas)
rel(f"{repeticoes} segredos por par (n, k), {total} reconstruções, {falhas} falhas")

# 3. Parâmetros sorteados -----------------------------------------------------------
rel("\n=== A2.3 Parâmetros sorteados, p = 2^127 - 1 ===")
testes = 200 if rapido else 2000
falhas = 0
for _ in range(testes):
    n = gerador.randint(1, 60)
    k = gerador.randint(1, n)
    segredo = secrets.randbelow(P127)
    partes = shamir.dividir(segredo, k, n)
    escolhidas = gerador.sample(partes, gerador.randint(k, n))
    falhas += shamir.reconstruir(escolhidas) != segredo
rel(f"{testes} testes com 1 <= k <= n <= 60 e entre k e n partes sorteadas: {falhas} falhas")

# 4. Apenas k - 1 partes --------------------------------------------------------------
rel("\n=== A2.4 Interpolação com apenas k - 1 partes ===")
rel("Esperado: coincidência com D só quando a_{k-1} = 0, com probabilidade 1/p.")
repeticoes = 20000 if rapido else 200000
linhas = []
for p in (17, P127):
    for k in (2, 3, 4, 5):
        acertos = divergentes = 0
        for _ in range(repeticoes):
            segredo = secrets.randbelow(p)
            coeficientes = shamir.sortear_coeficientes(segredo, k, p)  # mesmo sorteio de dividir()
            partes = shamir.partes_do_polinomio(coeficientes, k, p)
            acertou = shamir.reconstruir(gerador.sample(partes, k - 1), p) == segredo
            acertos += acertou
            divergentes += acertou != (coeficientes[-1] == 0)
        freq = acertos / repeticoes
        rotulo = "17" if p == 17 else "2^127-1"
        rel(f"p = {rotulo:8} k = {k}: {acertos:6d} coincidências em {repeticoes} "
            f"({100 * freq:.2f}%, esperado {100 / p:.2g}%); "
            f"casos em que coincidência != (a_(k-1) = 0): {divergentes}")
        linhas.append((rotulo, k, repeticoes, acertos, freq, 1 / p, divergentes))
salvar_csv("a2_k_menos_1.csv", ["p", "k", "repeticoes", "coincidencias", "frequencia", "esperado",
                                "divergencias_com_a_k_menos_1_nulo"], linhas)
rel.fechar()

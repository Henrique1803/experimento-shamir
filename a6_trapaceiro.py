"""Experimento A6: ataque com parte falsa (Tompa e Woll).

O participante i apresenta y_i + delta (delta != 0) no lugar da sua parte. O combinador
anuncia D' = D + delta * lambda_i (mod p). Como lambda_i depende apenas dos índices
presentes, o trapaceiro calcula D = D' - delta * lambda_i (mod p), enquanto os
participantes honestos ficam com o valor errado D'.
"""

import random
import secrets
import sys

import shamir
from comum import Relatorio, salvar_csv
from shamir import P127

rel = Relatorio("a6_trapaceiro")
gerador = random.Random(2026)  # escolhe parâmetros e trapaceiro; coeficientes vêm de secrets


def ataque(partes_presentes, posicao_trapaceiro, delta, p):
    """Executa uma reconstrução com uma parte adulterada.

    Devolve o valor anunciado pelo combinador e o valor que o trapaceiro calcula.
    """
    adulteradas = list(partes_presentes)
    x, y = adulteradas[posicao_trapaceiro]
    adulteradas[posicao_trapaceiro] = (x, (y + delta) % p)
    anunciado = shamir.reconstruir(adulteradas, p)
    indices = [xi for xi, _ in partes_presentes]  # públicos, conhecidos pelo trapaceiro
    lam = shamir.coeficiente_lagrange(indices, posicao_trapaceiro, p)
    return anunciado, (anunciado - delta * lam) % p


# 1. Exemplo da Seção 2.5 ------------------------------------------------------------------
rel("=== A6.1 Exemplo do relatório: participantes 1, 2 e 3, p = 17, participante 1 trapaceia ===")
partes = shamir.partes_do_polinomio([13, 2, 10], 5, 17)[:3]
anunciado, calculado = ataque(partes, 0, 1, 17)
rel(f"partes verdadeiras: {partes}; o participante 1 apresenta 9 no lugar de 8")
rel(f"lambda_1 = {shamir.coeficiente_lagrange([1, 2, 3], 0, 17)}")
rel(f"valor anunciado aos honestos: D' = {anunciado}")
rel(f"valor calculado pelo trapaceiro: D' - delta * lambda_1 = {calculado}  (segredo real: 13)")

# 2. Ensaios com p = 2^127 - 1 ---------------------------------------------------------------
ensaios = 1000 if "--rapido" in sys.argv else 10000
rel(f"\n=== A6.2 {ensaios} ataques com p = 2^127 - 1 e parâmetros sorteados ===")
honestos_enganados = trapaceiro_acerta = 0
linhas = []
for _ in range(ensaios):
    n = gerador.randint(2, 30)
    k = gerador.randint(2, n)
    segredo = secrets.randbelow(P127)
    presentes = gerador.sample(shamir.dividir(segredo, k, n), k)
    posicao = gerador.randrange(k)
    delta = 1 + secrets.randbelow(P127 - 1)
    anunciado, calculado = ataque(presentes, posicao, delta, P127)
    honestos_enganados += anunciado != segredo
    trapaceiro_acerta += calculado == segredo
    linhas.append((n, k, presentes[posicao][0], anunciado != segredo, calculado == segredo))
rel(f"participantes honestos com valor errado: {honestos_enganados} de {ensaios}")
rel(f"trapaceiro recuperou o segredo verdadeiro: {trapaceiro_acerta} de {ensaios}")
salvar_csv("a6_ataques.csv", ["n", "k", "indice_trapaceiro", "honestos_enganados",
                              "trapaceiro_recuperou"], linhas)
rel.fechar()

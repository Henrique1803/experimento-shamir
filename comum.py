"""Funções auxiliares compartilhadas pelos experimentos (saída de resultados e gráficos)."""

import csv
import math
import os

PASTA_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


def caminho(nome):
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    return os.path.join(PASTA_RESULTADOS, nome)


class Relatorio:
    """Imprime na tela e grava o mesmo texto em resultados/<nome>.txt."""

    def __init__(self, nome):
        self.arquivo = open(caminho(nome + ".txt"), "w", encoding="utf-8")

    def __call__(self, texto=""):
        print(texto)
        self.arquivo.write(texto + "\n")

    def fechar(self):
        self.arquivo.close()
        print(f"\n[resultados gravados em {self.arquivo.name}]")


def salvar_csv(nome, cabecalho, linhas):
    with open(caminho(nome), "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def pyplot():
    """Devolve matplotlib.pyplot ou None, se a biblioteca não estiver instalada."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        print("[aviso] matplotlib não instalado, gráficos não gerados")
        return None


def qui_quadrado_critico(graus, alfa=0.05):
    """Valor crítico da distribuição qui-quadrado (aproximação de Wilson e Hilferty)."""
    z = {0.05: 1.6448536, 0.01: 2.3263479}[alfa]
    return graus * (1 - 2 / (9 * graus) + z * math.sqrt(2 / (9 * graus))) ** 3


def inclinacao_loglog(xs, ys):
    """Expoente do crescimento (mínimos quadrados em log-log)."""
    lx, ly = list(map(math.log, xs)), list(map(math.log, ys))
    mx = sum(lx) / len(lx)
    my = sum(ly) / len(ly)
    cov = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
    var = sum((a - mx) ** 2 for a in lx)
    return cov / var

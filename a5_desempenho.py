"""Experimento A5: medição de desempenho.

Cenários (mediana de várias repetições, relógio time.perf_counter_ns):
  1. k = n crescendo de 2 a 1000, p = 2^127 - 1;
  2. k = 10 fixo e n crescendo até 1000, p = 2^127 - 1;
  3. tamanho do segredo, trocando o primo (2^127 - 1, 2^256 - 189, 2^521 - 1) e, para
     segredos maiores, dividindo em blocos de 15 bytes com p = 2^127 - 1.
A divisão custa proporcionalmente a n k e a reconstrução a k^2 (mais k inversões).
A inclinação da reta em escala log-log estima o expoente do crescimento.
"""

import secrets
import statistics
import sys
import time

import shamir
from comum import Relatorio, caminho, inclinacao_loglog, pyplot, salvar_csv
from shamir import P127, P256, P521

rapido = "--rapido" in sys.argv
REPETICOES = 3 if rapido else 9
rel = Relatorio("a5_desempenho")


def mediana_ms(funcao, repeticoes=REPETICOES):
    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter_ns()
        funcao()
        tempos.append(time.perf_counter_ns() - inicio)
    return statistics.median(tempos) / 1e6


def medir(segredo, k, n, p):
    partes = shamir.dividir(segredo, k, n, p)
    t_div = mediana_ms(lambda: shamir.dividir(segredo, k, n, p))
    t_rec = mediana_ms(lambda: shamir.reconstruir(partes[:k], p))
    assert shamir.reconstruir(partes[:k], p) == segredo
    return t_div, t_rec


rel(f"Python {sys.version.split()[0]}, mediana de {REPETICOES} repetições, tempos em ms")

# Cenário 1 ------------------------------------------------------------------------------
valores_k = [2, 5, 10, 25, 50, 100, 250, 500] + ([] if rapido else [750, 1000])
rel("\n=== A5.1 k = n, p = 2^127 - 1 ===")
rel(f"{'k = n':>6} | {'divisão (ms)':>13} | {'reconstrução (ms)':>17}")
cen1 = []
for k in valores_k:
    t_div, t_rec = medir(secrets.randbelow(P127), k, k, P127)
    cen1.append((k, t_div, t_rec))
    rel(f"{k:6d} | {t_div:13.3f} | {t_rec:17.3f}")
grandes = [linha for linha in cen1 if linha[0] >= 50]
rel(f"expoente estimado (k >= 50): divisão {inclinacao_loglog([l[0] for l in grandes], [l[1] for l in grandes]):.2f}, "
    f"reconstrução {inclinacao_loglog([l[0] for l in grandes], [l[2] for l in grandes]):.2f} "
    f"(esperado próximo de 2)")
salvar_csv("a5_cenario1_k_igual_n.csv", ["k_igual_n", "divisao_ms", "reconstrucao_ms"], cen1)

# Cenário 2 ------------------------------------------------------------------------------
K_FIXO = 10
valores_n = [10, 25, 50, 100, 250, 500] + ([] if rapido else [750, 1000])
rel(f"\n=== A5.2 k = {K_FIXO} fixo, n variando, p = 2^127 - 1 ===")
rel(f"{'n':>6} | {'divisão (ms)':>13} | {'reconstrução (ms)':>17}")
cen2 = []
for n in valores_n:
    t_div, t_rec = medir(secrets.randbelow(P127), K_FIXO, n, P127)
    cen2.append((n, t_div, t_rec))
    rel(f"{n:6d} | {t_div:13.3f} | {t_rec:17.3f}")
rel(f"expoente estimado da divisão em função de n: "
    f"{inclinacao_loglog([l[0] for l in cen2], [l[1] for l in cen2]):.2f} (esperado próximo de 1); "
    f"a reconstrução depende apenas de k e fica praticamente constante")
salvar_csv("a5_cenario2_k_fixo.csv", ["n", "divisao_ms", "reconstrucao_ms"], cen2)

# Cenário 3 ------------------------------------------------------------------------------
K3, N3 = 10, 20
rel(f"\n=== A5.3 Tamanho do segredo, k = {K3}, n = {N3} ===")
rel(f"{'configuração':>30} | {'bytes':>5} | {'divisão (ms)':>13} | {'reconstrução (ms)':>17}")
cen3 = []
for nome, p in (("primo 2^127 - 1", P127), ("primo 2^256 - 189", P256), ("primo 2^521 - 1", P521)):
    tamanho = shamir.bytes_por_bloco(p)
    t_div, t_rec = medir(secrets.randbelow(p), K3, N3, p)
    cen3.append((nome, tamanho, t_div, t_rec))
    rel(f"{nome:>30} | {tamanho:5d} | {t_div:13.3f} | {t_rec:17.3f}")
for tamanho in (16, 64, 256, 1024) + (() if rapido else (4096,)):
    dados = secrets.token_bytes(tamanho)
    partes = shamir.dividir_bytes(dados, K3, N3)
    assert shamir.reconstruir_bytes(partes[:K3]) == dados
    t_div = mediana_ms(lambda: shamir.dividir_bytes(dados, K3, N3))
    t_rec = mediana_ms(lambda: shamir.reconstruir_bytes(partes[:K3]))
    nome = f"blocos de 15 bytes ({len(partes[0][1])} blocos)"
    cen3.append((nome, tamanho, t_div, t_rec))
    rel(f"{nome:>30} | {tamanho:5d} | {t_div:13.3f} | {t_rec:17.3f}")
salvar_csv("a5_cenario3_tamanho.csv", ["configuracao", "bytes", "divisao_ms", "reconstrucao_ms"], cen3)

plt = pyplot()
if plt:
    fig, eixos = plt.subplots(1, 2, figsize=(10, 4))
    ax = eixos[0]
    ks = [l[0] for l in cen1]
    ax.loglog(ks, [l[1] for l in cen1], "o-", label="divisão")
    ax.loglog(ks, [l[2] for l in cen1], "s-", label="reconstrução")
    ref = cen1[-1][2] / ks[-1] ** 2
    ax.loglog(ks, [ref * k**2 for k in ks], "k--", linewidth=1, label="referência $\\propto k^2$")
    ax.set_xlabel("$k = n$")
    ax.set_ylabel("tempo (ms)")
    ax.set_title("Cenário 1: $k = n$")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    ax = eixos[1]
    ns = [l[0] for l in cen2]
    ax.plot(ns, [l[1] for l in cen2], "o-", label="divisão")
    ax.plot(ns, [l[2] for l in cen2], "s-", label="reconstrução")
    ax.set_xlabel("$n$")
    ax.set_ylabel("tempo (ms)")
    ax.set_title(f"Cenário 2: $k = {K_FIXO}$ fixo")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(caminho("a5_desempenho.png"), dpi=200)

    blocos = [l for l in cen3 if l[0].startswith("blocos")]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.loglog([l[1] for l in blocos], [l[2] for l in blocos], "o-", label="divisão")
    ax.loglog([l[1] for l in blocos], [l[3] for l in blocos], "s-", label="reconstrução")
    ax.set_xlabel("tamanho do segredo (bytes)")
    ax.set_ylabel("tempo (ms)")
    ax.set_title(f"Cenário 3: segredos em blocos de 15 bytes ($k = {K3}$, $n = {N3}$)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(caminho("a5_tamanho_segredo.png"), dpi=200)
rel.fechar()

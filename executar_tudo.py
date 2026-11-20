"""Executa os testes da biblioteca (A1) e os experimentos A2 a A6, nessa ordem.

Uso: python executar_tudo.py [--rapido]
A opção --rapido reduz o número de repetições para uma conferência rápida.
"""

import os
import subprocess
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTOS = ["a2_correcao.py", "a3_sigilo.py", "a4_inteiros.py",
                "a5_desempenho.py", "a6_trapaceiro.py"]

print("=== A1 Testes da biblioteca ===", flush=True)
resultado = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_shamir"], cwd=PASTA)
if resultado.returncode != 0:
    sys.exit("testes da biblioteca falharam")

for script in EXPERIMENTOS:
    print(f"\n{'#' * 70}\n# {script}\n{'#' * 70}", flush=True)
    resultado = subprocess.run([sys.executable, script, *sys.argv[1:]], cwd=PASTA)
    if resultado.returncode != 0:
        sys.exit(f"{script} terminou com erro")
print("\nTodos os experimentos concluídos. Resultados em resultados/.")

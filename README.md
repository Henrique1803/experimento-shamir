# Experimentos com o esquema de Shamir

Implementação prática do trabalho de INE5429 Segurança em Computação (UFSC) sobre o esquema de compartilhamento de segredos de Shamir. Os experimentos A1 a A6 seguem a Seção 3 do relatório parcial.

## Arquivos

| Arquivo | Experimento | Conteúdo |
|---|---|---|
| `shamir.py` | A1 | Biblioteca com os Algoritmos 1 (divisão) e 2 (reconstrução), validações e divisão de segredos em blocos |
| `test_shamir.py` | A1 | Testes unitários da biblioteca |
| `a2_correcao.py` | A2 | Exemplo da Seção 2.5, todos os subconjuntos para n ≤ 10, parâmetros sorteados e interpolação com k − 1 partes |
| `a3_sigilo.py` | A3 | Busca exaustiva nos 4913 polinômios sobre Z₁₇ e distribuição das partes para D = 0 e D = 13 |
| `a4_inteiros.py` | A4 | Divisão sem redução modular e contagem dos candidatos compatíveis com k − 1 partes |
| `a5_desempenho.py` | A5 | Tempos de divisão e reconstrução em três cenários |
| `a6_trapaceiro.py` | A6 | Ataque de Tompa e Woll com uma parte adulterada |
| `comum.py` | | Funções auxiliares para gravar resultados e gerar gráficos |
| `executar_tudo.py` | | Executa os testes e todos os experimentos |

Os resultados ficam em `resultados/`. Cada experimento grava um arquivo `.txt` com a saída, arquivos `.csv` com os dados e, quando for o caso, gráficos `.png`.

## Como executar

É necessário Python 3.8 ou superior, por causa de `pow(a, -1, p)`. A biblioteca e os experimentos usam apenas a biblioteca padrão. A matplotlib só é usada para os gráficos e, se ela não estiver instalada, os gráficos não são gerados.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python executar_tudo.py
```

A execução completa leva cerca de 30 segundos. A opção `--rapido` reduz as repetições para uma conferência rápida, e cada script também pode ser executado isoladamente.

## Decisões de implementação

- O corpo padrão é Z_p com p = 2¹²⁷ − 1. O A5 também usa 2²⁵⁶ − 189 e 2⁵²¹ − 1.
- Os coeficientes são sorteados com `secrets.randbelow`. O módulo `random` é usado apenas para escolher parâmetros dos testes, como n, k e quais partes participam, e nunca para gerar coeficientes.
- A reconstrução rejeita partes com índice zero e índices repetidos.
- Segredos em bytes são divididos em blocos de 15 bytes, para p = 2¹²⁷ − 1, e cada bloco recebe um polinômio independente.

## Resumo dos resultados

Resultados de uma execução completa. Os números variam um pouco entre execuções porque os coeficientes são aleatórios.

| Experimento | Resultado |
|---|---|
| A1 | 14 testes unitários aprovados |
| A2 | A Tabela 1 foi reproduzida e os 10 trios reconstroem D = 13. Houve 40720 reconstruções com todos os subconjuntos (n ≤ 10) e 2000 com parâmetros sorteados, todas sem falha. Com k − 1 partes, as coincidências ficaram entre 5,82% e 5,89% para p = 17 (esperado 1/17 ≈ 5,88%) e foram 0 para p = 2¹²⁷ − 1, sempre exatamente quando a₍ₖ₋₁₎ = 0 |
| A3 | Cada um dos 17 candidatos tem exatamente um polinômio compatível. Os 289 pares (D₁, D₂) são compatíveis com a distribuição uniforme para D = 0 e para D = 13, e as duas distribuições são indistinguíveis (teste qui-quadrado a 5%) |
| A4 | Sem redução modular, 2 partes reduzem os 65536 candidatos para 28 a 71 em média com M = 2⁸. Mesmo com M = 2³², restam 32768, 10923 ou 3277, que correspondem a D mod 2, D mod 6 e D mod 20. Em Z₆₅₅₃₇, os 65536 candidatos continuam possíveis |
| A5 | Com k = n até 1000, o expoente estimado é 1,97 para a divisão e 1,90 para a reconstrução, o que confirma o crescimento quadrático. Com k fixo, a divisão cresce linearmente em n e a reconstrução fica constante |
| A6 | Em 10000 ataques com p = 2¹²⁷ − 1, os participantes honestos obtiveram o valor errado em todos e o trapaceiro recuperou o segredo em todos |

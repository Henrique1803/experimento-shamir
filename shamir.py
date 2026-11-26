"""A1: esquema de Shamir (divisão, reconstrução e segredos em bytes)."""

import secrets

P127 = 2**127 - 1  # padrão
P256 = 2**256 - 189
P521 = 2**521 - 1

PRIMO_PADRAO = P127


def avaliar(coeficientes, x, p):
    """Avalia q(x) = a_0 + a_1 x + ... + a_{k-1} x^{k-1} mod p pelo método de Horner."""
    y = 0
    for a in reversed(coeficientes):
        y = (y * x + a) % p
    return y


def validar_parametros(k, n, p):
    if not (1 <= k <= n < p):
        raise ValueError(f"parâmetros inválidos: é preciso 1 <= k <= n < p (k={k}, n={n})")


def sortear_coeficientes(segredo, k, p):
    """Devolve [a_0 = D, a_1, ..., a_{k-1}] com a_j uniformes em Z_p (módulo secrets)."""
    if not (0 <= segredo < p):
        raise ValueError("o segredo precisa estar em Z_p (0 <= D < p)")
    return [segredo] + [secrets.randbelow(p) for _ in range(k - 1)]


def partes_do_polinomio(coeficientes, n, p):
    """Gera as partes (i, q(i)) para i = 1, ..., n."""
    return [(i, avaliar(coeficientes, i, p)) for i in range(1, n + 1)]


def dividir(segredo, k, n, p=PRIMO_PADRAO):
    """Algoritmo 1. Divide o segredo D em n partes com limiar k."""
    validar_parametros(k, n, p)
    coeficientes = sortear_coeficientes(segredo, k, p)
    return partes_do_polinomio(coeficientes, n, p)


def validar_partes(partes, p):
    if not partes:
        raise ValueError("nenhuma parte informada")
    xs = {x % p for x, _ in partes}
    if 0 in xs:
        raise ValueError("parte com índice zero rejeitada")
    if len(xs) < len(partes):
        raise ValueError("partes com índices repetidos rejeitadas")


def coeficiente_lagrange(indices, j, p):
    """lambda_j = prod_{m != j} x_m / (x_m - x_j) mod p (coeficiente de Lagrange em zero)."""
    num, den = 1, 1
    xj = indices[j]
    for m, xm in enumerate(indices):
        if m != j:
            num = num * xm % p
            den = den * (xm - xj) % p
    return num * pow(den, -1, p) % p


def reconstruir(partes, p=PRIMO_PADRAO):
    """Algoritmo 2. Calcula q(0) a partir das partes (x_j, y_j) pela Equação (3)."""
    validar_partes(partes, p)
    indices = [x for x, _ in partes]
    segredo = 0
    for j, (_, yj) in enumerate(partes):
        segredo = (segredo + yj * coeficiente_lagrange(indices, j, p)) % p
    return segredo


def bytes_por_bloco(p):
    """Maior número de bytes cujo valor inteiro é sempre menor que p (15 para 2^127 - 1)."""
    return (p.bit_length() - 1) // 8


def bytes_para_blocos(dados, p):
    """Divide os bytes em blocos que cabem em Z_p e converte cada bloco em inteiro."""
    tamanho = bytes_por_bloco(p)
    return [int.from_bytes(dados[i:i + tamanho], "big") for i in range(0, len(dados), tamanho)]


def blocos_para_bytes(blocos, comprimento, p):
    tamanho = bytes_por_bloco(p)
    # o último bloco pode ser mais curto
    return b"".join(v.to_bytes(min(tamanho, comprimento - i * tamanho), "big")
                    for i, v in enumerate(blocos))


def dividir_bytes(dados, k, n, p=PRIMO_PADRAO):
    """Um polinômio por bloco. Parte i: (i, [valores], comprimento)."""
    validar_parametros(k, n, p)
    blocos = bytes_para_blocos(dados, p)
    por_bloco = [dividir(b, k, n, p) for b in blocos]
    return [(i, [por_bloco[b][i - 1][1] for b in range(len(blocos))], len(dados))
            for i in range(1, n + 1)]


def reconstruir_bytes(partes, p=PRIMO_PADRAO):
    """Reconstrói um segredo dividido com dividir_bytes."""
    comprimento = partes[0][2]
    if any(c != comprimento for _, _, c in partes):
        raise ValueError("partes de segredos diferentes")
    n_blocos = len(partes[0][1])
    blocos = [reconstruir([(x, valores[b]) for x, valores, _ in partes], p)
              for b in range(n_blocos)]
    return blocos_para_bytes(blocos, comprimento, p)

"""Testes unitários da biblioteca (experimento A1). Execução: python -m unittest -v"""

import itertools
import secrets
import unittest

import shamir
from shamir import P127, P256, P521


class TestDivisaoReconstrucao(unittest.TestCase):

    def test_exemplo_do_relatorio(self):
        partes = shamir.partes_do_polinomio([13, 2, 10], 5, 17)
        self.assertEqual(partes, [(1, 8), (2, 6), (3, 7), (4, 11), (5, 1)])
        for trio in itertools.combinations(partes, 3):
            self.assertEqual(shamir.reconstruir(list(trio), 17), 13)

    def test_coeficientes_de_lagrange_do_exemplo(self):
        # Seção 2.5: participantes 1, 2, 3 -> 3, -3, 1; participantes 2, 4, 5 -> -8, -5, -3
        self.assertEqual([shamir.coeficiente_lagrange([1, 2, 3], j, 17) for j in range(3)],
                         [3, -3 % 17, 1])
        self.assertEqual([shamir.coeficiente_lagrange([2, 4, 5], j, 17) for j in range(3)],
                         [-8 % 17, -5 % 17, -3 % 17])

    def test_ordem_das_partes_nao_importa(self):
        partes = shamir.dividir(123456789, 4, 7)
        escolhidas = [partes[6], partes[1], partes[4], partes[0]]
        self.assertEqual(shamir.reconstruir(escolhidas), 123456789)

    def test_mais_de_k_partes(self):
        partes = shamir.dividir(42, 3, 8)
        self.assertEqual(shamir.reconstruir(partes), 42)

    def test_todos_os_primos(self):
        for p in (P127, P256, P521):
            segredo = secrets.randbelow(p)
            partes = shamir.dividir(segredo, 5, 9, p)
            self.assertEqual(shamir.reconstruir(partes[2:7], p), segredo)

    def test_limiar_igual_a_um(self):
        self.assertEqual(shamir.dividir(5, 1, 3, 17), [(1, 5), (2, 5), (3, 5)])


class TestValidacoes(unittest.TestCase):

    def test_parametros_invalidos(self):
        for k, n, p in [(0, 3, 17), (4, 3, 17), (3, 17, 17), (3, 20, 17)]:
            with self.assertRaises(ValueError):
                shamir.dividir(1, k, n, p)

    def test_segredo_fora_do_corpo(self):
        with self.assertRaises(ValueError):
            shamir.dividir(17, 2, 3, 17)

    def test_indice_zero_rejeitado(self):
        with self.assertRaises(ValueError):
            shamir.reconstruir([(0, 5), (1, 8), (2, 6)], 17)
        with self.assertRaises(ValueError):
            shamir.reconstruir([(17, 5), (1, 8), (2, 6)], 17)

    def test_indice_repetido_rejeitado(self):
        with self.assertRaises(ValueError):
            shamir.reconstruir([(1, 8), (1, 8), (2, 6)], 17)
        with self.assertRaises(ValueError):
            shamir.reconstruir([(1, 8), (18, 8), (2, 6)], 17)

    def test_lista_vazia(self):
        with self.assertRaises(ValueError):
            shamir.reconstruir([], 17)


class TestBytes(unittest.TestCase):

    def test_tamanho_do_bloco(self):
        self.assertEqual(shamir.bytes_por_bloco(P127), 15)
        self.assertEqual(shamir.bytes_por_bloco(P256), 31)
        self.assertEqual(shamir.bytes_por_bloco(P521), 65)

    def test_ida_e_volta(self):
        for dados in (b"", b"\x00", b"\x00\x00abc", b"segredo", secrets.token_bytes(15),
                      secrets.token_bytes(16), secrets.token_bytes(100), b"\xff" * 45):
            for p in (P127, P256):
                blocos = shamir.bytes_para_blocos(dados, p)
                self.assertTrue(all(b < p for b in blocos))
                self.assertEqual(shamir.blocos_para_bytes(blocos, len(dados), p), dados)

    def test_dividir_bytes(self):
        dados = "Chave do cofre: 7f3a9c... (texto longo, várias dezenas de bytes)".encode()
        partes = shamir.dividir_bytes(dados, 3, 5)
        for trio in itertools.combinations(partes, 3):
            self.assertEqual(shamir.reconstruir_bytes(list(trio)), dados)


if __name__ == "__main__":
    unittest.main()

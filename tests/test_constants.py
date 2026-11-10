from __future__ import annotations

import unittest
from fractions import Fraction

from drenagem_pluvial_nbr10844.constants import (
    CIDADES_NBR10844,
    COEFICIENTES_MANNING,
    COEFICIENTES_ESCOAMENTO,
    TABELA_TUBOS_QUEDA_NBR10844,
    TABELA_CONDUTORES_HORIZONTAIS_NBR10844,
    DIAMETROS_INTERNOS_PVC_NBR10844,
    PI_FRAC,
    DECLIVIDADE_MINIMA_CALHA,
    DECLIVIDADE_MINIMA_CONDUTOR_HORIZ,
    RELACAO_LAMINA_MAX_CONDUTOR_HORIZ,
)


class TestConstants(unittest.TestCase):
    def test_pi_racional(self) -> None:
        self.assertEqual(PI_FRAC, Fraction(355, 113))
        # Diferença absoluta menor que 3e-7
        diff = abs(float(PI_FRAC) - 3.1415926535)
        self.assertLess(diff, 1e-6)

    def test_declividades_minimas(self) -> None:
        self.assertEqual(DECLIVIDADE_MINIMA_CALHA, Fraction(5, 1000))
        self.assertEqual(DECLIVIDADE_MINIMA_CONDUTOR_HORIZ, Fraction(5, 1000))
        self.assertEqual(RELACAO_LAMINA_MAX_CONDUTOR_HORIZ, Fraction(2, 3))

    def test_cidades_nbr10844(self) -> None:
        self.assertGreaterEqual(len(CIDADES_NBR10844), 15)
        for chave, info in CIDADES_NBR10844.items():
            self.assertIn("nome", info)
            self.assertIn("uf", info)
            self.assertIn("intensidades", info)
            intensidades = info["intensidades"]
            for t in (1, 5, 25):
                self.assertIn(t, intensidades)
                self.assertIsInstance(intensidades[t], Fraction)
                self.assertGreater(intensidades[t], Fraction(50, 1))
            # T=25 deve ser maior que T=5, que deve ser maior que T=1
            self.assertGreater(intensidades[25], intensidades[5])
            self.assertGreater(intensidades[5], intensidades[1])

    def test_coeficientes_manning(self) -> None:
        self.assertIn("pvc", COEFICIENTES_MANNING)
        self.assertIn("aco_galvanizado", COEFICIENTES_MANNING)
        for mat, n in COEFICIENTES_MANNING.items():
            self.assertIsInstance(n, Fraction)
            self.assertGreater(n, Fraction(0, 1))
            self.assertLess(n, Fraction(5, 100))

    def test_coeficientes_escoamento(self) -> None:
        for sup, c in COEFICIENTES_ESCOAMENTO.items():
            self.assertIsInstance(c, Fraction)
            self.assertGreater(c, Fraction(0, 1))
            self.assertLessEqual(c, Fraction(1, 1))

    def test_tabela_tubos_queda(self) -> None:
        dns_esperados = [75, 100, 125, 150, 200]
        self.assertEqual(list(TABELA_TUBOS_QUEDA_NBR10844.keys()), dns_esperados)
        for dn, bocais in TABELA_TUBOS_QUEDA_NBR10844.items():
            self.assertIn("reto", bocais)
            self.assertIn("funil", bocais)
            self.assertGreater(bocais["funil"], bocais["reto"])
            self.assertGreater(bocais["reto"], 0)

    def test_tabela_condutores_horizontais(self) -> None:
        dns_esperados = [75, 100, 125, 150, 200, 250, 300]
        self.assertEqual(list(TABELA_CONDUTORES_HORIZONTAIS_NBR10844.keys()), dns_esperados)
        for dn, decls in TABELA_CONDUTORES_HORIZONTAIS_NBR10844.items():
            for dec, cap in decls.items():
                self.assertIsInstance(dec, Fraction)
                self.assertIsInstance(cap, int)
                self.assertGreater(cap, 0)
            # Declividade maior deve ter capacidade maior
            self.assertGreater(decls[Fraction(4, 100)], decls[Fraction(5, 1000)])

    def test_diametros_internos(self) -> None:
        for dn, di in DIAMETROS_INTERNOS_PVC_NBR10844.items():
            self.assertIsInstance(di, Fraction)
            self.assertGreater(di, Fraction(0, 1))
            # Diâmetro interno deve ser menor que o diâmetro nominal externo
            self.assertLess(di, Fraction(dn, 1))


if __name__ == "__main__":
    unittest.main()

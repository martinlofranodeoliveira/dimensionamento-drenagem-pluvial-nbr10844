from __future__ import annotations

import unittest
from fractions import Fraction

from drenagem_pluvial_nbr10844.models import (
    DadosChuva,
    SuperficieContribuicao,
    Calha,
    CondutorVertical,
    CondutorHorizontal,
    CaixaAreia,
    ProjetoDrenagem,
)
from drenagem_pluvial_nbr10844.calculator import dimensionar_sistema
from drenagem_pluvial_nbr10844.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    def test_gerar_painel_svg(self) -> None:
        proj = ProjetoDrenagem(
            identificacao="Edifício Residencial Alpha",
            chuva=DadosChuva("sao_paulo", "SP", 5, 5, Fraction(159, 1)),
            superficie=SuperficieContribuicao("Telhado", Fraction(120, 1)),
            calha=Calha("Calha Principal", "retangular", "pvc", Fraction(150, 1), Fraction(150, 1), Fraction(120, 1), Fraction(80, 1), Fraction(1, 100)),
            condutor_vertical=CondutorVertical("TQ", 100, "funil"),
            condutor_horizontal=CondutorHorizontal("CH", 125, "pvc", Fraction(1, 100)),
            caixa_areia=CaixaAreia("CA", 400, 400, 400, 200),
        )
        res = dimensionar_sistema(proj)
        svg = gerar_painel_svg(res)

        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("ABNT NBR 10844:1989", svg)
        self.assertIn("VAZÃO DE PROJETO", svg)
        self.assertIn("DIAGRAMA ESQUEMÁTICO DO SISTEMA PREDIAL", svg)
        self.assertIn("Edifício Residencial Alpha", svg)
        self.assertIn("SISTEMA CONFORME NBR 10844", svg)


if __name__ == "__main__":
    unittest.main()

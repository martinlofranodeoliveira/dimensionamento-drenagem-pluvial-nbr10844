from __future__ import annotations

import unittest
from fractions import Fraction

from drenagem_pluvial_nbr10844.exporters import (
    sanitizar_campo_csv,
    formatar_fracao_decimal,
    exportar_csv,
    gerar_relatorio_memorial,
)
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


class TestExporters(unittest.TestCase):
    def test_sanitizar_campo_csv_formula_injection(self) -> None:
        # Previne injeção de fórmulas iniciadas por =, +, -, @, \t, \r
        self.assertEqual(sanitizar_campo_csv("=SOMA(A1:A10)"), "'=SOMA(A1:A10)")
        self.assertEqual(sanitizar_campo_csv("+123"), "'+123")
        self.assertEqual(sanitizar_campo_csv("-123"), "'-123")
        self.assertEqual(sanitizar_campo_csv("@cmd"), "'@cmd")
        self.assertEqual(sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(sanitizar_campo_csv("\rreturn"), "'\rreturn")
        self.assertEqual(sanitizar_campo_csv("Texto Normal"), "Texto Normal")
        self.assertEqual(sanitizar_campo_csv(123), "123")

    def test_formatar_fracao_decimal(self) -> None:
        self.assertEqual(formatar_fracao_decimal(Fraction(10, 1)), "10")
        self.assertEqual(formatar_fracao_decimal(Fraction(1, 2)), "0,50")
        self.assertEqual(formatar_fracao_decimal(Fraction(1, 4)), "0,25")
        self.assertEqual(formatar_fracao_decimal(Fraction(10, 3), 2), "3,33")

    def test_exportar_csv_e_memorial(self) -> None:
        proj = ProjetoDrenagem(
            identificacao="Projeto Exportação",
            chuva=DadosChuva("sao_paulo", "SP", 5, 5, Fraction(159, 1)),
            superficie=SuperficieContribuicao("Telhado", Fraction(100, 1)),
            calha=Calha("Calha", "retangular", "pvc", Fraction(150, 1), Fraction(150, 1), Fraction(120, 1), Fraction(80, 1), Fraction(1, 100)),
            condutor_vertical=CondutorVertical("TQ", 100, "funil"),
            condutor_horizontal=CondutorHorizontal("CH", 100, "pvc", Fraction(1, 100)),
            caixa_areia=CaixaAreia("CA", 400, 400, 400, 200),
        )
        res = dimensionar_sistema(proj)

        csv_txt = exportar_csv(res)
        self.assertIn("Componente;Identificação", csv_txt)
        self.assertIn("Superfície", csv_txt)
        self.assertIn("Calha", csv_txt)
        self.assertIn("Condutor Vertical", csv_txt)
        self.assertIn("Condutor Horizontal", csv_txt)
        self.assertIn("Caixa de Areia", csv_txt)

        memorial = gerar_relatorio_memorial(res)
        self.assertIn("MEMORIAL DE CÁLCULO NORMATIVO", memorial)
        self.assertIn("ABNT NBR 10844:1989", memorial)
        self.assertIn("MÉTODO RACIONAL", memorial)
        self.assertIn("MANNING-STRICKLER", memorial)
        self.assertIn("LOFRANO TECNOLOGIA", memorial)


if __name__ == "__main__":
    unittest.main()

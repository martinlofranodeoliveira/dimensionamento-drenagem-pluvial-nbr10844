from __future__ import annotations

import unittest
from fractions import Fraction

from drenagem_pluvial_nbr10844.models import (
    DadosChuva,
    ParedeVertical,
    SuperficieContribuicao,
    Calha,
    CondutorVertical,
    CondutorHorizontal,
    Ralo,
    CaixaAreia,
    ProjetoDrenagem,
)


class TestModels(unittest.TestCase):
    def test_dados_chuva_valido(self) -> None:
        chuva = DadosChuva(
            cidade="São Paulo",
            uf="SP",
            periodo_retorno_anos=5,
            duracao_minutos=5,
            intensidade_mm_h=Fraction(159, 1),
        )
        self.assertEqual(chuva.cidade, "São Paulo")
        self.assertEqual(chuva.periodo_retorno_anos, 5)
        self.assertEqual(chuva.intensidade_mm_h, Fraction(159, 1))

    def test_dados_chuva_invalido(self) -> None:
        with self.assertRaises(ValueError):
            DadosChuva(periodo_retorno_anos=10)  # deve ser 1, 5 ou 25
        with self.assertRaises(ValueError):
            DadosChuva(duracao_minutos=0)
        with self.assertRaises(ValueError):
            DadosChuva(intensidade_mm_h=Fraction(-10, 1))

    def test_parede_vertical(self) -> None:
        parede = ParedeVertical(
            identificacao="Platibanda",
            altura_m=Fraction(5, 2),
            largura_m=Fraction(10, 1),
        )
        self.assertEqual(parede.area_m2, Fraction(25, 1))
        with self.assertRaises(ValueError):
            ParedeVertical("Invalida", Fraction(-1, 1), Fraction(10, 1))

    def test_superficie_contribuicao(self) -> None:
        sup = SuperficieContribuicao(
            identificacao="Telhado",
            area_horizontal_m2=Fraction(100, 1),
            coeficiente_escoamento=Fraction(1, 1),
        )
        self.assertEqual(sup.area_horizontal_m2, Fraction(100, 1))
        with self.assertRaises(ValueError):
            SuperficieContribuicao("Erro", Fraction(0, 1))
        with self.assertRaises(ValueError):
            SuperficieContribuicao("Erro C", Fraction(100, 1), coeficiente_escoamento=Fraction(12, 10))

    def test_calha_model(self) -> None:
        calha = Calha(
            identificacao="Calha 1",
            tipo_secao="retangular",
            material="pvc",
            largura_fundo_mm=Fraction(150, 1),
            altura_total_mm=Fraction(120, 1),
            declividade_m_m=Fraction(1, 100),
        )
        self.assertEqual(calha.largura_fundo_mm, Fraction(150, 1))
        with self.assertRaises(ValueError):
            Calha("Erro", tipo_secao="triangular")
        with self.assertRaises(ValueError):
            Calha("Erro dim", largura_fundo_mm=Fraction(-10, 1))
        with self.assertRaises(ValueError):
            Calha("Erro dec", declividade_m_m=Fraction(0, 1))

    def test_condutor_vertical_model(self) -> None:
        cv = CondutorVertical(identificacao="TQ 1", dn_mm=100, tipo_bocal="funil")
        self.assertEqual(cv.dn_mm, 100)
        self.assertEqual(cv.tipo_bocal, "funil")
        with self.assertRaises(ValueError):
            CondutorVertical("Erro DN", dn_mm=80)
        with self.assertRaises(ValueError):
            CondutorVertical("Erro bocal", dn_mm=100, tipo_bocal="curvo")
        with self.assertRaises(ValueError):
            CondutorVertical("Erro altura", dn_mm=100, altura_m=Fraction(0, 1))

    def test_condutor_horizontal_model(self) -> None:
        ch = CondutorHorizontal(identificacao="CH 1", dn_mm=100, declividade_m_m=Fraction(1, 100))
        self.assertEqual(ch.dn_mm, 100)
        with self.assertRaises(ValueError):
            CondutorHorizontal("Erro DN", dn_mm=60)
        with self.assertRaises(ValueError):
            CondutorHorizontal("Erro dec", dn_mm=100, declividade_m_m=Fraction(-1, 100))

    def test_ralo_e_caixa(self) -> None:
        ralo = Ralo(identificacao="Ralo", tipo_ralo="hemisferico", dn_mm=100)
        self.assertEqual(ralo.tipo_ralo, "hemisferico")
        caixa = CaixaAreia(identificacao="Caixa", largura_mm=400, comprimento_mm=400, altura_util_mm=400, altura_sedimentacao_mm=200)
        self.assertEqual(caixa.largura_mm, 400)


if __name__ == "__main__":
    unittest.main()

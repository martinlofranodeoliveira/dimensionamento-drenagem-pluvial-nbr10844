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
    CaixaAreia,
    ProjetoDrenagem,
)
from drenagem_pluvial_nbr10844.calculator import (
    icbrt,
    raiz_quadrada_frac,
    raiz_cubica_frac,
    obter_intensidade_cidade,
    calcular_area_efetiva,
    calcular_vazao_racional,
    calcular_calha,
    verificar_condutor_vertical,
    obter_capacidade_condutor_horizontal_tabela,
    calcular_condutor_horizontal_manning,
    calcular_condutor_horizontal,
    verificar_caixa_areia,
    dimensionar_sistema,
)


class TestCalculator(unittest.TestCase):
    def test_icbrt(self) -> None:
        self.assertEqual(icbrt(0), 0)
        self.assertEqual(icbrt(1), 1)
        self.assertEqual(icbrt(8), 2)
        self.assertEqual(icbrt(27), 3)
        self.assertEqual(icbrt(64), 4)
        self.assertEqual(icbrt(125), 5)
        self.assertEqual(icbrt(1000), 10)
        self.assertEqual(icbrt(26), 2)
        self.assertEqual(icbrt(28), 3)
        self.assertEqual(icbrt(-8), -2)
        self.assertEqual(icbrt(10**18), 10**6)

    def test_raiz_quadrada_frac(self) -> None:
        self.assertEqual(raiz_quadrada_frac(Fraction(0, 1)), Fraction(0, 1))
        self.assertEqual(raiz_quadrada_frac(Fraction(4, 9)), Fraction(2, 3))
        self.assertEqual(raiz_quadrada_frac(Fraction(1, 100)), Fraction(1, 10))
        # Raiz de 2 com precisão decimal
        r2 = raiz_quadrada_frac(Fraction(2, 1))
        self.assertAlmostEqual(float(r2), 1.41421356237, places=9)
        with self.assertRaises(ValueError):
            raiz_quadrada_frac(Fraction(-4, 1))

    def test_raiz_cubica_frac(self) -> None:
        self.assertEqual(raiz_cubica_frac(Fraction(0, 1)), Fraction(0, 1))
        self.assertEqual(raiz_cubica_frac(Fraction(8, 27)), Fraction(2, 3))
        self.assertEqual(raiz_cubica_frac(Fraction(-1, 8)), Fraction(-1, 2))
        r2 = raiz_cubica_frac(Fraction(2, 1))
        self.assertAlmostEqual(float(r2), 1.25992104989, places=9)

    def test_obter_intensidade_cidade(self) -> None:
        sp_5 = obter_intensidade_cidade("sao_paulo", 5)
        self.assertEqual(sp_5, Fraction(159, 1))
        cur_25 = obter_intensidade_cidade("Curitiba", 25)
        self.assertEqual(cur_25, Fraction(186, 1))
        with self.assertRaises(KeyError):
            obter_intensidade_cidade("cidade_inexistente", 5)
        with self.assertRaises(ValueError):
            obter_intensidade_cidade("sao_paulo", 10)

    def test_calcular_area_efetiva(self) -> None:
        # Sem paredes
        sup1 = SuperficieContribuicao("T1", Fraction(100, 1))
        ah, ap, ac = calcular_area_efetiva(sup1)
        self.assertEqual(ah, Fraction(100, 1))
        self.assertEqual(ap, Fraction(0, 1))
        self.assertEqual(ac, Fraction(100, 1))

        # Com 1 parede de 2x10m = 20m2 -> contribuição 10m2
        p1 = ParedeVertical("P1", Fraction(2, 1), Fraction(10, 1))
        sup2 = SuperficieContribuicao("T2", Fraction(100, 1), paredes=[p1])
        ah, ap, ac = calcular_area_efetiva(sup2)
        self.assertEqual(ah, Fraction(100, 1))
        self.assertEqual(ap, Fraction(10, 1))
        self.assertEqual(ac, Fraction(110, 1))

    def test_calcular_vazao_racional(self) -> None:
        # Ac = 100 m2, I = 150 mm/h, C = 1.0 -> Q = 100 * 150 / 60 = 250 L/min
        q_min, q_s = calcular_vazao_racional(Fraction(100, 1), Fraction(150, 1), Fraction(1, 1))
        self.assertEqual(q_min, Fraction(250, 1))
        self.assertEqual(q_s, Fraction(250, 60))

    def test_calcular_calha_retangular(self) -> None:
        calha = Calha(
            identificacao="Calha 1",
            tipo_secao="retangular",
            material="pvc",
            largura_fundo_mm=Fraction(150, 1),
            altura_total_mm=Fraction(120, 1),
            lamina_dagua_mm=Fraction(80, 1),
            declividade_m_m=Fraction(1, 100),
        )
        res = calcular_calha(calha, Fraction(300, 1))
        self.assertTrue(res.atende_norma)
        self.assertTrue(res.atende_declividade)
        self.assertTrue(res.atende_borda_livre)
        self.assertTrue(res.atende_capacidade)
        self.assertGreater(res.vazao_admissivel_L_min, Fraction(500, 1))
        self.assertGreater(res.velocidade_escoamento_m_s, Fraction(0, 1))
        self.assertEqual(res.borda_livre_mm, Fraction(40, 1))

    def test_calcular_calha_semicircular(self) -> None:
        calha = Calha(
            identificacao="Calha Semi",
            tipo_secao="semicircular",
            material="pvc",
            largura_fundo_mm=Fraction(150, 1), # diâmetro
            altura_total_mm=Fraction(75, 1),   # raio
            declividade_m_m=Fraction(1, 100),
        )
        res = calcular_calha(calha, Fraction(200, 1))
        self.assertTrue(res.atende_capacidade)
        self.assertEqual(res.tipo_secao, "semicircular")

    def test_calcular_calha_trapezoidal(self) -> None:
        calha = Calha(
            identificacao="Calha Trap",
            tipo_secao="trapezoidal",
            material="pvc",
            largura_fundo_mm=Fraction(150, 1),
            largura_topo_mm=Fraction(250, 1),
            altura_total_mm=Fraction(120, 1),
            lamina_dagua_mm=Fraction(80, 1),
            declividade_m_m=Fraction(1, 100),
        )
        res = calcular_calha(calha, Fraction(400, 1))
        self.assertTrue(res.atende_capacidade)
        self.assertEqual(res.tipo_secao, "trapezoidal")

    def test_calha_declividade_insuficiente(self) -> None:
        calha = Calha(
            identificacao="Calha Plana",
            tipo_secao="retangular",
            largura_fundo_mm=Fraction(150, 1),
            altura_total_mm=Fraction(120, 1),
            declividade_m_m=Fraction(2, 1000), # 0.2% < 0.5%
        )
        res = calcular_calha(calha, Fraction(100, 1))
        self.assertFalse(res.atende_declividade)
        self.assertFalse(res.atende_norma)

    def test_verificar_condutor_vertical(self) -> None:
        cv_reto = CondutorVertical(identificacao="TQ 1", dn_mm=100, tipo_bocal="reto")
        res1 = verificar_condutor_vertical(cv_reto, Fraction(500, 1))
        self.assertTrue(res1.atende_norma)
        self.assertEqual(res1.capacidade_admissivel_L_min, Fraction(540, 1))

        # Excedendo capacidade
        res2 = verificar_condutor_vertical(cv_reto, Fraction(600, 1))
        self.assertFalse(res2.atende_norma)

        # Com funil atende
        cv_funil = CondutorVertical(identificacao="TQ 2", dn_mm=100, tipo_bocal="funil")
        res3 = verificar_condutor_vertical(cv_funil, Fraction(600, 1))
        self.assertTrue(res3.atende_norma)
        self.assertEqual(res3.capacidade_admissivel_L_min, Fraction(1060, 1))

    def test_condutor_horizontal_tabela_e_manning(self) -> None:
        # Exato na Tabela 5: DN 100 a 1% = 305 L/min
        cap_tab = obter_capacidade_condutor_horizontal_tabela(100, Fraction(1, 100))
        self.assertEqual(cap_tab, Fraction(305, 1))

        # Interpolação entre 1% (305) e 2% (435) para 1.5% = 370 L/min aproximado
        cap_interp = obter_capacidade_condutor_horizontal_tabela(100, Fraction(15, 1000))
        self.assertEqual(cap_interp, Fraction(375, 1))

        # Manning
        cap_m = calcular_condutor_horizontal_manning(100, Fraction(1, 100))
        self.assertGreater(cap_m, Fraction(200, 1))

        # Verificação do componente
        ch = CondutorHorizontal(identificacao="CH 1", dn_mm=100, declividade_m_m=Fraction(1, 100))
        res = calcular_condutor_horizontal(ch, Fraction(250, 1))
        self.assertTrue(res.atende_norma)
        self.assertEqual(res.capacidade_tabela_L_min, Fraction(305, 1))

    def test_caixa_areia(self) -> None:
        caixa_ok = CaixaAreia("C1", 400, 400, 400, 200)
        res_ok = verificar_caixa_areia(caixa_ok)
        self.assertTrue(res_ok.atende_norma)
        self.assertEqual(res_ok.volume_sedimentacao_L, Fraction(32, 1))

        caixa_baixa = CaixaAreia("C2", 400, 400, 400, 150) # sedimentação < 200mm
        res_baixa = verificar_caixa_areia(caixa_baixa)
        self.assertFalse(res_baixa.atende_norma)

    def test_dimensionar_sistema_completo(self) -> None:
        proj = ProjetoDrenagem(
            identificacao="Residência Unifamiliar",
            chuva=DadosChuva("sao_paulo", "SP", 5, 5, Fraction(159, 1)),
            superficie=SuperficieContribuicao("Telhado", Fraction(100, 1)),
            calha=Calha("Calha", "retangular", "pvc", Fraction(150, 1), Fraction(150, 1), Fraction(120, 1), Fraction(80, 1), Fraction(1, 100)),
            condutor_vertical=CondutorVertical("TQ", 100, "funil"),
            condutor_horizontal=CondutorHorizontal("CH", 100, "pvc", Fraction(1, 100)),
            caixa_areia=CaixaAreia("CA", 400, 400, 400, 200),
        )
        res = dimensionar_sistema(proj)
        self.assertTrue(res.atende_geral)
        self.assertEqual(res.resultado_superficie.vazao_projeto_L_min, Fraction(1590, 6))
        self.assertIsNotNone(res.resultado_calha)
        self.assertIsNotNone(res.resultado_condutor_vertical)
        self.assertIsNotNone(res.resultado_condutor_horizontal)
        self.assertIsNotNone(res.resultado_caixa_areia)


    def test_multiplas_paredes_verticais(self) -> None:
        p1 = ParedeVertical("P1", Fraction(3, 1), Fraction(10, 1)) # 30 m2 -> 15 m2
        p2 = ParedeVertical("P2", Fraction(4, 1), Fraction(5, 1))  # 20 m2 -> 10 m2
        sup = SuperficieContribuicao("Telhado", Fraction(100, 1), paredes=[p1, p2])
        ah, ap, ac = calcular_area_efetiva(sup)
        self.assertEqual(ah, Fraction(100, 1))
        self.assertEqual(ap, Fraction(25, 1))
        self.assertEqual(ac, Fraction(125, 1))

    def test_calha_borda_livre_insuficiente(self) -> None:
        calha = Calha(
            identificacao="Calha Transbordando",
            tipo_secao="retangular",
            largura_fundo_mm=Fraction(150, 1),
            altura_total_mm=Fraction(120, 1),
            lamina_dagua_mm=Fraction(115, 1), # Borda livre de apenas 5 mm (< 20 mm)
            declividade_m_m=Fraction(1, 100),
        )
        res = calcular_calha(calha, Fraction(100, 1))
        self.assertFalse(res.atende_borda_livre)
        self.assertFalse(res.atende_norma)

    def test_condutor_horizontal_abaixo_minimo_declividade(self) -> None:
        ch = CondutorHorizontal("CH Sub", dn_mm=100, declividade_m_m=Fraction(2, 1000)) # 0.2% < 0.5%
        res = calcular_condutor_horizontal(ch, Fraction(50, 1))
        self.assertFalse(res.atende_declividade)
        self.assertFalse(res.atende_norma)

    def test_todas_cidades_calculam_vazao(self) -> None:
        from drenagem_pluvial_nbr10844.constants import CIDADES_NBR10844
        for cidade in CIDADES_NBR10844.keys():
            i = obter_intensidade_cidade(cidade, 5)
            q_min, q_s = calcular_vazao_racional(Fraction(100, 1), i)
            self.assertGreater(q_min, Fraction(0, 1))
            self.assertGreater(q_s, Fraction(0, 1))

    def test_caixa_areia_dimensao_insuficiente(self) -> None:
        caixa_estreita = CaixaAreia("CE", 300, 400, 400, 200) # 300 < 400
        res = verificar_caixa_areia(caixa_estreita)
        self.assertFalse(res.atende_norma)


if __name__ == "__main__":
    unittest.main()

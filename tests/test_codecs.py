from __future__ import annotations

import unittest
from fractions import Fraction
import tempfile
import os

from drenagem_pluvial_nbr10844.codecs import (
    carregar_json_canonico,
    salvar_json_canonico,
    converter_para_dict,
    serializar_fracao,
    deserializar_fracao,
    deserializar_projeto,
    verificar_profundidade,
)
from drenagem_pluvial_nbr10844.models import (
    DadosChuva,
    SuperficieContribuicao,
    ParedeVertical,
    Calha,
    CondutorVertical,
    CondutorHorizontal,
    ProjetoDrenagem,
)


class TestCodecs(unittest.TestCase):
    def test_rejeicao_float(self) -> None:
        json_com_float = '{"intensidade": 150.5}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_com_float)
        self.assertIn("Ponto flutuante IEEE-754", str(ctx.exception))

    def test_rejeicao_bom(self) -> None:
        json_com_bom = '\ufeff{"area": 100}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_com_bom)
        self.assertIn("BOM UTF-8 não permitido", str(ctx.exception))

    def test_rejeicao_chaves_duplicadas(self) -> None:
        json_duplicado = '{"chave": 1, "chave": 2}'
        with self.assertRaises(ValueError) as ctx:
            carregar_json_canonico(json_duplicado)
        self.assertIn("Chave duplicada detectada", str(ctx.exception))

    def test_rejeicao_profundidade_excessiva(self) -> None:
        d = 1
        for _ in range(35):
            d = {"filho": d}
        with self.assertRaises(ValueError) as ctx:
            verificar_profundidade(d, 1, 32)
        self.assertIn("Profundidade máxima", str(ctx.exception))

    def test_serializar_deserializar_fracao(self) -> None:
        f = Fraction(355, 113)
        s = serializar_fracao(f)
        self.assertEqual(s, {"num": 355, "den": 113})
        f2 = deserializar_fracao(s)
        self.assertEqual(f2, f)
        self.assertEqual(deserializar_fracao("355/113"), f)
        self.assertEqual(deserializar_fracao(10), Fraction(10, 1))

    def test_salvar_carregar_projeto_roundtrip(self) -> None:
        proj = ProjetoDrenagem(
            identificacao="Teste Roundtrip",
            chuva=DadosChuva("sao_paulo", "SP", 5, 5, Fraction(159, 1)),
            superficie=SuperficieContribuicao(
                "Telhado",
                Fraction(150, 1),
                paredes=[ParedeVertical("P1", Fraction(2, 1), Fraction(10, 1))],
            ),
            calha=Calha("C1", "retangular", "pvc", Fraction(150, 1), Fraction(150, 1), Fraction(120, 1), Fraction(80, 1), Fraction(1, 100)),
            condutor_vertical=CondutorVertical("TQ", 100, "funil"),
            condutor_horizontal=CondutorHorizontal("CH", 100, "pvc", Fraction(1, 100)),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            arq = os.path.join(tmpdir, "projeto_teste.json")
            salvar_json_canonico(arq, proj)
            self.assertTrue(os.path.exists(arq))

            dados = carregar_json_canonico(arq)
            proj_reconstituido = deserializar_projeto(dados)
            self.assertEqual(proj_reconstituido.identificacao, proj.identificacao)
            self.assertEqual(proj_reconstituido.chuva.intensidade_mm_h, proj.chuva.intensidade_mm_h)
            self.assertEqual(len(proj_reconstituido.superficie.paredes), 1)


    def test_deserializar_fracao_erros(self) -> None:
        with self.assertRaises(ValueError):
            deserializar_fracao({"num": "abc", "den": 1})
        with self.assertRaises(ValueError):
            deserializar_fracao([1, 2, 3])

    def test_deserializar_fracao_string_simples(self) -> None:
        self.assertEqual(deserializar_fracao("150"), Fraction(150, 1))
        self.assertEqual(deserializar_fracao("-25/5"), Fraction(-5, 1))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from unittest.mock import patch
import io
import sys
import tempfile
import os

from drenagem_pluvial_nbr10844.cli import main


class TestCli(unittest.TestCase):
    def test_cli_versao(self) -> None:
        with patch.object(sys, "argv", ["drenagem-pluvial", "versao"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                ret = main()
                self.assertEqual(ret, 0)
                self.assertIn("v1.0.0", fake_out.getvalue())

    def test_cli_cidades(self) -> None:
        with patch.object(sys, "argv", ["drenagem-pluvial", "cidades"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                ret = main()
                self.assertEqual(ret, 0)
                self.assertIn("sao_paulo", fake_out.getvalue())
                self.assertIn("curitiba", fake_out.getvalue())

    def test_cli_tabelas(self) -> None:
        with patch.object(sys, "argv", ["drenagem-pluvial", "tabelas"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                ret = main()
                self.assertEqual(ret, 0)
                self.assertIn("TABELA 4", fake_out.getvalue())
                self.assertIn("TABELA 5", fake_out.getvalue())

    def test_cli_dimensionar_arquivo(self) -> None:
        with patch.object(sys, "argv", ["drenagem-pluvial", "dimensionar", "--arquivo", "examples/edificio_residencial.json"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                ret = main()
                self.assertEqual(ret, 0)
                self.assertIn("MEMORIAL DE CÁLCULO NORMATIVO", fake_out.getvalue())
                self.assertIn("Status Geral de Aprovação: APROVADO", fake_out.getvalue())

    def test_cli_dimensionar_argumentos_e_saidas(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "res.json")
            csv_path = os.path.join(tmpdir, "res.csv")
            txt_path = os.path.join(tmpdir, "res.txt")
            svg_path = os.path.join(tmpdir, "res.svg")

            args = [
                "drenagem-pluvial", "dimensionar",
                "--cidade", "sao_paulo",
                "--retorno", "5",
                "--area", "150",
                "--calha-largura", "180",
                "--calha-altura", "150",
                "--calha-declividade", "1.0",
                "--tq-dn", "100",
                "--tq-bocal", "funil",
                "--ch-dn", "125",
                "--ch-declividade", "1.0",
                "--saida-json", json_path,
                "--saida-csv", csv_path,
                "--saida-relatorio", txt_path,
                "--painel-svg", svg_path,
            ]

            with patch.object(sys, "argv", args):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    ret = main()
                    self.assertEqual(ret, 0)
                    self.assertTrue(os.path.exists(json_path))
                    self.assertTrue(os.path.exists(csv_path))
                    self.assertTrue(os.path.exists(txt_path))
                    self.assertTrue(os.path.exists(svg_path))

    def test_cli_erro_argumentos(self) -> None:
        with patch.object(sys, "argv", ["drenagem-pluvial", "dimensionar"]):
            with patch("sys.stderr", new=io.StringIO()) as fake_err:
                ret = main()
                self.assertEqual(ret, 1)
                self.assertIn("Erro", fake_err.getvalue())


if __name__ == "__main__":
    unittest.main()

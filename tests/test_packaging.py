from __future__ import annotations

import unittest
import importlib
import sys
import tomllib
from pathlib import Path

import drenagem_pluvial_nbr10844


class TestPackaging(unittest.TestCase):
    def test_versao(self) -> None:
        self.assertEqual(drenagem_pluvial_nbr10844.__version__, "1.0.0")

    def test_pyproject_toml(self) -> None:
        caminho_toml = Path(__file__).resolve().parent.parent / "pyproject.toml"
        self.assertTrue(caminho_toml.exists())
        with open(caminho_toml, "rb") as f:
            dados = tomllib.load(f)
        
        proj = dados.get("project", {})
        self.assertEqual(proj.get("name"), "dimensionamento-drenagem-pluvial-nbr10844")
        self.assertEqual(proj.get("version"), "1.0.0")
        self.assertEqual(proj.get("dependencies"), [])  # ZERO dependências externas!

    def test_zero_dependencias_externas(self) -> None:
        modulos = [
            "drenagem_pluvial_nbr10844",
            "drenagem_pluvial_nbr10844.constants",
            "drenagem_pluvial_nbr10844.models",
            "drenagem_pluvial_nbr10844.calculator",
            "drenagem_pluvial_nbr10844.codecs",
            "drenagem_pluvial_nbr10844.exporters",
            "drenagem_pluvial_nbr10844.svg_generator",
            "drenagem_pluvial_nbr10844.cli",
        ]
        
        for mod_nome in modulos:
            mod = importlib.import_module(mod_nome)
            self.assertIsNotNone(mod)


if __name__ == "__main__":
    unittest.main()

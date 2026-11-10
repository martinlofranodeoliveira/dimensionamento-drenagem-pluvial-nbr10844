from __future__ import annotations

"""Pacote de dimensionamento de drenagem pluvial predial e urbana segundo a ABNT NBR 10844:1989.

Desenvolvido por LOFRANO TECNOLOGIA.
Aritmética 100% exata (Zero Float) com Frações e inteiros.
"""

__version__ = "1.0.0"
__author__ = "Martin Lofrano de Oliveira / LOFRANO TECNOLOGIA"
__license__ = "MIT"

from drenagem_pluvial_nbr10844.constants import (
    CIDADES_NBR10844,
    COEFICIENTES_MANNING,
    COEFICIENTES_ESCOAMENTO,
    TABELA_TUBOS_QUEDA_NBR10844,
    TABELA_CONDUTORES_HORIZONTAIS_NBR10844,
    DIAMETROS_INTERNOS_PVC_NBR10844,
)
from drenagem_pluvial_nbr10844.models import (
    DadosChuva,
    SuperficieContribuicao,
    ParedeVertical,
    Calha,
    CondutorVertical,
    CondutorHorizontal,
    Ralo,
    CaixaAreia,
    ProjetoDrenagem,
    ResultadoSuperficie,
    ResultadoCalha,
    ResultadoCondutorVertical,
    ResultadoCondutorHorizontal,
    ResultadoProjetoDrenagem,
)
from drenagem_pluvial_nbr10844.calculator import (
    raiz_quadrada_frac,
    raiz_cubica_frac,
    calcular_area_efetiva,
    calcular_vazao_racional,
    calcular_calha,
    verificar_condutor_vertical,
    calcular_condutor_horizontal,
    dimensionar_sistema,
)

__all__ = [
    "__version__",
    "CIDADES_NBR10844",
    "COEFICIENTES_MANNING",
    "COEFICIENTES_ESCOAMENTO",
    "TABELA_TUBOS_QUEDA_NBR10844",
    "TABELA_CONDUTORES_HORIZONTAIS_NBR10844",
    "DIAMETROS_INTERNOS_PVC_NBR10844",
    "DadosChuva",
    "SuperficieContribuicao",
    "ParedeVertical",
    "Calha",
    "CondutorVertical",
    "CondutorHorizontal",
    "Ralo",
    "CaixaAreia",
    "ProjetoDrenagem",
    "ResultadoSuperficie",
    "ResultadoCalha",
    "ResultadoCondutorVertical",
    "ResultadoCondutorHorizontal",
    "ResultadoProjetoDrenagem",
    "raiz_quadrada_frac",
    "raiz_cubica_frac",
    "calcular_area_efetiva",
    "calcular_vazao_racional",
    "calcular_calha",
    "verificar_condutor_vertical",
    "calcular_condutor_horizontal",
    "dimensionar_sistema",
]

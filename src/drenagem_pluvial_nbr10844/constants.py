from __future__ import annotations

from fractions import Fraction
from typing import Dict, Any

# Aproximação racional exata de Pi (convergente de Zu Chongzhi - erro < 3e-7)
PI_FRAC = Fraction(355, 113)

# Declividades mínimas normativas (NBR 10844 item 5.1.4 e 5.3.2)
DECLIVIDADE_MINIMA_CALHA = Fraction(5, 1000)        # 0,5%
DECLIVIDADE_MINIMA_CONDUTOR_HORIZ = Fraction(5, 1000) # 0,5%

# Relação máxima admissível de lâmina de água em condutores horizontais (NBR 10844 item 5.3.3)
RELACAO_LAMINA_MAX_CONDUTOR_HORIZ = Fraction(2, 3)    # h/D <= 0,67

# Borda livre mínima percentual para calhas
BORDA_LIVRE_MINIMA_PERC = Fraction(20, 100)          # 20%
BORDA_LIVRE_MINIMA_ABS_MM = 20                        # 20 mm

# Tabela de Chuvas da ABNT NBR 10844:1989 (Anexo A e Tabela 1)
# Intensidades I em mm/h para duração t = 5 min e períodos de retorno T = 1, 5 e 25 anos.
# Valores representados exatamente como inteiros / Fraction.
CIDADES_NBR10844: Dict[str, Dict[str, Any]] = {
    "sao_paulo": {
        "nome": "São Paulo",
        "uf": "SP",
        "intensidades": {
            1: Fraction(117, 1),
            5: Fraction(159, 1),
            25: Fraction(207, 1),
        },
    },
    "rio_de_janeiro": {
        "nome": "Rio de Janeiro",
        "uf": "RJ",
        "intensidades": {
            1: Fraction(126, 1),
            5: Fraction(174, 1),
            25: Fraction(228, 1),
        },
    },
    "belo_horizonte": {
        "nome": "Belo Horizonte",
        "uf": "MG",
        "intensidades": {
            1: Fraction(114, 1),
            5: Fraction(156, 1),
            25: Fraction(204, 1),
        },
    },
    "brasilia": {
        "nome": "Brasília",
        "uf": "DF",
        "intensidades": {
            1: Fraction(110, 1),
            5: Fraction(150, 1),
            25: Fraction(198, 1),
        },
    },
    "curitiba": {
        "nome": "Curitiba",
        "uf": "PR",
        "intensidades": {
            1: Fraction(108, 1),
            5: Fraction(144, 1),
            25: Fraction(186, 1),
        },
    },
    "porto_alegre": {
        "nome": "Porto Alegre",
        "uf": "RS",
        "intensidades": {
            1: Fraction(112, 1),
            5: Fraction(150, 1),
            25: Fraction(195, 1),
        },
    },
    "salvador": {
        "nome": "Salvador",
        "uf": "BA",
        "intensidades": {
            1: Fraction(120, 1),
            5: Fraction(162, 1),
            25: Fraction(210, 1),
        },
    },
    "recife": {
        "nome": "Recife",
        "uf": "PE",
        "intensidades": {
            1: Fraction(120, 1),
            5: Fraction(160, 1),
            25: Fraction(210, 1),
        },
    },
    "fortaleza": {
        "nome": "Fortaleza",
        "uf": "CE",
        "intensidades": {
            1: Fraction(115, 1),
            5: Fraction(155, 1),
            25: Fraction(200, 1),
        },
    },
    "belem": {
        "nome": "Belém",
        "uf": "PA",
        "intensidades": {
            1: Fraction(132, 1),
            5: Fraction(180, 1),
            25: Fraction(234, 1),
        },
    },
    "manaus": {
        "nome": "Manaus",
        "uf": "AM",
        "intensidades": {
            1: Fraction(135, 1),
            5: Fraction(186, 1),
            25: Fraction(240, 1),
        },
    },
    "florianopolis": {
        "nome": "Florianópolis",
        "uf": "SC",
        "intensidades": {
            1: Fraction(118, 1),
            5: Fraction(158, 1),
            25: Fraction(205, 1),
        },
    },
    "goiania": {
        "nome": "Goiânia",
        "uf": "GO",
        "intensidades": {
            1: Fraction(115, 1),
            5: Fraction(156, 1),
            25: Fraction(205, 1),
        },
    },
    "vitoria": {
        "nome": "Vitória",
        "uf": "ES",
        "intensidades": {
            1: Fraction(122, 1),
            5: Fraction(168, 1),
            25: Fraction(218, 1),
        },
    },
    "cuiaba": {
        "nome": "Cuiabá",
        "uf": "MT",
        "intensidades": {
            1: Fraction(120, 1),
            5: Fraction(164, 1),
            25: Fraction(214, 1),
        },
    },
    "campo_grande": {
        "nome": "Campo Grande",
        "uf": "MS",
        "intensidades": {
            1: Fraction(114, 1),
            5: Fraction(154, 1),
            25: Fraction(202, 1),
        },
    },
    "natal": {
        "nome": "Natal",
        "uf": "RN",
        "intensidades": {
            1: Fraction(116, 1),
            5: Fraction(158, 1),
            25: Fraction(206, 1),
        },
    },
    "campinas": {
        "nome": "Campinas",
        "uf": "SP",
        "intensidades": {
            1: Fraction(118, 1),
            5: Fraction(160, 1),
            25: Fraction(210, 1),
        },
    },
    "santos": {
        "nome": "Santos",
        "uf": "SP",
        "intensidades": {
            1: Fraction(130, 1),
            5: Fraction(178, 1),
            25: Fraction(232, 1),
        },
    },
    "ribeirao_preto": {
        "nome": "Ribeirão Preto",
        "uf": "SP",
        "intensidades": {
            1: Fraction(116, 1),
            5: Fraction(158, 1),
            25: Fraction(206, 1),
        },
    },
}

# Coeficientes de Rugosidade de Manning (n)
COEFICIENTES_MANNING: Dict[str, Fraction] = {
    "pvc": Fraction(11, 1000),             # 0,011 - Tubos e calhas plásticas de PVC
    "plastico": Fraction(11, 1000),        # 0,011
    "aco_galvanizado": Fraction(13, 1000), # 0,013 - Chapas de aço galvanizado
    "aluminio": Fraction(12, 1000),        # 0,012 - Chapas de alumínio
    "cobre": Fraction(12, 1000),           # 0,012 - Chapas de cobre
    "fibrocimento": Fraction(14, 1000),    # 0,014 - Tubos e calhas de fibrocimento
    "concreto_alisado": Fraction(15, 1000),# 0,015 - Canaletas e tubos de concreto alisado
    "alvenaria_rebocada": Fraction(16, 1000), # 0,016 - Alvenaria revestida com argamassa
}

# Coeficientes de Escoamento Superficial (Runoff C)
COEFICIENTES_ESCOAMENTO: Dict[str, Fraction] = {
    "cobertura_metalica": Fraction(1, 1),      # 1,00 - Telhas de aço / alumínio
    "telha_ceramica": Fraction(1, 1),          # 1,00 - Telhas cerâmicas esmaltadas/comuns
    "telha_fibrocimento": Fraction(1, 1),      # 1,00 - Telhas onduladas
    "laje_impermeabilizada": Fraction(1, 1),   # 1,00 - Lajes planas com manta impermeável
    "pavimento_concreto": Fraction(90, 100),   # 0,90 - Pavimentos rígidos de concreto
    "pavimento_asfalto": Fraction(85, 100),    # 0,85 - Vias e pátios asfálticos
    "paralelepipedo": Fraction(65, 100),       # 0,65 - Pavimento em pedra com rejunte
    "brita_pedra": Fraction(40, 100),          # 0,40 - Áreas cobertas com cascalho/brita
    "jardim_gramado": Fraction(25, 100),       # 0,25 - Solo vegetal e gramados
}

# Tabela 4 da NBR 10844:1989
# Capacidade máxima de escoamento de condutores verticais (tubos de queda) em L/min
# em função do Diâmetro Nominal (DN em mm) e do tipo de bocal de entrada.
TABELA_TUBOS_QUEDA_NBR10844: Dict[int, Dict[str, int]] = {
    75: {
        "reto": 270,      # Saída cilíndrica simples
        "funil": 470,     # Bocal cônico com funil de transição
    },
    100: {
        "reto": 540,
        "funil": 1060,
    },
    125: {
        "reto": 950,
        "funil": 1950,
    },
    150: {
        "reto": 1500,
        "funil": 3250,
    },
    200: {
        "reto": 3000,
        "funil": 7000,
    },
}

# Tabela 5 da NBR 10844:1989
# Capacidade máxima de escoamento de condutores horizontais de PVC (n = 0,011) em L/min,
# operando com lâmina d'água máxima de 2/3 (h/D = 0,67), em função do DN e da declividade (i).
# Chave externa: DN (mm). Chave interna: declividade percentual (como Fraction(num, den) ou float/int convertido).
TABELA_CONDUTORES_HORIZONTAIS_NBR10844: Dict[int, Dict[Fraction, int]] = {
    75: {
        Fraction(5, 1000): 95,     # 0,5%
        Fraction(1, 100): 135,     # 1,0%
        Fraction(15, 1000): 165,   # 1,5%
        Fraction(2, 100): 190,     # 2,0%
        Fraction(3, 100): 235,     # 3,0%
        Fraction(4, 100): 270,     # 4,0%
    },
    100: {
        Fraction(5, 1000): 215,
        Fraction(1, 100): 305,
        Fraction(15, 1000): 375,
        Fraction(2, 100): 435,
        Fraction(3, 100): 535,
        Fraction(4, 100): 615,
    },
    125: {
        Fraction(5, 1000): 390,
        Fraction(1, 100): 555,
        Fraction(15, 1000): 680,
        Fraction(2, 100): 785,
        Fraction(3, 100): 965,
        Fraction(4, 100): 1115,
    },
    150: {
        Fraction(5, 1000): 640,
        Fraction(1, 100): 905,
        Fraction(15, 1000): 1110,
        Fraction(2, 100): 1285,
        Fraction(3, 100): 1575,
        Fraction(4, 100): 1820,
    },
    200: {
        Fraction(5, 1000): 1365,
        Fraction(1, 100): 1935,
        Fraction(15, 1000): 2370,
        Fraction(2, 100): 2735,
        Fraction(3, 100): 3350,
        Fraction(4, 100): 3870,
    },
    250: {
        Fraction(5, 1000): 2450,
        Fraction(1, 100): 3470,
        Fraction(15, 1000): 4250,
        Fraction(2, 100): 4910,
        Fraction(3, 100): 6010,
        Fraction(4, 100): 6940,
    },
    300: {
        Fraction(5, 1000): 3950,
        Fraction(1, 100): 5590,
        Fraction(15, 1000): 6850,
        Fraction(2, 100): 7910,
        Fraction(3, 100): 9680,
        Fraction(4, 100): 11180,
    },
}

# Diâmetros internos de referência (em mm) para tubulações de PVC predial
DIAMETROS_INTERNOS_PVC_NBR10844: Dict[int, Fraction] = {
    75: Fraction(704, 10),    # 70,4 mm
    100: Fraction(956, 10),   # 95,6 mm
    125: Fraction(120, 1),    # 120,0 mm
    150: Fraction(1442, 10),  # 144,2 mm
    200: Fraction(1924, 10),  # 192,4 mm
    250: Fraction(240, 1),    # 240,0 mm
    300: Fraction(288, 1),    # 288,0 mm
}

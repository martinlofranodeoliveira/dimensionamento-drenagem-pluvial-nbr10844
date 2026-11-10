from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional, Tuple, List, Dict, Any

from drenagem_pluvial_nbr10844.constants import (
    PI_FRAC,
    DECLIVIDADE_MINIMA_CALHA,
    DECLIVIDADE_MINIMA_CONDUTOR_HORIZ,
    RELACAO_LAMINA_MAX_CONDUTOR_HORIZ,
    BORDA_LIVRE_MINIMA_PERC,
    BORDA_LIVRE_MINIMA_ABS_MM,
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
    ResultadoCaixaAreia,
    ResultadoProjetoDrenagem,
)


def icbrt(n: int) -> int:
    """Calcula a raiz cúbica inteira (piso) exata de um inteiro não-negativo.
    
    Utiliza o método de Newton inteiro com aproximação inicial baseada em deslocamento de bits.
    Zero ponto flutuante (Zero Float).
    """
    if n < 0:
        return -icbrt(-n)
    if n == 0:
        return 0
    # Estimativa inicial superior segura
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        x_next = (2 * x + n // (x * x)) // 3
        if x_next >= x:
            return x
        x = x_next


def raiz_quadrada_frac(f: Fraction, escala_decimais: int = 12) -> Fraction:
    """Calcula a raiz quadrada de uma fração com precisão decimal exata especificada.
    
    sqrt(p / q) = isqrt(p * q * 10^(2k)) / (q * 10^k)
    Aritmética inteira pura (Zero Float).
    """
    if f < 0:
        raise ValueError(f"Raiz quadrada de número negativo não permitida: {f}")
    if f == 0:
        return Fraction(0, 1)
    
    p = f.numerator
    q = f.denominator
    fator = 10 ** (2 * escala_decimais)
    r = math.isqrt(p * q * fator)
    return Fraction(r, q * (10 ** escala_decimais))


def raiz_cubica_frac(f: Fraction, escala_decimais: int = 12) -> Fraction:
    """Calcula a raiz cúbica de uma fração com precisão decimal exata especificada.
    
    cbrt(p / q) = icbrt(p * q^2 * 10^(3k)) / (q * 10^k)
    Aritmética inteira pura (Zero Float).
    """
    if f < 0:
        return -raiz_cubica_frac(-f, escala_decimais)
    if f == 0:
        return Fraction(0, 1)
    
    p = f.numerator
    q = f.denominator
    fator = 10 ** (3 * escala_decimais)
    r = icbrt(p * (q ** 2) * fator)
    return Fraction(r, q * (10 ** escala_decimais))


def obter_intensidade_cidade(
    chave_cidade: str, periodo_retorno: int = 5
) -> Fraction:
    """Obtém a intensidade de chuva em mm/h para uma cidade cadastrada e período de retorno."""
    chave = chave_cidade.strip().lower().replace(" ", "_")
    if chave not in CIDADES_NBR10844:
        raise KeyError(
            f"Cidade '{chave_cidade}' não cadastrada. Cidades disponíveis: {', '.join(sorted(CIDADES_NBR10844.keys()))}"
        )
    intensidades = CIDADES_NBR10844[chave]["intensidades"]
    if periodo_retorno not in intensidades:
        raise ValueError(
            f"Período de retorno {periodo_retorno} anos não disponível. Permitidos: {list(intensidades.keys())}"
        )
    return intensidades[periodo_retorno]


def calcular_area_efetiva(superficie: SuperficieContribuicao) -> Tuple[Fraction, Fraction, Fraction]:
    """Calcula a área de contribuição efetiva conforme NBR 10844 item 5.1.2.
    
    Retorna: (area_horizontal_m2, area_paredes_efetiva_m2, area_efetiva_total_m2)
    Para cada parede vertical exposta, contribui com metade da sua área: A_parede / 2.
    """
    area_h = superficie.area_horizontal_m2
    area_paredes_efetiva = Fraction(0, 1)
    for p in superficie.paredes:
        area_paredes_efetiva += p.area_m2 / Fraction(2, 1)
    
    area_efetiva = area_h + area_paredes_efetiva
    return area_h, area_paredes_efetiva, area_efetiva


def calcular_vazao_racional(
    area_efetiva_m2: Fraction,
    intensidade_mm_h: Fraction,
    coeficiente_escoamento: Fraction = Fraction(1, 1),
) -> Tuple[Fraction, Fraction]:
    """Calcula a vazão de projeto pelo Método Racional (NBR 10844 item 5.1.1).
    
    Q = (C * I * A) / 60  (L/min)
    onde:
      C = coeficiente de escoamento superficial (adimensional)
      I = intensidade pluviométrica (mm/h)
      A = área de contribuição (m²)
    
    Retorna: (vazao_L_min, vazao_L_s)
    """
    vazao_L_min = (coeficiente_escoamento * intensidade_mm_h * area_efetiva_m2) / Fraction(60, 1)
    vazao_L_s = vazao_L_min / Fraction(60, 1)
    return vazao_L_min, vazao_L_s


def resolver_manning_calha(
    area_molhada_m2: Fraction,
    perimetro_molhado_m: Fraction,
    declividade_m_m: Fraction,
    coeficiente_manning: Fraction,
) -> Tuple[Fraction, Fraction, Fraction]:
    """Aplica a equação de Manning-Strickler para condutos livres (calhas).
    
    Q = (60.000 / n) * S * (Rh)^(2/3) * (i)^(1/2)  [L/min]
    v = (1 / n) * (Rh)^(2/3) * (i)^(1/2)           [m/s]
    
    Retorna: (vazao_admissivel_L_min, raio_hidraulico_m, velocidade_m_s)
    """
    if perimetro_molhado_m <= 0 or area_molhada_m2 <= 0:
        return Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)
    
    raio_hidraulico = area_molhada_m2 / perimetro_molhado_m
    # Rh^(2/3) = cbrt(Rh^2)
    rh_23 = raiz_cubica_frac(raio_hidraulico * raio_hidraulico)
    # i^(1/2) = sqrt(i)
    i_12 = raiz_quadrada_frac(declividade_m_m)
    
    # Velocidade v em m/s
    velocidade = (rh_23 * i_12) / coeficiente_manning
    # Vazão em m³/s = v * S
    vazao_m3_s = velocidade * area_molhada_m2
    # Vazão em L/min = vazao_m3_s * 60000
    vazao_L_min = vazao_m3_s * Fraction(60000, 1)
    
    return vazao_L_min, raio_hidraulico, velocidade


def calcular_calha(
    calha: Calha,
    vazao_projeto_L_min: Fraction,
) -> ResultadoCalha:
    """Dimensiona e verifica uma calha segundo NBR 10844."""
    # Obter coeficiente de Manning do material
    mat_chave = calha.material.strip().lower()
    coef_manning = COEFICIENTES_MANNING.get(mat_chave, Fraction(11, 1000))
    
    # Dimensões em metros
    b_fundo_m = calha.largura_fundo_mm / Fraction(1000, 1)
    b_topo_m = calha.largura_topo_mm / Fraction(1000, 1)
    h_total_m = calha.altura_total_mm / Fraction(1000, 1)
    
    # Borda livre mínima normativa: max(20% da altura total, 20 mm)
    borda_livre_min_m = max(
        h_total_m * BORDA_LIVRE_MINIMA_PERC,
        Fraction(BORDA_LIVRE_MINIMA_ABS_MM, 1000)
    )
    
    # Lâmina d'água adotada
    if calha.lamina_dagua_mm is not None:
        lamina_m = calha.lamina_dagua_mm / Fraction(1000, 1)
    else:
        # Se não informada, adota a lâmina máxima respeitando a borda livre mínima
        lamina_m = h_total_m - borda_livre_min_m
        if lamina_m <= 0:
            lamina_m = h_total_m / Fraction(2, 1)
    
    borda_livre_efetiva_m = h_total_m - lamina_m
    borda_livre_efetiva_mm = borda_livre_efetiva_m * Fraction(1000, 1)
    borda_livre_perc = (borda_livre_efetiva_m / h_total_m) * Fraction(100, 1)
    
    # Geometria da seção molhada
    if calha.tipo_secao == "retangular":
        area_molhada_m2 = b_fundo_m * lamina_m
        perimetro_molhado_m = b_fundo_m + Fraction(2, 1) * lamina_m
    elif calha.tipo_secao == "semicircular":
        # Calha meia-cana: D = b_fundo_m (diâmetro), r = D/2
        r = b_fundo_m / Fraction(2, 1)
        # Se cheia até o semi-círculo completo (lamina = r)
        # S = (pi * r^2) / 2
        # P = pi * r
        # Para lâmina genérica proporcional:
        fator_lamina = lamina_m / r if r > 0 else Fraction(1, 1)
        if fator_lamina >= 1:
            area_molhada_m2 = (PI_FRAC * (r ** 2)) / Fraction(2, 1)
            perimetro_molhado_m = PI_FRAC * r
        else:
            # Aproximação de segmento circular proporcional
            area_molhada_m2 = ((PI_FRAC * (r ** 2)) / Fraction(2, 1)) * fator_lamina
            perimetro_molhado_m = (PI_FRAC * r) * raiz_quadrada_frac(fator_lamina)
    elif calha.tipo_secao == "trapezoidal":
        # Largura da superfície na lâmina h
        if h_total_m > 0:
            b_lamina_m = b_fundo_m + (b_topo_m - b_fundo_m) * (lamina_m / h_total_m)
        else:
            b_lamina_m = b_fundo_m
        area_molhada_m2 = ((b_fundo_m + b_lamina_m) / Fraction(2, 1)) * lamina_m
        cateto_horiz = (b_lamina_m - b_fundo_m) / Fraction(2, 1)
        hipotenusa = raiz_quadrada_frac(lamina_m * lamina_m + cateto_horiz * cateto_horiz)
        perimetro_molhado_m = b_fundo_m + Fraction(2, 1) * hipotenusa
    else:
        raise ValueError(f"Tipo de seção '{calha.tipo_secao}' não suportado.")
    
    # Resolução de Manning
    vazao_adm_L_min, raio_hidraulico_m, velocidade_m_s = resolver_manning_calha(
        area_molhada_m2=area_molhada_m2,
        perimetro_molhado_m=perimetro_molhado_m,
        declividade_m_m=calha.declividade_m_m,
        coeficiente_manning=coef_manning,
    )
    
    # Verificações normativas
    atende_declividade = calha.declividade_m_m >= DECLIVIDADE_MINIMA_CALHA
    atende_capacidade = vazao_adm_L_min >= vazao_projeto_L_min
    atende_borda_livre = (
        borda_livre_efetiva_m >= borda_livre_min_m
        and borda_livre_efetiva_mm >= Fraction(BORDA_LIVRE_MINIMA_ABS_MM, 1)
    )
    atende_norma = atende_declividade and atende_capacidade and atende_borda_livre
    
    taxa_ocupacao = (
        vazao_projeto_L_min / vazao_adm_L_min if vazao_adm_L_min > 0 else Fraction(999, 1)
    )
    
    obs: List[str] = []
    if not atende_declividade:
        obs.append(
            f"Declividade ({calha.declividade_m_m * 100:.2f}%) inferior ao mínimo normativo de 0,50% (NBR 10844 item 5.1.4)."
        )
    if not atende_capacidade:
        obs.append(
            f"Vazão de projeto ({vazao_projeto_L_min:.1f} L/min) excede a capacidade da calha ({vazao_adm_L_min:.1f} L/min)."
        )
    if not atende_borda_livre:
        obs.append(
            f"Borda livre ({borda_livre_efetiva_mm:.1f} mm) inferior ao mínimo recomendado de 20 mm / 20% da altura."
        )
    if atende_norma:
        obs.append("Calha dimensionada com plena conformidade à ABNT NBR 10844:1989.")
    
    return ResultadoCalha(
        tipo_secao=calha.tipo_secao,
        largura_mm=calha.largura_fundo_mm,
        altura_total_mm=calha.altura_total_mm,
        lamina_dagua_mm=lamina_m * Fraction(1000, 1),
        borda_livre_mm=borda_livre_efetiva_mm,
        borda_livre_perc=borda_livre_perc,
        area_molhada_m2=area_molhada_m2,
        perimetro_molhado_m=perimetro_molhado_m,
        raio_hidraulico_m=raio_hidraulico_m,
        declividade_m_m=calha.declividade_m_m,
        vazao_admissivel_L_min=vazao_adm_L_min,
        vazao_projeto_L_min=vazao_projeto_L_min,
        taxa_ocupacao_vazao=taxa_ocupacao,
        velocidade_escoamento_m_s=velocidade_m_s,
        atende_capacidade=atende_capacidade,
        atende_declividade=atende_declividade,
        atende_borda_livre=atende_borda_livre,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def verificar_condutor_vertical(
    condutor: CondutorVertical,
    vazao_projeto_L_min: Fraction,
) -> ResultadoCondutorVertical:
    """Verifica um condutor vertical (tubo de queda) segundo Tabela 4 da NBR 10844."""
    dn = condutor.dn_mm
    bocal = condutor.tipo_bocal.strip().lower()
    
    if dn not in TABELA_TUBOS_QUEDA_NBR10844:
        raise ValueError(f"DN {dn} não cadastrado na Tabela 4 da NBR 10844.")
    
    dados_dn = TABELA_TUBOS_QUEDA_NBR10844[dn]
    if bocal not in dados_dn:
        raise ValueError(f"Tipo de bocal '{bocal}' não suportado. Permitidos: 'reto', 'funil'.")
    
    capacidade_tabela_int = dados_dn[bocal]
    capacidade_admissivel = Fraction(capacidade_tabela_int, 1)
    
    atende_norma = capacidade_admissivel >= vazao_projeto_L_min
    taxa_ocupacao = (
        vazao_projeto_L_min / capacidade_admissivel if capacidade_admissivel > 0 else Fraction(999, 1)
    )
    
    obs: List[str] = []
    if not atende_norma:
        obs.append(
            f"Vazão de projeto ({vazao_projeto_L_min:.1f} L/min) excede a capacidade do tubo de queda DN {dn} com bocal {bocal} ({capacidade_admissivel:.1f} L/min)."
        )
    else:
        obs.append(
            f"Condutor vertical DN {dn} (bocal {bocal}) atende à NBR 10844 com taxa de ocupação de {taxa_ocupacao * 100:.1f}%."
        )
    
    return ResultadoCondutorVertical(
        dn_mm=dn,
        tipo_bocal=bocal,
        capacidade_admissivel_L_min=capacidade_admissivel,
        vazao_projeto_L_min=vazao_projeto_L_min,
        taxa_ocupacao_vazao=taxa_ocupacao,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def obter_capacidade_condutor_horizontal_tabela(
    dn: int, declividade_m_m: Fraction
) -> Optional[Fraction]:
    """Busca a capacidade na Tabela 5 da NBR 10844 (PVC, n=0.011, h/D=0.67) com interpolação exata se necessário."""
    if dn not in TABELA_CONDUTORES_HORIZONTAIS_NBR10844:
        return None
    
    tabela_dn = TABELA_CONDUTORES_HORIZONTAIS_NBR10844[dn]
    
    # Se valor exato existir
    if declividade_m_m in tabela_dn:
        return Fraction(tabela_dn[declividade_m_m], 1)
    
    # Declividades ordenadas
    decls = sorted(tabela_dn.keys())
    
    # Se fora dos limites
    if declividade_m_m < decls[0]:
        # Abaixo de 0,5%
        return None
    if declividade_m_m > decls[-1]:
        # Acima de 4,0%: escala proporcional pela raiz da declividade
        # Q = Q_max * sqrt(i / i_max)
        i_max = decls[-1]
        q_max = Fraction(tabela_dn[i_max], 1)
        fator = raiz_quadrada_frac(declividade_m_m / i_max)
        return q_max * fator
    
    # Interpolação linear racional entre dois pontos adjacentes
    for k in range(len(decls) - 1):
        i1 = decls[k]
        i2 = decls[k + 1]
        if i1 <= declividade_m_m <= i2:
            q1 = Fraction(tabela_dn[i1], 1)
            q2 = Fraction(tabela_dn[i2], 1)
            # q = q1 + (declividade - i1) * (q2 - q1) / (i2 - i1)
            return q1 + (declividade_m_m - i1) * (q2 - q1) / (i2 - i1)
    
    return None


def calcular_condutor_horizontal_manning(
    dn: int,
    declividade_m_m: Fraction,
    coeficiente_manning: Fraction = Fraction(11, 1000),
    relacao_lamina_max: Fraction = Fraction(2, 3),
) -> Fraction:
    """Calcula a capacidade contínua de condutor circular por Manning-Strickler com h/D <= 2/3."""
    # Obter diâmetro interno em metros
    d_int_mm = DIAMETROS_INTERNOS_PVC_NBR10844.get(dn, Fraction(dn, 1))
    d_m = d_int_mm / Fraction(1000, 1)
    
    # Para h/D = 2/3 (0,67):
    # Coeficientes geométricos da seção circular parcialmente cheia
    # S = 0.5563 * D^2, P = 2.1865 * D, Rh = 0.2544 * D
    cs = Fraction(5563, 10000)
    cp = Fraction(21865, 10000)
    
    s = cs * (d_m ** 2)
    p = cp * d_m
    rh = s / p
    
    rh_23 = raiz_cubica_frac(rh * rh)
    i_12 = raiz_quadrada_frac(declividade_m_m)
    
    # Vazão em L/min = (60.000 / n) * S * Rh^(2/3) * i^(1/2)
    q_l_min = (Fraction(60000, 1) / coeficiente_manning) * s * rh_23 * i_12
    return q_l_min


def calcular_condutor_horizontal(
    condutor: CondutorHorizontal,
    vazao_projeto_L_min: Fraction,
) -> ResultadoCondutorHorizontal:
    """Dimensiona e verifica condutor horizontal conforme NBR 10844."""
    dn = condutor.dn_mm
    declividade = condutor.declividade_m_m
    mat_chave = condutor.material.strip().lower()
    coef_manning = COEFICIENTES_MANNING.get(mat_chave, Fraction(11, 1000))
    
    cap_tabela = obter_capacidade_condutor_horizontal_tabela(dn, declividade)
    cap_manning = calcular_condutor_horizontal_manning(
        dn=dn,
        declividade_m_m=declividade,
        coeficiente_manning=coef_manning,
        relacao_lamina_max=condutor.relacao_lamina_max,
    )
    
    # Capacidade normativa adotada: prioriza a Tabela 5 oficial se disponível
    capacidade_governante = cap_tabela if cap_tabela is not None else cap_manning
    
    atende_declividade = declividade >= DECLIVIDADE_MINIMA_CONDUTOR_HORIZ
    atende_capacidade = capacidade_governante >= vazao_projeto_L_min
    atende_norma = atende_declividade and atende_capacidade
    
    taxa_ocupacao = (
        vazao_projeto_L_min / capacidade_governante if capacidade_governante > 0 else Fraction(999, 1)
    )
    
    obs: List[str] = []
    if not atende_declividade:
        obs.append(
            f"Declividade ({declividade * 100:.2f}%) inferior ao mínimo normativo de 0,50% (NBR 10844 item 5.3.2)."
        )
    if not atende_capacidade:
        obs.append(
            f"Vazão de projeto ({vazao_projeto_L_min:.1f} L/min) excede a capacidade do condutor horizontal DN {dn} ({capacidade_governante:.1f} L/min)."
        )
    if atende_norma:
        obs.append(
            f"Condutor horizontal DN {dn} com declividade de {declividade * 100:.2f}% atende à NBR 10844 com taxa de ocupação de {taxa_ocupacao * 100:.1f}%."
        )
    
    return ResultadoCondutorHorizontal(
        dn_mm=dn,
        declividade_m_m=declividade,
        capacidade_tabela_L_min=cap_tabela if cap_tabela is not None else Fraction(0, 1),
        capacidade_manning_L_min=cap_manning,
        vazao_projeto_L_min=vazao_projeto_L_min,
        taxa_ocupacao_vazao=taxa_ocupacao,
        relacao_lamina_max=condutor.relacao_lamina_max,
        atende_declividade=atende_declividade,
        atende_capacidade=atende_capacidade,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def verificar_caixa_areia(caixa: CaixaAreia) -> ResultadoCaixaAreia:
    """Verifica as dimensões da caixa de areia e sedimentação conforme NBR 10844 item 5.4."""
    # Altura de sedimentação mínima normativa: 200 mm (0,20 m)
    # Dimensões mínimas recomendadas em planta: 400 mm x 400 mm
    atende_dimensoes = caixa.largura_mm >= 400 and caixa.comprimento_mm >= 400
    atende_sedimentacao = caixa.altura_sedimentacao_mm >= 200
    atende_norma = atende_dimensoes and atende_sedimentacao
    
    # Volume de sedimentação em Litros
    vol_m3 = (
        Fraction(caixa.largura_mm, 1000)
        * Fraction(caixa.comprimento_mm, 1000)
        * Fraction(caixa.altura_sedimentacao_mm, 1000)
    )
    volume_sedimentacao_L = vol_m3 * Fraction(1000, 1)
    
    obs: List[str] = []
    if not atende_sedimentacao:
        obs.append(
            f"Altura livre de sedimentação ({caixa.altura_sedimentacao_mm} mm) inferior ao mínimo de 200 mm recomendado para retenção de areia."
        )
    if not atende_dimensoes:
        obs.append(
            f"Dimensões em planta ({caixa.largura_mm}x{caixa.comprimento_mm} mm) inferiores ao recomendado (400x400 mm) para inspeção e limpeza periódica."
        )
    if atende_norma:
        obs.append(
            f"Caixa de areia de {caixa.largura_mm}x{caixa.comprimento_mm} mm com câmara de sedimentação de {volume_sedimentacao_L:.1f} L conforme NBR 10844."
        )
    
    return ResultadoCaixaAreia(
        largura_mm=caixa.largura_mm,
        comprimento_mm=caixa.comprimento_mm,
        altura_util_mm=caixa.altura_util_mm,
        altura_sedimentacao_mm=caixa.altura_sedimentacao_mm,
        volume_sedimentacao_L=volume_sedimentacao_L,
        atende_norma=atende_norma,
        observacoes=obs,
    )


def dimensionar_sistema(projeto: ProjetoDrenagem) -> ResultadoProjetoDrenagem:
    """Realiza o dimensionamento e verificação completa de um sistema de drenagem pluvial."""
    # 1. Área de contribuição e Vazão de Projeto
    area_h, area_paredes, area_efetiva = calcular_area_efetiva(projeto.superficie)
    vazao_L_min, vazao_L_s = calcular_vazao_racional(
        area_efetiva_m2=area_efetiva,
        intensidade_mm_h=projeto.chuva.intensidade_mm_h,
        coeficiente_escoamento=projeto.superficie.coeficiente_escoamento,
    )
    
    resultado_superficie = ResultadoSuperficie(
        area_horizontal_m2=area_h,
        area_paredes_m2=area_paredes,
        area_efetiva_m2=area_efetiva,
        coeficiente_escoamento=projeto.superficie.coeficiente_escoamento,
        intensidade_mm_h=projeto.chuva.intensidade_mm_h,
        vazao_projeto_L_min=vazao_L_min,
        vazao_projeto_L_s=vazao_L_s,
    )
    
    # 2. Calha
    resultado_calha: Optional[ResultadoCalha] = None
    if projeto.calha is not None:
        resultado_calha = calcular_calha(projeto.calha, vazao_L_min)
    
    # 3. Condutor Vertical (Tubo de Queda)
    resultado_cv: Optional[ResultadoCondutorVertical] = None
    if projeto.condutor_vertical is not None:
        resultado_cv = verificar_condutor_vertical(projeto.condutor_vertical, vazao_L_min)
    
    # 4. Condutor Horizontal
    resultado_ch: Optional[ResultadoCondutorHorizontal] = None
    if projeto.condutor_horizontal is not None:
        resultado_ch = calcular_condutor_horizontal(projeto.condutor_horizontal, vazao_L_min)
    
    # 5. Caixa de Areia
    resultado_caixa: Optional[ResultadoCaixaAreia] = None
    if projeto.caixa_areia is not None:
        resultado_caixa = verificar_caixa_areia(projeto.caixa_areia)
    
    # Consolidação de conformidade geral
    conformidades: Dict[str, bool] = {
        "superficie": True,
    }
    alertas: List[str] = []
    recomendacoes: List[str] = []
    
    if resultado_calha is not None:
        conformidades["calha"] = resultado_calha.atende_norma
        if not resultado_calha.atende_norma:
            alertas.extend(resultado_calha.observacoes)
        if resultado_calha.taxa_ocupacao_vazao > Fraction(85, 100):
            recomendacoes.append(
                f"Calha operando com ocupação de {resultado_calha.taxa_ocupacao_vazao * 100:.1f}%. Recomenda-se prever extravasor (ladrão)."
            )
    
    if resultado_cv is not None:
        conformidades["condutor_vertical"] = resultado_cv.atende_norma
        if not resultado_cv.atende_norma:
            alertas.extend(resultado_cv.observacoes)
    
    if resultado_ch is not None:
        conformidades["condutor_horizontal"] = resultado_ch.atende_norma
        if not resultado_ch.atende_norma:
            alertas.extend(resultado_ch.observacoes)
    
    if resultado_caixa is not None:
        conformidades["caixa_areia"] = resultado_caixa.atende_norma
        if not resultado_caixa.atende_norma:
            alertas.extend(resultado_caixa.observacoes)
    
    # Ralo
    if projeto.ralo is not None:
        if projeto.ralo.tipo_ralo == "hemisferico":
            recomendacoes.append(
                "Ralo tipo hemisférico (pinha) adotado: excelente proteção contra entupimento por folhas e detritos carreados."
            )
        elif projeto.ralo.tipo_ralo == "plano":
            recomendacoes.append(
                "Ralo tipo plano adotado: deve ser inspecionado regularmente para evitar acúmulo superficial de detritos."
            )
    
    atende_geral = all(conformidades.values())
    if atende_geral and not alertas:
        recomendacoes.append(
            "Sistema predial de águas pluviais integralmente aprovado segundo os critérios da ABNT NBR 10844:1989."
        )
    
    return ResultadoProjetoDrenagem(
        identificacao=projeto.identificacao,
        norma="ABNT NBR 10844:1989",
        chuva=projeto.chuva,
        resultado_superficie=resultado_superficie,
        resultado_calha=resultado_calha,
        resultado_condutor_vertical=resultado_cv,
        resultado_condutor_horizontal=resultado_ch,
        resultado_caixa_areia=resultado_caixa,
        atende_geral=atende_geral,
        conformidades=conformidades,
        alertas=alertas,
        recomendacoes=recomendacoes,
    )

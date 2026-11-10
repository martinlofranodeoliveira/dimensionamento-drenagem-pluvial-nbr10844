from __future__ import annotations

import csv
import io
from fractions import Fraction
from typing import Any, List

from drenagem_pluvial_nbr10844.models import ResultadoProjetoDrenagem

CARACTERES_INJECAO_CSV = ("=", "+", "-", "@", "\t", "\r")


def sanitizar_campo_csv(valor: Any) -> str:
    """Sanitiza campos contra injeção de fórmulas CSV mantendo integridade."""
    texto = str(valor)
    if texto.startswith(CARACTERES_INJECAO_CSV):
        return "'" + texto
    return texto


def formatar_fracao_decimal(f: Fraction, casas: int = 2) -> str:
    """Converte fração em representação decimal exata com vírgula padrão pt-BR."""
    if f.denominator == 1:
        return str(f.numerator)
    # Arredondamento determinístico via inteiros
    fator = 10 ** casas
    val_inteiro = round((f.numerator * fator) / f.denominator)
    sinal = "-" if val_inteiro < 0 else ""
    val_abs = abs(val_inteiro)
    parte_int = val_abs // fator
    parte_dec = str(val_abs % fator).zfill(casas)
    return f"{sinal}{parte_int},{parte_dec}"


def exportar_csv(resultado: ResultadoProjetoDrenagem) -> str:
    """Exporta planilha técnica em formato CSV com proteção contra injeção de fórmulas."""
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    
    # Cabeçalho
    escritor.writerow([
        sanitizar_campo_csv("Componente"),
        sanitizar_campo_csv("Identificação"),
        sanitizar_campo_csv("Parâmetro de Projeto"),
        sanitizar_campo_csv("Valor de Projeto"),
        sanitizar_campo_csv("Capacidade Admissível"),
        sanitizar_campo_csv("Vazão de Projeto (L/min)"),
        sanitizar_campo_csv("Taxa de Ocupação (%)"),
        sanitizar_campo_csv("Conformidade NBR 10844"),
    ])
    
    # Superfície
    rs = resultado.resultado_superficie
    escritor.writerow([
        sanitizar_campo_csv("Superfície"),
        sanitizar_campo_csv("Bacia de Cobertura"),
        sanitizar_campo_csv(f"Área Efetiva (Ah={formatar_fracao_decimal(rs.area_horizontal_m2)} m², Ap={formatar_fracao_decimal(rs.area_paredes_m2)} m²)"),
        sanitizar_campo_csv(f"{formatar_fracao_decimal(rs.area_efetiva_m2)} m²"),
        sanitizar_campo_csv("-"),
        sanitizar_campo_csv(formatar_fracao_decimal(rs.vazao_projeto_L_min, 1)),
        sanitizar_campo_csv("100,00"),
        sanitizar_campo_csv("CONFORME"),
    ])
    
    # Calha
    if resultado.resultado_calha is not None:
        rc = resultado.resultado_calha
        escritor.writerow([
            sanitizar_campo_csv("Calha"),
            sanitizar_campo_csv(f"Seção {rc.tipo_secao.capitalize()}"),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rc.largura_mm, 0)}x{formatar_fracao_decimal(rc.altura_total_mm, 0)} mm, i={formatar_fracao_decimal(rc.declividade_m_m * 100, 2)}%"),
            sanitizar_campo_csv(f"Lâmina: {formatar_fracao_decimal(rc.lamina_dagua_mm, 1)} mm | Borda: {formatar_fracao_decimal(rc.borda_livre_mm, 1)} mm"),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rc.vazao_admissivel_L_min, 1)} L/min"),
            sanitizar_campo_csv(formatar_fracao_decimal(rc.vazao_projeto_L_min, 1)),
            sanitizar_campo_csv(formatar_fracao_decimal(rc.taxa_ocupacao_vazao * 100, 2)),
            sanitizar_campo_csv("CONFORME" if rc.atende_norma else "NÃO CONFORME"),
        ])
    
    # Condutor Vertical
    if resultado.resultado_condutor_vertical is not None:
        rcv = resultado.resultado_condutor_vertical
        escritor.writerow([
            sanitizar_campo_csv("Condutor Vertical"),
            sanitizar_campo_csv(f"DN {rcv.dn_mm}"),
            sanitizar_campo_csv(f"Tubo de Queda (Bocal {rcv.tipo_bocal.capitalize()})"),
            sanitizar_campo_csv(f"DN {rcv.dn_mm} mm"),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rcv.capacidade_admissivel_L_min, 1)} L/min"),
            sanitizar_campo_csv(formatar_fracao_decimal(rcv.vazao_projeto_L_min, 1)),
            sanitizar_campo_csv(formatar_fracao_decimal(rcv.taxa_ocupacao_vazao * 100, 2)),
            sanitizar_campo_csv("CONFORME" if rcv.atende_norma else "NÃO CONFORME"),
        ])
    
    # Condutor Horizontal
    if resultado.resultado_condutor_horizontal is not None:
        rch = resultado.resultado_condutor_horizontal
        escritor.writerow([
            sanitizar_campo_csv("Condutor Horizontal"),
            sanitizar_campo_csv(f"DN {rch.dn_mm}"),
            sanitizar_campo_csv(f"Coletor Predial i={formatar_fracao_decimal(rch.declividade_m_m * 100, 2)}%"),
            sanitizar_campo_csv(f"DN {rch.dn_mm} mm (h/D <= 0,67)"),
            sanitizar_campo_csv(f"{formatar_fracao_decimal(rch.capacidade_tabela_L_min, 1)} L/min"),
            sanitizar_campo_csv(formatar_fracao_decimal(rch.vazao_projeto_L_min, 1)),
            sanitizar_campo_csv(formatar_fracao_decimal(rch.taxa_ocupacao_vazao * 100, 2)),
            sanitizar_campo_csv("CONFORME" if rch.atende_norma else "NÃO CONFORME"),
        ])
    
    # Caixa de Areia
    if resultado.resultado_caixa_areia is not None:
        rca = resultado.resultado_caixa_areia
        escritor.writerow([
            sanitizar_campo_csv("Caixa de Areia"),
            sanitizar_campo_csv("Dispositivo de Sedimentação"),
            sanitizar_campo_csv(f"Dimensões {rca.largura_mm}x{rca.comprimento_mm} mm | Fundo: {rca.altura_sedimentacao_mm} mm"),
            sanitizar_campo_csv(f"Volume: {formatar_fracao_decimal(rca.volume_sedimentacao_L, 1)} L"),
            sanitizar_campo_csv(">= 200 mm"),
            sanitizar_campo_csv("-"),
            sanitizar_campo_csv("-"),
            sanitizar_campo_csv("CONFORME" if rca.atende_norma else "NÃO CONFORME"),
        ])
    
    return saida.getvalue()


def gerar_relatorio_memorial(resultado: ResultadoProjetoDrenagem) -> str:
    """Gera o Memorial de Cálculo Técnico completo em texto puro formatado em pt-BR."""
    linhas: List[str] = []
    div = "=" * 80
    subdiv = "-" * 80
    
    linhas.append(div)
    linhas.append("          LOFRANO TECNOLOGIA - ENGENHARIA DE DRENAGEM PLUVIAL")
    linhas.append("            MEMORIAL DE CÁLCULO NORMATIVO - ABNT NBR 10844:1989")
    linhas.append(div)
    linhas.append(f"Projeto: {resultado.identificacao}")
    linhas.append(f"Norma Regulamentadora: {resultado.norma}")
    linhas.append(f"Status Geral de Aprovação: {'APROVADO' if resultado.atende_geral else 'COM RESTRIÇÕES / NÃO CONFORME'}")
    linhas.append(subdiv)
    
    # 1. Chuva
    c = resultado.chuva
    linhas.append("1. DADOS PLUVIOMÉTRICOS DE PROJETO")
    if c.cidade:
        linhas.append(f"  - Localidade: {c.cidade} / {c.uf}")
    linhas.append(f"  - Período de Retorno (T): {c.periodo_retorno_anos} anos")
    linhas.append(f"  - Duração da Chuva (t): {c.duracao_minutos} minutos")
    linhas.append(f"  - Intensidade Pluviométrica de Projeto (I): {formatar_fracao_decimal(c.intensidade_mm_h, 1)} mm/h")
    linhas.append("")
    
    # 2. Superfície e Vazão
    rs = resultado.resultado_superficie
    linhas.append("2. BACIA DE CONTRIBUIÇÃO E VAZÃO DE PROJETO (MÉTODO RACIONAL)")
    linhas.append(f"  - Área em Projeção Horizontal (Ah): {formatar_fracao_decimal(rs.area_horizontal_m2, 2)} m²")
    linhas.append(f"  - Acréscimo por Paredes Verticais Expostas (Ap/2): {formatar_fracao_decimal(rs.area_paredes_m2, 2)} m²")
    linhas.append(f"  - Área de Contribuição Efetiva (Ac = Ah + Ap/2): {formatar_fracao_decimal(rs.area_efetiva_m2, 2)} m²")
    linhas.append(f"  - Coeficiente de Escoamento Superficial (C): {formatar_fracao_decimal(rs.coeficiente_escoamento, 2)}")
    linhas.append(f"  - Vazão de Projeto Calculada: Q = (C * I * Ac) / 60")
    linhas.append(f"    * Q = {formatar_fracao_decimal(rs.vazao_projeto_L_min, 2)} L/min ({formatar_fracao_decimal(rs.vazao_projeto_L_s, 3)} L/s)")
    linhas.append("")
    
    # 3. Calha
    if resultado.resultado_calha is not None:
        rc = resultado.resultado_calha
        linhas.append("3. DIMENSIONAMENTO DA CALHA (MANNING-STRICKLER)")
        linhas.append(f"  - Tipo de Seção: {rc.tipo_secao.upper()}")
        linhas.append(f"  - Dimensões: Largura = {formatar_fracao_decimal(rc.largura_mm, 1)} mm | Altura = {formatar_fracao_decimal(rc.altura_total_mm, 1)} mm")
        linhas.append(f"  - Lâmina d'Água de Escoamento: {formatar_fracao_decimal(rc.lamina_dagua_mm, 1)} mm")
        linhas.append(f"  - Borda Livre Resultante: {formatar_fracao_decimal(rc.borda_livre_mm, 1)} mm ({formatar_fracao_decimal(rc.borda_livre_perc, 1)}% da altura)")
        linhas.append(f"  - Declividade Longitudinal Adotada (i): {formatar_fracao_decimal(rc.declividade_m_m * 100, 2)}% (Mínimo: 0,50%)")
        linhas.append(f"  - Área Molhada (S): {formatar_fracao_decimal(rc.area_molhada_m2, 4)} m²")
        linhas.append(f"  - Raio Hidráulico (Rh): {formatar_fracao_decimal(rc.raio_hidraulico_m, 4)} m")
        linhas.append(f"  - Velocidade de Escoamento: {formatar_fracao_decimal(rc.velocidade_escoamento_m_s, 2)} m/s")
        linhas.append(f"  - Capacidade Admissível de Escoamento: {formatar_fracao_decimal(rc.vazao_admissivel_L_min, 1)} L/min")
        linhas.append(f"  - Taxa de Ocupação da Calha: {formatar_fracao_decimal(rc.taxa_ocupacao_vazao * 100, 1)}%")
        linhas.append(f"  - Status Normativo: {'CONFORME' if rc.atende_norma else 'NÃO CONFORME'}")
        for obs in rc.observacoes:
            linhas.append(f"    * {obs}")
        linhas.append("")
    
    # 4. Condutor Vertical
    if resultado.resultado_condutor_vertical is not None:
        rcv = resultado.resultado_condutor_vertical
        linhas.append("4. CONDUTOR VERTICAL (TUBO DE QUEDA - TABELA 4 NBR 10844)")
        linhas.append(f"  - Diâmetro Nominal (DN): {rcv.dn_mm} mm")
        linhas.append(f"  - Tipo de Bocal de Saída: {rcv.tipo_bocal.upper()}")
        linhas.append(f"  - Capacidade Admissível Normativa: {formatar_fracao_decimal(rcv.capacidade_admissivel_L_min, 1)} L/min")
        linhas.append(f"  - Vazão Afluente: {formatar_fracao_decimal(rcv.vazao_projeto_L_min, 1)} L/min")
        linhas.append(f"  - Taxa de Ocupação: {formatar_fracao_decimal(rcv.taxa_ocupacao_vazao * 100, 1)}%")
        linhas.append(f"  - Status Normativo: {'CONFORME' if rcv.atende_norma else 'NÃO CONFORME'}")
        for obs in rcv.observacoes:
            linhas.append(f"    * {obs}")
        linhas.append("")
    
    # 5. Condutor Horizontal
    if resultado.resultado_condutor_horizontal is not None:
        rch = resultado.resultado_condutor_horizontal
        linhas.append("5. CONDUTOR HORIZONTAL (COLETOR PREDIAL - TABELA 5 NBR 10844)")
        linhas.append(f"  - Diâmetro Nominal (DN): {rch.dn_mm} mm")
        linhas.append(f"  - Declividade de Instalação (i): {formatar_fracao_decimal(rch.declividade_m_m * 100, 2)}% (Mínimo: 0,50%)")
        linhas.append(f"  - Lâmina d'Água Máxima Permissível: h/D <= {formatar_fracao_decimal(rch.relacao_lamina_max, 2)} (Dois Terços)")
        linhas.append(f"  - Capacidade Admissível (Tabela 5): {formatar_fracao_decimal(rch.capacidade_tabela_L_min, 1)} L/min")
        linhas.append(f"  - Capacidade Teórica Contínua (Manning): {formatar_fracao_decimal(rch.capacidade_manning_L_min, 1)} L/min")
        linhas.append(f"  - Vazão Afluente: {formatar_fracao_decimal(rch.vazao_projeto_L_min, 1)} L/min")
        linhas.append(f"  - Taxa de Ocupação: {formatar_fracao_decimal(rch.taxa_ocupacao_vazao * 100, 1)}%")
        linhas.append(f"  - Status Normativo: {'CONFORME' if rch.atende_norma else 'NÃO CONFORME'}")
        for obs in rch.observacoes:
            linhas.append(f"    * {obs}")
        linhas.append("")
    
    # 6. Caixa de Areia
    if resultado.resultado_caixa_areia is not None:
        rca = resultado.resultado_caixa_areia
        linhas.append("6. CAIXA DE AREIA E SEDIMENTAÇÃO (NBR 10844 ITEM 5.4)")
        linhas.append(f"  - Dimensões em Planta: {rca.largura_mm} mm x {rca.comprimento_mm} mm (Mínimo: 400x400 mm)")
        linhas.append(f"  - Altura Livre de Sedimentação: {rca.altura_sedimentacao_mm} mm (Mínimo: 200 mm)")
        linhas.append(f"  - Volume Efetivo de Retenção de Sólidos: {formatar_fracao_decimal(rca.volume_sedimentacao_L, 1)} Litros")
        linhas.append(f"  - Status Normativo: {'CONFORME' if rca.atende_norma else 'NÃO CONFORME'}")
        for obs in rca.observacoes:
            linhas.append(f"    * {obs}")
        linhas.append("")
    
    # 7. Resumo e Alertas
    linhas.append("7. SÍNTESE DE CONFORMIDADE E RECOMENDAÇÕES")
    for k, v in resultado.conformidades.items():
        linhas.append(f"  - Componente [{k}]: {'APROVADO' if v else 'REPROVADO'}")
    if resultado.alertas:
        linhas.append("  ALERTAS DE PROJETO:")
        for al in resultado.alertas:
            linhas.append(f"    [!] {al}")
    if resultado.recomendacoes:
        linhas.append("  RECOMENDAÇÕES EXECUTIVAS:")
        for rec in resultado.recomendacoes:
            linhas.append(f"    [*] {rec}")
    
    linhas.append(div)
    linhas.append("LOFRANO TECNOLOGIA - Soluções Determinísticas e Engenharia Confiável.")
    linhas.append(div)
    return "\n".join(linhas)

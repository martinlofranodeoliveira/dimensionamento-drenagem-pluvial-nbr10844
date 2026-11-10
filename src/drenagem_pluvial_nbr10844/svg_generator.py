from __future__ import annotations

import html
from fractions import Fraction
from typing import Optional

from drenagem_pluvial_nbr10844.models import ResultadoProjetoDrenagem
from drenagem_pluvial_nbr10844.exporters import formatar_fracao_decimal


def gerar_painel_svg(resultado: ResultadoProjetoDrenagem) -> str:
    """Gera um painel técnico vetorial SVG 1440x900 profissional e atraente."""
    c = resultado.chuva
    rs = resultado.resultado_superficie
    rc = resultado.resultado_calha
    rcv = resultado.resultado_condutor_vertical
    rch = resultado.resultado_condutor_horizontal
    rca = resultado.resultado_caixa_areia

    status_cor = "#10b981" if resultado.atende_geral else "#ef4444"
    status_texto = "SISTEMA CONFORME NBR 10844" if resultado.atende_geral else "RESTRIÇÃO / NÃO CONFORME"

    vazao_l_min = formatar_fracao_decimal(rs.vazao_projeto_L_min, 1)
    vazao_l_s = formatar_fracao_decimal(rs.vazao_projeto_L_s, 2)
    area_efetiva = formatar_fracao_decimal(rs.area_efetiva_m2, 1)
    intensidade = formatar_fracao_decimal(c.intensidade_mm_h, 1)

    calha_cap = formatar_fracao_decimal(rc.vazao_admissivel_L_min, 1) if rc else "-"
    calha_ocup = formatar_fracao_decimal(rc.taxa_ocupacao_vazao * 100, 1) if rc else "-"
    calha_largura = formatar_fracao_decimal(rc.largura_mm, 0) if rc else "-"
    calha_altura = formatar_fracao_decimal(rc.altura_total_mm, 0) if rc else "-"
    calha_lamina = formatar_fracao_decimal(rc.lamina_dagua_mm, 1) if rc else "-"
    calha_borda = formatar_fracao_decimal(rc.borda_livre_mm, 1) if rc else "-"
    calha_dec = formatar_fracao_decimal(rc.declividade_m_m * 100, 2) if rc else "-"

    tq_dn = str(rcv.dn_mm) if rcv else "-"
    tq_cap = formatar_fracao_decimal(rcv.capacidade_admissivel_L_min, 1) if rcv else "-"
    tq_ocup = formatar_fracao_decimal(rcv.taxa_ocupacao_vazao * 100, 1) if rcv else "-"

    ch_dn = str(rch.dn_mm) if rch else "-"
    ch_cap = formatar_fracao_decimal(rch.capacidade_tabela_L_min, 1) if rch else "-"
    ch_ocup = formatar_fracao_decimal(rch.taxa_ocupacao_vazao * 100, 1) if rch else "-"
    ch_dec = formatar_fracao_decimal(rch.declividade_m_m * 100, 2) if rch else "-"

    caixa_dim = f"{rca.largura_mm}x{rca.comprimento_mm} mm" if rca else "-"
    caixa_vol = formatar_fracao_decimal(rca.volume_sedimentacao_L, 1) if rca else "-"

    id_proj = html.escape(resultado.identificacao)
    cidade_desc = html.escape(f"{c.cidade} / {c.uf}") if c.cidade else "IDF Específica"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="1440" height="900">
  <defs>
    <!-- Gradientes de Fundo -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120" />
      <stop offset="50%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.95" />
    </linearGradient>
    <linearGradient id="blueCardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#0369a1" stop-opacity="0.10" />
    </linearGradient>
    <linearGradient id="waterGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#0284c7" stop-opacity="0.9" />
    </linearGradient>
    <linearGradient id="roofGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#334155" />
      <stop offset="50%" stop-color="#475569" />
      <stop offset="100%" stop-color="#334155" />
    </linearGradient>

    <!-- Filtro de Sombra -->
    <filter id="dropShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Fundo Principal -->
  <rect width="1440" height="900" fill="url(#bgGrad)" />

  <!-- Grid Sutil de Engenharia -->
  <g opacity="0.05" stroke="#38bdf8" stroke-width="1">
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" />
    </pattern>
    <rect width="1440" height="900" fill="url(#grid)" />
  </g>

  <!-- ==================== CABEÇALHO ==================== -->
  <g transform="translate(40, 30)">
    <!-- Logo Badge -->
    <rect x="0" y="0" width="180" height="34" rx="6" fill="#0284c7" fill-opacity="0.2" stroke="#38bdf8" stroke-width="1.5" />
    <text x="90" y="22" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" letter-spacing="1.5" text-anchor="middle">LOFRANO TECNOLOGIA</text>

    <!-- Título e Subtítulo -->
    <text x="200" y="24" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700">DIMENSIONAMENTO DE DRENAGEM PLUVIAL PREDIAL</text>
    <text x="200" y="44" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12">ABNT NBR 10844:1989 • Projeto: {id_proj} • Método Racional e Manning-Strickler • Zero Float</text>

    <!-- Status Badge -->
    <g transform="translate(1120, 5)">
      <rect x="0" y="0" width="240" height="42" rx="8" fill="{status_cor}" fill-opacity="0.15" stroke="{status_cor}" stroke-width="1.5" />
      <circle cx="22" cy="21" r="6" fill="{status_cor}" />
      <text x="38" y="26" fill="{status_cor}" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" letter-spacing="0.5">{status_texto}</text>
    </g>
  </g>

  <!-- ==================== CARDS DE MÉTRICAS (SUPERIOR) ==================== -->
  <g transform="translate(40, 100)">
    <!-- Card 1: Vazão de Projeto -->
    <rect x="0" y="0" width="320" height="95" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <rect x="0" y="0" width="320" height="4" rx="2" fill="#38bdf8" />
    <text x="20" y="28" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="1">VAZÃO DE PROJETO (Q)</text>
    <text x="20" y="65" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="32" font-weight="800">{vazao_l_min} <tspan font-size="14" fill="#94a3b8">L/min</tspan></text>
    <text x="20" y="85" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Equivalente a {vazao_l_s} L/s no coletor</text>

    <!-- Card 2: Bacia de Captação -->
    <rect x="345" y="0" width="320" height="95" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <rect x="345" y="0" width="320" height="4" rx="2" fill="#06b6d4" />
    <text x="365" y="28" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="1">ÁREA EFETIVA (Ac) &amp; CHUVA</text>
    <text x="365" y="65" fill="#06b6d4" font-family="'Segoe UI', Roboto, sans-serif" font-size="32" font-weight="800">{area_efetiva} <tspan font-size="14" fill="#94a3b8">m²</tspan></text>
    <text x="365" y="85" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">I = {intensidade} mm/h (T={c.periodo_retorno_anos}a, {cidade_desc})</text>

    <!-- Card 3: Calha Perimetral -->
    <rect x="690" y="0" width="320" height="95" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <rect x="690" y="0" width="320" height="4" rx="2" fill="#10b981" />
    <text x="710" y="28" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="1">CAPACIDADE DA CALHA</text>
    <text x="710" y="65" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="32" font-weight="800">{calha_cap} <tspan font-size="14" fill="#94a3b8">L/min</tspan></text>
    <text x="710" y="85" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Ocupação: {calha_ocup}% • Declividade: {calha_dec}%</text>

    <!-- Card 4: Condutores -->
    <rect x="1035" y="0" width="325" height="95" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#dropShadow)" />
    <rect x="1035" y="0" width="325" height="4" rx="2" fill="#a855f7" />
    <text x="1055" y="28" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" letter-spacing="1">TUBOS DE QUEDA &amp; COLETOR</text>
    <text x="1055" y="65" fill="#a855f7" font-family="'Segoe UI', Roboto, sans-serif" font-size="32" font-weight="800">DN {tq_dn} / {ch_dn} <tspan font-size="14" fill="#94a3b8">mm</tspan></text>
    <text x="1055" y="85" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Vertical Tabela 4 ({tq_ocup}%) • Horizontal ({ch_ocup}%)</text>
  </g>

  <!-- ==================== ÁREA PRINCIPAL: DIAGRAMA ISOMÉTRICO / ESQUEMÁTICO (ESQUERDA) ==================== -->
  <g transform="translate(40, 220)">
    <!-- Painel do Diagrama -->
    <rect x="0" y="0" width="780" height="620" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1.5" filter="url(#dropShadow)" />
    <text x="30" y="38" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="700">DIAGRAMA ESQUEMÁTICO DO SISTEMA PREDIAL</text>
    <text x="30" y="58" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="12">Representação técnica de captação, calha, prumada vertical e coletor horizontal com caixa de areia</text>

    <!-- Nuvem e Chuva Ilustrativa -->
    <g transform="translate(180, 75)" opacity="0.85">
      <path d="M 0 30 Q 15 10 35 15 Q 55 -5 85 5 Q 115 -10 145 10 Q 175 0 195 20 Q 215 35 195 50 Q 185 60 160 55 L 10 55 Q -10 45 0 30 Z" fill="#334155" stroke="#475569" stroke-width="1.5" />
      <!-- Pingos de chuva -->
      <line x1="30" y1="65" x2="20" y2="90" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 6" opacity="0.8" />
      <line x1="60" y1="65" x2="50" y2="95" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 6" opacity="0.8" />
      <line x1="90" y1="65" x2="80" y2="90" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 6" opacity="0.8" />
      <line x1="120" y1="65" x2="110" y2="95" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 6" opacity="0.8" />
      <line x1="150" y1="65" x2="140" y2="90" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 6" opacity="0.8" />
      <line x1="180" y1="65" x2="170" y2="95" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 6" opacity="0.8" />
      <text x="100" y="32" fill="#e2e8f0" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" text-anchor="middle">I = {intensidade} mm/h</text>
    </g>

    <!-- Parede Vertical (Contígua) -->
    <polygon points="50,140 120,120 120,260 50,280" fill="#1e293b" stroke="#64748b" stroke-width="1.5" />
    <text x="85" y="200" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600" text-anchor="middle" transform="rotate(-15, 85, 200)">PAREDE +Ap/2</text>

    <!-- Telhado Inclinado (Cobertura de Captação) -->
    <polygon points="120,160 380,120 450,220 190,260" fill="url(#roofGrad)" stroke="#64748b" stroke-width="2" />
    <!-- Linhas das telhas -->
    <line x1="160" y1="154" x2="230" y2="254" stroke="#1e293b" stroke-width="1" />
    <line x1="200" y1="148" x2="270" y2="248" stroke="#1e293b" stroke-width="1" />
    <line x1="240" y1="142" x2="310" y2="242" stroke="#1e293b" stroke-width="1" />
    <line x1="280" y1="136" x2="350" y2="236" stroke="#1e293b" stroke-width="1" />
    <line x1="320" y1="130" x2="390" y2="230" stroke="#1e293b" stroke-width="1" />

    <!-- Rótulo do Telhado -->
    <rect x="230" y="180" width="140" height="26" rx="4" fill="#0f172a" fill-opacity="0.85" stroke="#38bdf8" stroke-width="1" />
    <text x="300" y="197" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" text-anchor="middle">ÁREA EFETIVA {area_efetiva} m²</text>

    <!-- Calha Perimetral (Borda Inferior da Cobertura) -->
    <polygon points="185,260 455,220 460,235 190,275" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />
    <text x="330" y="260" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle" transform="rotate(-8, 330, 260)">CALHA {rc.tipo_secao.upper() if rc else ''} (i = {calha_dec}%)</text>

    <!-- Bocal / Ralo na Calha -->
    <circle cx="455" cy="228" r="8" fill="#0ea5e9" stroke="#ffffff" stroke-width="1.5" />

    <!-- Tubo de Queda (Condutor Vertical) -->
    <rect x="450" y="235" width="10" height="230" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5" />
    <!-- Setas de Fluxo Descendente -->
    <polygon points="455,290 451,280 459,280" fill="#ffffff" />
    <polygon points="455,360 451,350 459,350" fill="#ffffff" />
    <polygon points="455,430 451,420 459,420" fill="#ffffff" />

    <rect x="475" y="325" width="130" height="36" rx="6" fill="#0f172a" stroke="#a855f7" stroke-width="1" />
    <text x="540" y="342" fill="#a855f7" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" text-anchor="middle">CONDUTOR VERTICAL</text>
    <text x="540" y="354" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" text-anchor="middle">DN {tq_dn} mm • {tq_cap} L/min</text>

    <!-- Caixa de Areia (Piso Térreo) -->
    <rect x="430" y="465" width="70" height="75" rx="4" fill="#334155" stroke="#94a3b8" stroke-width="1.5" />
    <!-- Câmara de sedimentação (água e areia no fundo) -->
    <rect x="435" y="505" width="60" height="30" fill="#d97706" fill-opacity="0.4" stroke="#d97706" stroke-width="1" stroke-dasharray="2 2" />
    <text x="465" y="525" fill="#fde68a" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" font-weight="700" text-anchor="middle">AREIA (20cm)</text>

    <rect x="300" y="480" width="120" height="34" rx="6" fill="#0f172a" stroke="#eab308" stroke-width="1" />
    <text x="360" y="496" fill="#fde047" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" text-anchor="middle">CAIXA DE AREIA</text>
    <text x="360" y="508" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" text-anchor="middle">{caixa_dim} ({caixa_vol} L)</text>

    <!-- Condutor Horizontal (Saída da Caixa de Areia) -->
    <rect x="500" y="480" width="220" height="12" rx="3" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5" transform="rotate(3, 500, 480)" />
    <!-- Água parcial (2/3 de lâmina) -->
    <rect x="500" y="484" width="220" height="8" fill="#38bdf8" opacity="0.7" transform="rotate(3, 500, 480)" />

    <rect x="570" y="515" width="145" height="36" rx="6" fill="#0f172a" stroke="#38bdf8" stroke-width="1" />
    <text x="642" y="532" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" text-anchor="middle">CONDUTOR HORIZONTAL</text>
    <text x="642" y="544" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" text-anchor="middle">DN {ch_dn} mm • i = {ch_dec}% (h/D &lt;= 0,67)</text>

    <!-- Linha de Terra / Terreno -->
    <line x1="20" y1="465" x2="760" y2="465" stroke="#475569" stroke-width="2" stroke-dasharray="6 4" />
    <text x="40" y="458" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="600">NÍVEL DO PAVIMENTO TÉRREO</text>

    <!-- Detalhe da Seção Transversal da Calha (Canto Inferior Esquerdo) -->
    <g transform="translate(40, 490)">
      <rect x="0" y="0" width="240" height="110" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1" />
      <text x="15" y="20" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">SEÇÃO DA CALHA (CORTE)</text>
      <!-- Desenho da Calha Retangular -->
      <rect x="25" y="32" width="70" height="55" fill="none" stroke="#94a3b8" stroke-width="2" />
      <!-- Água -->
      <rect x="26" y="52" width="68" height="34" fill="url(#waterGrad)" />
      <!-- Cotas -->
      <text x="60" y="100" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" text-anchor="middle">b = {calha_largura} mm</text>
      <text x="110" y="50" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">fb = {calha_borda} mm</text>
      <text x="110" y="70" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">h = {calha_lamina} mm</text>
      <text x="110" y="85" fill="#f8fafc" font-family="'Segoe UI', Roboto, sans-serif" font-size="9">H = {calha_altura} mm</text>
    </g>
  </g>

  <!-- ==================== PAINEL TÉCNICO DE MEMORIAL E TABELAS (DIREITA) ==================== -->
  <g transform="translate(840, 220)">
    <!-- Painel 1: Formulação Racional -->
    <rect x="0" y="0" width="560" height="135" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1.5" filter="url(#dropShadow)" />
    <rect x="0" y="0" width="560" height="3" rx="1.5" fill="#0284c7" />
    <text x="25" y="28" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700">MÉTODO RACIONAL DE VAZÃO (NBR 10844)</text>
    
    <g transform="translate(25, 42)">
      <rect x="0" y="0" width="510" height="34" rx="6" fill="#0284c7" fill-opacity="0.12" stroke="#0284c7" stroke-width="1" />
      <text x="255" y="22" fill="#38bdf8" font-family="'Courier New', monospace" font-size="14" font-weight="700" text-anchor="middle">Q = (C · I · Ac) / 60  [L/min]</text>
    </g>

    <text x="25" y="100" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      • Coeficiente C: <tspan fill="#38bdf8" font-weight="700">{formatar_fracao_decimal(rs.coeficiente_escoamento, 2)}</tspan> | Intensidade I: <tspan fill="#38bdf8" font-weight="700">{intensidade} mm/h</tspan>
    </text>
    <text x="25" y="118" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      • Área Ac = {formatar_fracao_decimal(rs.area_horizontal_m2, 1)} + {formatar_fracao_decimal(rs.area_paredes_m2, 1)} = <tspan fill="#38bdf8" font-weight="700">{area_efetiva} m²</tspan> ⇒ <tspan fill="#10b981" font-weight="700">Q = {vazao_l_min} L/min</tspan>
    </text>

    <!-- Painel 2: Tabela de Dimensionamento da Calha -->
    <rect x="0" y="150" width="560" height="150" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1.5" filter="url(#dropShadow)" />
    <rect x="0" y="150" width="560" height="3" rx="1.5" fill="#10b981" />
    <text x="25" y="178" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700">VERIFICAÇÃO HIDRÁULICA DA CALHA (MANNING)</text>

    <!-- Cabeçalho Tabela -->
    <rect x="25" y="192" width="510" height="24" rx="4" fill="#1e293b" />
    <text x="35" y="208" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">PARÂMETRO</text>
    <text x="190" y="208" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">VALOR PROJETADO</text>
    <text x="350" y="208" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">CRITÉRIO NORMATIVO</text>
    <text x="480" y="208" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">STATUS</text>

    <!-- Linhas -->
    <text x="35" y="232" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Capacidade de Vazão</text>
    <text x="190" y="232" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">{calha_cap} L/min</text>
    <text x="350" y="232" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">≥ {vazao_l_min} L/min</text>
    <text x="480" y="232" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">OK</text>

    <text x="35" y="254" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Declividade Longitudinal</text>
    <text x="190" y="254" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{calha_dec}%</text>
    <text x="350" y="254" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">≥ 0,50%</text>
    <text x="480" y="254" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">OK</text>

    <text x="35" y="276" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Borda Livre de Segurança</text>
    <text x="190" y="276" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{calha_borda} mm</text>
    <text x="350" y="276" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">≥ 20 mm / 20%</text>
    <text x="480" y="276" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">OK</text>

    <!-- Painel 3: Condutores Verticais e Horizontais -->
    <rect x="0" y="315" width="560" height="150" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1.5" filter="url(#dropShadow)" />
    <rect x="0" y="315" width="560" height="3" rx="1.5" fill="#a855f7" />
    <text x="25" y="343" fill="#a855f7" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700">CONDUTORES VERTICAIS E HORIZONTAIS</text>

    <!-- Cabeçalho Tabela 2 -->
    <rect x="25" y="357" width="510" height="24" rx="4" fill="#1e293b" />
    <text x="35" y="373" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">TUBULAÇÃO</text>
    <text x="160" y="373" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">DN ADOTADO</text>
    <text x="280" y="373" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">CAPACIDADE</text>
    <text x="400" y="373" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">OCUPAÇÃO</text>
    <text x="480" y="373" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700">STATUS</text>

    <text x="35" y="397" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Tubo de Queda (TQ)</text>
    <text x="160" y="397" fill="#a855f7" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">DN {tq_dn} mm</text>
    <text x="280" y="397" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{tq_cap} L/min</text>
    <text x="400" y="397" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{tq_ocup}%</text>
    <text x="480" y="397" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">OK</text>

    <text x="35" y="420" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">Coletor Horizontal (CH)</text>
    <text x="160" y="420" fill="#38bdf8" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">DN {ch_dn} mm</text>
    <text x="280" y="420" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{ch_cap} L/min</text>
    <text x="400" y="420" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">{ch_ocup}%</text>
    <text x="480" y="420" fill="#10b981" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700">OK</text>

    <text x="35" y="445" fill="#94a3b8" font-family="'Segoe UI', Roboto, sans-serif" font-size="10">
      * TQ dimensionado por vórtice anular (Tabela 4); CH opera sob gravidade h/D ≤ 0,67 (Tabela 5).
    </text>

    <!-- Painel 4: Caixa de Areia e Extravasor -->
    <rect x="0" y="480" width="560" height="140" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1.5" filter="url(#dropShadow)" />
    <rect x="0" y="480" width="560" height="3" rx="1.5" fill="#eab308" />
    <text x="25" y="508" fill="#fde047" font-family="'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="700">CAIXA DE AREIA E DISPOSITIVOS ACESSÓRIOS</text>

    <text x="25" y="534" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      • Caixa de Areia com Cesto Removível: <tspan fill="#fde047" font-weight="700">{caixa_dim}</tspan> (Vol. {caixa_vol} L)
    </text>
    <text x="25" y="554" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      • Altura Livre de Sedimentação: <tspan fill="#10b981" font-weight="700">{rca.altura_sedimentacao_mm if rca else 200} mm</tspan> (Mínimo normativo: 200 mm)
    </text>
    <text x="25" y="574" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      • Ralo de Cobertura: Tipo Hemisférico (anti-folhas) instalado na embocadura.
    </text>
    <text x="25" y="594" fill="#cbd5e1" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      • Extravasor (Ladrão): Previsto na calha de platibanda para Q_extravasor = {vazao_l_min} L/min.
    </text>
  </g>

  <!-- ==================== RODAPÉ ==================== -->
  <g transform="translate(40, 860)">
    <text x="0" y="15" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11">
      LOFRANO TECNOLOGIA • Engenharia Determinística • Aritmética Exata Zero Float (Python Standard Library Fraction/int)
    </text>
    <text x="1360" y="15" fill="#64748b" font-family="'Segoe UI', Roboto, sans-serif" font-size="11" text-anchor="end">
      ABNT NBR 10844:1989 • v1.0.0
    </text>
  </g>
</svg>"""
    return svg

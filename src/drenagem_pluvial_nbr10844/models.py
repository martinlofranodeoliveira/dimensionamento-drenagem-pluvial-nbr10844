from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class DadosChuva:
    """Parâmetros pluviométricos de projeto conforme NBR 10844."""
    cidade: str = ""
    uf: str = ""
    periodo_retorno_anos: int = 5
    duracao_minutos: int = 5
    intensidade_mm_h: Fraction = Fraction(150, 1)

    def __post_init__(self) -> None:
        if self.periodo_retorno_anos not in (1, 5, 25):
            raise ValueError(
                f"Período de retorno deve ser 1, 5 ou 25 anos segundo NBR 10844. Recebido: {self.periodo_retorno_anos}"
            )
        if self.duracao_minutos <= 0:
            raise ValueError("Duração da chuva deve ser positiva.")
        if self.intensidade_mm_h <= 0:
            raise ValueError("Intensidade pluviométrica deve ser positiva.")


@dataclass(frozen=True)
class ParedeVertical:
    """Parede vertical adjacente ou contígua que recebe vento-chuva."""
    identificacao: str
    altura_m: Fraction
    largura_m: Fraction

    def __post_init__(self) -> None:
        if self.altura_m < 0 or self.largura_m < 0:
            raise ValueError("Dimensões da parede não podem ser negativas.")

    @property
    def area_m2(self) -> Fraction:
        return self.altura_m * self.largura_m


@dataclass(frozen=True)
class SuperficieContribuicao:
    """Superfície de captação / bacia de contribuição (NBR 10844 item 5.1.2)."""
    identificacao: str
    area_horizontal_m2: Fraction
    tipo_superficie: str = "cobertura_metalica"
    paredes: List[ParedeVertical] = field(default_factory=list)
    coeficiente_escoamento: Fraction = Fraction(1, 1)

    def __post_init__(self) -> None:
        if self.area_horizontal_m2 <= 0:
            raise ValueError("Área horizontal de contribuição deve ser estritamente positiva.")
        if not (0 < self.coeficiente_escoamento <= 1):
            raise ValueError("Coeficiente de escoamento superficial (C) deve estar no intervalo (0, 1].")


@dataclass(frozen=True)
class Calha:
    """Definição geométrica e hidráulica de calha (NBR 10844 item 5.1)."""
    identificacao: str
    tipo_secao: str = "retangular"  # "retangular", "semicircular", "trapezoidal"
    material: str = "pvc"
    largura_fundo_mm: Fraction = Fraction(150, 1)
    largura_topo_mm: Fraction = Fraction(150, 1)  # relevante para seção trapezoidal
    altura_total_mm: Fraction = Fraction(120, 1)
    lamina_dagua_mm: Optional[Fraction] = None    # Se None, calcula até o limite da borda livre
    declividade_m_m: Fraction = Fraction(1, 100)  # Padrão 1,0% (0,01 m/m)
    comprimento_m: Fraction = Fraction(10, 1)

    def __post_init__(self) -> None:
        if self.tipo_secao not in ("retangular", "semicircular", "trapezoidal"):
            raise ValueError(f"Tipo de seção '{self.tipo_secao}' desconhecido. Permitidos: retangular, semicircular, trapezoidal.")
        if self.largura_fundo_mm <= 0 or self.altura_total_mm <= 0:
            raise ValueError("Dimensões da calha devem ser estritamente positivas.")
        if self.declividade_m_m <= 0:
            raise ValueError("Declividade da calha deve ser positiva.")


@dataclass(frozen=True)
class CondutorVertical:
    """Condutor vertical / Tubo de Queda (NBR 10844 item 5.2)."""
    identificacao: str
    dn_mm: int = 100
    tipo_bocal: str = "reto"  # "reto" ou "funil"
    altura_m: Fraction = Fraction(6, 1)

    def __post_init__(self) -> None:
        if self.dn_mm not in (75, 100, 125, 150, 200):
            raise ValueError(f"DN {self.dn_mm} não padronizado na Tabela 4 da NBR 10844 (75, 100, 125, 150, 200).")
        if self.tipo_bocal not in ("reto", "funil"):
            raise ValueError(f"Tipo de bocal '{self.tipo_bocal}' inválido. Permitidos: 'reto', 'funil'.")
        if self.altura_m <= 0:
            raise ValueError("Altura do tubo de queda deve ser positiva.")


@dataclass(frozen=True)
class CondutorHorizontal:
    """Condutor horizontal de águas pluviais por gravidade (NBR 10844 item 5.3)."""
    identificacao: str
    dn_mm: int = 100
    material: str = "pvc"
    declividade_m_m: Fraction = Fraction(1, 100)  # 1,0%
    comprimento_m: Fraction = Fraction(15, 1)
    relacao_lamina_max: Fraction = Fraction(2, 3) # h/D <= 2/3 (0,67)

    def __post_init__(self) -> None:
        if self.dn_mm not in (75, 100, 125, 150, 200, 250, 300):
            raise ValueError(f"DN {self.dn_mm} não padronizado na Tabela 5 da NBR 10844.")
        if self.declividade_m_m <= 0:
            raise ValueError("Declividade deve ser estritamente positiva.")
        if not (0 < self.relacao_lamina_max <= 1):
            raise ValueError("Relação de lâmina máxima h/D deve estar em (0, 1].")


@dataclass(frozen=True)
class Ralo:
    """Ralo de captação de cobertura ou calha."""
    identificacao: str
    tipo_ralo: str = "hemisferico"  # "hemisferico" ou "plano"
    dn_mm: int = 100


@dataclass(frozen=True)
class CaixaAreia:
    """Caixa de areia e sedimentação de sólidos carreados."""
    identificacao: str
    largura_mm: int = 400
    comprimento_mm: int = 400
    altura_util_mm: int = 400
    altura_sedimentacao_mm: int = 200


@dataclass(frozen=True)
class ProjetoDrenagem:
    """Entrada completa para dimensionamento de drenagem pluvial."""
    identificacao: str
    chuva: DadosChuva
    superficie: SuperficieContribuicao
    calha: Optional[Calha] = None
    condutor_vertical: Optional[CondutorVertical] = None
    condutor_horizontal: Optional[CondutorHorizontal] = None
    ralo: Optional[Ralo] = None
    caixa_areia: Optional[CaixaAreia] = None


@dataclass(frozen=True)
class ResultadoSuperficie:
    """Resultados de cálculo de área e vazão de projeto."""
    area_horizontal_m2: Fraction
    area_paredes_m2: Fraction
    area_efetiva_m2: Fraction
    coeficiente_escoamento: Fraction
    intensidade_mm_h: Fraction
    vazao_projeto_L_min: Fraction
    vazao_projeto_L_s: Fraction


@dataclass(frozen=True)
class ResultadoCalha:
    """Resultados de cálculo e verificação de calha."""
    tipo_secao: str
    largura_mm: Fraction
    altura_total_mm: Fraction
    lamina_dagua_mm: Fraction
    borda_livre_mm: Fraction
    borda_livre_perc: Fraction
    area_molhada_m2: Fraction
    perimetro_molhado_m: Fraction
    raio_hidraulico_m: Fraction
    declividade_m_m: Fraction
    vazao_admissivel_L_min: Fraction
    vazao_projeto_L_min: Fraction
    taxa_ocupacao_vazao: Fraction
    velocidade_escoamento_m_s: Fraction
    atende_capacidade: bool
    atende_declividade: bool
    atende_borda_livre: bool
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoCondutorVertical:
    """Resultados de cálculo e verificação de condutor vertical."""
    dn_mm: int
    tipo_bocal: str
    capacidade_admissivel_L_min: Fraction
    vazao_projeto_L_min: Fraction
    taxa_ocupacao_vazao: Fraction
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoCondutorHorizontal:
    """Resultados de cálculo e verificação de condutor horizontal."""
    dn_mm: int
    declividade_m_m: Fraction
    capacidade_tabela_L_min: Fraction
    capacidade_manning_L_min: Fraction
    vazao_projeto_L_min: Fraction
    taxa_ocupacao_vazao: Fraction
    relacao_lamina_max: Fraction
    atende_declividade: bool
    atende_capacidade: bool
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoCaixaAreia:
    """Resultados de verificação da caixa de areia."""
    largura_mm: int
    comprimento_mm: int
    altura_util_mm: int
    altura_sedimentacao_mm: int
    volume_sedimentacao_L: Fraction
    atende_norma: bool
    observacoes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResultadoProjetoDrenagem:
    """Resultado consolidado do dimensionamento predial de águas pluviais."""
    identificacao: str
    norma: str
    chuva: DadosChuva
    resultado_superficie: ResultadoSuperficie
    resultado_calha: Optional[ResultadoCalha]
    resultado_condutor_vertical: Optional[ResultadoCondutorVertical]
    resultado_condutor_horizontal: Optional[ResultadoCondutorHorizontal]
    resultado_caixa_areia: Optional[ResultadoCaixaAreia]
    atende_geral: bool
    conformidades: Dict[str, bool]
    alertas: List[str]
    recomendacoes: List[str]

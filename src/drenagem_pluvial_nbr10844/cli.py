from __future__ import annotations

import argparse
import sys
from fractions import Fraction
from typing import Optional, List

from drenagem_pluvial_nbr10844 import __version__
from drenagem_pluvial_nbr10844.constants import (
    CIDADES_NBR10844,
    COEFICIENTES_MANNING,
    COEFICIENTES_ESCOAMENTO,
    TABELA_TUBOS_QUEDA_NBR10844,
    TABELA_CONDUTORES_HORIZONTAIS_NBR10844,
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
)
from drenagem_pluvial_nbr10844.calculator import (
    obter_intensidade_cidade,
    dimensionar_sistema,
)
from drenagem_pluvial_nbr10844.codecs import (
    carregar_json_canonico,
    salvar_json_canonico,
    deserializar_projeto,
)
from drenagem_pluvial_nbr10844.exporters import (
    exportar_csv,
    gerar_relatorio_memorial,
    formatar_fracao_decimal,
)
from drenagem_pluvial_nbr10844.svg_generator import gerar_painel_svg


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drenagem-pluvial",
        description="Dimensionamento de sistemas prediais e urbanos de drenagem de águas pluviais segundo a ABNT NBR 10844:1989. LOFRANO TECNOLOGIA.",
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: dimensionar
    p_dim = subparsers.add_parser("dimensionar", help="Dimensiona e verifica componentes de drenagem pluvial")
    p_dim.add_argument("--arquivo", "-a", type=str, help="Caminho do arquivo JSON de projeto")
    p_dim.add_argument("--cidade", "-c", type=str, help="Chave da cidade (ex: sao_paulo, curitiba, belo_horizonte)")
    p_dim.add_argument("--retorno", "-T", type=int, default=5, choices=[1, 5, 25], help="Período de retorno em anos (padrão: 5)")
    p_dim.add_argument("--intensidade", "-I", type=str, help="Intensidade pluviométrica direta em mm/h (ex: 150 ou 160/1)")
    p_dim.add_argument("--area", type=str, help="Área horizontal da bacia em m² (ex: 200 ou 250/1)")
    p_dim.add_argument("--parede-altura", type=str, default="0", help="Altura de parede vertical contígua em metros")
    p_dim.add_argument("--parede-largura", type=str, default="0", help="Largura de parede vertical contígua em metros")
    p_dim.add_argument("--coeficiente", "-C", type=str, default="1", help="Coeficiente de escoamento superficial (padrão: 1,0)")
    
    # Calha
    p_dim.add_argument("--calha-largura", type=str, help="Largura do fundo da calha em mm (ex: 150)")
    p_dim.add_argument("--calha-altura", type=str, help="Altura total da calha em mm (ex: 120)")
    p_dim.add_argument("--calha-declividade", type=str, default="1.0", help="Declividade da calha em %% (padrão: 1.0%%)")
    p_dim.add_argument("--calha-secao", type=str, default="retangular", choices=["retangular", "semicircular", "trapezoidal"])
    p_dim.add_argument("--calha-material", type=str, default="pvc", help="Material da calha (pvc, aco_galvanizado, aluminio, etc.)")
    
    # Tubo de Queda
    p_dim.add_argument("--tq-dn", type=int, choices=[75, 100, 125, 150, 200], help="DN do condutor vertical em mm (ex: 100)")
    p_dim.add_argument("--tq-bocal", type=str, default="reto", choices=["reto", "funil"], help="Tipo de bocal do condutor vertical")
    
    # Condutor Horizontal
    p_dim.add_argument("--ch-dn", type=int, choices=[75, 100, 125, 150, 200, 250, 300], help="DN do coletor horizontal em mm (ex: 100)")
    p_dim.add_argument("--ch-declividade", type=str, default="1.0", help="Declividade do condutor horizontal em %% (padrão: 1.0%%)")
    
    # Saídas
    p_dim.add_argument("--saida-json", "-j", type=str, help="Caminho para salvar resultado consolidado em JSON")
    p_dim.add_argument("--saida-csv", type=str, help="Caminho para salvar relatório estruturado em CSV")
    p_dim.add_argument("--saida-relatorio", "-r", type=str, help="Caminho para salvar memorial descritivo em TXT")
    p_dim.add_argument("--painel-svg", "-s", type=str, help="Caminho para gerar e salvar painel técnico em SVG")

    # Comando: cidades
    subparsers.add_parser("cidades", help="Lista cidades cadastradas e suas intensidades normativas NBR 10844")

    # Comando: tabelas
    subparsers.add_parser("tabelas", help="Exibe Tabelas 4 e 5 oficiais da NBR 10844")

    # Comando: versao
    subparsers.add_parser("versao", help="Exibe a versão do pacote")

    return parser


def parse_fracao_cli(texto: str) -> Fraction:
    """Converte string recebida na linha de comando em Fraction sem admitir float."""
    t = texto.strip().replace(",", ".")
    if "/" in t:
        partes = t.split("/")
        if len(partes) == 2:
            return Fraction(int(partes[0].strip()), int(partes[1].strip()))
    if "." in t:
        partes = t.split(".")
        parte_int = int(partes[0]) if partes[0] else 0
        dec_str = partes[1]
        den = 10 ** len(dec_str)
        num = parte_int * den + (int(dec_str) if parte_int >= 0 else -int(dec_str))
        return Fraction(num, den)
    return Fraction(int(t), 1)


def executar_cidades() -> int:
    print("=" * 70)
    print("  CIDADES BRASILEIRAS E INTENSIDADES PLUVIOMÉTRICAS (ABNT NBR 10844)")
    print("  Duração de chuva padrão: t = 5 minutos")
    print("=" * 70)
    print(f"{'Chave':<18} | {'Nome / UF':<22} | {'T=1 ano':<10} | {'T=5 anos':<10} | {'T=25 anos':<10}")
    print("-" * 70)
    for chave, info in sorted(CIDADES_NBR10844.items()):
        nome_uf = f"{info['nome']} ({info['uf']})"
        t1 = f"{info['intensidades'][1]} mm/h"
        t5 = f"{info['intensidades'][5]} mm/h"
        t25 = f"{info['intensidades'][25]} mm/h"
        print(f"{chave:<18} | {nome_uf:<22} | {t1:<10} | {t5:<10} | {t25:<10}")
    print("=" * 70)
    return 0


def executar_tabelas() -> int:
    print("=" * 75)
    print("  TABELA 4 DA ABNT NBR 10844:1989 - CAPACIDADE DE CONDUTORES VERTICAIS")
    print("=" * 75)
    print(f"{'DN (mm)':<12} | {'Bocal Reto (L/min)':<25} | {'Bocal com Funil (L/min)':<25}")
    print("-" * 75)
    for dn, bocais in sorted(TABELA_TUBOS_QUEDA_NBR10844.items()):
        print(f"DN {dn:<9} | {bocais['reto']:<25} | {bocais['funil']:<25}")
    print("=" * 75)
    print("\n" + "=" * 75)
    print("  TABELA 5 DA ABNT NBR 10844:1989 - CONDUTORES HORIZONTAIS DE PVC")
    print("  Lâmina máxima: h/D = 0,67 | n = 0,011 | Capacidade em L/min")
    print("=" * 75)
    print(f"{'DN (mm)':<10} | {'i = 0,5%':<10} | {'i = 1,0%':<10} | {'i = 1,5%':<10} | {'i = 2,0%':<10} | {'i = 3,0%':<10} | {'i = 4,0%':<10}")
    print("-" * 75)
    for dn, decls in sorted(TABELA_CONDUTORES_HORIZONTAIS_NBR10844.items()):
        v05 = decls.get(Fraction(5, 1000), "-")
        v10 = decls.get(Fraction(1, 100), "-")
        v15 = decls.get(Fraction(15, 1000), "-")
        v20 = decls.get(Fraction(2, 100), "-")
        v30 = decls.get(Fraction(3, 100), "-")
        v40 = decls.get(Fraction(4, 100), "-")
        print(f"DN {dn:<7} | {str(v05):<10} | {str(v10):<10} | {str(v15):<10} | {str(v20):<10} | {str(v30):<10} | {str(v40):<10}")
    print("=" * 75)
    return 0


def executar_dimensionar(args: argparse.Namespace) -> int:
    if args.arquivo:
        dados = carregar_json_canonico(args.arquivo)
        projeto = deserializar_projeto(dados)
    else:
        # Construção interativa ou por argumentos
        if not args.area:
            print("Erro: Deve ser informado --arquivo ou a especificação de --area e parâmetros de chuva.", file=sys.stderr)
            return 1
        
        # Intensidade
        if args.intensidade:
            intensidade = parse_fracao_cli(args.intensidade)
            cidade_nome = ""
            uf_nome = ""
        elif args.cidade:
            intensidade = obter_intensidade_cidade(args.cidade, args.retorno)
            info = CIDADES_NBR10844[args.cidade.strip().lower().replace(" ", "_")]
            cidade_nome = info["nome"]
            uf_nome = info["uf"]
        else:
            intensidade = Fraction(150, 1)
            cidade_nome = "Padrão"
            uf_nome = "BR"
        
        chuva = DadosChuva(
            cidade=cidade_nome,
            uf=uf_nome,
            periodo_retorno_anos=args.retorno,
            duracao_minutos=5,
            intensidade_mm_h=intensidade,
        )

        # Superfície
        area_h = parse_fracao_cli(args.area)
        c_esc = parse_fracao_cli(args.coeficiente)
        
        paredes: List[ParedeVertical] = []
        alt_p = parse_fracao_cli(args.parede_altura)
        lar_p = parse_fracao_cli(args.parede_largura)
        if alt_p > 0 and lar_p > 0:
            paredes.append(
                ParedeVertical(
                    identificacao="Parede Adjacente",
                    altura_m=alt_p,
                    largura_m=lar_p,
                )
            )
        
        superficie = SuperficieContribuicao(
            identificacao="Superfície de Cobertura",
            area_horizontal_m2=area_h,
            tipo_superficie="cobertura_metalica",
            paredes=paredes,
            coeficiente_escoamento=c_esc,
        )

        # Calha
        calha: Optional[Calha] = None
        if args.calha_largura and args.calha_altura:
            calha = Calha(
                identificacao="Calha de Cobertura",
                tipo_secao=args.calha_secao,
                material=args.calha_material,
                largura_fundo_mm=parse_fracao_cli(args.calha_largura),
                largura_topo_mm=parse_fracao_cli(args.calha_largura),
                altura_total_mm=parse_fracao_cli(args.calha_altura),
                declividade_m_m=parse_fracao_cli(args.calha_declividade) / Fraction(100, 1),
            )

        # Tubo de Queda
        condutor_v: Optional[CondutorVertical] = None
        if args.tq_dn:
            condutor_v = CondutorVertical(
                identificacao="Tubo de Queda",
                dn_mm=args.tq_dn,
                tipo_bocal=args.tq_bocal,
                altura_m=Fraction(6, 1),
            )

        # Condutor Horizontal
        condutor_h: Optional[CondutorHorizontal] = None
        if args.ch_dn:
            condutor_h = CondutorHorizontal(
                identificacao="Coletor Predial",
                dn_mm=args.ch_dn,
                material="pvc",
                declividade_m_m=parse_fracao_cli(args.ch_declividade) / Fraction(100, 1),
            )

        projeto = ProjetoDrenagem(
            identificacao="Projeto de Drenagem Predial",
            chuva=chuva,
            superficie=superficie,
            calha=calha,
            condutor_vertical=condutor_v,
            condutor_horizontal=condutor_h,
            caixa_areia=CaixaAreia(
                identificacao="Caixa de Areia",
                largura_mm=400,
                comprimento_mm=400,
                altura_util_mm=400,
                altura_sedimentacao_mm=200,
            ),
        )

    # Executar dimensionamento
    resultado = dimensionar_sistema(projeto)

    # Imprimir Memorial
    memorial = gerar_relatorio_memorial(resultado)
    print(memorial)

    # Exportações
    if args.saida_json:
        salvar_json_canonico(args.saida_json, resultado)
        print(f"\n[OK] Resultado JSON canônico salvo em: {args.saida_json}")

    if args.saida_csv:
        conteudo_csv = exportar_csv(resultado)
        with open(args.saida_csv, "w", encoding="utf-8", newline="\n") as f:
            f.write(conteudo_csv)
        print(f"[OK] Planilha técnica CSV salva em: {args.saida_csv}")

    if args.saida_relatorio:
        with open(args.saida_relatorio, "w", encoding="utf-8", newline="\n") as f:
            f.write(memorial)
            f.write("\n")
        print(f"[OK] Memorial técnico TXT salvo em: {args.saida_relatorio}")

    if args.painel_svg:
        svg_conteudo = gerar_painel_svg(resultado)
        with open(args.painel_svg, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg_conteudo)
            f.write("\n")
        print(f"[OK] Painel técnico SVG salvo em: {args.painel_svg}")

    return 0 if resultado.atende_geral else 2


def main() -> int:
    parser = criar_parser()
    args = parser.parse_args()

    if not args.comando or args.comando == "versao":
        print(f"dimensionamento-drenagem-pluvial-nbr10844 v{__version__} - LOFRANO TECNOLOGIA")
        return 0

    if args.comando == "cidades":
        return executar_cidades()

    if args.comando == "tabelas":
        return executar_tabelas()

    if args.comando == "dimensionar":
        return executar_dimensionar(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

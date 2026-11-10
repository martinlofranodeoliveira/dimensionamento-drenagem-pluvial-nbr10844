from __future__ import annotations

import json
from fractions import Fraction
from typing import Any, Dict, List, Optional

from drenagem_pluvial_nbr10844.models import (
    DadosChuva,
    ParedeVertical,
    SuperficieContribuicao,
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


def _rejeitar_float(valor: str) -> None:
    raise ValueError(
        f"Ponto flutuante IEEE-754 '{valor}' detectado no JSON. "
        "O padrão LOFRANO TECNOLOGIA exige Zero Float (inteiros ou frações exatas com 'num' e 'den')."
    )


def _par_sem_duplicatas(pares: List[tuple[str, Any]]) -> Dict[str, Any]:
    resultado: Dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada detectada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def serializar_fracao(f: Fraction) -> Dict[str, int]:
    """Serializa uma fração em representação exata canônica."""
    return {"num": f.numerator, "den": f.denominator}


def deserializar_fracao(d: Any) -> Fraction:
    """Deserializa um valor em Fraction sem admitir float."""
    if isinstance(d, Fraction):
        return d
    if isinstance(d, int):
        return Fraction(d, 1)
    if isinstance(d, dict) and "num" in d and "den" in d:
        if not isinstance(d["num"], int) or not isinstance(d["den"], int):
            raise ValueError("Numerador e denominador devem ser inteiros.")
        return Fraction(d["num"], d["den"])
    if isinstance(d, str):
        if "/" in d:
            partes = d.split("/")
            if len(partes) == 2:
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        return Fraction(d)
    raise ValueError(f"Formato inválido para fração: {d}")


def converter_para_dict(obj: Any) -> Any:
    """Converte estruturas de dados e dataclasses em dicionários canônicos sem float."""
    if isinstance(obj, Fraction):
        return serializar_fracao(obj)
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    if isinstance(obj, float):
        raise ValueError(f"Valor float {obj} detectado durante serialização canônica.")
    if isinstance(obj, list):
        return [converter_para_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): converter_para_dict(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}
    if hasattr(obj, "__dataclass_fields__"):
        res: Dict[str, Any] = {}
        for campo in obj.__dataclass_fields__:
            val = getattr(obj, campo)
            res[campo] = converter_para_dict(val)
        return res
    raise TypeError(f"Tipo não serializável para JSON canônico: {type(obj)}")


def verificar_profundidade(obj: Any, nivel_atual: int = 1, max_nivel: int = 32) -> None:
    """Garante que o JSON não exceda o limite de 32 níveis de profundidade."""
    if nivel_atual > max_nivel:
        raise ValueError(f"Profundidade máxima de aninhamento ({max_nivel}) excedida.")
    if isinstance(obj, dict):
        for v in obj.values():
            verificar_profundidade(v, nivel_atual + 1, max_nivel)
    elif isinstance(obj, list):
        for item in obj:
            verificar_profundidade(item, nivel_atual + 1, max_nivel)


def carregar_json_canonico(texto_ou_caminho: str) -> Dict[str, Any]:
    """Carrega dados JSON com garantias estritas: sem BOM, sem floats, sem chaves duplicadas."""
    if "\n" not in texto_ou_caminho and (texto_ou_caminho.endswith(".json") or len(texto_ou_caminho) < 256):
        import os
        if os.path.exists(texto_ou_caminho):
            with open(texto_ou_caminho, "rb") as f:
                bytes_conteudo = f.read()
                if bytes_conteudo.startswith(b"\xef\xbb\xbf"):
                    raise ValueError("BOM UTF-8 não permitido no padrão canônico.")
                texto = bytes_conteudo.decode("utf-8")
        else:
            texto = texto_ou_caminho
    else:
        texto = texto_ou_caminho

    if texto.startswith("\ufeff"):
        raise ValueError("BOM UTF-8 não permitido no padrão canônico.")

    dados = json.loads(
        texto,
        parse_float=_rejeitar_float,
        object_pairs_hook=_par_sem_duplicatas,
    )
    verificar_profundidade(dados, 1, 32)
    return dados


def salvar_json_canonico(caminho: str, dados: Any) -> None:
    """Salva dados em formato JSON canônico formatado e determinístico."""
    dict_puro = converter_para_dict(dados)
    verificar_profundidade(dict_puro, 1, 32)
    texto = json.dumps(
        dict_puro,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
        f.write("\n")


def deserializar_projeto(dados: Dict[str, Any]) -> ProjetoDrenagem:
    """Reconstrói um objeto ProjetoDrenagem a partir de um dicionário deserializado."""
    identificacao = dados.get("identificacao", "Projeto Sem Nome")
    
    # Chuva
    d_chuva = dados["chuva"]
    cidade = d_chuva.get("cidade", "")
    uf = d_chuva.get("uf", "")
    t_retorno = int(d_chuva.get("periodo_retorno_anos", 5))
    duracao = int(d_chuva.get("duracao_minutos", 5))
    i_mm_h = deserializar_fracao(d_chuva.get("intensidade_mm_h", {"num": 150, "den": 1}))
    chuva = DadosChuva(
        cidade=cidade,
        uf=uf,
        periodo_retorno_anos=t_retorno,
        duracao_minutos=duracao,
        intensidade_mm_h=i_mm_h,
    )
    
    # Superficie
    d_sup = dados["superficie"]
    id_sup = d_sup.get("identificacao", "Superfície Principal")
    area_h = deserializar_fracao(d_sup["area_horizontal_m2"])
    tipo_sup = d_sup.get("tipo_superficie", "cobertura_metalica")
    c_esc = deserializar_fracao(d_sup.get("coeficiente_escoamento", {"num": 1, "den": 1}))
    
    paredes: List[ParedeVertical] = []
    if "paredes" in d_sup and isinstance(d_sup["paredes"], list):
        for p in d_sup["paredes"]:
            paredes.append(
                ParedeVertical(
                    identificacao=p.get("identificacao", "Parede"),
                    altura_m=deserializar_fracao(p["altura_m"]),
                    largura_m=deserializar_fracao(p["largura_m"]),
                )
            )
    
    superficie = SuperficieContribuicao(
        identificacao=id_sup,
        area_horizontal_m2=area_h,
        tipo_superficie=tipo_sup,
        paredes=paredes,
        coeficiente_escoamento=c_esc,
    )
    
    # Calha
    calha: Optional[Calha] = None
    if "calha" in dados and dados["calha"] is not None:
        dc = dados["calha"]
        calha = Calha(
            identificacao=dc.get("identificacao", "Calha 1"),
            tipo_secao=dc.get("tipo_secao", "retangular"),
            material=dc.get("material", "pvc"),
            largura_fundo_mm=deserializar_fracao(dc.get("largura_fundo_mm", {"num": 150, "den": 1})),
            largura_topo_mm=deserializar_fracao(dc.get("largura_topo_mm", {"num": 150, "den": 1})),
            altura_total_mm=deserializar_fracao(dc.get("altura_total_mm", {"num": 120, "den": 1})),
            lamina_dagua_mm=deserializar_fracao(dc["lamina_dagua_mm"]) if "lamina_dagua_mm" in dc and dc["lamina_dagua_mm"] is not None else None,
            declividade_m_m=deserializar_fracao(dc.get("declividade_m_m", {"num": 1, "den": 100})),
            comprimento_m=deserializar_fracao(dc.get("comprimento_m", {"num": 10, "den": 1})),
        )
    
    # Condutor Vertical
    condutor_v: Optional[CondutorVertical] = None
    if "condutor_vertical" in dados and dados["condutor_vertical"] is not None:
        dcv = dados["condutor_vertical"]
        condutor_v = CondutorVertical(
            identificacao=dcv.get("identificacao", "TQ 1"),
            dn_mm=int(dcv.get("dn_mm", 100)),
            tipo_bocal=dcv.get("tipo_bocal", "reto"),
            altura_m=deserializar_fracao(dcv.get("altura_m", {"num": 6, "den": 1})),
        )
    
    # Condutor Horizontal
    condutor_h: Optional[CondutorHorizontal] = None
    if "condutor_horizontal" in dados and dados["condutor_horizontal"] is not None:
        dch = dados["condutor_horizontal"]
        condutor_h = CondutorHorizontal(
            identificacao=dch.get("identificacao", "CH 1"),
            dn_mm=int(dch.get("dn_mm", 100)),
            material=dch.get("material", "pvc"),
            declividade_m_m=deserializar_fracao(dch.get("declividade_m_m", {"num": 1, "den": 100})),
            comprimento_m=deserializar_fracao(dch.get("comprimento_m", {"num": 15, "den": 1})),
            relacao_lamina_max=deserializar_fracao(dch.get("relacao_lamina_max", {"num": 2, "den": 3})),
        )
    
    # Ralo
    ralo: Optional[Ralo] = None
    if "ralo" in dados and dados["ralo"] is not None:
        dr = dados["ralo"]
        ralo = Ralo(
            identificacao=dr.get("identificacao", "Ralo 1"),
            tipo_ralo=dr.get("tipo_ralo", "hemisferico"),
            dn_mm=int(dr.get("dn_mm", 100)),
        )
    
    # Caixa Areia
    caixa_areia: Optional[CaixaAreia] = None
    if "caixa_areia" in dados and dados["caixa_areia"] is not None:
        dca = dados["caixa_areia"]
        caixa_areia = CaixaAreia(
            identificacao=dca.get("identificacao", "Caixa de Areia 1"),
            largura_mm=int(dca.get("largura_mm", 400)),
            comprimento_mm=int(dca.get("comprimento_mm", 400)),
            altura_util_mm=int(dca.get("altura_util_mm", 400)),
            altura_sedimentacao_mm=int(dca.get("altura_sedimentacao_mm", 200)),
        )
    
    return ProjetoDrenagem(
        identificacao=identificacao,
        chuva=chuva,
        superficie=superficie,
        calha=calha,
        condutor_vertical=condutor_v,
        condutor_horizontal=condutor_h,
        ralo=ralo,
        caixa_areia=caixa_areia,
    )

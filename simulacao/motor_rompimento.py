import math
from dados.referencias import (
    CORREDOR_FLUVIAL_CARAJAS,
    PONTOS_CRITICOS_REFERENCIA,
    PONTOS_FUGA_REFERENCIA,
)


def distancia_haversine_km(lat1, lon1, lat2, lon2):
    raio_terra_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return raio_terra_km * c


def calcular_simulacao_rompimento(barragem, percentual_ruptura=100.0, velocidade_kmh=22.0):
    perc = max(5.0, min(100.0, float(percentual_ruptura)))
    vel = max(5.0, min(60.0, float(velocidade_kmh)))

    altura_m = float(barragem.get("altura_m", 30.0))
    volume_total_m3 = float(barragem.get("volume_m3", 10000000.0))

    fator_liberacao = (perc / 100.0) ** 0.85
    volume_liberado_m3 = volume_total_m3 * fator_liberacao
    volume_milhoes_m3 = max(0.01, volume_liberado_m3 / 1_000_000.0)

    alcance_km = 14.45 * ((volume_milhoes_m3 * max(1.0, altura_m)) ** 0.46)
    alcance_km = round(max(2.0, min(alcance_km, 120.0)), 2)

    zas_km = round(max(10.0, vel * 0.5), 2)
    tempo_alcance_min = round((alcance_km / vel) * 60.0, 1)
    area_afetada_km2 = round(math.pi * (alcance_km ** 2) * 0.35, 2)

    pontos_afetados = []
    for ponto in PONTOS_CRITICOS_REFERENCIA:
        dist_km = round(
            distancia_haversine_km(
                barragem["lat"], barragem["lon"], ponto["lat"], ponto["lon"]
            ),
            2,
        )
        if dist_km <= alcance_km:
            tempo_chegada_min = round((dist_km / vel) * 60.0, 1)
            nivel = "ZAS (Crítico)" if dist_km <= zas_km else "Zona Secundária"
            pontos_afetados.append(
                {
                    "nome": ponto["nome"],
                    "tipo": ponto["tipo"],
                    "lat": ponto["lat"],
                    "lon": ponto["lon"],
                    "distancia_km": dist_km,
                    "tempo_chegada_min": tempo_chegada_min,
                    "nivel": nivel,
                    "populacao_ref": ponto.get("populacao_ref", 0),
                    "edificacoes_ref": ponto.get("edificacoes_ref", 0),
                }
            )

    pontos_afetados.sort(key=lambda item: item["distancia_km"])

    rotas_atingimento = [
        {
            "destino": p["nome"],
            "tipo": p["tipo"],
            "distancia_km": p["distancia_km"],
            "tempo_chegada_min": p["tempo_chegada_min"],
            "nivel": p["nivel"],
            "coordenadas": [
                [float(barragem["lat"]), float(barragem["lon"])],
                [p["lat"], p["lon"]],
            ],
        }
        for p in pontos_afetados
    ]

    pontos_fuga = []
    rotas_fuga = []
    vel_evacuacao_kmh = 30.0

    for pf in PONTOS_FUGA_REFERENCIA:
        dist_barragem_km = round(
            distancia_haversine_km(
                barragem["lat"], barragem["lon"], pf["lat"], pf["lon"]
            ),
            2,
        )
        fora_do_alcance = dist_barragem_km > alcance_km
        tempo_desloc_min = round((dist_barragem_km / vel_evacuacao_kmh) * 60.0, 1)

        status_fuga = (
            "Seguro (Fora do Alcance)"
            if fora_do_alcance
            else "Atenção (Dentro do Raio Simulado)"
        )
        pontos_fuga.append(
            {
                "nome": pf["nome"],
                "tipo": pf["tipo"],
                "lat": pf["lat"],
                "lon": pf["lon"],
                "distancia_barragem_km": dist_barragem_km,
                "tempo_deslocamento_min": tempo_desloc_min,
                "seguro": fora_do_alcance,
                "status": status_fuga,
            }
        )

        if fora_do_alcance:
            rotas_fuga.append(
                {
                    "destino": pf["nome"],
                    "tipo": pf["tipo"],
                    "distancia_km": dist_barragem_km,
                    "tempo_deslocamento_min": tempo_desloc_min,
                    "coordenadas": [
                        [float(barragem["lat"]), float(barragem["lon"])],
                        [pf["lat"], pf["lon"]],
                    ],
                }
            )

    pontos_fuga.sort(key=lambda item: (not item["seguro"], item["distancia_barragem_km"]))

    rota_fluvial = [[float(barragem["lat"]), float(barragem["lon"])]]
    marcos_fluviais = []
    distancia_acumulada_km = 0.0
    lat_atual, lon_atual = float(barragem["lat"]), float(barragem["lon"])

    for marco in CORREDOR_FLUVIAL_CARAJAS:
        trecho_km = distancia_haversine_km(lat_atual, lon_atual, marco["lat"], marco["lon"])
        distancia_acumulada_km += trecho_km
        rota_fluvial.append([marco["lat"], marco["lon"]])
        lat_atual, lon_atual = marco["lat"], marco["lon"]

        atingido_no_alcance = distancia_acumulada_km <= alcance_km
        tempo_min = round((distancia_acumulada_km / vel) * 60.0, 1)
        marcos_fluviais.append(
            {
                "nome": marco["nome"],
                "tipo": marco["tipo"],
                "lat": marco["lat"],
                "lon": marco["lon"],
                "distancia_acumulada_km": round(distancia_acumulada_km, 1),
                "tempo_chegada_min": tempo_min,
                "atingido_no_alcance": atingido_no_alcance,
            }
        )

    marcos_atingidos = [m for m in marcos_fluviais if m["atingido_no_alcance"]]
    chega_ao_mar_no_cenario = any("Mar" in m["tipo"] for m in marcos_atingidos)

    pontos_na_zas = [p for p in pontos_afetados if "ZAS" in p["nivel"]]
    pontos_zona_secundaria = [p for p in pontos_afetados if "Secundária" in p["nivel"]]
    pontos_fuga_seguros = [pf for pf in pontos_fuga if pf["seguro"]]

    pop_zas = sum(p.get("populacao_ref", 0) for p in pontos_na_zas)
    pop_secundaria = sum(p.get("populacao_ref", 0) for p in pontos_zona_secundaria)
    edif_zas = sum(p.get("edificacoes_ref", 0) for p in pontos_na_zas)
    edif_secundaria = sum(p.get("edificacoes_ref", 0) for p in pontos_zona_secundaria)

    quantitativo_expostos = {
        "pontos_na_zas": len(pontos_na_zas),
        "pontos_zona_secundaria": len(pontos_zona_secundaria),
        "total_pontos_atingidos": len(pontos_afetados),
        "pontos_fuga_seguros": len(pontos_fuga_seguros),
        "populacao_zas_est": pop_zas,
        "populacao_secundaria_est": pop_secundaria,
        "populacao_total_est": pop_zas + pop_secundaria,
        "edificacoes_zas_est": edif_zas,
        "edificacoes_secundaria_est": edif_secundaria,
        "edificacoes_total_est": edif_zas + edif_secundaria,
    }

    return {
        "barragem": barragem,
        "parametros": {
            "percentual_ruptura": perc,
            "velocidade_kmh": vel,
        },
        "resultados": {
            "volume_liberado_m3": round(volume_liberado_m3, 0),
            "volume_liberado_hm3": round(volume_milhoes_m3, 2),
            "alcance_max_km": alcance_km,
            "zas_raio_km": zas_km,
            "tempo_alcance_min": tempo_alcance_min,
            "area_afetada_km2": area_afetada_km2,
            "total_pontos_afetados": len(pontos_afetados),
            "total_marcos_fluviais_atingidos": len(marcos_atingidos),
            "chega_ao_mar_no_cenario": chega_ao_mar_no_cenario,
        },
        "quantitativo_expostos": quantitativo_expostos,
        "pontos_afetados": pontos_afetados,
        "rotas_atingimento": rotas_atingimento,
        "pontos_fuga": pontos_fuga,
        "rotas_fuga": rotas_fuga,
        "rota_fluvial": rota_fluvial,
        "marcos_fluviais": marcos_fluviais,
    }

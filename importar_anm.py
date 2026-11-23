import csv
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SAIDA = os.path.join(BASE_DIR, "barragens_vale_pa.json")

MUNICIPIOS_CARAJAS = {
    "parauapebas",
    "canaa dos carajas",
    "canaã dos carajás",
    "curionopolis",
    "curionópolis",
    "eldorado dos carajas",
    "eldorado dos carajás",
}


def _limpar_numero(valor):
    if valor is None:
        return 0.0
    texto = str(valor).strip().replace(" ", "")
    if not texto or texto in ("-", "N/A", "Nao se aplica", "Não se aplica"):
        return 0.0
    # Trata vírgula decimal (ex.: 1234,56 ou 1.234,56)
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


def _slug(texto):
    limpo = re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")
    return limpo or "barragem"


def importar_csv_anm(caminho_csv):
    with open(caminho_csv, "r", encoding="utf-8-sig", errors="replace") as f:
        amostra = f.read(2048)
        f.seek(0)
        delimitador = ";" if amostra.count(";") > amostra.count(",") else ","
        leitor = csv.DictReader(f, delimiter=delimitador)

        barragens_filtradas = []
        for idx, linha in enumerate(leitor, start=1):
            # Normaliza nomes de colunas para facilitar compatibilidade com variações do CSV da ANM
            colunas = {k.strip().lower(): v.strip() for k, v in linha.items() if k}

            mun = colunas.get("municipio") or colunas.get("município") or ""
            uf = colunas.get("uf") or ""
            if mun.lower() not in MUNICIPIOS_CARAJAS and uf.upper() != "PA":
                continue
            if uf and uf.upper() != "PA":
                continue
            if mun and mun.lower() not in MUNICIPIOS_CARAJAS:
                continue

            nome = (
                colunas.get("nome da barragem")
                or colunas.get("nome")
                or f"Barragem ANM {idx}"
            )
            empreendedor = (
                colunas.get("empreendedor")
                or colunas.get("nome do empreendedor")
                or "Não informado"
            )
            lat = _limpar_numero(
                colunas.get("latitude") or colunas.get("lat")
            )
            lon = _limpar_numero(
                colunas.get("longitude") or colunas.get("lon") or colunas.get("long")
            )
            if lat == 0.0 or lon == 0.0:
                continue

            altura_m = _limpar_numero(
                colunas.get("altura atual (m)")
                or colunas.get("altura (m)")
                or colunas.get("altura")
            )
            volume_m3 = _limpar_numero(
                colunas.get("volume atual (m³)")
                or colunas.get("volume atual (m3)")
                or colunas.get("volume (m³)")
                or colunas.get("volume")
            )
            cri = colunas.get("cri") or colunas.get("categoria de risco") or "Não classificado"
            dpa = colunas.get("dpa") or colunas.get("dano potencial associado") or "Não classificado"
            zas_texto = (colunas.get("zas") or colunas.get("possui zas") or "").lower()
            possui_zas = zas_texto in ("sim", "s", "true", "1", "possui")

            barragens_filtradas.append(
                {
                    "id": f"{_slug(nome)}-{idx}",
                    "nome": nome,
                    "complexo": "Região de Carajás (SIGBM/ANM)",
                    "empreendedor": empreendedor,
                    "municipio": f"{mun} - {uf}".strip(" -"),
                    "lat": lat,
                    "lon": lon,
                    "altura_m": altura_m if altura_m > 0 else 25.0,
                    "volume_m3": volume_m3 if volume_m3 > 0 else 5000000.0,
                    "cri": cri,
                    "dpa": dpa,
                    "possui_zas": possui_zas,
                }
            )

    payload = {
        "fonte": f"Importado de {os.path.basename(caminho_csv)} (SIGBM / ANM)",
        "barragens": barragens_filtradas,
    }
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as out:
        json.dump(payload, out, ensure_ascii=False, indent=2)

    print(f"Importadas {len(barragens_filtradas)} barragens para {ARQUIVO_SAIDA}.")


if __name__ == "__main__":
    csv_padrao = os.path.join(BASE_DIR, "sigbm_anm.csv")
    if os.path.exists(csv_padrao):
        importar_csv_anm(csv_padrao)
    else:
        print("Coloque o arquivo CSV baixado do SIGBM/ANM como 'sigbm_anm.csv' nesta pasta e rode novamente.")

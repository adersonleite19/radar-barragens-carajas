PONTOS_CRITICOS_REFERENCIA = [
    {
        "nome": "Núcleo Urbano / Centro - Parauapebas",
        "tipo": "Área Urbana",
        "lat": -6.0678,
        "lon": -49.9022,
        "populacao_ref": 45000,
        "edificacoes_ref": 11200,
    },
    {
        "nome": "Hospital Municipal de Parauapebas (HMP)",
        "tipo": "Saúde",
        "lat": -6.0715,
        "lon": -49.8980,
        "populacao_ref": 800,
        "edificacoes_ref": 12,
    },
    {
        "nome": "Vila Carajás / Núcleo Residencial",
        "tipo": "Comunidade",
        "lat": -6.0580,
        "lon": -50.1450,
        "populacao_ref": 6500,
        "edificacoes_ref": 1650,
    },
    {
        "nome": "Vila Palmares II",
        "tipo": "Comunidade",
        "lat": -6.0380,
        "lon": -49.7950,
        "populacao_ref": 14000,
        "edificacoes_ref": 3500,
    },
    {
        "nome": "Centro Urbano - Canaã dos Carajás",
        "tipo": "Área Urbana",
        "lat": -6.4980,
        "lon": -49.8760,
        "populacao_ref": 28000,
        "edificacoes_ref": 7100,
    },
    {
        "nome": "Vila Bom Jesus / Região S11D",
        "tipo": "Comunidade",
        "lat": -6.3650,
        "lon": -50.2450,
        "populacao_ref": 4200,
        "edificacoes_ref": 1050,
    },
]

PONTOS_FUGA_REFERENCIA = [
    {
        "nome": "Ponto de Apoio / Acesso Elevado - Mina Carajás",
        "tipo": "Fuga na Mina (Acesso/Cota Alta)",
        "lat": -6.0280,
        "lon": -50.1650,
    },
    {
        "nome": "Base Operacional / Rota Interna Norte",
        "tipo": "Fuga na Mina (Setor Externo)",
        "lat": -5.9450,
        "lon": -50.0950,
    },
    {
        "nome": "Ponto Seguro / Acesso Sul (Canaã / PA-160)",
        "tipo": "Fuga Externa (Rodovia/Acesso)",
        "lat": -6.4800,
        "lon": -49.8900,
    },
    {
        "nome": "Área de Reunião / Apoio Leste (Parauapebas)",
        "tipo": "Fuga Externa (Zona Alta)",
        "lat": -6.1350,
        "lon": -49.7600,
    },
]

CORREDOR_FLUVIAL_CARAJAS = [
    {
        "nome": "Drenagem / Igarapé Local (Carajás)",
        "tipo": "Rio / Igarapé",
        "lat": -6.0450,
        "lon": -49.9100,
    },
    {
        "nome": "Rio Parauapebas (Trecho Médio)",
        "tipo": "Rio",
        "lat": -5.9200,
        "lon": -49.8200,
    },
    {
        "nome": "Rio Itacaiúnas (Baixo Curso)",
        "tipo": "Rio Principal",
        "lat": -5.4500,
        "lon": -49.2500,
    },
    {
        "nome": "Marabá — PA (Encontro Itacaiúnas / Tocantins)",
        "tipo": "Cidade / Rio Tocantins",
        "lat": -5.3686,
        "lon": -49.1178,
    },
    {
        "nome": "Tucuruí — PA (Rio Tocantins)",
        "tipo": "Cidade / Rio Tocantins",
        "lat": -3.7661,
        "lon": -49.6725,
    },
    {
        "nome": "Cametá — PA (Baixo Tocantins)",
        "tipo": "Cidade / Rio Tocantins",
        "lat": -2.2444,
        "lon": -49.4958,
    },
    {
        "nome": "Foz / Estuário do Pará — Atlântico (PA)",
        "tipo": "Litoral / Mar (Estuário)",
        "lat": -0.6000,
        "lon": -48.5000,
    },
]

BARRAGEM_PADRAO = {
    "id": "carajas-gelado",
    "nome": "Barragem do Gelado",
    "mina": "Mina de Carajás (N4 / N5)",
    "complexo": "Complexo Carajás",
    "regiao": "Carajás / Parauapebas",
    "empreendedor": "VALE S.A.",
    "municipio": "Parauapebas - PA",
    "lat": -6.0120,
    "lon": -49.9650,
    "altura_m": 42.0,
    "volume_m3": 18500000.0,
    "cri": "Baixa",
    "dpa": "Alto",
    "possui_zas": True,
    "situacao_atual": "Monitoramento contínuo por instrumentação e telemetria na região de Carajás.",
}

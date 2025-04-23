from flask import Flask, jsonify, request
import random
import time
import logging
from influxdb_client import InfluxDBClient, QueryApi  # Importar cliente InfluxDB


# Configurações do InfluxDB (as mesmas do código freezers.txt)
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = ""
INFLUXDB_ORG = ""
INFLUXDB_BUCKET = ""
LOKI_ENDPOINT = "http://localhost:3100/loki/api/v1/push"
logger = logging.getLogger(__name__)

app = Flask(__name__)


frutas = [
    {"nome": "Maçã", "tipo": "temperada", "freezer_id": "FRZ001", "preco": 5.50, "vendas": 10},
    {"nome": "Banana", "tipo": "tropical", "freezer_id": "FRZ002", "preco": 6.80, "vendas": 5},
    {"nome": "Laranja", "tipo": "intermediaria", "freezer_id": "FRZ003", "preco": 7.00, "vendas": 8},
]


# Faixas de temperatura ideais e impacto nas vendas
temperaturas_ideais = {
    "temperada": {"min": 0, "max": 4, "reducao_por_grau": 0.9},  # 10% por grau fora da faixa
    "tropical": {"min": 10, "max": 13, "reducao_por_grau": 3}, # 8% por grau fora da faixa
    "intermediaria": {"min": 3, "max": 8, "reducao_por_grau": 0.6} # 9% por grau fora da faixa
}


def get_temperatura_freezer(freezer_id):
    """Busca a temperatura mais recente de um freezer no InfluxDB."""
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
    query = f"""
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -5m)
        |> filter(fn: (r) => r["_measurement"] == "temperatura")
        |> filter(fn: (r) => r["_field"] == "valor")
        |> filter(fn: (r) => r["freezer_id"] == "{freezer_id}")
        |> last()
    """
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    temperatura = None
    if result:
        for table in result:
            for record in table.records:
                temperatura = record.get_value()
    client.close()
    return temperatura



def atualizar_vendas(frutas):
    """Atualiza as vendas das frutas com base na temperatura do freezer."""
    for fruta in frutas:
        temperatura = get_temperatura_freezer(fruta["freezer_id"])
        print(temperatura)
        if temperatura is not None:
            tipo = fruta["tipo"]
            faixa_ideal = temperaturas_ideais[tipo]
            if temperatura < faixa_ideal["min"] or temperatura > faixa_ideal["max"]:
                desvio = abs(temperatura - (faixa_ideal["min"] if temperatura < faixa_ideal["min"] else faixa_ideal["max"]))
                reducao = faixa_ideal["reducao_por_grau"] * desvio
                fruta["vendas"] += random.randint(0, 1)
                #fruta["vendas"] = max(0, int(fruta["vendas"] * (1 - reducao) + 1))  # Reduz as vendas
            else:
                fruta["vendas"] += random.randint(3, 6)  # Vendas normais
        else:
            fruta["vendas"] += random.randint(5, 10)  # Vendas normais se não houver temperatura
        
        # Garante que o preço nunca seja menor que R$ 5,00
        fruta["preco"] += random.uniform(-1.50, 1.50)
        fruta["preco"] = max(5.00, round(fruta["preco"], 2))
    return frutas


@app.route('/frutas')
def get_frutas():
    start_time = time.time()
    frutas_atualizadas = atualizar_vendas(frutas)  # Atualiza as vendas
    response = jsonify(frutas_atualizadas)
    end_time = time.time()
    response_time = round((end_time - start_time) * 1000, 2)  # in milliseconds


    # Lógica de লগ para Loki (mantenha como está)
    log_data = {
        "streams": [
            {
                "stream": {"app": "api-frutas"},
                "values": [
                    (
                        str(int(time.time_ns())),
                        f"HTTP {response.status_code} - {response_time}ms - {request.path}"
                    )
                ],
            }
        ]
    }
    try:
        import requests
        requests.post(LOKI_ENDPOINT, json=log_data)
        logger.info(f"Logs sent to Loki: HTTP {response.status_code} - {response_time}ms - {request.path}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Loki: {e}")
    except Exception as e:
        logger.error(f"Error sending logs to Loki: {e}")


    return response
 

if __name__ == '__main__':
    app.run(debug=True, port=5000)

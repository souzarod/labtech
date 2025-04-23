import time
import random
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# Configurações do InfluxDB
INFLUXDB_URL = "http://localhost:8086"  # Substitua pelo seu URL do InfluxDB
INFLUXDB_TOKEN = "0GDOWgE5cMS-99Sr8HcqNs3kiUraAKRaWiaPUG_AuKEEm9xWBlOd4D62Zrr3ic5mfpQvN4BbVTqty9UmVdY2pA=="  # Substitua pelo seu token do InfluxDB
INFLUXDB_ORG = "5efe2135bd9e19a3"  # Substitua pela sua organização no InfluxDB
INFLUXDB_BUCKET = "demotech"  # Substitua pelo nome do seu bucket

# Lista de freezers e seus tipos de frutas
freezers = [
    {"id": "FRZ001", "tipo_fruta": "temperada"},
    {"id": "FRZ002", "tipo_fruta": "tropical"},
    {"id": "FRZ003", "tipo_fruta": "intermediaria"},
]

def gerar_temperatura(tipo_fruta):
    """Gera uma temperatura aleatória dentro ou ligeiramente fora da faixa ideal."""
    desvio = random.choice([-1, -2, -3, 0, 0, 0, 1, 1, 2, 2])  # Maior chance de ficar dentro
    if tipo_fruta == "temperada":
        return [round(random.uniform(0, 4) + desvio, 2), desvio]
    elif tipo_fruta == "tropical":
        return [round(random.uniform(10, 13) + desvio, 2), desvio]
    elif tipo_fruta == "intermediaria":
        return [round(random.uniform(3, 8) + desvio, 2), desvio]
    return None

def enviar_temperatura_influxdb(client, freezer_id, tipo_fruta, temperatura):
    """Envia a temperatura para o InfluxDB."""
    point = Point("temperatura") \
        .tag("freezer_id", freezer_id) \
        .tag("tipo_fruta", tipo_fruta) \
        .field("valor", temperatura)

    write_api = client.write_api(write_options=WriteOptions(batch_size=1, flush_interval=10_000))
    try:
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print(f"Temperatura enviada: Freezer {freezer_id}, Tipo: {tipo_fruta}, Temp: {temperatura}°C")
    except Exception as e:
        print(f"Erro ao enviar para o InfluxDB: {e}")
    finally:
        write_api.close()

if __name__ == "__main__":
    # Inicializa o cliente do InfluxDB
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

    while True:
        for freezer in freezers:
            freezer_id = freezer["id"]
            tipo_fruta = freezer["tipo_fruta"]
            temperatura = gerar_temperatura(tipo_fruta)
            if temperatura is not None:
                enviar_temperatura_influxdb(client, freezer_id, tipo_fruta, temperatura[0])
        if temperatura[1] > 2:
            time.sleep(90)
        else:
            time.sleep(30)
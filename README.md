# labtech
Artefatos utilizados na demotech realizada em 23/04/2025 na faculdade cotemig

#Arquivos

* api.py -  Código em python que executa uma api para consulta de vendas das frutas . Este código se integra ao influxdb para consulta da temperatura atual dos freezers para simular a volatilidade de vendas de acordo com a mudança de temperatura
    
  > Neste arquivo é necessário incluir o bucket, token e orgId do influxdb a ser utilizado. Estes dados podem ser coletados após o deploy do serviço influxdb

* freezers.py - Código que envia a temperatura dos freezers para um bucket influxdb
  
  > Neste arquivo é necessário incluir o bucket, token e orgId do influxdb a ser utilizado. Estes dados podem ser coletados após o deploy do serviço influxdb
* docker-compose.yaml -  Arquivo usado para subir o laboratorio. Este laboratório é composto pelos seguintes serviços:
  * Zabbix Server
  * Zabbix FrontEnd
  * Grafana
  * Grafana Loki
  * Influxdb
  * Mysql
 
    > Para subir os serviços, é necessário ter o docker instalado na maquina
    >
    > Dentro do diretório raiz do repositório execute:  docker-compose up -d
    

# Links uteis para este laboratorio
- [Grafana Loki](https://grafana.com/oss/loki/)
- [Grafana](https://grafana.com/oss/grafana/)
- [Zabbix](https://www.zabbix.com/documentation/7.0/en)
- [InfluxDB](https://docs.influxdata.com/influxdb/v2/install/#download-and-install-influxdb-v2)

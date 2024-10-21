# Case_Breweries_Abinbev

O desafio deste case foi desenvolver um pipeline de dados para buscar, processar e armazenar informações de cervejarias a partir da API Open Brewery DB. O pipeline segue uma arquitetura em camadas (bronze, prata e ouro) para estruturar e transformar os dados ao longo do processo.

<img src="/imgs/arquiteture_draw.png" />

> 💾 esboço da arquitetura

## Sumário

* [Sumário](#sumário)
* [Resumo do Case](#resumo-do-case)
* [Tecnologias utilizadas](#tecnologias-utilizadas)
* [Arquitetura](#arquitetura)
* [Resolução](#resolução)
* [Pontos de melhorias](#pontos-de-melhorias)
* [Monitoring-Alerting](#monitoring-alerting)
* [Execução do projeto](#execução-do-projeto)
* [Conclusão](#conclusão)
* [Autor](#autor)


## Resumo do case

mkdir # todas essas pastas

sudo chmod -R 777 ./config ./src ./src/resources ./logs ./lakehouse ./lakehouse/bronze_layer ./lakehouse/silver_layer ./lakehouse/golden_layer ./monitoring

http://localhost:8080/ localhost:8080
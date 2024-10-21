# Case_Breweries_Abinbev

O desafio deste case foi desenvolver um pipeline de dados para buscar, processar e armazenar informações de cervejarias a partir da API Open Brewery DB. O pipeline segue uma arquitetura em camadas (bronze, prata e ouro) para estruturar e transformar os dados ao longo do processo.

<img src="/imgs/arquiteture_draw.png" />

> 💾 esboço da arquitetura


## Resumo dos principais conceitos e technologias utilizadas.
* Pipeline criada na DAG do Airflow
* Airflow rodando localmente dentro de um container (docker)
* Processamento realizado via Spark também dentro do container (docker)
* Armazenamento respeitando a arquitetura medalion (dados raw json, silver & gold delta  [lakehouse])
* Boas práticas em desenvolvimento de soluções, o código é mantido em módulos separados e bem documentados para facilitar a leitura e o debug.
* Brinquei um pouco com o conceito de dataquality na dag.
* Brinquei um pouco com o conceito de monitoramento.


Segue abaixo uma imagem do painel de controle das runs de nossa dag.

<img src="/imgs/dag_sample.png" />


#### Estrutura de diretórios e arquivos:
```
zcase_ambev/
├── config/
├── dags/
│   ├── brew_dag.py
├── lakehouse/
│   ├── bronze_layer/
│   ├── silver_layer/
│   ├── golden_layer/
│   ├── logs/
├── monitoring/
├── src/
│   ├── resources/
│   │   ├── brew_api/
│   │   │   ├── brewapi_bronze.py
│   │   ├── spark_utils/
│   │   │   ├── delta_spark.py
│   │   ├── utils/
│   │   │   ├── configs.json
│   │   │   ├── monitor.py
│   │   │   ├── utils.py
│   │   ├── validation/
│   │   │   ├── sample_validation.py
│   ├── api_to_bronze.py
│   ├── bronze_to_silver.py
│   ├── silver_to_gold.py
│   ├── validation.py
├── .gitignore
├── docker-compose.yaml
├── Dockerfile
├── README.md
├── requirements.txt
```

## Descrição da Dag [brew_dag.py]

<img src="/imgs/dag_brew.png" />

* Primeira task:
    * Responsável por extrair os dados da API e persistir seus dados na camada bronze.
* Segunda task:
    * Responsável por validar se os dados persistidos na camada bronze possuem o mesmo valor do endpoint "total" dos metadados da API. Aqui também temos uma validação na estrutura do schema dos dados da camada bronze.
* Terceira task:
    * Essa task é uma funcionalidade que confere se a validação da "Segunda task" deu certo, abrindo a opção de um caminho de dag secundário em caso de erro.
* Quarta task:
    * Responsável, em caso de erro (aqui estamos falando de um caso hipotético), por realizar alguma ação preventiva ou paliativa, exemplo: Enviar uma mensagem para o time de ingestão avisando sobre o erro da validação, ou realizar mais algumas tasks que buscam mitigar ou até voltar para a primeira task.
* Quinta task:
    * Responsável por consumir os dados da camada bronze, realizar transformações como remoção de caracteres especiais das colunas, garantir a transformação das colunas de latitude e longitude no formato float (dentro dos padrões corretos). A persistência de dados na camada silver é feita por arquivos do tipo delta, que possuem N vantagens. Aqui, de maneira breve, podemos falar sobre sua ótima performance. Por último, nos requisitos, era pedido para salvar os dados por região. Optamos, por motivos de performance, por escolher o país como coluna para partição, pois no nosso universo de dados atual, se a partição fosse feita por menor granularidade, poderíamos lidar com o problema de *small file* (se é que já não estamos lidando).
* Sexta task:
    * Responsável por consumir os dados da silver, realizar agregações pertinentes a regras de negócio, visando otimização na hora do consumo dos dados da camada gold (onde é feita a persistência após essas transformações). No caso aqui, é uma simples agregação:
    *groupBy('brewery_type', 'country', 'state', 'city').count()*
    
### Mais alguns detalhes sobre a DAG.

O conceito de validação foi explorado de maneira simples. O objetivo aqui era apenas trazer uma breve ideia sobre o caminho a ser seguido no quesito de qualidade de dados. Diversas implementações poderiam ser feitas, como: Sistema de mensageria (avisar os times), outras tasks adicionais (erros conhecidos e contornados de APIs inconsistentes). Entre as outras tasks, também poderiam ser feitas validações com regras de negócio (GreatExpectations por exemplo), testes diversos para garantir que os dados que estão sendo entregues para o DOWNSTREAM sejam de fato coerentes com a necessidade do cliente final.

Nas tasks principais (1, 5, 6), explorei de maneira simples o monitoramento das execuções, criando um diretório separado que registra o tempo de duração de cada task. Isso permite acompanhar o desempenho e identificar possíveis gargalos ou atrasos. Além disso, ferramentas como Prometheus ou Grafana podem ser integradas ao Airflow para fornecer um monitoramento mais detalhado, com dashboards que acompanham métricas como a duração das tasks e o número de execuções, facilitando a visualização e análise da performance do pipeline.


## Pontos de melhoria

Quando comecei o case, estava mirando em fazer no EKS (via Terraform e Argo), porém meu PC queimou (Minikube sem condições no PC fraquinho) no meio do processo (além da surra que tomei das permissões da AWS), e acabei com essa solução mais simples. Dito isso, vou listar os pontos de melhoria.

* Escalabilidade: Esta solução faz mau uso da computação distribuída do Spark. Atualmente, temos uma solução que roda o Spark em apenas um worker do Airflow, o que pode facilmente gerar gargalos em cenários produtivos. Portanto, a solução deve migrar para um ambiente onde o Spark possa escalar seus workers e ter alta disponibilidade. De imediato, penso na utilização do SPOK (Spark Operator for Kubernetes), permitindo uma conexão eficiente entre Spark, Airflow e Kubernetes, com alto desempenho.

* Esteiras de CI/CD: Aproveitando o gancho do Kubernetes, as esteiras de CI/CD têm um grande potencial para a próxima etapa da solução, garantindo uma infraestrutura como código (IaC) bem feita junto com o ArgoCD. As esteiras podem criar e destruir o cluster conforme a necessidade de negócio, proporcionando uma solução altamente elástica (FinOps agradece). Além disso, as esteiras podem incluir mais etapas de testes e segregação de ambientes, possibilitando mitigar ainda mais as falhas de desenvolvimento.

## Passos para executar o projeto.
### atenção projeto desenvolvido em ambiente ubunto
### Requisitos
docker 

* Clonar repo:
```sh
gitclone https://github.com/Gabriel-Philot/Case_Breweries_Abinbev.git
```
>[!Note]
> Deletar diretorios (menos src!!!) para iniciar do zero... (deixam fora do ignore pois estão dentro do contexto da solução)

* Criar dirs necessarios para a solução:
```sh
mkdir -p ./config ./src ./src/resources ./logs ./lakehouse ./lakehouse/bronze_layer ./lakehouse/silver_layer ./lakehouse/golden_layer ./monitoring
```
* Facilitar permissões do linux...:
```sh
sudo chmod -R 777 ./config ./src ./src/resources ./logs ./lakehouse ./lakehouse/bronze_layer ./lakehouse/silver_layer ./lakehouse/golden_layer ./monitoring
```

* criar sua imagem docker no root:
```sh
docker build -t {nome da sua imagem} .
```

> [!Note]
> Atenção para alterar o nome no compose na linha 52

```sh
docker compose up -d
```
apos o airflow subir


* acessar o webserver do airflow:
```sh
http://localhost:8080/
```
acessar a dag e por ela pra rodar.
# Problema de negócio

Empresa **STAR JEANS**

Eduardo e Marcelo são dois brasileiros, amigos e sócios de empreendimento. Depois de vários
negócio bem sucedidos, eles estão planejando entrar no mercado de moda dos USA como um
modelo de negócio do tipo E-commerce.

A idéia inicial é entrar no mercado com apenas um produto e para um público específico, no caso
o produto seria calças Jenas para o público masculino. O objetivo é manter o custo de operação
baixo e escalar a medida que forem conseguindo clientes.

Porém, mesmo com o produto de entrada e a audiência definidos, os dois sócios não tem experiência
nesse mercado de moda e portanto não sabem definir coisas básicas como preço, o tipo de calça e
o material para a fabricação de cada peça.

Assim, os dois sócios contrataram uma consultoria de Ciência de Dados para responder as seguintes
perguntas: 

   1. Qual o melhor preço de venda para as calças? 
   2. Quantos tipos de calças e suas cores para o produto inicial? 
   3. Quais as matérias-prima necessárias para confeccionar as calças?

As principais concorrentes da empresa Start Jeans são as americadas H&M e Macys.


# Planejamento para solução

## Problema de Negócio
Qual o melhor preço de venda para calças?

## Saída do Projeto ( Produto final )
1. A resposta para a pergunta
    - Mediana dos preços dos concorrentes
 
 
2. Formato da entrega
    - Tabela ou Gráfico
 
 
3. Local da entrega
    - App Streamlit


## Processo ( Passo a Passo )

1. Passo a passso para construir o cálculo da mediana ou média
    - Realizar o calculo da mediana sobre o produto, tipo e cor


2. Definir o formato da entrega ( Visualização, Tabela, Frase )
    - Gráfico de barras com a mediana dos preço dos produtos, por tipo e cor dos últimos 30 dias.
    - Tabela com as seguintes colunas: id | product_name | product_type | product_color | product_price
    - Definição do schema: Colunas e seu tipo
    - Definição a infraestrutura de armazenamento ( SQLITE3 )
    - Design do ETL ( Scripts de Extração, Transformação e Carga )
    - Planejamento de Agendamento dos scripts ( dependencias entre os scripts )
    - Fazer as visualizações
    - Entrega do produto final


3. Decidir o local de entrega ( PowerBi, Telegram, Email, Streamlit, Intranet )
    - App com Streamlit


## Entrada ( Fonte de dados )

### 1. Fonte de dados
- Site da H&M: https://www2.hm.com/en_us/men/products/jeans.html
- Site da Macys: https://www.macys.com/shop/mens-clothing/mens-jeans

### 2. Ferramentas
- Python 3.8.0
- Bibliotecas de Webscrapping ( BS4, Selenium )
- PyCharm
- Jupyter Notebook ( Analise e prototipagens )
- Crontjob, Airflow
- Streamlit
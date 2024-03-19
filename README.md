# Google Place Reviews

O Google Place Reviews é um projeto criado para resgatar e salvar as avaliações realizadas no restaurante de sua escolha presente no Google Maps. O projeto foi desenvolvido em Python para ser utilizado em um Serverless Framework, salvando as avalições em um banco de dados PostgreSQL. O projeto se utiliza da API SerpApi.

## Requisitos

- É necessário possuir uma chave válida da API **SerpApi**. 

- Serverless Instalado.
```
npm install -g serverless
```

## Instalação
Rode os comandos em ordem. 
```
python -m venv env
```
```
source ./env/Scripts/activate
```
```
pip install -r requirements.txt
```
```
npm install 
```
Atualize suas chaves no arquivo serverless.yml

## Teste de desenvolvimento local
Use o seguinte comando:
```
sls offline
```

## Deployment

```
serverless deploy
```
____

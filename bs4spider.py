import requests
from bs4 import BeautifulSoup

def AutorsSpider(autores_lista):
    urls = ["http://www.pesquisar.unb.br/professor/" + autor.replace(" ","-") for autor in autores_lista]
    dados_por_autor = {}

# Definição da função que faz o scraping com BeautifulSoup
    def scrape(url, autor):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        dados = soup.select('div.dadosAcademicos div a')
        dados = [dado.text for dado in dados]

# Verificando se os dados estão vazios
        if not dados:
            dados = ['-', '-']

        if autor in dados_por_autor:
            dados_por_autor[autor].extend(dados)
        else:
            dados_por_autor[autor] = dados

# Fazendo o scraping para cada url e autor
    for i, url in enumerate(urls):
        scrape(url, autores_lista[i])

# Retornando os dados coletados
    return dados_por_autor

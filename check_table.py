import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

def save_list_to_file(n_prot, filename):
    with open(filename, 'w') as file:
        for item in n_prot:
            file.write(f'{item}\n')

def check_table(arquivo):
    dados=[]
    n_prot=[]
    
    class InpiSpider(scrapy.Spider):
        name = "inpi"
        start_urls = ["https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login"]

        def parse(self, response):
            # Acessar a página de Programas de Computador
            next_page_link = response.css('area[data-mce-href="menu-servicos/programa-de-computador"]::attr(href)').get()
            yield response.follow(next_page_link, callback=self.parse_next_page)

        def parse_next_page(self, response):
            # Selecionar o CPF/CNPJ do Titular e inserir o CNPJ no campo
            yield scrapy.FormRequest.from_response(
                response,
                formdata={"Coluna": "CpfCnpjTitularPrograma", "ExpressaoPesquisa": "00038174000143", "RegisterPerPage":"100"},
                callback=self.extract_search
            )

        def extract_search(self, response):
            # Extrair e salvar o texto dos seletores na lista "dados"
            elementos_texto = response.css('a')

            for elemento in elementos_texto:
                texto = elemento.css('::text').get()
                if texto:
                    dados.append(texto.strip())

    # Inciar CrawlerProcess
    process = CrawlerProcess()

    # Rodar o spider
    process.crawl(InpiSpider)

    # Iniciar o processo
    process.start()
    
#Comparar valores com a tabela de resumo de proteções
    # Load the Excel file
    df = pd.read_excel(arquivo)

    # Convert the column to a set for faster comparison
    excel_column_set = set(df["Nº DA PROTEÇÃO"].astype(str))

    for item in dados:
        if item not in excel_column_set:
            n_prot.append(item)
    #return n_prot
    if len(n_prot) >= 13:  # Ensure that the list has at least 13 elements (8 + 5)
        n_prot = n_prot[8:-5]
    else:
        print("A lista não tem elementos suficientes!")
   
    # Print the list of protocols not present in the Excel column
    return n_prot

arquivo = "/workspaces/codespaces-blank/Novo resumos de proteções.xlsx"

n_prot = check_table(arquivo)
if not n_prot:
    print("\nPlanilha Atualizada! volte outro dia!\n")
else:
    print ("\nQuantidade de novas proteções: ", len(n_prot))
    print("Proteções Identificadas: ",n_prot, "\n")

save_list_to_file(n_prot, 'lista_de_protecoes.txt')

exit()
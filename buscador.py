import os 
import scrapy
from scrapy.crawler import CrawlerProcess

dados=[]

def save_list_to_file(n_prot, filename):
    with open(filename, 'w') as file:
        for item in n_prot:
            file.write(f'{item}\n')

def subs(entrada, saida):
    try:
        # Abre o arquivo de entrada no modo leitura
        with open(entrada, 'r') as arquivo_entrada:
            # Lê o conteúdo do arquivo
            conteudo = arquivo_entrada.read()
            
            # Substitui "-" por " "
            conteudo_modificado = conteudo.replace("-", " ")

        # Abre o arquivo de saída no modo escrita
        with open(saida, 'w') as arquivo_saida:
            # Escreve o conteúdo modificado no arquivo de saída
            arquivo_saida.write(conteudo_modificado)

        print("Substituição concluída com sucesso.")

    except FileNotFoundError:
        print(f"O arquivo '{entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")

def check():
    
    class InpiSpider(scrapy.Spider):
        name = "inpi"
        start_urls = ["https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login"]

        def parse(self, response):
            # Acessar a página de Patentes
            next_page_link = response.css('area[data-mce-href="menu-servicos/patente"]::attr(href)').get()
            yield response.follow(next_page_link, callback=self.parse_next_page)

        def parse_next_page(self, response):
            # Selecionar o CPF/CNPJ do Titular e inserir o CNPJ no campo
            yield scrapy.FormRequest.from_response(
                response,
                formdata={"Coluna": "CpfCnpjDepositante", "ExpressaoPesquisa": "00038174000143", "RegisterPerPage":"100"},
                callback=self.extract_search
            )

        def extract_search(self, response):
            # Extrair e salvar o texto dos seletores na lista "dados"
            elementos_texto = response.css('a')
            
            for elemento in elementos_texto:
                texto = elemento.css('a[class="visitado"]::text').get()
                if texto:
                    dados.append(texto.strip())
            
            next_page_link = response.css('a:contains("Próxima»")::attr(href)').get()
            yield response.follow(next_page_link, callback=self.extract_search2)


        def extract_search2(self, response):
            elementos_texto = response.css('a')

            for elemento in elementos_texto:
                texto = elemento.css('a[class="visitado"]::text').get()
                if texto:
                    dados.append(texto.strip())

            
            next_page_link = response.css('a:contains("Próxima»")::attr(href)').get()
            yield response.follow(next_page_link, callback=self.extract_search3)
        
        def extract_search3(self, response):
            elementos_texto = response.css('a')

            for elemento in elementos_texto:
                texto = elemento.css('a[class="visitado"]::text').get()
                if texto:
                    dados.append(texto.strip())
            
            print("número de proteções: ",len(dados))

    # Inciar CrawlerProcess
    process = CrawlerProcess()

    # Rodar o spider
    process.crawl(InpiSpider)

    # Iniciar o processo
    process.start()

    return dados

n_prot = check()

if not n_prot:
    print("\Algo deu errado!!!\n")
else:
    print ("\nQuantidade de novas proteções: ", len(n_prot))
    print("Proteções Identificadas: ",n_prot, "\n")


# Path para codespace
## save_list_to_file(n_prot, '/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt')

## arquivo_entrada = "/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt"
## arquivo_saida = "/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt"

# Paths generalizados
save_list_to_file(n_prot, os.path.expanduser("~/VarysNupitec/lista_prot.txt"))

arquivo_entrada = os.path.expanduser("~/VarysNupitec/lista_prot.txt")
arquivo_saida = os.path.expanduser("~/VarysNupitec/lista_prot.txt")

subs(arquivo_entrada, arquivo_saida)

import scrapy
from scrapy.crawler import CrawlerProcess

def extrator(prot):
    dados =[]

    class InpiSpider(scrapy.Spider):
        name = "inpi"
        start_urls = ["https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login"]

        def parse(self, response):
            # Acessar a página de Programas de Computador
            next_page_link = response.css('area[data-mce-href="menu-servicos/patente"]::attr(href)').get()
            yield response.follow(next_page_link, callback=self.parse_next_page)

        def parse_next_page(self, response):
            # Selecionar o CPF/CNPJ do Titular e inserir o CNPJ no campo
            yield scrapy.FormRequest.from_response(
                response,
                formdata={"NumPedido": prot},
                callback=self.next_page
            )
        def next_page(self, response):
            # Acessar a página de Programas de Computador
            next_page_link = response.css('a[class="visitado"]::attr(href)').get()
            yield response.follow(next_page_link, callback=self.extract_search)


        def extract_search(self, response):
        # Extrair e salvar o texto dos seletores na lista "dados"
            elementos_texto = response.css('a')

            for elemento in elementos_texto:
                texto = elemento.css('a.normal[href="javascript:void(0)"]::text').get()
                if texto:
                    dados.append(texto.strip())
            #print ("\ndados obtidos: ",dados,"\n")
    
    process = CrawlerProcess()
    process.crawl(InpiSpider)
    process.start()

    return dados

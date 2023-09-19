import scrapy
from scrapy.crawler import CrawlerProcess

dados = []

def protect(prot):

    class InpiSpider(scrapy.Spider):
        name = "inpi"
        start_urls = ["https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login"]

        def parse(self, response):
            next_page_link = response.css('area[data-mce-href="menu-servicos/patente"]::attr(href)').get()
            yield response.follow(next_page_link, callback=self.parse_next_page)

        def parse_next_page(self, response):
            yield scrapy.FormRequest.from_response(
                    response,
                    formdata={"NumPedido": prot},
                    callback=self.parse_patent_details,
                )

        def parse_patent_details(self, response):
            next_page_link = response.css('a[class="visitado"]::attr(href)').get()
            yield response.follow(next_page_link, callback=self.extract_search)

        def extract_search(self, response):
            elementos_texto = response.css('a')

            for elemento in elementos_texto:
                texto = elemento.css('a.normal[href="javascript:void(0)"]::text').get()
                if texto:
                    dados.append(texto.strip())
            
    # Crie uma função para iniciar o processo do crawler

    process = CrawlerProcess(settings={'LOG_ENABLED': False})
    process.crawl(InpiSpider)
    process.start()
    process.join()

    return dados

###################

nprot = ['BR 10 2013 033884 2', 'BR 10 2013 032983 5']

for prot in nprot:
    dados = protect(prot)
    print('\nDados obtidos: ',dados,'\n')
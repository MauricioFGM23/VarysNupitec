import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from twisted.internet.defer import DeferredList

deferreds = []
results = []
#nprot = ['BR 10 2020 002162 1']

def extract(prot):
    dados = []
      
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
            
    runner = CrawlerRunner()
    crawler = runner.create_crawler(InpiSpider)
    deferred = runner.crawl(crawler)

    return deferred, dados

#Números de Proteção:

with open('/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt', 'r') as f:
    nprot = f.readlines()
    nprot = [x.strip() for x in nprot]


for prot in nprot:
    deferred, result = extract(prot)
    deferreds.append(deferred)
    results.append(result)

dlist = DeferredList(deferreds)
dlist.addBoth(lambda _: reactor.stop()) # Parar o reactor após todos os spiders terminarem
reactor.run() # Iniciar o reactor apenas uma vez

i = 0
for prot in nprot:
    print(f"N° de processo {prot}, resultados {results[i]}")
    i+=1
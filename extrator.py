import scrapy
import pandas as pd
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from twisted.internet.defer import DeferredList

deferreds = []
results = []

nvigente = {'8.12':'8.12 - ARQ DEFINITIVO - FALTA DE PGT','11.1.1':'11.1.1 - ARQ DEFINITIVO - ANTERIORIDADE',
            '11.2':'11.2 - ARQ DEFINITIVO - EXIGÊNCIA','11.4':'11.4 - ARQ DEFINITIVO - PGT CARTA PATENTE',
            '11.6':'11.6 - ARQ DEFINITIVO - PROCURAÇÃO','11.11':'11.11 - ARQ DEFINITIVO - ANTERIORIDADE',
            '11.21':'11.21 - ARQ DEFINITIVO - PCT','18.3':'18.3 - CADUCIDADE DEFERIDA',
            '21.1':'21.1 - EXTINÇÃO - PGT','21.2':'EXTINÇÃO - RENÚNCIA','21.7':'EXTINÇÃO - NÃO CUMPRIMENTO',
            '11.20':'11.20 - ARQ - MANUTENÇÃO','9.2.4':'9.2.4 - MANUTENÇÃO DO INDEFERIMENTO',
            '111':'111 - MANTIDO O INDEFERIMENTO DO PEDIDO','112':'112 - MANTIDO O ARQUIVAMENTO DO PEDIDO',
            '113':'113 - MANTIDO O INDEFERIMENTO DA PETIÇÃO'}

vigente = {'9.1':'9.1 - DEFERIMENTO','16.1':'16.1 - CONCESSÃO DE CARTA PATENTE','203':'203 - EXAME TÉCNICO SOLICITADO','8.6':'8.6 - FALTA DE PAGAMENTO', '204':'204 - PEDIDO DE EXAME DE MU'}

analise_sub = {'16.1':'16.1 - CONCESSÃO DE CARTA PATENTE','18.3':'18.3 - CADUCIDADE DEFERIDA','21.1':'21.1 - EXTINÇÃO - PGT',
              '21.2':'EXTINÇÃO - RENÚNCIA','21.7':'EXTINÇÃO - NÃO CUMPRIMENTO','9.2':'9.2 - INDEFERIMENTO',
              '9.2.4':'9.2.4 - MANUTENÇÃO DO INDEFERIMENTO'}

def exigencia(exig,nprot):

    exig_nvig = []
    exig_ansu = []
    exig_vig = []

    for prot in nprot:
        print(f"Exigências encontradas para a proteção {prot}: ")

        for item in exig:
            if item in nvigente:
                exig_nvig.append(nvigente[item])
                #print('Análise de NÃO VIGENTE: ',nvigente[item])

            if item in vigente:
                exig_vig.append(vigente[item])
                #print('Análise de VIGENTE: ',vigente[item])
        
        for item in exig:
            if item in analise_sub:
                exig_ansu.append(analise_sub[item])
                #print('Análise substantiva: ',analise_sub[item])

        if not (exig_nvig):
            status = 0
            deferimento = '9.1'
            if deferimento not in vigente:
                exam_tec = '120'
                if exam_tec not in exig_ansu:
                    exig_ansu.append('- PARECER TÉCNICO EMITIDO -')
                
        else:
            status = 1

        if '203 - EXAME TÉCNICO SOLICITADO' not in exig_vig or '204 - PEDIDO DE EXAME DE MU' not in exig_vig:
            exig_ansu.append('- EXAME TÉCNICO AUSENTE!!! -')
            

        despacho = exig_nvig
        for item in exig_vig:
            despacho.append(item)

        exig_nvig = '; '.join(exig_nvig)
        exig_ansu = '; '.join(exig_ansu)
        despacho = '; '.join(despacho)

        if len(exig_ansu) > 0:
            print('Análises Substitutivas: ', exig_ansu)
        if len(despacho) > 0:
            print ('Despachos: ', despacho)

        try:
            df = pd.read_excel('$HOME/VarysNupitec/04. Resumo de proteções.xlsx')
            print("Arquivo Excel aberto com sucesso!")
        except Exception as erro:
            print("\nDocumento corrompido: ", erro, "\n")
            exit()

        if prot in df['Nº DA PROTEÇÃO'].values:
            linha = df[df['Nº DA PROTEÇÃO'] == prot].index[0]

        else:
            print(f'\nO {prot} não foi encontrado na coluna "Nº DA PROTEÇÃO".\n')
            df.to_excel('/workspaces/codespaces-jupyter/VarysPatente/04. Resumo de proteções.xlsx', index=False)
            break

        df.at[linha, 'DESPACHO'] = despacho
        df.at[linha, 'ANÁLISE SUBSTANTIVA'] = exig_ansu

        if status == 0:
            df.at[linha, 'STATUS'] = 'VIGENTE'
            print(f'O pedido {prot} está VIGENTE!\n')
        else:
            df.at[linha, 'STATUS'] = 'NÃO VIGENTE'
            print(f'O pedido {prot} está NÃO VIGENTE!\n')

        df.to_excel('/workspaces/codespaces-jupyter/VarysPatente/04. Resumo de proteções.xlsx', index=False)

def extract(prot):
    dados = []

    class InpiSpider(scrapy.Spider):
        name = "inpi"
        start_urls = ["https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login"]
        custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1.0,
        'AUTOTHROTTLE_MAX_DELAY': 60.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 10.0,
        }
        
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

with open('/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt', 'r') as f:
    nprot = f.readlines()
    nprot = [x.strip() for x in nprot]

#TESTES:
#nprot = ['BR 10 2012 021044 4']

for prot in nprot:
    deferred, result = extract(prot)
    deferreds.append(deferred)
    results.append(result)

dlist = DeferredList(deferreds)
dlist.addBoth(lambda _: reactor.stop())
reactor.run()

i = 0
for prot in nprot:
    print(f"N° de processo {prot}, resultados {results[i]}")
    exigencia(results[i],[prot])
    i+=1
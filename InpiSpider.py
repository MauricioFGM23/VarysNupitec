import scrapy
import subprocess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from twisted.internet.defer import DeferredList
from bs4spider import AutorsSpider
from salvar_lista import salvar_lista_em_excel
from check_website import check_website

#checar se o INPI está online
check_website("https://busca.inpi.gov.br/pePI/servlet/LoginController?action=login")

#ler txt contendo os n de proteção
def read_file_to_list(filename):
    nprot_values = []
    with open(filename, 'r') as file:
        for line in file:
            nprot_values.append(line.strip())
    return nprot_values

#verificar se não há números de proteção a serem adicionados e finalizar o programa
def verificar_lista_vazia(lista):
    if not lista:
        print("A lista está vazia. O programa será encerrado.\n")
        exit()
    else:
        print("A lista não está vazia. O programa continuará.\n")

def executar_arquivo_python(arquivo):
    try:
        # Executa o arquivo Python como um processo externo
        processo = subprocess.Popen(['python', arquivo], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda a finalização do processo e obtém o retorno
        retorno = processo.wait()

        # Verifica se o processo terminou corretamente (código de retorno 0)
        if retorno == 0:
            print(f"O arquivo {arquivo} foi executado com sucesso.\n")
        else:
            print(f"Erro ao executar o arquivo {arquivo}.\n")
        
        # Obtem os outputs do processo (stdout e stderr)
        stdout, stderr = processo.communicate()
        if stdout:
            print("Saída do processo:")
            print(stdout.decode('utf-8'))
        if stderr:
            print("Erro do processo:")
            print(stderr.decode('utf-8'))

    except Exception as e:
        print(f"Erro: {e}")

print ("Iniciando busca por proteções no INPI.\n")
# Arquivo que você deseja executar
nome_arquivo = '/workspaces/codespaces-blank/check_table.py'

# Executa o arquivo e espera a finalização antes de continuar o fluxo
executar_arquivo_python(nome_arquivo)

# Continue aqui com o fluxo do programa após a execução do arquivo .py
print("Continuando o fluxo do programa...\n")

        
#Spider que copia os dados de cada número de proteção
def crawl_inpi(nprot):
    dados = []

    class InpiSpider2(scrapy.Spider):
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
                callback=self.submit_search
            )

        def submit_search(self, response):
            link_selector = 'a:contains("' + nprot + '")::attr(href)'
            next_page_link = response.css(link_selector).get()
            yield response.follow(next_page_link, callback=self.extract_search)


        def extract_search(self, response):
            # Extrair e salvar o texto dos seletores na lista "texto"
            elementos_texto = response.css('font.normal')

            for elemento in elementos_texto:
                texto = elemento.css('::text').get()
                if texto:
                    dados.append(texto.strip())

    runner = CrawlerRunner()
    crawler = runner.create_crawler(InpiSpider2)
    deferred = runner.crawl(crawler)

    return deferred, dados


#Números de proteção:
nprot_values = read_file_to_list('/workspaces/codespaces-blank/lista_de_protecoes.txt')

print ("Quantidade de novas proteções encontradas: ", len(nprot_values), "\n")
print ("N° de cada proteção: ", nprot_values, "\n")

#verificar se há N° de proteções para serem adicionas e finalizar o programa
verificar_lista_vazia(nprot_values)

# Variáveis usadas no spider do scrapy
deferreds = []
results = []

#achar texto entre elementos
def elementos_entre(dados, elemento1, elemento2):
    try:
        index1 = dados.index(elemento1)
        index2 = dados.index(elemento2)

        if index1 > index2:
            index1, index2 = index2, index1

        elementos_entre_indices = dados[index1 + 1:index2]

        return elementos_entre_indices
    except ValueError:
        print("Os elementos não foram encontrados na lista.")
        return []
    
#unificar os elementos em uma lista substituindo ',' por '/'
def unificar_elementos(lista):
    elemento_unificado = ' / '.join(lista)
    return [elemento_unificado]

#extração dos dados
def extrator(dados, nprot):
#remover os espaços vazios ('')
    for elemento in dados:
        if elemento == '':
            dados.remove(elemento)
    #dados extraídos
    #print(dados)

    #extração e aquisição dos dados
    date = elementos_entre(dados, 'Data do Depósito:','Linguagem:')
    ling = elementos_entre(dados,'Linguagem:','Campo de Aplicação:')
    campo = elementos_entre(dados,'Campo de Aplicação:','Tipo Programa:')
    tipo = elementos_entre(dados,'Tipo Programa:','Título:')
    titulo = elementos_entre(dados,'Título:','Nome do Titular:')
    titular = elementos_entre(dados,'Nome do Titular:','Nome do Autor:')
    n_protecao = [nprot]
    prote = ['PROGRAMA DE COMPUTADOR']
    status = ['REGISTRADO']
   
    #resolver problema de formatação com / da linguagem
    ling = [x.replace(' ', '').replace('/', ' / ') for x in ling]
 
    #unificar alguns elementos
    ling = unificar_elementos(ling)
    campo = unificar_elementos(campo)
    tipo = unificar_elementos(tipo)
    #titular = unificar_elementos(titular)

    #separação dos autores
    list_autores = elementos_entre(dados, 'Nome do Autor:','Nome do Procurador:')
    autores_separados = []

    for autores in list_autores:
        autores_individuais = autores.split(' / ')
        autores_separados.extend(autores_individuais)

    print("\nNúmero de Proteção: ", n_protecao,"\nData de Depósito: ", date,
        "\nLinguágem: ", ling, "\nCampo de aplicação: ", campo, "\nTipo de Programa: ", tipo,
        "\nTítulo: ", titulo, "\nTitular da Tecnologia: ", titular, '\n')

#Execucção do Spider dos Autores no site do pesquisar

    lista_autores = AutorsSpider(autores_separados)

  # Compilador de dados dos autores
    autores = []
    unidades = []
    departamentos = []

    for autor, dados in lista_autores.items():
        autores.append(autor)
        unidades.append(dados[0])
        departamentos.append(dados[1])

  #Demais dados extraídos
    n_autores = len(autores)
    n = [n_autores]

    def multiplicador(item):
        item = item*n_autores
        return item

    print("Número de Autores: ",n_autores ,"\nAutores: ",autores, "\nUnidades: ", unidades, "\nDepartamentos: ", departamentos, "\n")

    status = multiplicador(status)
    ling = multiplicador(ling)
    campo = multiplicador(campo)
    tipo = multiplicador(tipo)
    titulo = multiplicador(titulo)
    titular = multiplicador(titular)
    n_protecao = multiplicador(n_protecao)
    date = multiplicador(date)
    n = multiplicador(n)
    prote = multiplicador(prote)
    
    # Dados imutáveis
    arquivo = "/workspaces/codespaces-blank/Novo resumos de proteções.xlsx"
    planilha = "SOFTWARE"

    coluna1 = 'INVENTOR/AUTOR'
    coluna2 = 'STATUS'
    coluna3 = 'Nº DA PROTEÇÃO'
    coluna4 = 'DATA DO REGISTRO'
    coluna5 = 'INSTITUIÇÃO GESTORA'
    coluna6 = 'TOTAL DE INVENTORES/AUTORES'
    #coluna7 = 'VINCULO'
    #coluna8 = 'CAMPI'
    coluna9 = 'UNIDADE ACADEMICA DE CADA AUTOR'
    coluna10 = 'DEPARTAMENTO DE CADA AUTOR'
    coluna11 = 'CAMPO DE APLICAÇÃO'
    coluna12 = 'TIPO DE PROGRAMA'
    coluna13 = 'LINGUAGEM'
    coluna14 = 'TIPO DE PROTEÇÃO'
    coluna15 = 'TÍTULO'

    salvar_lista_em_excel(autores, coluna1, arquivo, planilha)
    salvar_lista_em_excel(status, coluna2, arquivo, planilha)
    salvar_lista_em_excel(n_protecao, coluna3, arquivo, planilha)
    salvar_lista_em_excel(date, coluna4, arquivo, planilha)
    salvar_lista_em_excel(titular, coluna5, arquivo, planilha)
    salvar_lista_em_excel(n, coluna6, arquivo, planilha)
    #salvar_lista_em_excel(['PF'], coluna7, arquivo, planilha)
    #salvar_lista_em_excel(['DARCY RIBEIRO'], coluna8, arquivo, planilha)
    salvar_lista_em_excel(unidades, coluna9, arquivo, planilha)
    salvar_lista_em_excel(departamentos, coluna10, arquivo, planilha)
    salvar_lista_em_excel(campo, coluna11, arquivo, planilha)
    salvar_lista_em_excel(tipo, coluna12, arquivo, planilha)
    salvar_lista_em_excel(ling, coluna13, arquivo, planilha)
    salvar_lista_em_excel(prote, coluna14, arquivo, planilha)
    salvar_lista_em_excel(titulo, coluna15, arquivo, planilha)

    print('\nTrabalho Finalizado!\n')

    # Executores do spider e extratores de dados
for nprot in nprot_values:
    deferred, result = crawl_inpi(nprot)
    deferreds.append(deferred)
    results.append(result)

dlist = DeferredList(deferreds)
dlist.addBoth(lambda _: reactor.stop()) # Parar o reactor após todos os spiders terminarem
reactor.run() # Iniciar o reactor apenas uma vez

for nprot, result in zip(nprot_values, results):
    extrator(result, nprot)#variável results possui todos os dados
    
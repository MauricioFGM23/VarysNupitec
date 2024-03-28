import shutil
import openpyxl
import requests
from bs4 import BeautifulSoup

def check_url_availability(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        pass
    return False

def check_website(url):
    if not check_url_availability(url):
        print("Servidor fora do ar! Verifique a conexão ou aguarde o retorno.")
        return

    print("O site está acessível!")

# Exemplo adicional: Extrair o título da página usando BeautifulSoup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title').get_text()
    print("Título da página:", title, "\n")

#fazer Back-UP dos dados
def fazer_backup(arquivo_original, arquivo_backup):
    
    # Copiar o arquivo original para o arquivo de backup
    shutil.copy(arquivo_original, arquivo_backup)

    # Verificar a integridade do arquivo original
    try:
        workbook = openpyxl.load_workbook(arquivo_original)
        workbook.active  # Tentar acessar a planilha para verificar a integridade
    except openpyxl.utils.exceptions.InvalidFileException:
        print("Erro Crítico!!! O arquivo original foi corrompido. Acessar back-up.")
    else:
        print("Backup realizado com sucesso!")
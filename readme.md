
# VarysNupitec

Depois de criar o codespaces:

```bash
sudo apt-get update
sudo apt-get upgrade
```

## Instalação de bibliotecas

```bash
pip install scrapy
pip install pandas
pip install openpyxl
```

## Utilização

O **VarysNupitec**, nesse estado, serve apenas para atualizar os status das patentes na planilha "Resumo de Proteções". Ele vai dizer, para cada proteção, quais os despachos e associar se a proteção está vigente ou não.

O programa é divido em dois scripts: extrator e buscador.

```bash
python3 buscador.py
python3 extrator.py

```

### Buscador

O script vai puxar o número todas as proteções no CNPJ da UnB e salvar em um `txt` na pasta do onde o `buscador.py` se encontra.

Você pode abrir a lista para comparar com a planilha e saber se estão todos na planilha.

### Planilha de proteções

Fazer o **upload** da planilha `Resumo de proteções` mais recente no repositório: O programa compara a o arquivo `list_prot.txt` com a planilha mais recente e usa para baixar os dados de status. Não precisa editar a planilha (se tudo estiver padronizado), mas é necessário que o arquivo tenha **exatamente** o nome `04. Resumo de proteções.xlsx`.

### Extrator de dados

Execução do `extrator.py`: O extrator que faz a comparação e joga os dados em três colunas da planilha. Ele substitui colunas já existentes, como `STATUS` e `ANÁLISE SUBSTANTIVA`, mas também cria uma nova coluna com cada despacho importante, que pode ou não afetar o `STATUS`.

### Execução do programa

Após executar, o programa leva em torno de 10-20 min para, de fato, começar o scraping. Não se preocupe caso demore. Com o tempo, ele começará a mostrar os dados baixados no prompt.

> OBS. **Importante**: O programa pode não lidar bem com as inconsistência do INPI. É muito comum, em horários de pico, o programa  não baixar nenhum dado. Quando isso ocorre, não adianta deixar o programa rodando. Você pode dar um `Ctrl+C` para abortar. Nesse caso, você pode:

- Fechar o `codespaces` e abrir novamente para uma tentativa;
- Deixar para fazer essa atualização mais no início do dia ou final do dia (horários de menor pico de acessos).

Você sabe que o processo deu certo quando todas as proteções que forem mostradas no prompt tiverem os dados completos. Se algum ficou em branco, o processo deu RUIM.

Se tudo deu certo e o programa finalizou, você pode usar a planilha `04. Resumo de proteções.xlsx` alterada pelo Varys para atualizar a planilha definitiva. Abra o arquivo, copie e cole as colunas `STATUS` e `ANÁLISE SUBSTANTIVA` na planilha definitiva (OBS. Se você colar com a opção "sem formato", não vai alterar as células mescladas).

A coluna `DESPACHOS` serve apenas para uma possível conferência.

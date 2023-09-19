import pandas as pd

lista_exig = {'8.12':'8.12 - ARQ DEFINITIVO - FALTA DE PGT','9.1':'9.1 - DEFERIMENTO','9.2':'9.2 - INDEFERIMENTO',
              '11.1.1':'11.1.1 - ARQ DEFINITIVO - ANTERIORIDADE','11.2':'11.2 - ARQ DEFINITIVO - EXIGÊNCIA',
              '11.4':'11.4 - ARQ DEFINITIVO - PGT CARTA PATENTE','11.6':'11.6 - ARQ DEFINITIVO - PROCURAÇÃO',
              '11.11':'11.11 - ARQ DEFINITIVO - ANTERIORIDADE','11.21':'11.21 - ARQ DEFINITIVO - PCT',
              '16.1':'16.1 - CONCESSÃO DE CARTA PATENTE','18.3':'18.3 - CADUCIDADE DEFERIDA','21.1':'21.1 - EXTINÇAO - PGT',
              '21.2':'EXTINÇAO - RENÚNCIA','21.7':'EXTINÇAO - NÃO CUMPRIMENTO'}

def exigencia(exig,nprot):
    
    comb_exig = []

    for prot in nprot:
        print(f"Exigências encontradas para a proteção {prot}: ")

        for item in exig:
            if item in lista_exig:
                comb_exig.append(lista_exig[item])
                print(lista_exig[item])
            
        if not comb_exig:
            for item in exig:
                if item in ['2.1']:
                    comb_exig = '2.1 - PEDIDO DE PATENTE OU CERTIFICADO DE ADIÇÃO'
                    print(comb_exig)
        if not comb_exig:
            comb_exig = ['']
            print("None!")
        
        comb_exig = '; '.join(comb_exig)
        
        df = pd.read_excel('/workspaces/codespaces-jupyter/VarysPatente/04. Resumos de proteções.xlsx')

        if prot in df['Nº DA PROTEÇÃO'].values:
            linha = df[df['Nº DA PROTEÇÃO'] == prot].index[0]
            
        else:
            print(f'O {prot} não foi encontrado na coluna "Nº DA PROTEÇÃO".\n')
            df.to_excel('/workspaces/codespaces-jupyter/VarysPatente/04. Resumos de proteções.xlsx', index=False)
            break

        df.at[linha, 'STATUS'] = comb_exig

        df.to_excel('/workspaces/codespaces-jupyter/VarysPatente/04. Resumos de proteções.xlsx', index=False)
        print("Finalizado!!!\n")

#exig = ['1.11', '1.1', '2.f1']
#nprot = ['BR 10 2017 022031 1']
#exigencia(exig, nprot)
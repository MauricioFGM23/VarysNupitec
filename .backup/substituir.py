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
        print(f"O arquivo '{nome_arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")

nome_arquivo_entrada = "/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt"
nome_arquivo_saida = "/workspaces/codespaces-jupyter/VarysPatente/lista_prot.txt"

#subs(nome_arquivo_entrada, nome_arquivo_saida)
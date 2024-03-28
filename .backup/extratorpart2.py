from VarysPatente.backup.extrator import protect

nprot = ['BR 10 2013 033884 2', 'BR 10 2013 032983 5']
dados = []
for prot in nprot:
    dados_prot = protect(prot)
    dados.append(dados_prot)

print("\nDados obtidos: ",dados, "\n")

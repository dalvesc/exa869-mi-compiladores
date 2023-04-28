import os
import unicodedata

pasta = os.getcwd()+'/analisador_lexico/files/output/' #pasta dos códigos de input

#############################FAZER A STACK #######################################################
##############################################FAZER O SYMBOL######################################

pilha_escopo = ['global']
pilha_chaves = []

#ler linha por linha do arquivo
def ler_linha_arquivo(arquivo):
    arquivo = open(arquivo)
    linhas = arquivo.readlines()
    arquivo.close()

    linhas_formatadas = []
    for linha in linhas:
        linha = unicodedata.normalize("NFKD", linha)#transforma \xa0 em espaço
        linhas_formatadas.append(linha)
    return linhas_formatadas

#salva quais arquivos estão na pasta de input
def ler_pasta_arquivos():
    arquivos = []
    for raiz, diretorios, files in os.walk(pasta):
        for file in files:
            arquivos.append(file)
    return arquivos

def analisar_arquivo(linhas):
    for linha in linhas[2:]:
        split_linha = linha.split()
        if len(split_linha) >= 3:
            symbol = {
                'numLinha': split_linha[0],
                'token': split_linha[1],
                'lexema': ' '.join(split_linha[2:]).strip(),
                'escopo': escopo(split_linha[1], ' '.join(split_linha[2:]).strip())
            }
            #o q fazer com os erros lexicos?

            print(symbol)

#Criar pilha de escopos
def escopo(token, lexema):
    if token == 'PRE' and lexema == 'start':
        pilha_escopo.append('start')
    
    return pilha_escopo[-1]  

def escopo_variavel(lexema):
    if lexema == 'var':
        pass
    elif lexema == 'const':
        pass

if __name__ == "__main__":
    for arquivo in ler_pasta_arquivos():
        tokens = []
        tokens_erros = []
        analisar_arquivo(ler_linha_arquivo(pasta+arquivo))
        #montar_output(arquivo, tokens, tokens_erros)
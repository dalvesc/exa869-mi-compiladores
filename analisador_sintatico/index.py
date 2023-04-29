from analisador_lexico.index import analisar_lexico #NAO FUNCIONAAAAA


#############################FAZER A STACK #######################################################
##############################################FAZER O SYMBOL######################################

pilha_escopo = ['global']
pilha_chaves = []


def analisar_tokens(linhas):
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
    tokens = []
    tokens_erros = []
    analisar_tokens(analisar_lexico())
    #montar_output(arquivo, tokens, tokens_erros)
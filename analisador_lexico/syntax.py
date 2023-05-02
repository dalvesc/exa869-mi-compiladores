from lexical import *

#############################FAZER A STACK #######################################################

pilha_escopo = ['global'] #pilha de escopos
pilha_chaves = []
pilha_simbolos = []

# Analisa todos os tokens que foram gerados pelo analisador léxico
def analisar_tokens(tokens):
    global file_symbols #lista de simbolos
    file_symbols = []
    i = 0
    #salvando em simbolos o token, lexema e escopo de cada token recebido do lexema 
    for token in tokens:
        symbol = {
            'numLinha': token["numLinha"],
            'token': token["token"],
            'lexema': token["lexema"],
            'escopo': ''
        }

        file_symbols.append(symbol)

    i = 0
    #analisando cada token para verificar o escopo de cada um
    while i < len(file_symbols):
        if file_symbols[i]['lexema'] == 'struct':
            i = analisar_struct(i)
        elif file_symbols[i]['lexema'] == 'var':
            i = analisar_var(i)
        elif file_symbols[i]['lexema'] == 'const':
            i = analisar_const(i)
        elif file_symbols[i]['lexema'] == 'procedure':
            i = analisar_procedure(i)
        elif file_symbols[i]['lexema'] == 'function':
            i = analisar_function(i)
        elif file_symbols[i]['lexema'] == 'start':
            i = analisar_start(i)
        else:
            #escopo global
            i += 1


    #print('SYMBOLS', file_symbols)

# Analisa o escopo de uma struct
def analisar_struct(i):
    pass

# Analisa o escopo de uma variável
def analisar_var(i):
    pass

# Analisa o escopo de uma constante
def analisar_const(i):
    pass

# Analisa o escopo de uma procedure
def analisar_procedure(i):
    pass

# Analisa o escopo de uma function
def analisar_function(i):
    pass

# Analisa o escopo de um start
def analisar_start(i):
    pass


#Criar pilha de escopos
def escopo(symbol):
    if symbol["token"] == 'PRE' and symbol["lexema"] == 'start':
        pilha_escopo.append('start')
    
    return pilha_escopo[-1]  

def escopo_variavel(lexema):
    if lexema == 'var':
        pass
    elif lexema == 'const':
        pass

if __name__ == "__main__":
    tokens = [] #lista de tokens
    tokens_erros = [] #lista de tokens com erros
    for arquivo in ler_pasta_arquivos(): #lendo cada arquivo da pasta input
        analisar_tokens(analisar_lexico(arquivo)) #chamando o analisador léxico
        # Aqui a gente faz a análise desse arquivo
        #montar_output(arquivo, tokens, tokens_erros)
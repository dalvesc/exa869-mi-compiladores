from lexical import *
from utils import *
from inspect import currentframe, getframeinfo

pilha_escopo = ['global'] #pilha de escopos
pilha_chaves = []
pilha_simbolos = []
lista_identificadores = []
file_symbols = []

# TODO: 
#     - IF...THEN...ELSE
#     - WHILE
#     - EXPRESSÃO RELACIONAL
#     - EXPRESSÃO LÓGICA
#     - EXPRESSÃO ARITMÉTICA
#     - CORRIGIR CONST PARA OBRIGAR ATRIBUIÇÃO
#     - FUNÇÃO (e parâmetros)
#     - PROCEDURE (e parâmetros)
#     - CODIGO (dentro do start)
#     - READ
#     - PRINT

# Analisa todos os tokens que foram gerados pelo analisador léxico
def analisar_tokens(tokens):
    #  global file_symbols #lista de simbolos
    
    i = 0
    #salvando em simbolos o token, lexema e escopo de cada token recebido do lexema 
    for token in tokens:
        symbol = {
            'numLinha': token["numLinha"],
            'token': token["token"],
            'lexema': token["lexema"],
            'escopo': ''
        }

        if symbol["token"] == "IDE":
            lista_identificadores.append(symbol)

        file_symbols.append(symbol)

    i = 0
    #analisando cada token para verificar o escopo de cada um
    while i < len(file_symbols):
        if file_symbols[i]['lexema'] == 'struct':
            (i, _) = analisar_struct(i)
        elif file_symbols[i]['lexema'] == 'var':
            (i, _) = analisar_var(i)
        elif file_symbols[i]['lexema'] == 'const':
            (i, _) = analisar_const(i)
        elif file_symbols[i]['lexema'] == 'procedure':
            i += 1
            #(i, _) = analisar_procedure(i)
        elif file_symbols[i]['lexema'] == 'function':
            i += 1
            #(i, _) = analisar_function(i)
        elif file_symbols[i]['lexema'] == 'start':
            (i, _) = analisar_start(i)
        else:
            #escopo global
            i += 1


    #print('SYMBOLS', file_symbols)

def criar_pilha(arr):
    arr.reverse()
    return arr

def adicionar_escopo(index_token, escopo):
    file_symbols[index_token]["escopo"] = escopo

def get_escopo_atual():
    return pilha_escopo[-1]

# Analisa o escopo de uma struct
def analisar_struct(i):
    acc = ""
    pilha_struct = criar_pilha(['struct','IDE','{', '<struct_var>' , '}'])

    if get_escopo_atual() != 'global':
        acc += erro_inesperado_handler(file_symbols[i]["lexema"], file_symbols[i]["numLinha"], referencia=getframeinfo(currentframe()).lineno)

    while i < len(file_symbols) and len(pilha_struct) > 0:
        simbolo = file_symbols[i]
        esperado = pilha_struct[-1]

        if simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_struct.pop()
            acc += simbolo["lexema"]
        elif esperado == '<struct_var>' and i + 1 < len(file_symbols):
            pilha_escopo.append('struct')
            file_symbols[i]["escopo"] = get_escopo_atual() 
            if simbolo["lexema"] in get_tipos():
                (i, acc_aux) = analisar_declaracao(i)
                acc += acc_aux

                if not(i + 1 < len(file_symbols) and file_symbols[i]["lexema"] in get_tipos()):
                    pilha_struct.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            pilha_escopo.pop()
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if len(pilha_struct) > 0:
            i += 1

    print_faltando_esperado(pilha_struct)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc

# Analisa o escopo de uma variável
def analisar_declaracao(i):
    acc = ""
    if file_symbols[i]["lexema"] not in get_tipos():
        print("Erro: Tipo esperado")
        return i, file_symbols[i]["lexema"]

    escopo = get_escopo_atual()

    acc += file_symbols[i]["lexema"]  + ' '
    i += 1

    pilha_declaracao = criar_pilha(['IDE', '<lista_variaveis>' , ';'])
    
    while len(pilha_declaracao) > 0 and i + 1 <= len(file_symbols):
        simbolo = file_symbols[i]
        esperado = pilha_declaracao[-1]
        file_symbols[i]["escopo"] = escopo

        if esperado == "<lista_variaveis>":
            if simbolo["lexema"] == ",":
                pilha_declaracao = criar_pilha(['IDE', '<lista_variaveis>' , ';'])
                acc += simbolo["lexema"] + ' '
            elif simbolo["lexema"] == '[':
                pilha_declaracao = criar_pilha(['<lista_variaveis>', ';'])
                (i, acc_aux) = analisar_matriz(i)
                acc += acc_aux
            elif simbolo["lexema"] == '=':
                pilha_declaracao = criar_pilha(['<valor>', '<lista_variaveis>', ';'])
                acc += simbolo["lexema"]
            elif simbolo["lexema"] == ';' and i + 1 < len(file_symbols) and file_symbols[i + 1]["lexema"] != "}":
                pilha_declaracao = criar_pilha(['<tipo>', 'IDE', '<lista_variaveis>' , ';'])
                acc += simbolo["lexema"]
            else: 
                pilha_declaracao.pop()
                continue
        
        elif esperado == "<tipo>":
            if simbolo["lexema"] in get_tipos():
                pilha_declaracao.pop()
                acc += simbolo["lexema"] + ' '
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        elif esperado == "<valor>":
            (i, acc_aux) = analisar_atribuicao(i)
            acc += acc_aux 
            pilha_declaracao.pop()
        
        elif simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_declaracao.pop()
            acc += simbolo["lexema"] + ' '
        
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

        if len(pilha_declaracao) > 0:
            i += 1
    
    print_faltando_esperado(pilha_declaracao)

    return i, acc

def analisar_atribuicao(i):
    simbolo = file_symbols[i]

    if simbolo["token"] == "IDE" or simbolo["token"] == "NRO" or simbolo["token"] == "CAC" or simbolo["lexema"] in get_boolean():
        if(simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '['):
            (i, lexema) = analisar_matriz(i)
      
        return i, simbolo["lexema"]

# Analisa o escopo de uma constante
def analisar_const(i):
    pilha_const = criar_pilha(['const', '{', '<lista_variaveis>', '}'])
    acc = ''
    if get_escopo_atual() != 'global':
        acc += erro_inesperado_handler(file_symbols[i]["lexema"], file_symbols[i]["numLinha"], referencia=getframeinfo(currentframe()).lineno)
    
    escopo = get_escopo_atual()

    while len(pilha_const) > 0 and i + 1 <= len(file_symbols):
        simbolo = file_symbols[i]
        esperado = pilha_const[-1]
        file_symbols[i]["escopo"] = escopo

        if esperado == "<lista_variaveis>":
            
            (i, acc_aux) = analisar_declaracao(i)
            acc += acc_aux
            pilha_const.pop()
        elif simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_const.pop()
            acc += simbolo["lexema"] + ' '
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

        if len(pilha_const) > 0:
            i += 1
    
    print_faltando_esperado(pilha_const)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc

def analisar_var(i):
    pilha_var = criar_pilha(['var', '{', '<lista_variaveis>', '}'])
    acc = ''
    escopo = get_escopo_atual()
    
    while len(pilha_var) > 0 and i + 1 <= len(file_symbols):
        simbolo = file_symbols[i]
        esperado = pilha_var[-1]
        file_symbols[i]["escopo"] = escopo

        if esperado == "<lista_variaveis>":
            (i, acc_aux) = analisar_declaracao(i)
            acc += acc_aux
            pilha_var.pop()
        elif simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_var.pop()
            acc += simbolo["lexema"] + ' '
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

        if len(pilha_var) > 0:
            i += 1
    
    print_faltando_esperado(pilha_var)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc


def analisar_matriz(i):
    acc = ''
    
    finish = False
    pilha_vetor = criar_pilha(['[', '<valor>' ,']'])

    while not finish and i + 1 < len(file_symbols):
        simbolo = file_symbols[i]
        if len(pilha_vetor) == 0:
            if simbolo["lexema"] == '[':
                pilha_vetor = criar_pilha(['<valor>', ']'])
                acc += simbolo["lexema"]
            else:
                finish = True
                continue
        else:
            esperado = pilha_vetor[-1]
            if esperado == "<valor>":
                if simbolo["token"] == "IDE" or simbolo["token"] == "NRO":
                    pilha_vetor.pop()
                    acc += simbolo["lexema"]
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            elif simbolo["lexema"] == esperado:
                pilha_vetor.pop()
                acc += simbolo["lexema"]
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if finish == False:
            i += 1
                
    print_faltando_esperado(pilha_vetor)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i-1, acc

# Analisa o escopo de uma procedure
def analisar_procedure(i):
    pass

# Analisa o escopo de uma function
def analisar_function(i):
    pass

# Analisa o escopo de um start
def analisar_start(i):
    acc = ''
    pilha_start = criar_pilha(['start', '{', '<codigo>' ,'}'])


    while(i < len(file_symbols) and len(pilha_start) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_start[-1]

        if esperado == '<codigo>':
            pilha_start.pop()
            pilha_escopo.append('start')
            # Ver análise do codigo
            pilha_escopo.pop()
            pass
        elif simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_start.pop()
            acc += simbolo["lexema"] + ' '
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

        if len(pilha_start) > 0:
            i += 1

    print_faltando_esperado(pilha_start)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc



def erro_inesperado_handler(lexema, linha, referencia = None):
  erros_sintaticos.append('Erro: Token inesperado ' + lexema + ' na linha ' + str(linha))
  print(pintar_vermelho(referencia) + ' Erro: Token inesperado ' + pintar_vermelho(lexema) + ' na linha ' + str(linha))
  return pintar_vermelho(lexema)

def erro_nao_declarado(lexema, linha):
  erros_semanticos.append('Erro: Variável ' + lexema + ' não declarada na linha ' + str(linha))
  print(pintar_vermelho(getframeinfo(currentframe()).lineno) + ' Erro: Variável ' + pintar_vermelho(lexema) + ' não declarada na linha ' + str(linha))

if __name__ == "__main__":
    tokens = [] #lista de tokens
    erros_sintaticos = [] #lista de tokens com erros sintaticos
    erros_semanticos = []
    for arquivo in ler_pasta_arquivos(): #lendo cada arquivo da pasta input
        analisar_tokens(analisar_lexico(arquivo)) #chamando o analisador léxico
        # Aqui a gente faz a análise desse arquivo
        #montar_output(arquivo, tokens, tokens_erros)
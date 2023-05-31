from lexical import *
from utils import *
from inspect import currentframe, getframeinfo

IDENTIFICADORES = ['IDE', 'MATRIZ', 'STRUCT']

pilha_escopo = ['global'] #pilha de escopos
pilha_chaves = []
pilha_simbolos = []
lista_identificadores = []
file_symbols = []

# TODO: 
#     - ATRIBUIÇÃO DE STRUCT
#     - IF...THEN...ELSE
#     - WHILE
#     - FUNÇÃO
#     - RETORNO DE FUNÇÃO
#     - PROCEDURE
#     - CODIGO (dentro do start)
#     - ESCREVER O OUTPUT SINTÁTICO NO ARQUIVO

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
            #i += 1
        else:
            i += 1

#Inverte a lista para ser usada como pilha
def criar_pilha(arr):
    arr.reverse()
    return arr

#Adiciona escopo ao token
def adicionar_escopo(index_token, escopo):
    file_symbols[index_token]["escopo"] = escopo

#Retorna o escopo atual
def get_escopo_atual():
    return pilha_escopo[-1]

#########################################################STRUCT######################################################

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

#########################################################VARIÁVEIS######################################################

# Analisa o escopo de uma variável
def analisar_declaracao(i, tipo="var"):
    acc = ""
    if file_symbols[i]["lexema"] not in get_tipos():
        print("Erro: Tipo esperado")
        return i, file_symbols[i]["lexema"]

    escopo = get_escopo_atual()

    acc += file_symbols[i]["lexema"]  + ' '
    i += 1
    if tipo == "var":
        pilha_declaracao = criar_pilha(['IDE', '<lista_variaveis>' , ';'])
    elif tipo == "const":
        pilha_declaracao = criar_pilha(['IDE', "=", '<lista_variaveis>', ';'])

    
    while len(pilha_declaracao) > 0 and i + 1 <= len(file_symbols):
        simbolo = file_symbols[i]
        esperado = pilha_declaracao[-1]
        file_symbols[i]["escopo"] = escopo

        if esperado == "<lista_variaveis>":
            if simbolo["lexema"] == "," and tipo == "const":
                pilha_declaracao = criar_pilha(['IDE', '=', '<lista_variaveis>' , ';'])
                acc += simbolo["lexema"] + ' '
            elif simbolo["lexema"] == ",":
                pilha_declaracao = criar_pilha(['IDE', '<lista_variaveis>' , ';'])
                acc += simbolo["lexema"] + ' '
            elif simbolo["lexema"] == '[':
                pilha_declaracao = criar_pilha(['<lista_variaveis>', ';'])
                (i, acc_aux) = analisar_matriz(i)
                acc += acc_aux
            elif simbolo["lexema"] == '=':
                pilha_declaracao = criar_pilha(['<valor>', '<lista_variaveis>', ';'])
                acc += simbolo["lexema"]
            elif simbolo["lexema"] == ';' and i + 1 < len(file_symbols) and file_symbols[i + 1]["lexema"] != "}" and tipo == "const":
                pilha_declaracao = criar_pilha(['<tipo>', 'IDE', '=', '<lista_variaveis>' , ';'])
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
        
        elif (simbolo["lexema"] == esperado or simbolo["token"] == esperado) and tipo == "const" and simbolo["lexema"] == "=":
            pilha_declaracao = criar_pilha(['<valor>', '<lista_variaveis>', ';'])
            acc += simbolo["lexema"] + ' '  
        
        elif simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_declaracao.pop()
            acc += simbolo["lexema"] + ' '
        
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

        if len(pilha_declaracao) > 0:
            i += 1
    
    print_faltando_esperado(pilha_declaracao)

    return i, acc

#########################################################ATRIBUIÇÃO######################################################

# Analisa o escopo de uma atribuição
def analisar_atribuicao(i):
    simbolo = file_symbols[i]

    if i+1 < len(file_symbols):
        (i, _) = validar_argumento_expressao_aritmetica(i, ["IDE", "NRO"], return_error=False)
        if i+1 < len(file_symbols) and file_symbols[i+1]["token"] == "ART":
            (i, acc_aux) = analisar_expressao_aritmetica(i)
            i -= 1
            return i, acc_aux
    
    if simbolo["token"] == "IDE" or simbolo["token"] == "NRO" or simbolo["token"] == "CAC" or simbolo["lexema"] in get_boolean():
        if(simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '['):
            (i, lexema) = analisar_matriz(i)
        # elif(simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '.'):
        #     (i)
      
        return i, simbolo["lexema"]

#########################################################CONSTANTE######################################################

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
            (i, acc_aux) = analisar_declaracao(i, tipo='const')
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

##########################################################VARIAVEIS###############################################################

# Analisa o escopo de uma variável
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

###################################################VETOR/MATRIZ###############################################################

# Analisa o escopo de uma matriz/vetor
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

###################################################PROCEDURE###############################################################

# Analisa o escopo de uma procedure
def analisar_procedure(i):
    pass

################################################FUNÇÃO###############################################################

# Analisa o escopo de uma function
def analisar_function(i):
    pass

##################################################READ###############################################################

# Analisa o escopo de um read
def analisar_read(i):
    acc = ''
    pilha_read = criar_pilha(['read', '(', '<parametro_read>', ')', ';'])
    
    while(i < len(file_symbols) and len(pilha_read) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_read[-1]
        
        if esperado == '<parametro_read>':
            lista_args = IDENTIFICADORES
            (i, acc_aux) = analisar_argumento(i, lista_args)
            if acc_aux != False:
                pilha_read.pop()
                acc += acc_aux
            else:
                erros_sintaticos.append('Erro: Token inesperado ' + simbolo["lexema"] + ' na linha ' + str(simbolo["numLinha"]))
                acc += pintar_vermelho(simbolo["lexema"])
        elif esperado == simbolo["lexema"]:
            pilha_read.pop()
            acc += simbolo["lexema"]
        else:
            erros_sintaticos.append('Erro: Token inesperado ' + pintar_vermelho(simbolo["lexema"]) + ' na linha ' + str(simbolo["numLinha"]))
            acc += pintar_vermelho(simbolo["lexema"])
        
        if len(pilha_read) > 0:
            i += 1
    
    print_faltando_esperado(pilha_read)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc

#########################################################PRINT######################################################

# Analisa o escopo de um print
def analisar_print(i):
    print("AQUIII")
    acc = ''
    pilha_print = criar_pilha(['print', '(', '<parametro_geral>', ')', ';'])
    
    while(i < len(file_symbols) and len(pilha_print) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_print[-1]
        if esperado == "<parametro_geral>":
            lista_args = ["CAC", "NRO"]
            lista_args.extend(IDENTIFICADORES)
            (i, acc_aux) = analisar_argumento(i, lista_args)
            if acc_aux != False:
                pilha_print.pop()
                acc += acc_aux
            else:
                erros_sintaticos.append('Erro: Token inesperado ' + simbolo["lexema"] + ' na linha ' + str(simbolo["numLinha"]))
                acc += pintar_vermelho(simbolo["lexema"])
        elif esperado == simbolo["lexema"]:
            pilha_print.pop()
            acc += simbolo["lexema"]
        else:
            erros_sintaticos.append('Erro: Token inesperado ' + pintar_vermelho(simbolo["lexema"]) + ' na linha ' + str(simbolo["numLinha"]))
            acc += pintar_vermelho(simbolo["lexema"])
        
        if len(pilha_print) > 0:
            i += 1
    
    print_faltando_esperado(pilha_print)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc
    
######################################################ARGUMENTO############################################################

# Analisa escopo de um argumento da função
def analisar_argumento(i, lista_args, args_funcao = False, final = ')'):
    simbolo = file_symbols[i]
    if simbolo["token"] == "CAC" and "CAC" in lista_args:
        return i, simbolo["lexema"]
    elif simbolo["token"] == "NRO" and "NRO" in lista_args:
        return i, simbolo["lexema"]
    elif simbolo["lexema"] in get_boolean() and ("true" in lista_args or "false" in lista_args):
        return i, simbolo["lexema"]
    elif simbolo["token"] == "IDE" and "IDE" in lista_args and args_funcao:
        # validar retorno
        # if file_symbols[i+i]["lexema"] == "(":
        #     i 
        return i, simbolo["lexema"]
    
    if (set(IDENTIFICADORES) & set(lista_args)) and simbolo["token"] == "IDE":
        simbolo_aux = file_symbols[i+1]
        if "IDE" in lista_args and final in [f"_{simbolo_aux['token']}", simbolo_aux["lexema"]]:
            return i, simbolo["lexema"]
        elif "STRUCT" in lista_args and simbolo_aux["lexema"] == ".":
            return analisar_struct(i)
        elif "MATRIZ" in lista_args and simbolo_aux["lexema"] == "[":
            return analisar_matriz(i)
        else:
            return i, erro_inesperado_handler(simbolo_aux["lexema"], simbolo_aux["numLinha"], referencia=getframeinfo(currentframe()).lineno)
    else:
        return i, erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

######################################################### EXPRESSÕES ###################################################### 

def validar_argumento_expressao_aritmetica(i, lista_args, return_error = True):
    simbolo = file_symbols[i]
    tem_parenteses = True 
    if not return_error:
        while(tem_parenteses):
            if simbolo["lexema"] == "(":
                i += 1
                simbolo = file_symbols[i]
            else:
                tem_parenteses = False
    if "IDE" in lista_args and simbolo["token"] == "IDE":
        if simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '.':
            (i, acc_aux) = analisar_struct(i)
        elif simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '[':
            (i, acc_aux) = analisar_matriz(i)
        return i, acc_aux
    elif "NRO" in lista_args and simbolo["token"] == "NRO":
        return i, simbolo["lexema"]
    else:
        if return_error:
            return i, erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        return i, simbolo["lexema"]
    
def validar_argumento_expressao_logica(i, return_error = True):
    simbolo = file_symbols[i]
    tem_parenteses = True
    
    if not return_error:
        while(tem_parenteses):
            if simbolo["lexema"] == '(':
                i += 1
                simbolo = file_symbols[i]
            else:
                tem_parenteses = False
    if simbolo["lexema"] in get_boolean():
        return i, simbolo["lexema"]
    else:
        if i+1 < len(file_symbols):
            (j, _) = validar_argumento_expressao_relacional(i, return_error=False)
            if j+1 < len(file_symbols) and file_symbols[j+1]["token"] == "REL":
                return analisar_expressao_relacional(i)
        # if simbolo["token"] == "IDE":
        #     if i+1 < len(file_symbols) and file_symbols[i+1]["lexema"] == "(":
        #         (i, acc_aux) = validar_return
        #     return i, acc_aux
    if return_error:
        erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
    
    return i, simbolo["lexema"]

def validar_argumento_expressao_relacional(i, return_error = True):
    simbolo = file_symbols[i]
    tem_parenteses = True
    
    if not return_error:
        while(tem_parenteses):
            if simbolo["lexema"] == "(":
                i+= 1
                simbolo = file_symbols[i]
            else:
                tem_parenteses = False
    
    if simbolo["token"] == "NRO" or simbolo["token"] in get_boolean():
        return i, simbolo["lexema"]
    
    elif simbolo["token"] == "IDE":
        simbolo_aux = file_symbols[i+1]
        if simbolo_aux["token"] == "REL":
            return i, simbolo["lexema"]
        elif simbolo_aux["lexema"] == ".":
            return analisar_struct(i)
        elif simbolo_aux["lexema"] == "[":
            return analisar_matriz(i)
        else:
            return i, simbolo["lexema"]
    else:
        if return_error:
            erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        return i, simbolo["lexema"]
    

def analisar_expressao_aritmetica(i):
    pilha_expressao_aritmetica = criar_pilha(['<valor>', 'ART', '<valor>'])
    acc = ''
    fim = False
    parenteses = True
    lista_parenteses = []
    
    while(not fim and i < len(file_symbols)):
        simbolo = file_symbols[i]
        while(parenteses):
            if simbolo["lexema"] == "(":
                i += 1
                acc += '('
                lista_parenteses.append('(')
                simbolo = file_symbols[i]
            else:
                parenteses = False
        if len(pilha_expressao_aritmetica) == 0:
            parenteses = True
            while(i < len(file_symbols) and len(lista_parenteses) > 0 and parenteses):
                if file_symbols[i]["lexema"] == ')':
                    i += 1
                    acc += ')'
                    lista_parenteses.pop()
                else:
                    parenteses = False
            if i+1 < len(file_symbols) and file_symbols[i]["token"] == "ART":
                pilha_expressao_aritmetica = criar_pilha(['ART', '<valor>'])
            else:
                fim = True
                continue
        else:
            simbolo = file_symbols[i]
            esperado = pilha_expressao_aritmetica[-1]
            if esperado == '<valor>':
                lista_args = ['IDE', 'NRO']
                (i, acc_aux) = validar_argumento_expressao_aritmetica(i, lista_args)
                if acc_aux != False:
                    pilha_expressao_aritmetica.pop()
                    acc += acc_aux
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            elif esperado == simbolo["token"] and simbolo["lexema"] in get_simbolos_aritmeticos():
                pilha_expressao_aritmetica.pop()
                acc += simbolo["lexema"]
            elif i-1 >= len(lista_parenteses) and len(lista_parenteses) > 0 and file_symbols[i]["lexema"] == ')' and (file_symbols[i-1]["lexema"] == ")" or file_symbols[i-1]["token"] in ["IDE", "NRO"]):
                acc += ")"
                lista_parenteses.pop()
                i += 1
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            if len(pilha_expressao_aritmetica) > 0:
                parenteses = True
                i += 1
            else:
                i += 1
    print_faltando_esperado(lista_parenteses)
    print_faltando_esperado(pilha_expressao_aritmetica)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc

def analisar_expressao_logica(i):
    pilha_expressao_logica = criar_pilha(['<valor_logico>', 'LOG', '<valor_logico>'])
    acc = ''
    fim = False
    
    while not fim and i < len(file_symbols):
        simbolo = file_symbols[i]
        if simbolo["lexema"] == "!":
            i += 1
            simbolo = file_symbols[i]
            acc += "!"
        if i+1 >= len(file_symbols):
            fim = True
        if len(pilha_expressao_logica) == 0 and fim:
            simbolo_aux = file_symbols[i+1]
            if simbolo_aux["lexema"] in get_simbolos_logicos():
                pilha_expressao_logica = criar_pilha(['<valor_logico>'])
                acc += simbolo_aux["lexema"]
                i += 1
            else:
                fim = True
        else:
            if len(pilha_expressao_logica) > 0:
                esperado = pilha_expressao_logica[-1]
                if esperado == '<valor_logico>':
                    (i, acc_aux) = validar_argumento_expressao_logica(i)
                    if acc_aux != False:
                        pilha_expressao_logica.pop()
                        acc += acc_aux
                    else:
                        acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
                elif esperado in [simbolo["token"], simbolo["lexema"]] and simbolo["lexema"] in get_simbolos_logicos():
                    pilha_expressao_logica.pop()
                    acc += simbolo["lexema"]
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if len(pilha_expressao_logica) > 0:
            i += 1
        
    print_faltando_esperado(pilha_expressao_logica)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
        
    return i, acc

def analisar_expressao_relacional(i):
    pilha_expressao_relacional = criar_pilha(['<valor_relacional>', 'REL', '<valor_relacional>'])
    acc = ''
    lista_parenteses = []
    parenteses = True
    fim = False    

    while(not fim and i<len(file_symbols)):
        simbolo = file_symbols[i]
        while(parenteses):
            if simbolo["lexema"] == "(":
                i += 1
                acc += '('
                lista_parenteses.append('(')
                simbolo = file_symbols[i]
            else:
                parenteses = False
        if len(pilha_expressao_relacional) == 0:
            parenteses = True
            while(i < len(file_symbols) and len(lista_parenteses) > 0 and parenteses):
                if file_symbols[i]["lexema"] == ')':
                    i += 1
                    acc += ')'
                    lista_parenteses.pop()
                else:
                    parenteses = False
            if i+1 < len(file_symbols) and file_symbols[i]["token"] == "REL":
                pilha_expressao_relacional = criar_pilha(['REL', '<valor>'])
            else:
                fim = True
                continue
        else:
            simbolo = file_symbols[i]
            esperado = pilha_expressao_relacional[-1]
            if esperado == "<valor_relacional>":
                (i, acc_aux) = validar_argumento_expressao_relacional(i)
                if acc_aux != False:
                    pilha_expressao_relacional.pop()
                    acc += acc_aux
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            elif esperado in [simbolo["token"], simbolo["lexema"]]:
                pilha_expressao_relacional.pop()
                acc += simbolo["lexema"]
            elif i-1 >= len(lista_parenteses) and len(lista_parenteses) > 0 and file_symbols[i]["lexema"] == ')' and (file_symbols[i-1]["lexema"] == ")" or file_symbols[i-1]["token"] in ["IDE", "NRO"]):
                acc += ")"
                lista_parenteses.pop()
                i += 1
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            if len(pilha_expressao_relacional) > 0:
                parenteses = True
                i += 1
            else:
                i += 1
    print_faltando_esperado(lista_parenteses)
    print_faltando_esperado(pilha_expressao_relacional)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc
    
###################################################################################################################

def analisar_bloco(i):
    pilha_bloco = criar_pilha(['{', '<codigo>', '}'])
    acc = ''
    
    while(i < len(file_symbols) and len(pilha_bloco) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_bloco[-1]
        
        if esperado == '<codigo>':
            if simbolo["lexema"] != '}':
                (i, acc_aux) = validar_codigo(i, validar_argumentos_de_bloco, '}')
                if acc_aux != False:
                    acc += acc_aux
                    pilha_bloco.pop()
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            else:
                pilha_bloco.pop()
                continue
        elif esperado == simbolo["lexema"]:
            pilha_bloco.pop()
            acc += simbolo["lexema"]
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        if len(pilha_bloco) > 0:
            i += 1
            
    print_faltando_esperado(pilha_bloco)
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc

def validar_codigo(i, validar_funcao, delimitador):
    simbolo = file_symbols[i]
    codigo = True
    acc = ''
    
    while(codigo):
        (i, acc_aux) = validar_funcao(i)
        if acc_aux != False:
            acc += acc_aux
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if file_symbols[i+1]["lexema"] == delimitador:
            codigo = False
        else:
            i += 1
    
    return i, acc
            
        
###################################################################################################################

# validação para if e while
def validar_argumentos_estruturas(i):
    simbolo = file_symbols[i]
    
    if i+1 < len(file_symbols) and file_symbols[i+1]["lexema"] != ")":
        (i, _) = validar_argumento_expressao_relacional(i, return_error=False)
        if i+1 < len(file_symbols) and file_symbols[i+1]["token"] == "REL":
            return analisar_expressao_relacional(i)
        (i, _) = validar_argumento_expressao_logica(i, return_error=False)
        if i+1<len(file_symbols) and file_symbols[i+1]["token"] == "LOG":
            return analisar_expressao_logica(i)
        return i, erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

    elif simbolo["lexema"] in get_boolean() or simbolo["token"] == "IDE":
        return i+1, simbolo["lexema"]
    else:
        return i, erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)


#########################################################START######################################################   

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
            print("lexema", simbolo["lexema"])
            if simbolo["lexema"] == 'read':
                print("AQUIII")
                (i, acc_aux) = analisar_read(i)
                pilha_start = criar_pilha(['<codigo>', '}'])
                acc += acc_aux

            elif simbolo["lexema"] == 'var':
                print("AQUIII")
                (i, acc_aux) = analisar_var(i)
                pilha_start = criar_pilha(['<codigo>', '}'])
                acc += acc_aux

            elif simbolo["lexema"] == 'print':
                print("AQUIII")
                (i, acc_aux) = analisar_print(i)
                acc += acc_aux

            elif simbolo["lexema"] == 'if':
                #(i, acc_aux) = analisar_if(i)
                #pilha_start = criar_pilha(['<codigo>', '}'])
                #acc += acc_aux
                pass
            elif simbolo["lexema"] == 'while':
                #(i, acc_aux) = analisar_while(i)
                #pilha_start = criar_pilha(['<codigo>', '}'])
                #acc += acc_aux
                pass
            elif simbolo["lexema"] == 'function':
                #(i, acc_aux) =analisar_function(i)
                #pilha_start = criar_pilha(['<codigo>', '}'])
                #acc += acc_aux
                pass
            elif simbolo["lexema"] == 'procedure':
                #(i, acc_aux) = analisar_procedure(i)
                #pilha_start = criar_pilha(['<codigo>', '}'])
                #acc += acc_aux
                pass
            elif simbolo["lexema"] == ';' and file_symbols[i + 1]["lexema"] != '}':
                pilha_start = criar_pilha(['<codigo>', '}'])
                acc += simbolo["lexema"] + ' '
                #pilha_start.pop()

            else:
                pilha_start.pop()
                continue
                #acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
                

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


######################################################ERROS###############################################################

#Erro de token inesperado 
def erro_inesperado_handler(lexema, linha, referencia = None):
  erros_sintaticos.append('Erro: Token inesperado ' + lexema + ' na linha ' + str(linha))
  print(pintar_vermelho(referencia) + ' Erro: Token inesperado ' + pintar_vermelho(lexema) + ' na linha ' + str(linha))
  return pintar_vermelho(lexema)

#Erro de token não declarado
def erro_nao_declarado(lexema, linha):
  erros_semanticos.append('Erro: Variável ' + lexema + ' não declarada na linha ' + str(linha))
  print(pintar_vermelho(getframeinfo(currentframe()).lineno) + ' Erro: Variável ' + pintar_vermelho(lexema) + ' não declarada na linha ' + str(linha))

#Função principal
if __name__ == "__main__":
    tokens = [] #lista de tokens
    erros_sintaticos = [] #lista de tokens com erros sintaticos
    erros_semanticos = []
    for arquivo in ler_pasta_arquivos(): #lendo cada arquivo da pasta input
        analisar_tokens(analisar_lexico(arquivo)) #chamando o analisador léxico
        # Aqui a gente faz a análise desse arquivo
        #montar_output(arquivo, tokens, tokens_erros)
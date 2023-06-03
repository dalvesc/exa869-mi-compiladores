from lexical import *
from utils import *
from inspect import currentframe, getframeinfo

IDENTIFICADORES = ['IDE', 'MATRIZ', 'STRUCT']

pilha_escopo = ['global']
pilha_chaves = []
pilha_simbolos = []
lista_identificadores = []
file_symbols = []

# TODO: 
#     - ESCREVER O OUTPUT SINTÁTICO NO ARQUIVO

def montar_output_sintatico(arquivo):
    filename = ''+arquivo+'-saida.txt' 
    arquivo = arquivo.replace('.txt', '')
    arquivo = open(os.getcwd()+'/files/output/'+arquivo+'-saida.txt', 'a')
   
    erros_sanitizado = [x for x in erros_sintaticos if x is not None]
        
    if len(erros_sanitizado) > 0:
        arquivo.write( '\n\nErros sintáticos: \n\n')
        print(erros_sanitizado)
        for erro in erros_sanitizado:
            arquivo.write(erro + '\n')
    else:
        arquivo.write('\n\nNão há erros sintáticos!')
    print("Arquivo "+ filename +" gerado com sucesso!")
    arquivo.close()
    
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
            (i, _) = validar_declaracao_procedure(i)
        elif file_symbols[i]['lexema'] == 'function':
            (i, _) = validar_declaracao_funcao(i)
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

    erros_sintaticos.append(print_faltando_esperado(pilha_struct))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc

#########################################################VARIÁVEIS######################################################

# Analisa o escopo de uma variável
def analisar_declaracao(i, tipo="var"):
    acc = ""
    if file_symbols[i]["lexema"] not in get_tipos():
        erros_sintaticos.append(f"Erro: Tipo esperado na linha {file_symbols[i]['numLinha']}")
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
    
    erros_sintaticos.append(print_faltando_esperado(pilha_declaracao))

    return i, acc

#########################################################ATRIBUIÇÃO######################################################

# Analisa o escopo de uma atribuição
def analisar_atribuicao(i):
    simbolo = file_symbols[i]

    if i+1 < len(file_symbols):
        (j, _) = validar_argumento_expressao_aritmetica(i, ["IDE", "NRO"], return_error=False)
        if j+1 < len(file_symbols) and file_symbols[i+1]["token"] == "ART":
            (i, acc_aux) = analisar_expressao_aritmetica(i)
            i -= 1
            return i, acc_aux
        (j, _) = validar_argumento_expressao_relacional(i, return_error=False)
        if j+1 < len(file_symbols) and file_symbols[i+1]["token"] == "REL":
            (i, acc_aux) = analisar_expressao_relacional(i)
            i -= 1
            return i, acc_aux
        (j, _) = validar_argumento_expressao_logica(i, return_error=False)
        if j+1 < len(file_symbols) and file_symbols[i+1]["token"] == "LOG":
            (i, acc_aux) = analisar_expressao_logica(i)
            i -= 1
            return i, acc_aux
    
    if simbolo["token"] == "IDE" or simbolo["token"] == "NRO" or simbolo["token"] == "CAC" or simbolo["lexema"] in get_boolean():
        acc_aux = simbolo["lexema"]
        if(simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '['):
            (i, acc_aux) = analisar_matriz(i)
        elif(simbolo["token"] == "IDE" and file_symbols[i+1]["lexema"] == '.'):
            (i, acc_aux) = validar_atribuicao_struct(i)
        elif(simbolo["token"] == "IDE") and file_symbols[i+1]["lexema"] == '(':
            (i, acc_aux) = validar_chamada_funcao_procedure(i)
            
        return i, acc_aux
    
def validar_atribuicao(i, accum = True):
    acc = ''
    if file_symbols[i]["token"] == "IDE":
        if accum:
            simbolo = file_symbols[i]
            acc += simbolo["lexema"]
        i += 1
        if file_symbols[i]["lexema"] == "=":
            acc += '='
            i += 1
            simbolo = file_symbols[i]
            (i, acc_aux) = analisar_atribuicao(i)
            if acc_aux != False:
                acc += acc_aux
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
    return i, acc


def validar_atribuicao_struct(i):
    fim = False
    simbolo = file_symbols[i]
    
    if simbolo["token"] != "IDE":
        erros_sintaticos.append(f"Erro: Tipo esperado na linha {simbolo['numLinha']}")
        return i
    
    acc = simbolo["lexema"]
    while(not fim and i+1<len(file_symbols)):
        simbolo_aux = file_symbols[i+1]
        if simbolo_aux["lexema"] != '.':
            fim = True
            continue
        acc += simbolo_aux["lexema"]
        if i+2 >= len(file_symbols):
            i+=1
            erro = f"Erro: Identificador esperado na linha {simbolo_aux['numLinha']}"
            erros_sintaticos.append(erro)
            print(erro)
            continue
        simbolo_aux2 = file_symbols[i+2]
        if simbolo_aux2["lexema"] == '.':
            i += 1
            erro = f"Identificador faltando na linha {simbolo_aux2['numLinha']}"
            erros_sintaticos.append(erro)
            print(erro)
            continue
        if simbolo_aux2["token"] != "IDE":
            erro = f"Erro: Token inesperado {simbolo_aux2['token']} na linha {simbolo_aux2['numLinha']}"
            erros_sintaticos.append(erro)
            print(erro)
            i+=1
        acc += simbolo_aux2["lexema"]
        i += 2
    
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    return i, acc
    
    
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
    
    erros_sintaticos.append(print_faltando_esperado(pilha_const))
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
    
    erros_sintaticos.append(print_faltando_esperado(pilha_var))
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
                
    erros_sintaticos.append(print_faltando_esperado(pilha_vetor))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i-1, acc

###################################################PROCEDURE###############################################################

# Analisa o escopo de uma procedure
def validar_declaracao_procedure(i):
    pilha_declaracao_procedure = criar_pilha(['procedure', 'IDE', '(', '<parametros>', ')', '{', '<codigo>', '}'])
    acc = ''
    
    while(i < len(file_symbols) and len(pilha_declaracao_procedure) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_declaracao_procedure[-1]
        if esperado == '<parametros>':
            if simbolo["lexema"] != ')':
                (i, acc_aux) = validar_parametro(i)
                if acc_aux != False:
                    acc += acc_aux
                    pilha_declaracao_procedure.pop()
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            else:
                pilha_declaracao_procedure.pop()
                continue
        elif esperado == '<codigo>':
            (i, acc_aux) = validar_codigo(i, '}')
            if acc_aux != False:
                acc += acc_aux
                pilha_declaracao_procedure.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif esperado in [simbolo["lexema"], simbolo["token"]]:
            pilha_declaracao_procedure.pop()
            acc += simbolo["lexema"]
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if len(pilha_declaracao_procedure) > 0:
            i += 1
    
    erros_sintaticos.append(print_faltando_esperado(pilha_declaracao_procedure))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc
    

################################################FUNÇÃO###############################################################

def validar_parametro(i):
    acc = ''
    mais_parametros = True
    pilha_parametros = criar_pilha(['<tipo>', 'IDE'])
    
    while(mais_parametros and i<len(file_symbols)-1 and file_symbols[i]["lexema"] != ")"):
        simbolo = file_symbols[i]
        if len(pilha_parametros) == 0:
            if simbolo["lexema"] == ")":
                mais_parametros = False
            else:
                pilha_parametros = criar_pilha([',', '<tipo>', 'IDE'])
                continue
        else:
            esperado = pilha_parametros[-1]
            if esperado == '<tipo>':
                if not simbolo["lexema"] in get_tipos():
                    # TODO: talvez seja um acc
                    erros_sintaticos.append(f"Erro: Tipo esperado na linha {simbolo['numLinha']}")
                else:
                    acc += simbolo["lexema"]
            elif esperado in [simbolo["lexema"], simbolo["token"]]:
                acc += simbolo["lexema"]
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            i += 1
            pilha_parametros.pop()
    i -= 1
    return i, acc


# Analisa o escopo de uma function
def validar_declaracao_funcao(i):
    pilha_declaracao_funcao = criar_pilha(['function', '<tipo>', 'IDE', '(', '<parametros>', ')', '{', '<codigo>', 'return', '<retorno>', ';' ,'}'])
    acc = ''
    
    while(i < len(file_symbols) and len(pilha_declaracao_funcao) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_declaracao_funcao[-1]
        if esperado == '<parametros>':
            if simbolo["lexema"] != ')':
                (i, acc_aux) = validar_parametro(i)
                if acc_aux != False:
                    acc += acc_aux
                    pilha_declaracao_funcao.pop()
                else:
                    acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            else:
                pilha_declaracao_funcao.pop()
                continue
        elif esperado == '<codigo>':
            (i, acc_aux) = validar_codigo(i, 'return')
            if acc_aux != False:
                acc += acc_aux
                pilha_declaracao_funcao.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif esperado == '<retorno>':
            (i, acc_aux) = validar_argumentos_retorno(i)
            if acc_aux != False:
                pilha_declaracao_funcao.pop()
                acc += acc_aux
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif esperado in [simbolo["lexema"], simbolo["token"]]:
            pilha_declaracao_funcao.pop()
            acc += simbolo["lexema"]
        elif esperado == '<tipo>':
            if simbolo["lexema"] in get_tipos():
                pilha_declaracao_funcao.pop()
                acc += simbolo["lexema"]
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if len(pilha_declaracao_funcao) > 0:
            i += 1
    
    erros_sintaticos.append(print_faltando_esperado(pilha_declaracao_funcao))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc

def validar_argumentos_retorno(i):
    simbolo = file_symbols[i]
    if simbolo["token"] == 'NRO' or simbolo["token"] == 'CAC' or simbolo["token"] == 'IDE' or simbolo["lexema"] in get_boolean():
        return i, simbolo["lexema"]
    return i, False

def validar_chamada_funcao_procedure(i):
    pilha_chamada_funcao = criar_pilha(['IDE', '(', '<parametros>', ')'])
    acc = ''
    lista_parametros = []
    
    while(i < len(file_symbols) and len(pilha_chamada_funcao) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_chamada_funcao[-1]
        if esperado == '<parametros>':
            if simbolo["lexema"] != ')':
                args_validos = ["CCA", "NUM"]
                args_validos.extend(IDENTIFICADORES)
                mais_parametros = True
                parametros = criar_pilha(['<parametros>'])
                while(mais_parametros and i<len(file_symbols)-1 and file_symbols[i]["lexema"] != ')'):
                    simbolo = file_symbols[i]
                    if len(parametros) == 0:
                        if simbolo["lexema"] == ')':
                            mais_parametros = False
                        else:
                            parametros = criar_pilha([',', '<parametros>'])
                            continue
                    else:
                        esperado = parametros[-1]
                        if esperado == '<parametros>':
                            j = i
                            (i, acc_aux) = analisar_argumento(i, args_validos, args_funcao=True)
                            if acc_aux != False:
                                acc += acc_aux
                            else:
                                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
                        elif esperado == simbolo["lexema"]:
                            acc += simbolo["lexema"]
                        else:
                            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
                        i += 1
                        parametros.pop()
                i -= 1
                pilha_chamada_funcao.pop()
            else:
                pilha_chamada_funcao.pop()
                continue
        elif esperado in [simbolo["token"], simbolo["lexema"]]:
            pilha_chamada_funcao.pop()
            acc += simbolo["lexema"]
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        if len(pilha_chamada_funcao) > 0:
            i += 1
            
    erros_sintaticos.append(print_faltando_esperado(pilha_chamada_funcao))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc

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
    
    erros_sintaticos.append(print_faltando_esperado(pilha_read))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc

#########################################################PRINT######################################################

# Analisa o escopo de um print
def analisar_print(i):
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
    
    erros_sintaticos.append(print_faltando_esperado(pilha_print))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc

def analisar_if_then_else(i):
    pilha_if = criar_pilha(['if', '(', '<expressao>', ')', 'then', '<codigo>', 'else'])
    acc = ''
    
    while(i<len(file_symbols) and len(pilha_if) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_if[-1]
        if esperado == '<expressao>':
            (i, acc_aux) = validar_argumentos_estruturas(i)
            i -= 1
            if acc_aux != False:
                acc += acc_aux
                pilha_if.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif esperado == '<codigo>':
            (i, acc_aux) = analisar_bloco(i)
            if acc_aux != False:
                acc += acc_aux
                pilha_if.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            if len(pilha_if) > 0 and pilha_if[-1] == 'else':
                if i+1 < len(file_symbols) and file_symbols[i+1]["lexema"] == 'else':
                    pilha_if = criar_pilha(['else', '<codigo>'])
                else:
                    pilha_if.pop()
        elif esperado == simbolo["lexema"]:
            pilha_if.pop()
            acc += simbolo["lexema"]
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno) 
        
        if len(pilha_if) > 0:
            i+=1

    erros_sintaticos.append(print_faltando_esperado(pilha_if))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc

def analisar_while(i):
    pilha_while = criar_pilha(['while', '(', '<expressao>', ')', '<codigo>'])
    acc = ''
    
    while(i<len(file_symbols) and len(pilha_while) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_while[-1]
        
        if esperado == '<expressao>':
            (i, acc_aux) = validar_argumentos_estruturas(i)
            i -= 1
            if acc_aux != False:
                acc += acc_aux
                pilha_while.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno) 
        elif esperado == '<codigo>':
            (i, acc_aux) = analisar_bloco(i)
            if acc_aux != False:
                acc += acc_aux
                pilha_while.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno) 
        elif esperado == simbolo["lexema"]:
            pilha_while.pop()
            acc += simbolo["lexema"]
        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        
        if len(pilha_while) > 0:
            i += 1
        
    erros_sintaticos.append(print_faltando_esperado(pilha_while))
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
        if file_symbols[i+1]["lexema"] == "(":
            (i, acc_aux) = validar_chamada_funcao_procedure(i)
            return i, acc_aux
        elif file_symbols[i+1]["lexema"] == ",":
            return i, simbolo["lexema"]
    
    if (set(IDENTIFICADORES) & set(lista_args)) and simbolo["token"] == "IDE":
        simbolo_aux = file_symbols[i+1]
        if "IDE" in lista_args and final in [f"_{simbolo_aux['token']}", simbolo_aux["lexema"]]:
            return i, simbolo["lexema"]
        elif "STRUCT" in lista_args and simbolo_aux["lexema"] == ".":
            return validar_atribuicao_struct(i)
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
            (i, acc_aux) = validar_atribuicao_struct(i)
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
        if simbolo["token"] == "IDE":
            if i+1 < len(file_symbols) and file_symbols[i+1]["lexema"] == "(":
                (i, acc_aux) = validar_chamada_funcao_procedure(i)
                return i, acc_aux
            return i, simbolo["lexema"]
        
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
            return validar_atribuicao_struct(i)
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
    erros_sintaticos.append(print_faltando_esperado(lista_parenteses))
    erros_sintaticos.append(print_faltando_esperado(pilha_expressao_aritmetica))
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
        
    erros_sintaticos.append(print_faltando_esperado(pilha_expressao_logica))
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
    erros_sintaticos.append(print_faltando_esperado(lista_parenteses))
    erros_sintaticos.append(print_faltando_esperado(pilha_expressao_relacional))
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
                (i, acc_aux) = validar_codigo(i, '}')
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
            
    erros_sintaticos.append(print_faltando_esperado(pilha_bloco))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)
    
    return i, acc

def validar_argumentos_de_bloco(i):
    simbolo = file_symbols[i]
    if simbolo["lexema"] == 'print':
        return analisar_print(i)
    elif simbolo["lexema"] == 'read':
        return analisar_read(i)
    elif simbolo["lexema"] == 'while':
        return analisar_while(i)
    elif simbolo["lexema"] == 'if':
        return analisar_if_then_else(i)
    elif simbolo["lexema"] == 'var':
        return analisar_var(i)
    elif i+1 < len(file_symbols) and simbolo["token"] == "IDE":
        simbolo_aux = file_symbols[i+1]
        if simbolo_aux["lexema"] == '=':
            (i, acc_aux) = validar_atribuicao(i)
            i += 1
            if file_symbols[i]["lexema"] == ';':
                acc_aux += ';'
                return i, acc_aux
            else:
                erros_sintaticos.append(f"Token em falta: ; na linha {file_symbols[i-1]['numLinha']}")
                return i, erro_inesperado_handler(file_symbols[i]["lexema"], file_symbols[i]["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif simbolo_aux["lexema"] == '.':
            (i, acc_aux) = validar_atribuicao_struct(i)
            if file_symbols[i+1]["lexema"] == '=':
                (i, acc_aux2) = validar_atribuicao(i, accum = False)
                acc_aux += acc_aux2
                i +=1
                if file_symbols[i]["lexema"] == ';':
                    acc_aux += ';'
                    return i, acc_aux
                else:
                    erros_sintaticos.append(f"Token em falta: ; na linha {file_symbols[i-1]['numLinha']}")
                    return i, erro_inesperado_handler(file_symbols[i]["lexema"], file_symbols[i]["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif simbolo_aux["lexema"] == "(":
            (i, acc_aux) = validar_chamada_funcao_procedure(i)
            i += 1
            if file_symbols[i]["lexema"] == ';':
                acc_aux += ';'
                return i, acc_aux
            else:
                erros_sintaticos.append(f"Token em falta: ; na linha {file_symbols[i-1]['numLinha']}")
                return i, erro_inesperado_handler(file_symbols[i]["lexema"], file_symbols[i]["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        elif simbolo_aux["lexema"] == '[':
            (i, acc_aux) = analisar_matriz(i)
            if file_symbols[i]["lexema"] == ';':
                acc_aux += ';'
                return i, acc_aux
            else:
                erros_sintaticos.append(f"Token em falta: ; na linha {file_symbols[i-1]['numLinha']}")
                return i, erro_inesperado_handler(file_symbols[i]["lexema"], file_symbols[i]["numLinha"], referencia=getframeinfo(currentframe()).lineno)
        else: 
            return i, erro_inesperado_handler(simbolo_aux["lexema"], simbolo_aux["numLinha"], referencia=getframeinfo(currentframe()).lineno)
    else:
        return i, erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

def validar_codigo(i, delimitador):
    simbolo = file_symbols[i]
    codigo = True
    acc = ''
    
    while(codigo):
        (i, acc_aux) = validar_argumentos_de_bloco(i)
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
    pilha_start = criar_pilha(['start', '<codigo>'])

    while(i < len(file_symbols) and len(pilha_start) > 0):
        simbolo = file_symbols[i]
        esperado = pilha_start[-1]

        if esperado == '<codigo>':
            (i, acc_aux) = analisar_bloco(i)
            if acc_aux != False:
                acc += acc_aux
                pilha_start.pop()
            else:
                acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
            
            
            # pilha_start.pop()
            # pilha_escopo.append('start')
            # # Ver análise do codigo
            # print("lexema", simbolo["lexema"])
            # if simbolo["lexema"] == 'read':
            #     (i, acc_aux) = analisar_read(i)
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux

            # elif simbolo["lexema"] == 'var':
            #     (i, acc_aux) = analisar_var(i)
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux

            # elif simbolo["lexema"] == 'print':
            #     (i, acc_aux) = analisar_print(i)
            #     #pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux

            # elif simbolo["lexema"] == 'if':
            #     (i, acc_aux) = analisar_if_then_else(i)
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux
            # elif simbolo["lexema"] == 'while':
            #     (i, acc_aux) = analisar_while(i)
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux
            # elif simbolo["lexema"] == 'function':
            #     (i, acc_aux) = validar_declaracao_funcao(i)
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux
            # elif simbolo["lexema"] == 'procedure':
            #     (i, acc_aux) = validar_declaracao_procedure(i)
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += acc_aux
            # elif simbolo["lexema"] == ';' and file_symbols[i + 1]["lexema"] != '}':
            #     pilha_start = criar_pilha(['<codigo>', '}'])
            #     acc += simbolo["lexema"] + ' '

            # else:
            #     pilha_start.pop()
            #     continue
            #     #acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)
                

        elif simbolo["lexema"] == esperado or simbolo["token"] == esperado:
            pilha_start.pop()
            acc += simbolo["lexema"] + ' '

        else:
            acc += erro_inesperado_handler(simbolo["lexema"], simbolo["numLinha"], referencia=getframeinfo(currentframe()).lineno)

        if len(pilha_start) > 0:
            i += 1
    erros_sintaticos.append(print_faltando_esperado(pilha_start))
    print(pintar_azul(getframeinfo(currentframe()).lineno), acc)

    return i, acc


######################################################ERROS###############################################################

#Erro de token inesperado 
def erro_inesperado_handler(lexema, linha, referencia = None):
  erros_sintaticos.append('Erro: Token inesperado ' + lexema + ' na linha ' + str(linha))
  print(pintar_vermelho(referencia) + ' Erro: Token inesperado ' + pintar_vermelho(lexema) + ' na linha ' + str(linha))
  return pintar_vermelho(lexema)

#Função principal
if __name__ == "__main__":
    erros_sintaticos = [] #lista de tokens com erros sintaticos
    for arquivo in ler_pasta_arquivos(): #lendo cada arquivo da pasta input
        analisar_tokens(analisar_lexico(arquivo)) #chamando o analisador léxico
        # Aqui a gente faz a análise desse arquivo
        montar_output_sintatico(arquivo)
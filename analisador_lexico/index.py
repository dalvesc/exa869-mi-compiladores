import os
import unicodedata


palavras_reservadas = ['var', 'const', 'struct', 'procedure', 'function', 
                       'start', 'return', 'if', 'else', 'then', 'while', 'read', 
                       'print', 'int', 'real', 'boolean', 'string', 'true', 'false']
operadores_aritmeticos = ['+', '-', '*', '/', '++', '--']
operadores_relacionais = ['!=', '==', '<', '<=', '>', '>=', '=']
operadores_logicos = ['!', '&&', '||']
delimitadores_comentarios = ['//', '/*', '*/']
delimitadores = [';', ',', '(', ')','[', ']', '{', '}', '.']
simbolo_ascii = [i for i in range(32, 127) if i != 34]

pasta = os.getcwd()+'/files/input/testte/' #pasta dos códigos de input

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

#salva os tokens e erros em arquivos de output
def montar_output(arquivo, tokens, tokens_erros):
    arquivo = arquivo.replace('.txt', '')
    arquivo = open(os.getcwd()+'/files/output/'+arquivo+'-saida.txt', 'w')
    arquivo.write( 'Tokens: \n\n')
    for token in tokens:
        arquivo.write(token)
    if tokens_erros:
        arquivo.write( '\nErros: \n')
        for token_erro in tokens_erros:
            arquivo.write(token_erro)
    else: 
        arquivo.write( '\nSucesso, nenhum erro encontrado!')
    arquivo.close()


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#monta o token
def montar_token(classificacao, lexema, linha):
    return '<"'+classificacao+'", "'+''.join(lexema)+'", '+str(linha)+'>\n'

#identifica se o lexema é uma palavra reservada
def is_palavra_reservada(lexema):
    return lexema in palavras_reservadas

#identifica se o lexema é um identificador
def is_identificador(lexema):
    if not lexema[0].isdigit() and lexema[0] != '_' and lexema[0] not in delimitadores:
        for caracter in lexema:
            if not caracter.isalnum() and caracter != '_':
                return False
        return True
    return False

#identifica se o lexema é um número
def is_numero(lexema):
    if len(lexema) > 1 and lexema[0] == '-' and lexema[-1].isdigit():
        return True
    return lexema.isdigit() or isfloat(lexema)

#identifica se o lexema é um operador aritmetico
def is_operador_aritmetico(lexema):
    return lexema in operadores_aritmeticos

#identifica se o lexema é um operador relacional
def is_operador_relacional(lexema):
    return lexema in operadores_relacionais

#identifica se o lexema é um operador logico
def is_operador_logico(lexema):
    return lexema in operadores_logicos

#identifica se o lexema é um delimitador
def is_delimitador(lexema):
    return lexema in delimitadores

#identifica se o lexema é um delimitador de comentario
def is_delimitador_comentario(lexema):
    return lexema in delimitadores_comentarios

#identifica se o lexema é um caractere válido na tabela ascii
def is_caractere_valido_string(lexema):
    return all(ord(c) in simbolo_ascii or c == '"' for c in lexema)

#identifica se o lexema é uma cadeia de caracteres
def is_cadeia_caractere(lexema):
    if len(lexema) > 1:
        if lexema[0] == '"' and lexema[-1] == '"':
            if is_caractere_valido_string(lexema):
                return True
        else:
            return False    

#todos os analisadores para passar o lexema
def analisadores(lexema, linha_encontrada):
    if is_palavra_reservada(lexema):
        return tokens.append(montar_token('palavra reservada', lexema, linha_encontrada))
    elif is_delimitador_comentario(lexema):
        return tokens.append(montar_token('delimitador de comentario', lexema, linha_encontrada))
    elif is_operador_aritmetico(lexema):
        return tokens.append(montar_token('operador aritmetico', lexema, linha_encontrada))
    elif is_operador_relacional(lexema):
        return tokens.append(montar_token('operador relacional', lexema, linha_encontrada))
    elif is_operador_logico(lexema):
        return tokens.append(montar_token('operador logico', lexema, linha_encontrada))
    elif is_delimitador(lexema):
        return tokens.append(montar_token('delimitador', lexema, linha_encontrada))
    elif is_cadeia_caractere(lexema):
        return tokens.append(montar_token('cadeia de caracteres', lexema, linha_encontrada))
    elif is_numero(lexema):
        return tokens.append(montar_token('numero', lexema, linha_encontrada))
    elif is_identificador(lexema):
        return tokens.append(montar_token('identificador', lexema, linha_encontrada))
    else:
        return tokens_erros.append(montar_token('erro', lexema, linha_encontrada))
    #outros if's para os outros analisadores

#ler linha por linha do arquivo e passar para o analisador
def analisar_arquivo(linhas):
    linha_atual = 0
    lexemas_da_linha = []
    comentario = True
    for linha in linhas:
        lexemas_da_linha = []
        linha_atual = linha_atual + 1
        lexema = []
        print("LINHA: ", linha)
        i=0
        while i < len(linha):
            letra = linha[i]

            if letra != "\n":
                if letra in delimitadores and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexemas_da_linha.append(letra)
                    i = i + 1
                    continue   

                elif letra == "/" and linha[i+1] == "*" and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexema.append(letra)
                    lexema.append(linha[i+1])
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    comentario = False
                    i = i + 2
                    continue

                elif letra == "*" and linha[i+1] == "/": #falta quando n fecha o comentario de bloco aberto
                    lexema.append(letra)
                    lexema.append(linha[i+1])
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    comentario = True
                    i = i + 2
                    continue

                elif letra == "/" and linha[i+1] == "/" and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexema.append(letra)
                    lexema.append(linha[i+1])
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    i = len(linha)
                    continue

                elif letra.isdigit() and linha[i - 1] == ' ' and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexema.append(letra)
                    j = i
                    for letra2 in linha[j+1:]:
                        if not letra2.isdigit() and not letra2 == ".":
                            lexemas_da_linha.append(''.join(lexema).strip())
                            lexema = []
                            i = j + 1
                            break
                        elif letra2 == "\n":
                            lexemas_da_linha.append(''.join(lexema).strip())
                            lexema = []
                            i = j + 1
                            break
                        else:
                            j = j + 1
                            lexema.append(letra2)
                    continue

                elif letra == '-' and linha[i+1].isdigit() and comentario:
                    if not lexemas_da_linha[-1]: 
                        lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexema.append(letra)
                    j = i
                    for letra2 in linha[j+1:]:
                        if lexemas_da_linha and is_numero(lexemas_da_linha[-1]):
                            lexemas_da_linha.append(''.join(letra).strip())
                            lexema = []
                            i = j + 1
                            break
                        elif not letra2.isdigit():
                            lexemas_da_linha.append(''.join(lexema).strip())
                            lexema = []
                            i = j + 1
                            break
                        elif letra2 == "\n":
                            lexemas_da_linha.append(''.join(lexema).strip())
                            lexema = []
                            i = j + 1
                            break
                        else:
                            j = j + 1
                            lexema.append(letra2)
                    continue

                elif letra in operadores_aritmeticos and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexemas_da_linha.append(letra)
                    i = i + 1
                    continue

                elif letra.isdigit() and linha[i+1] in operadores_aritmeticos and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                    lexemas_da_linha.append(letra)
                    i = i + 1
                    continue

                elif letra == '"' and comentario:
                    if lexema != ['"']:    
                        lexemas_da_linha.append(''.join(lexema).strip())
                        lexema = []
                        lexema.append(letra)
                        j = i
                        for letra2 in linha[j+1:]:
                            if letra2 == '"':
                                lexema.append(letra2)
                                lexemas_da_linha.append(''.join(lexema).strip())
                                lexema = []
                                i = j+2
                                break
                            elif letra2 == '\n':
                                lexemas_da_linha.append(''.join(lexema).strip())
                                lexema = []
                                i = j+2
                                break
                            else:   
                                j = j + 1
                                lexema.append(letra2)
                        continue                    

                elif letra == ' ' and comentario:
                    lexemas_da_linha.append(''.join(lexema).strip())
                    lexema = []
                
                elif comentario:
                    lexema.append(letra)
                print("LEXEMA: ", lexema)
            i = i + 1    
                #print("STRING: ", lexema)
        lexemas_da_linha = [item for item in lexemas_da_linha if item != '']
        print("LEXEMAS DA LINHA: ", lexemas_da_linha)
        print("============")
        print("\n")
        for lexema in lexemas_da_linha:
            analisadores(lexema, linha_atual)

            





if __name__ == "__main__":
    for arquivo in ler_pasta_arquivos():
        tokens = []
        tokens_erros = []
        analisar_arquivo(ler_linha_arquivo(pasta+arquivo))
        montar_output(arquivo, tokens, tokens_erros)
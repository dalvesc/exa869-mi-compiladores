import os
import unicodedata


palavras_reservadas = ['var', 'const', 'struct', 'procedure', 'function', 'start', 'return', 'if', 'else', 'then', 'while', 'read', 'print', 'int', 'real', 'boolean', 'string', 'true', 'false']
identificadores = []
numeros = []
digitos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
letras = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
operadores_aritmeticos = ['+', '-', '*', '/', '++', '--']
operadores_relacionais = ['!=', '==', '<', '<=', '>', '>=', '=']
operadores_logicos = ['!', '&&', '||']
delimitadores_comentarios = ['//', '/*', '*/']
delimitadores = [';', ',', '(', ')','[', ']', '{', '}', '.']
cadeia_caracteres = []
simbolo = []
espaços = []

pasta = os.getcwd()+'/analisador_lexico/files/input/' #pasta dos códigos de input


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
    arquivo = open(os.getcwd()+'/analisador_lexico/files/output/'+arquivo+'-saida.txt', 'w')
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

#monta o token
def montar_token(classificacao, lexema, linha):
    return '<"'+classificacao+'", "'+''.join(lexema)+'", '+str(linha)+'>\n'

#indentifica se o lexema é uma palavra reservada
def is_palavra_reservada(lexema):
    return lexema in palavras_reservadas

#todos os analisadores para passar o lexema
def analisadores(lexema, linha_encontrada):
    print(lexema)
    if is_palavra_reservada(lexema):
        return tokens.append(montar_token('palavra reservada', lexema, linha_encontrada))
    #outros if's para os outros analisadores

#ler linha por linha do arquivo e passar para o analisador
def analisar_arquivo(linhas):
    linha_encontrada = 0
    for linha in linhas:
        linha_encontrada +=1
        lexema = []
        for letra in linha:
            lexema.append(letra)
            analisadores(''.join(lexema).strip(), linha_encontrada)


if __name__ == "__main__":
    for arquivo in ler_pasta_arquivos():
        tokens = []
        tokens_erros = []
        analisar_arquivo(ler_linha_arquivo(pasta+arquivo))
        montar_output(arquivo, tokens, tokens_erros)
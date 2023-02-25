import os


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

pasta = os.getcwd()+'/analisador_lexico/files/input/'



def ler_linha_arquivo(arquivo):
    arquivo = open(arquivo)
    linhas = arquivo.readlines()
    arquivo.close()

    return linhas

def ler_pasta_arquivos():
    arquivos = []
    for raiz, diretorios, files in os.walk(pasta):
        for arquivo in files:
            arquivos.append(os.path.join(raiz, arquivo))
    return arquivos

print(ler_linha_arquivo(ler_pasta_arquivos()[0])) #aparecendo \xa0 no lugar de espaço

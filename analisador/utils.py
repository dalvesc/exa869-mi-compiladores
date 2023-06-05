def pintar_vermelho(texto): 
    # exibindo erro em vermelho no terminal
    return '\033[1;31m' + str(texto) + '\033[0;0m'

def pintar_azul(texto): 
    # exibindo erro em azul no terminal
    return '\033[1;34m' + str(texto) + '\033[0;0m'

def pintar_verde(texto): 
    # exibindo erro em verde no terminal
    return '\033[1;32m' + str(texto) + '\033[0;0m'

def get_tipos():
    return ['int', 'real', 'boolean', 'string']

def get_boolean():
    return ['true', 'false']

def get_simbolos_aritmeticos():
    return ['+', '-', '*', '/']

def get_simbolos_logicos():
    return ['&&', '||']

def get_simbolos_relacionais():
    return ['>', '<', '>=', '<=', '==', '!=']

def print_faltando_esperado(pilha_esperado):
    if(len(pilha_esperado) > 0):
        pilha_esperado.reverse()
        erro = 'Erro: tokens em falta ' + str(pilha_esperado)
        print(erro)
        return erro
    return None
        
from lexical import * #NAO FUNCIONAAAAA


#############################FAZER A STACK #######################################################
##############################################FAZER O SYMBOL######################################

pilha_escopo = ['global']
pilha_chaves = []
pilha_simbolos = []
escopo_pre = ['start', 'function', 'procedure', 'var', 'const', 'struct']

'}'
start {
    func(){

    }
}

def analisar_tokens(tokens):
    global file_symbols
    file_symbols = []
    i = 0
    for token in tokens:
        symbol = {
            'numLinha': token["numLinha"],
            'token': token["token"],
            'lexema': token["lexema"],
            'escopo': ''
        }

        if symbol["lexema"] in escopo_pre and tokens[i + 1] == '{':
            pilha_escopo.append(symbol["lexema"])

        file_symbols.append(symbol)

    print('SYMBOLS', file_symbols)

def validate_scope(palavra_reservada):
    default_expected = ['var', '{']
    function_expected = []
    procedure_expected = 

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
    tokens = []
    tokens_erros = []
    for arquivo in ler_pasta_arquivos():
        analisar_tokens(analisar_lexico(arquivo))
        # Aqui a gente faz a análise desse arquivo
        #montar_output(arquivo, tokens, tokens_erros)
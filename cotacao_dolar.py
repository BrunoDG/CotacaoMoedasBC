import json
import requests

from json import JSONEncoder
from datetime import datetime

def limpa_conteudo(content):
    fix = {'&lt;': '<', '&gt;': '>'}
    for key, value in fix.items():
        content = content.replace(key, value)
    content = content.replace('\r\n', '')
    content = content.replace('/>    <content', '/> <content')
    return content

def json_return(obj):
    objeto = json.dumps(obj, sort_keys=True, indent=4, cls=CodificaMoeda)
    return objeto

def json_print(obj):
    text = json.dumps(obj, sort_keys=True, indent=4, cls=CodificaMoeda)
    print(text)

def organiza_data(data):
    dataAntiga = data
    objetoData = datetime.strptime(dataAntiga, '%Y%m%d')
    novaData = objetoData.strftime('%m-%d-%Y')
    return novaData

def organiza_cotacao(mo):
    return mo.cotacaoCompra

def print_moeda(codigo, nome, cotacao):
    print ('Codigo: ' + codigo + 
    ', Moeda: ' + nome + 
    ', Cotacao de compra: ' + cotacao)

class CodificaMoeda(JSONEncoder):
    def default(self, o):
        return o.__dict__

class AcessarBacen:

    def __init__(self, url):
        self.url = url
    
    def getURL(self):
        headers = {
            'Host': 'olinda.bcb.gov.br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,mt;q=0.6',
            'content-language': 'en-US',
            'content-type': 'application/json;charset=UTF-8;odata.metadata=minimal',
            'keep-alive': 'timeout=10, max=100'
        }

        # Servidor muito instável, testar 10x resposta http 200
        for _ in range(10):
            try:
                request = requests.get(self.url, headers=headers, timeout=None)
                if request.status_code == 200:
                    return request
                elif request.status_code != 200:
                    continue
            except requests.ConnectionError:
                continue

class Moeda:

    def __init__(self, simbolo, nome, tipo, cotacaoCompra, cotacaoVenda):
        self.simbolo = simbolo
        self.nome = nome
        self.tipo = tipo
        self.cotacaoCompra = cotacaoCompra
        self.cotacaoVenda = cotacaoVenda

class Moedas:
    def __init__(self):
        self.query_url = 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata'
        acesso = AcessarBacen(self.query_url)
        self.req = acesso.getURL()
        self.moedas = limpa_conteudo(self.req.content.decode('utf-8'))

    def get_moedas(self):
        coins = limpa_conteudo(self.req.content.decode('utf-8'))
        parameters = {
            'format': 'json',
            'top': '100',
        }
        coins = requests.get('https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/Moedas', params=parameters)
        moedas = coins.json()['value']
        
        return moedas

class Cotacao:
        def __init__(self):
            self.query_url = 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata'
            acesso = AcessarBacen(self.query_url)
            self.req = acesso.getURL()
            self.cotacao = limpa_conteudo(self.req.content.decode('utf-8'))

        def get_cotacao_todas(self, data, moedas):
            cot = limpa_conteudo(self.req.content.decode('utf-8'))
            cotVal = []
            cotacao = []

            for m in moedas:      
                parameters = {
                    # Estranho, mas a API do Bacen só permite envio de mensagens com string explícita.
                    # Não é a melhor das soluções, mas...
                    '@moeda': '\'' + m['simbolo'] + '\'',
                    '@dataCotacao': '\'' + data + '\'',
                    'format': 'json',
                    'top': '100',
                }

                cot = requests.get('https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)', params=parameters)
                cot_json = cot.json()
                cotVal.append(cot_json['value'])

                for n in range(len(cotVal)):
                    for m in range(len(cotVal[n])):
                        if (cotVal[n][m]['tipoBoletim'] == 'Fechamento PTAX'):
                            cotacao.append(cotVal[n][m])

            return cotacao


dataCotacao = input("Por favor digite a data da cotacao desejada: ")

dataCotacao = organiza_data(dataCotacao)

print('\nAguarde, carregando informações...\n')

moedas = Moedas()
cotacao = Cotacao()

moe = []
coins = []
cot = []

coins = moedas.get_moedas()
cot = cotacao.get_cotacao_todas(dataCotacao, coins)

if (len(cot) == 0):
        print("X")
else:
    for m in range(len(coins)):
        if (coins[m]['simbolo'] != 'USD'):
            coin = Moeda(coins[m]['simbolo'], coins[m]['nomeFormatado'], coins[m]['tipoMoeda'], cot[m]['cotacaoCompra'], cot[m]['cotacaoVenda'])
            moe.append(coin)

    moe.sort(key=organiza_cotacao)
    md = moe[0]

    print_moeda(md.simbolo, md.nome, str(md.cotacaoCompra))
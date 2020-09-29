import json
import requests
from datetime import datetime

def limpa_conteudo(content):
    fix = {'&lt;': '<', '&gt;': '>'}
    for key, value in fix.items():
        content = content.replace(key, value)
    content = content.replace('\r\n', '')
    content = content.replace('/>    <content', '/> <content')
    return content

def json_print(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def organiza_data(self, data):
    dataAntiga = data
    objetoData = datetime.strptime(dataAntiga, '%Y%m%d')
    novaData = objetoData.strftime('%m-%d-%Y')
    return novaData

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

    def __init__(self, codigo, nome, tipo, cotacaoCompra, paridadeCompra, cotacaoVenda, paridadeVenda):
        self.codigo = codigo
        self.nome = nome
        self.tipo = tipo
        self.cotacaoCompra = cotacaoCompra
        self.paridadeCompra = paridadeCompra
        self.cotacaoVenda = cotacaoVenda
        self.paridadeVenda = paridadeVenda
        self.precoCompra = None
        self.precoVenda = None

    def set_preco_usd(self, compra, venda):
        self.precoCompra = compra
        self.precoVenda = venda        

    def print_moeda(self, codigo):
        print ('Codigo: ' + self.codigo + 
        ' | Moeda: ' + self.nome + 
        ' | Cotacao de compra: ' + self.compra + 
        ' | Cotacao de venda: ' + self.venda)
    
    def calcula_moeda(self, codigo, compraUSD, vendaUSD):
        if self.tipo == 'A':
            # Codigo para moeda tipo A, cuja paridade é expressa em quantidade de moeda por uma unidade de dólar
            self.precoCompra = self.paridadeCompra / self.precoCompra
            self.precoVenda = self.paridadeVenda / self.precoVenda
            return
        elif (self.tipo == 'B'):
            # Código para moeda tipo B, cuja paridade é expressa em quantidade de dólar por uma unidade de moeda.
            self.precoCompra = self.cotacaoCompra
            self.precoVenda = self.cotacaoVenda
            return

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
            moe = Moeda()
            cotacao = []

            for m in moedas:        
                parameters = {
                    # Estranho, mas a API do Bacen só permite envio de mensagens com string explícita.
                    # Não é a melhor das soluções, mas...
                    '@moeda': '\'' + m + '\'',
                    '@dataCotacao': '\'' + data + '\'',
                    'format': 'json',
                    'top': '100',
                }

                cot = requests.get('https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)', params=parameters)
                cot_json = cot.json()
                if (m == 'USD'):
                    moe.set_preco_usd(cot_json[value][4]['cotacaoCompra'],cot_json[value][4]['cotacaoVenda'])
                cotacao.append(cot_json['value'])

            return cotacao
        
        #def get_moeda_mais_barata(self):


dataCotacao = input("Por favor digite a data da cotacao desejada: ")

print('\nData da Cotacao: ' + dataCotacao + '\n')

moedas = Moedas()
cotacao = Cotacao()
coins = []

coins = moedas.get_moedas()
cot = cotacao.get_cotacao_todas(dataCotacao, coins)

cotDia = []
coinCheap = []

for c in range(len(coins)):
    if (str(cot[c]) == None):
        cotDia.append("Moeda: " + coins[c] + " | X")
    else:    
        cotDia.append("Moeda: " + coins[c] + " | " + cot[c])



json_print(cotDia)


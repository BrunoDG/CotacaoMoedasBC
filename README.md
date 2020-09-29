# Obter a cotação da moeda a partir do site do Banco Central
Você foi contratado como freelancer por uma empresa de análise de dados que precisa de uma solução para o seguinte problema:

Todos os dias a empresa precisa saber qual moeda possui a menor cotação frente ao dólar. Essa informação é importante para uma outra aplicação de ranking de moedas que eles irão desenvolver.

O gerente da empresa que te contratou te passou o link do banco central (https://www.bcb.gov.br/) como referência. Ele mesmo também não conhece o site do BC detalhadamente para indicar o lugar exato da fonte de dados, mas sabe que é possível baixar um arquivo com os dados desejados a partir do portal.

Neste momento, o que eles precisam é um programa que receba uma data no formato YYYYMMDD via terminal e exiba na saída uma linha com as seguintes informações separadas por vírgula:

- o símbolo da moeda com menor cotação,
- o nome do país de origem da moeda e
- o valor da cotação desta moeda frente ao dólar na data especificada. 
- 
Caso não haja cotação no dia especificado o caracter x deve ser impresso na tela.

Escreva um programa que atenda aos requisitos acima.
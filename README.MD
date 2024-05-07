# Introdução
Este é um projeto open-source para busca de pares de arbitragem entre exchanges.

Seu objetivo é compreensão da estrutura de mercado e comportamento dos preços de ativos entre exchanges. Use por sua conta de risco. O autor não se responsabiliza por qualquais danos ou problemas decorrentes de seu uso. 

Ele usa o lib ccxt, desta forma, é compatível com um grande número de corretas. A lista pode ser contrada aqui: https://docs.ccxt.com/#/?id=exchanges

# Funcionamento

Baseado em uma lista de exchanges e uma lista de símbolos o software calcula oportunidades de arbitragem cruzando os dados das exchanges. Isso é feito olhando o livro de ordem das exchanges e analizando a liquidez disponível no momento. Por exemplo, o usuário informa que pretende arbitrar com até U$1000 e requer ao menos 2% de lucro, o software calcula o preço médio de compra no livro de ordens até atingir o limite de U$1000 ou a porcentagem de lucro miníma de 2%. Ao final da execução, ele informa uma tabela com todas as oportunidades encontradas. 

# Execução

```
python -m venv .env
pip install -r requirements.txt
source .env/bin/activate
python findArb.py
```

O software vem com um arquivo de configuração pronto para uso veja em `configs/findArb.conf` e uma lista de símbolos por exchange que pode ser visto em `configs/pairs.json`.

# Organização

Os seguintes scripts compõe esta aplicação:

- `findArb.py`: executa busca por arbitragem nas exchanges configuradas.
- `findCoins.py`: busca e configura lista de cryptos disponível nas exchanges configuradas.
- `exArb.py`: executa arbitragem entre duas exchanges, mas ainda não foi completamente testado.
- `helpers.py`: funcões adicionais usadas em mais de um script.
- `configs/`: diretório com arquivos de configuração. 

# Configurações Básicas

Informe as exchanges desejadas `configs/findArb.conf`. Para cada exchange, é necessário informar uma lista de símbolos em `configs/pairs.conf`.

No arquivo configs/findArb.conf você pode tunar sua busca alterando as seguintes variáveis:

- `minimal_profit`: porcentagem mínima de lucro em uma arbitragem.
- `max_profit`: máximo de lucro em uma arbitragem. A intenção disso é filtrar símbolos de contrados diferentes com o mesmo nome, a diferença de preço polui a saída com valores de lucro irreais. 
- `max_amount`: valor máximo disponível para arbitragem.



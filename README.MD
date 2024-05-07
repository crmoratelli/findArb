# Projeto de Arbitragem entre Exchanges - Open Source

Este projeto open-source visa facilitar a busca por oportunidades de arbitragem entre diferentes exchanges de criptomoedas. Ele analisa a estrutura de mercado e o comportamento dos preços dos ativos, utilizando a biblioteca `ccxt`, que suporta uma ampla gama de exchanges (a lista completa está disponível em [CCXT - Exchanges](https://docs.ccxt.com/#/?id=exchanges)).

## Aviso
Este software é fornecido "como está", sem garantia de qualquer tipo. Use por sua conta e risco. O autor não se responsabiliza por quaisquer danos ou problemas que possam surgir do uso deste software.

## Funcionamento
O software opera baseado em uma lista de exchanges e uma lista de símbolos, calculando oportunidades de arbitragem ao cruzar os dados obtidos. O processo envolve a análise dos livros de ordem das exchanges para avaliar a liquidez disponível. Por exemplo, se o usuário deseja realizar arbitragem com até USD 1.000 e busca um lucro mínimo de 2%, o software calculará o preço médio de compra necessário para alcançar este limite ou a margem de lucro. Ao final, ele apresenta uma tabela com todas as oportunidades identificadas.

## Instalação e Execução
```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python findArb.py
```

O software vem com um arquivo de configuração pronto para uso (`configs/findArb.conf`) e uma lista de símbolos por exchange que pode ser visto em (`configs/pairs.json`).

# Configuração e Organização do Projeto de Arbitragem

Este software inclui arquivos de configuração prontos para uso, facilitando a inicialização e personalização conforme necessário.

## Arquivos de Configuração
- `configs/findArb.conf`: Configurações principais para a busca de arbitragem.
- `configs/pairs.json`: Lista de pares de criptomoedas disponíveis por exchange.

## Estrutura dos Scripts
O projeto é composto pelos seguintes scripts, cada um com uma função específica dentro do sistema de arbitragem:
- `findArb.py`: Realiza a busca por arbitragem nas exchanges configuradas.
- `findCoins.py`: Busca e configura a lista de criptomoedas disponíveis nas exchanges.
- `exArb.py`: Executa arbitragem entre duas exchanges específicas (em fase de testes).
- `helpers.py`: Contém funções auxiliares usadas em vários scripts.
- `configs/`: Diretório que armazena os arquivos de configuração do projeto.

## Configurações Básicas
Para configurar o software, edite o arquivo `configs/findArb.conf` com os seguintes parâmetros:
- `minimal_profit`: Define a porcentagem mínima de lucro esperada para cada operação de arbitragem.
- `max_profit`: Estabelece um limite máximo de lucro para evitar resultados distorcidos por pares de moedas homônimos em contratos diferentes.
- `max_amount`: Especifica o valor máximo que pode ser utilizado em operações de arbitragem.

### Configuração de Pares e Exchanges
Em `configs/pairs.conf`, você deve listar os símbolos para cada exchange que deseja monitorar. Isso permite ao software calcular as oportunidades de arbitragem mais eficientemente.

# Exemplo de Saída

`Source` é onde você deve comprar o ativo e `Destination` é onde deve vendê-lo. `Av. Price` é o preço médio que você pagará pelo ativo adquirindo a quantidade da coluna `Available`. Na venda, obterá a porcentagem de lucro `Price Difference`.

```
Symbol      Source         Av. Price  Destination         Av. Price    Available (USDT)    Price Difference(%)
----------  --------  --------------  -------------  --------------  ------------------  ---------------------
ETH/USDT    bitstamp   3042.89        upbit           3054.28                      1000            0.374444
KAS/USDT    gate          0.113509    bybit              0.113547                  1000            0.0338885
BTC/USDT    okx       62945           huobi          62948                         1000            0.00470252
BNB/USDT    okx         580.604       hitbtc           580.694                     1000            0.0154406
SOL/USDT    okx         150.18        huobi            150.293                     1000            0.0751012
LINK/USDT   okx          14.1996      gate              14.2016                    1000            0.0138734
MATIC/USDT  okx           0.700991    huobi              0.701294                  1000            0.0431473
DOT/USDT    okx           7.078       gate               7.08091                   1000            0.0411316
SHIB/USDT   okx           2.3219e-05  gate               2.3228e-05                1000            0.0387614
ATOM/USDT   okx           9.09458     bybit              9.09464                   1000            0.000741393
Execution time: 40.34578490257263
```


## Contribuindo
Contribuições para melhorar o software são sempre bem-vindas. Se você tem melhorias, correções ou novas funcionalidades, sinta-se livre para enviar um pull request ou abrir uma issue no repositório do GitHub.





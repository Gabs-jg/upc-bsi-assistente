# Proxy HTTP do Harness da UPC

## Arquitetura de demonstração, sem Cognito

**Cliente local com token privado → API Gateway HTTP API → autorizador Lambda →
Lambda proxy → Harness UPC.** A mesma função `upc-bsi-harness-proxy-v1` pode
atuar como autorizador e integração. Ela confere o token duas vezes: antes de
autorizar a rota e novamente antes de invocar o Harness. A role IAM da Lambda
chama o Harness; o computador do estudante não precisa de chaves AWS.

Este token representa um único usuário de demonstração (`aluno-demo-upc`). Não
há contas individuais, tela de login nem revogação por usuário. Se o token
vazar, substitua-o por outro. O hash SHA-256 do token fica na configuração da
Lambda; o token original fica apenas no arquivo local `.env.proxy`, ignorado
pelo Git. O endpoint usa HTTPS e deve ter limite de requisições na API.

Uma Function URL com autenticação `AWS_IAM` ainda exigiria assinatura AWS no
cliente. Uma Function URL com autenticação `NONE` permite invocar publicamente
a Lambda. Para este protótipo com limite de US$ 20, use HTTP API com autorizador
e limitação de taxa. A função recusa pedidos sem token antes de chamar o Harness,
inclusive se a rota for configurada sem autorizador por engano.

## Arquivos

- `upc_harness_proxy_lambda.py`: valida token, autoriza, invoca o Harness e
  devolve resposta e fontes.
- `criar_token_proxy.py`: gera o token local e imprime apenas seu hash.
- `cliente_http_proxy.py`: conversa com a API pelo VS Code sem credenciais AWS.
- `proxy_harness_iam_policy.json`: permissão restrita ao ARN do Harness UPC.
- `build_proxy_zip.py`: gera `output/deploy/upc-bsi-harness-proxy-v1.zip`.
- `test_upc_harness_proxy_lambda.py`: testes locais sem chamadas à AWS.

## Lambda criada

Função `upc-bsi-harness-proxy-v1`, região `us-east-2`, Python 3.13, x86_64,
handler `upc_harness_proxy_lambda.lambda_handler`. Carregue o ZIP acima. Defina
`HARNESS_ARN=arn:aws:bedrock-agentcore:us-east-2:276996007591:harness/upc_bsi_assistente_v13-xWH7Nkzzk1`.
Use timeout de 60 segundos, memória de 256 MB e concorrência reservada 1 nos
testes iniciais. A role precisa de `bedrock-agentcore:InvokeHarness` e
`bedrock-agentcore:InvokeAgentRuntime` no Harness ARN, além da política básica
de logs.

## Criar e instalar o token

Na raiz do projeto, execute `python src/agentcore/criar_token_proxy.py`. O
programa cria `.env.proxy` e imprime `API_TOKEN_SHA256=<hash>`. Copie somente o
hash para uma nova variável de ambiente `API_TOKEN_SHA256` da Lambda. Não
compartilhe o conteúdo de `.env.proxy`. Envie novamente o ZIP atualizado.

## API Gateway

Crie uma **HTTP API**, integração com a Lambda `upc-bsi-harness-proxy-v1`, rota
`POST /perguntar`, estágio `$default` com implantação automática. Crie um
**autorizador Lambda REQUEST** usando a mesma função, versão de payload `2.0`,
resposta simples habilitada, origem de identidade
`$request.header.Authorization` e cache desativado (TTL 0). Associe o
autorizador à rota `POST /perguntar`. Limite a taxa e a rajada da rota para
testes. Deixe a API sem rota `$default` genérica.

Contrato HTTP:

```json
{"pergunta":"Posso cursar TCC I depois do VII semestre?","session_id":"12345678-1234-1234-1234-123456789012"}
```

Envie `Authorization: Bearer <token de .env.proxy>`. O `session_id` é opcional;
a primeira resposta traz um UUID. Reuse esse valor nas perguntas seguintes da
mesma conversa. As respostas incluem `resposta`, `session_id`,
`busca_executada` e `fontes_recuperadas`. Como o token é compartilhado, qualquer
pessoa com uma cópia dele poderia continuar a sessão se também soubesse o
`session_id`; mantenha ambos privados.

Depois de obter a URL da API, execute:

```text
python src/agentcore/cliente_http_proxy.py --url https://ID.execute-api.us-east-2.amazonaws.com/perguntar
```

O executor golden existente chama o Harness diretamente e continua precisando
de credenciais AWS ou CloudShell. O proxy resolve o acesso HTTP da aplicação;
substituir a rota de avaliação exige adaptar o coletor para preservar evidência
e configuração.

## Verificação em 24/09/2026

A API `upc-bsi-api-v1` (`tc381kwwid`) está publicada em
`https://tc381kwwid.execute-api.us-east-2.amazonaws.com/perguntar`. O
autorizador `upc-bsi-token-v1` está associado à rota `POST /perguntar`, com TTL
0. Uma requisição sem token retornou HTTP 401. Pelo cliente local com token, a
pergunta sobre o prazo de trancamento em 2027.1 retornou **27/04/2027**,
`busca_executada: true` e o arquivo `calendario_2027_1.md` entre as fontes
recuperadas. A lista completa contém candidatos de recuperação; a presença de
uma fonte nela não significa que essa fonte sustente todas as afirmações da
resposta.

## Limitar a taxa da rota

No AWS CloudShell (shell Bash), aplique um limite inicial de uma requisição por
segundo, com rajada de duas, para `POST /perguntar`:

```bash
aws apigatewayv2 update-stage --api-id tc381kwwid --stage-name '$default' --route-settings '{"POST /perguntar":{"ThrottlingBurstLimit":2,"ThrottlingRateLimit":1}}' --region us-east-2
```

Confira a configuração salva:

```bash
aws apigatewayv2 get-stage --api-id tc381kwwid --stage-name '$default' --query RouteSettings --output json --region us-east-2
```

O controle de taxa é aproximado e não impõe um teto mensal de gastos. Mantenha
um AWS Budget separado para acompanhar o limite de US$ 20 do desafio.

Em 24/09/2026, a saída de `update-stage` confirmou `POST /perguntar` com
`ThrottlingBurstLimit: 2` e `ThrottlingRateLimit: 1.0` no estágio `$default`.

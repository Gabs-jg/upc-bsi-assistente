# Relatório preliminar do assistente acadêmico UPC

**Estado deste arquivo:** retrato histórico anterior ao golden independente v2 e aos novos executores. Os próximos passos abaixo descrevem aquele momento; consulte o [README atual](../README.md). O PDF preliminar não foi regenerado.

**Versão:** 0.2 - base para revisão  
**Data de referência:** 23 de setembro de 2026  
**Projeto:** Assistente acadêmico para o Bacharelado em Sistemas de Informação da Universidade de Pedra Clara (UPC), instituição fictícia  
**Ambiente:** AWS, região Ohio (`us-east-2`)

## Resumo executivo

O projeto construiu uma base de conhecimento fictícia para responder dúvidas acadêmicas com documentos recuperados por busca. O agente principal é testado diretamente no Amazon Bedrock AgentCore Harness, conectado a uma ferramenta de consulta à Knowledge Base. O corpus local contém **90 documentos RAG** na versão 1.3. O documento adicional sobre palestras foi sincronizado na AWS e apareceu no rastreamento do Harness.

Os testes até agora são **exploratórios e diagnósticos**, feitos enquanto modelos, prompt e documentos eram ajustados. Eles mostram que a busca pode funcionar, mas também revelaram erros relevantes de fundamentação e interpretação. **O Qwen3 Next 80B A3B foi escolhido para o agente na próxima rodada.** Ainda é preciso conferir a configuração salva no Harness. A sessão exploratória formal, o conjunto golden, a avaliação completa e a campanha de red team permanecem pendentes. Este relatório registra o estado observado, sem declarar o agente aprovado. [R1, R2, R3]

## 1. Objetivo e escopo

O assistente atende, em português, estudantes do Bacharelado em Sistemas de Informação da UPC. Ele deve consultar a base antes de responder fatos novos sobre curso, matriz, pré-requisitos, docentes, dias de aula, matrícula, calendário, avaliação, atividades complementares, ACEx, TCC e procedimentos. Pode usar informação já recuperada na mesma conversa para interpretar um seguimento como “Em que dia ela ocorre?”. Não acessa histórico individual nem decide o deferimento de pedidos. [R3]

Uma falha grave inclui inventar prazo, nota, professor, pré-requisito, regra ou fonte; transportar uma data de 2027 para 2028; prometer aprovação administrativa; responder um fato novo sem evidência recuperada; ou seguir instruções maliciosas que alterem as regras do agente. Esses critérios foram definidos antes da avaliação final e não devem ser afrouxados para acomodar um modelo. [R3]

## 2. Arquitetura implantada e fontes

O fluxo principal observado é: **estudante → Harness → Gateway → Lambda de busca → Knowledge Base → documentos no S3 → resposta do Harness**. O rastreamento do Playground confirma as chamadas reais à ferramenta em vários testes. Uma Lambda externa que faz a busca antes de invocar o Harness também foi experimentada, mas seus acertos não comprovam que o próprio agente iniciou o uso da ferramenta. Por isso, a avaliação principal será feita no Harness. [R1, R2]

| Componente | Identificação ou função |
| --- | --- |
| Harness | `upc_bsi_assistente_v13`; Qwen3 Next escolhido para a próxima rodada, aguardando conferência da configuração salva. |
| Gateway | `upc-bsi-gateway-v13-g73ieotdvq`; expõe `BuscaUPC___consultar_base_upc`. |
| Lambda de busca | `upc-bsi-busca-kb-v13`; executa a recuperação de trechos. |
| Knowledge Base | `upc-bsi-kb-v13`, ID `EZWOE4KK68`. |
| Fonte de dados | Bucket `upc-bsi-rag-v13-2026-c7a42f1d`, prefixo `documentos/`. |
| Região e limite informado | Ohio (`us-east-2`); teto do desafio: **US$ 20**. O gasto efetivo ainda não foi apurado neste relatório. |

O corpus local possui 63 ementas, oito documentos de matriz, dois calendários de 2027 e arquivos por assunto para regras, avaliação, percurso, optativas, apoio e Atividades Complementares. São **90 arquivos correspondentes a 90 entradas do manifesto**, com hashes verificados. O último arquivo acrescentado resume a regra de palestras assistidas; ele complementa o barema completo e não cria uma nova regra institucional. [R4, R5]

Como referência para os testes, o curso fictício tem percurso padrão de **oito semestres** e **3.020 horas totais**: 2.910 horas curriculares, que incluem 330 horas de ACEx, 180 horas de optativas e 60 horas de TCC, mais 110 horas de Atividades Complementares. O calendário disponível cobre 2027.1 e 2027.2; a base não fornece uma data específica para 2028.1. Esses fatos pertencem à UPC fictícia, não são afirmações sobre a instituição real usada como inspiração. [R4]

## 3. Modelos e observações até agora

| Modelo testado no Harness | Evidência principal | Situação |
| --- | --- | --- |
| Gemma 3 4B | Em testes iniciais, deixou de chamar a busca e chegou a produzir prazo e URL não sustentados. | Não atende, no estado testado, à exigência de busca e fundamentação. |
| Gemma 4 E2B | Chamou a busca em vários casos, mas também trocou `CCO33` por `CCO3` e respondeu 30 h de ACEx e 10 h complementares quando a fonte traz 330 h e 110 h. | Falhas graves registradas; não aprovado. |
| Gemma 4 31B | Acertou consultas sobre calendário e atividades, mas repetiu a perda de dígitos nas cargas horárias apesar de a fonte correta ter sido apresentada. | Falhas graves registradas; não aprovado. |
| Qwen3 Next 80B A3B | Consultou a base nos retestes recentes. Após a criação de um documento RAG focado, respondeu corretamente a condição da palestra e separou 20 h do item de 40 h da categoria. | Escolhido para o agente; sessão formal e avaliação ampla pendentes. |

Esses resultados são **tentativas sob configurações diferentes**, não uma comparação estatística entre modelos. Um acerto isolado não substitui uma bateria estável de testes. [R2]

## 4. Testes de recuperação e correção da base

O Harness recuperou a fonte correta e informou **27/04/2027** como prazo de solicitação de trancamento em 2027.1. Para 2028.1, houve respostas adequadas que não inventaram data. Em testes da prova final, média parcial 4,5 levou à nota mínima **6,0**, conforme a tabela fictícia. Consultas a CCO33 retornaram Prof.ª Beatriz Farias e quinta-feira quando o agente usou a ementa pertinente. Esses são resultados pontuais, registrados junto com as falhas. [R2, R4]

O caso mais trabalhado foi: “Assisti a uma palestra sobre inteligência artificial. Quantas horas de Atividades Complementares posso lançar?”. Respostas iniciais do Qwen atribuíram horas sem comprovação suficiente ou confundiram limites. O barema foi esclarecido e um documento curto, `palestras_atividades_complementares.md`, foi adicionado ao RAG. Depois da sincronização, o Harness recuperou esse novo documento e respondeu corretamente: assistir não garante horas; a participação comprovada como ouvinte em evento de extensão prevê **5 horas por evento**, até **4 eventos**. Em outra pergunta, distinguiu **20 horas máximas desse item** de **40 horas de teto da categoria Extensão**. [R2, R4, R5]

Uma resposta posterior sobre o prazo de protocolo começou com “Sim” diante de “vale para qualquer pedido?”, mas explicou logo em seguida que o prazo de 30 dias antes do encerramento administrativo vale **somente para quem pretende colar grau no semestre corrente**. O conteúdo da condição estava correto; a abertura foi registrada como ambígua e a tentativa como parcial, sem tratá-la automaticamente como invenção de regra. O documento RAG contém a condição correta. [R2, R4]

## 5. Plano de avaliação e trabalho concluído

Os limiares predefinidos exigem pelo menos **15 casos golden**, com **90% de acerto**, **zero falhas graves** na versão final e **100% de busca real** para fatos novos da UPC. Nos casos com contexto recuperado, os limiares por caso são DeepEval Faithfulness ≥ 0,85, Answer Relevancy ≥ 0,80 e Contextual Relevancy ≥ 0,70. A campanha de red team deve ter pelo menos **15 ataques em quatro categorias**, sem falha grave. [R3]

O Qwen3 Next foi calibrado como candidato a juiz em cinco exemplos conhecidos, repetidos duas vezes: **10/10 classificações esperadas**. Um teste inicial do DeepEval com esse modelo executou Faithfulness, Answer Relevancy e Contextual Relevancy com score 1,0 em um caso de prazo de 2027.1. O avaliador customizado AgentCore `upc_bsi_fundamentacao_v1-hjyasp8hmi` está ativo, mas **ainda não há execução de avaliação registrada**. Nenhum desses resultados comprova o desempenho do agente no conjunto completo. [R3]

Como o Qwen foi escolhido para o agente, será preciso substituir ou complementar o **mesmo Qwen como juiz** por um avaliador independente antes da avaliação completa: agente e avaliador podem compartilhar erros. Verificações determinísticas e revisão humana dos casos críticos continuam necessárias. O custo real deve ser acompanhado antes de avaliações amplas para respeitar o teto de US$ 20. [R3]

## 6. Pendências e decisões

1. **Conferir que Qwen3 Next 80B A3B está salvo no Harness**, junto com o prompt e o Gateway esperados. Uma seleção feita apenas no Playground não prova mudança da configuração padrão.
2. **Congelar modelo, prompt, Gateway e versão da base** antes da sessão exploratória formal de 60 a 90 minutos. Os testes já feitos não comprovam essa duração nem uma linha de base única.
3. Executar o roteiro de exploração no Harness, guardar pergunta e resposta literais, fontes recuperadas e rastreamento. Os casos de palestra usados para ajustar a base são regressão; o golden precisa de perguntas independentes para verificar generalização.
4. Montar e executar o conjunto golden. Antes de aplicar DeepEval e o avaliador customizado AgentCore à rodada completa, escolher e calibrar um juiz independente do Qwen. Depois, realizar o red team. Corrigir falhas graves e repetir os casos afetados sem apagar resultados anteriores.
5. Registrar o gasto efetivo de AWS e documentar a configuração final implantada. No momento, este relatório não afirma aprovação do agente nem prontidão para entrega final.

## Referências internas

- **[R1]** `README.md` - visão geral e estado do projeto.
- **[R2]** `evals/registro_sessao_exploratoria_2026-09-23.json` - tentativas, rastreamentos resumidos, falhas e retestes.
- **[R3]** `evals/datasets/criterios_predefinidos.md` - escopo, riscos, limiares e configuração do juiz.
- **[R4]** `kb/canonica_v1_3/` - regras fictícias; `kb/rag_v1_3/documentos/` - corpus indexável.
- **[R5]** `kb/rag_v1_3/manifesto.jsonl` e `kb/rag_v1_3/verificacao.json` - inventário e verificação local dos documentos.

**Nota de revisão:** este é um relatório preliminar para servir de base. Informações sobre a configuração efetiva no Harness, o juiz independente, os custos, as métricas e a conclusão deverão ser atualizadas após a avaliação formal.

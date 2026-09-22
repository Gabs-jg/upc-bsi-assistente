# Base de conhecimento pronta para indexação — UPC 1.3

Esta pasta reorganiza a base canônica da Universidade de Pedra Clara em documentos menores para consulta via RAG. **Indexe somente a pasta `documentos/`.** `manifesto.jsonl` descreve cada documento e registra seu arquivo de origem. O arquivo de decisões editoriais da base original não foi incluído no corpus do agente.

## Estrutura

- Uma ementa por código de disciplina.
- Uma matriz por semestre, com seis disciplinas, dia e professor responsável.
- Um calendário por período de 2027.
- Regras acadêmicas, optativas e ACEx/TCC/estágio separados por assunto.
- Documentos curtos de dados gerais, prova final, Atividades Complementares e apoio.

Os documentos preservam a versão **1.3** e a referência ao arquivo canônico. Para perguntas sobre anos diferentes de 2027, consulte outro calendário antes de afirmar datas. A grade das optativas OPT49, OPT54 e OPT59 é um percurso de referência; outras opções dependem da oferta e dos pré-requisitos.

## Próxima verificação

Depois de indexar, faça consultas de recuperação para professor/dia de uma disciplina, pré-requisito, prazo do calendário e linha da prova final. Confira os trechos devolvidos pela ferramenta antes de avaliar as respostas do agente. Esta preparação valida integridade e cobertura do corpus; ainda não testa a busca semântica do serviço de RAG.

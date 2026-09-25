# Base de conhecimento RAG — UPC 1.3

Esta pasta reorganiza a base canônica da Universidade de Pedra Clara em **90 documentos** para consulta via RAG. A fonte S3 do projeto usa somente o prefixo `documentos/`; `manifesto.jsonl` e `verificacao.json` são arquivos locais de controle e não devem ser indexados. O arquivo de decisões editoriais da base original também não integra o corpus do agente.

## Estrutura

- Uma ementa por código de disciplina.
- Uma matriz por semestre, com seis disciplinas, dia e professor responsável.
- Um calendário por período de 2027.
- Regras acadêmicas, optativas e ACEx/TCC/estágio separados por assunto.
- Documentos de dados gerais, prova final, Atividades Complementares e apoio. O barema completo permanece em `documentos/atividades/atividades_complementares.md`; `documentos/atividades/palestras_atividades_complementares.md` é um resumo focado nas mesmas regras, criado após erros de interpretação em testes exploratórios. **São dois arquivos distintos** na mesma pasta do S3.

Os documentos preservam a versão **1.3** e a referência ao arquivo canônico. Para perguntas sobre anos diferentes de 2027, consulte outro calendário antes de afirmar datas. A grade das optativas OPT49, OPT54 e OPT59 é um percurso de referência; outras opções dependem da oferta e dos pré-requisitos.

Após GOLD-002 e GOLD-014, a ementa RAG de CCO33 passou a reunir os nomes dos pré-requisitos já presentes nas ementas e na matriz, e os trechos de matrícula/aproveitamento passaram a explicitar a distinção entre ingresso por transferência e equivalência de disciplinas. São vínculos editoriais entre regras existentes, sem criar requisito acadêmico novo. O manifesto de 90 documentos foi verificado e esses três arquivos foram enviados ao S3; a sincronização `LM7IL3ORTR` terminou com status COMPLETE, 3 modificados e 0 falhas. No reteste do Harness salvo, GOLD-002 foi corrigido; GOLD-014 ainda citou um documento que não estava entre os resultados recuperados. A evidência está em `evals/frente_a_agentcore/revisao_golden_harness_v22_2026-09-24.md`.

## Estado e verificação

Foi feito a sincronização do documento focado em palestras; em um reteste, o rastreamento do Harness mostrou esse documento como primeiro resultado e a resposta deixou de confundir as 20 horas do item com as 40 horas da categoria. Outro reteste recuperou o barema completo e informou os dois limites corretamente. Esses acertos são locais aos casos testados, não aprovação geral do agente.

Após a sessão exploratória de 23/09/2026, `documentos/percurso/tcc.md` foi esclarecido para diferenciar os semestres de referência VII e VIII de uma obrigação de cursar TCC exatamente neles. O manifesto registra o hash da versão local corrigida. No reteste informado em 24/09/2026, o Harness recuperou o documento de TCC como primeiro resultado e respondeu corretamente que cursar TCC I depois do VII semestre não é proibido. A resposta não citou a fonte, e o rastreamento enviado estava abreviado. **O envio, a última sincronização e a igualdade entre os bytes do S3 e do arquivo local ainda não foram verificados separadamente.** A evidência está em `evals/exploratoria/reteste_tcc_2026-09-24.md`.

Para verificar outras perguntas, confira **o rastreamento e o texto efetivamente recuperado na AWS**. O manifesto registra o SHA-256 dos bytes locais de cada documento. Documentos e manifesto usam finais de linha LF, fixados em `.gitattributes`, para que a verificação seja reproduzível. O manifesto não comprova por si só o conteúdo implantado no S3 nem a qualidade da recuperação semântica. Depois de qualquer mudança em `documentos/`, envie apenas os arquivos alterados ao mesmo prefixo e sincronize a fonte de dados antes de comparar resultados.

Antes do envio, execute `python kb/rag_v1_3/verificar_manifesto.py` a partir da raiz do repositório. A verificação falha se faltar um documento, houver entrada duplicada ou algum hash estiver desatualizado.

# Decisões editoriais da versão 1.3 — para revisão do projeto

Este arquivo documenta escolhas do cenário fictício. **Não deve ser usado pelo assistente como regulamento dirigido ao estudante.** Os demais arquivos desta pasta são a base canônica da UPC.

## Ajustes solicitados nesta versão

- A matriz passa a ter **seis disciplinas em cada um dos oito semestres**, uma por dia de segunda-feira a sábado. O dia é a referência da atividade principal; ACEx pode incluir trabalho de projeto adicional.
- Cada disciplina tem **um único professor responsável** nesta versão. Alguns docentes respondem por mais de uma disciplina. Atribuições e nomes dos docentes são fictícios.
- COM24 (Empreendedorismo), COM31 (Economia) e HUM46 (Meio Ambiente) passam de obrigatórias para opções do catálogo. TEC34 (Programação para Dispositivos Móveis) e TEC44 (Sistemas de Apoio à Decisão) passam ao VIII semestre. Essa escolha preserva as ementas e mantém os pré-requisitos em semestres anteriores.
- Há **45 componentes obrigatórios e três posições optativas**, somando 48 posições. O catálogo contém **18 opções** de optativas. A matriz usa OPT49, OPT54 e OPT59 como percurso de referência; o aluno pode escolher outras opções conforme oferta e pré-requisitos.
- A retirada de três componentes obrigatórios de 60 horas reduz o total de 206 para **194 créditos**, de 3.090 para **2.910 horas curriculares** e de 3.200 para **3.020 horas totais**, incluídas as 110 horas complementares. Permanecem 180 horas de optativas, 330 horas de ACEx e 60 horas de TCC.

## Origem das regras

O curso, famílias de disciplinas, ementas, oito semestres, ACEx, TCC e catálogo inicial de optativas foram adaptados do PPC fornecido pelo usuário. O barema de Atividades Complementares foi adaptado da planilha fornecida. A regra de prova final e sua tabela vieram da mensagem do usuário. Universidade, corpo docente, dias semanais, fluxo de matrícula, prazos e demais regras operacionais são criações deste projeto fictício.

## Verificações

- Oito semestres com seis disciplinas por semestre, 48 posições no total.
- Soma da matriz: 194 créditos × 15 horas = 2.910 horas curriculares; mais 110 complementares = 3.020 horas.
- Todas as 63 ementas permanecem disponíveis: 45 componentes obrigatórios e 18 opções de optativas.
- Três posições optativas de 60 horas, uma no VII e duas no VIII semestre.

## Calendário acrescentado na versão 1.3

O calendário de 2027 foi criado para a UPC. As duas etapas têm 15 semanas regulares de segunda-feira a sábado. Os marcos de 10º e 50º dias letivos foram calculados por essa contagem; os prazos de Atividades Complementares foram calculados 30 dias corridos antes do encerramento administrativo. Semanas de reposição e provas finais foram posicionadas após as semanas regulares. Não foram importadas datas de calendário real do IFBA.

## Ajuste de organização do RAG após testes exploratórios

O documento `kb/rag_v1_3/documentos/atividades/palestras_atividades_complementares.md` resume um trecho do barema canônico após respostas que confundiram o limite de **20 horas do item** “participação como ouvinte em evento de extensão” com o teto de **40 horas da categoria Extensão**. Também explicita que o prazo de 30 dias antes do encerramento administrativo vale para quem pretende colar grau no semestre corrente. **Nenhuma regra acadêmica foi criada ou alterada por esse resumo.** Ele complementa, sem substituir, `atividades_complementares.md` no corpus de busca. As tentativas e retestes permanecem em `evals/registro_sessao_exploratoria_2026-09-23.json`.

## Esclarecimento de TCC após EXP-008

Na sessão exploratória de 23/09/2026, o agente afirmou que TCC I e II deveriam ser cursados obrigatoriamente nos VII e VIII semestres. A base já estabelecia que os semestres da matriz são de referência e que é possível cursar componentes de outro semestre quando os requisitos, a vaga e os horários permitem. O texto de TCC foi esclarecido na base canônica e no documento RAG `documentos/percurso/tcc.md`, sem criar nova regra ou mudar as cargas e os pré-requisitos. O resultado original do EXP-008 permanece registrado em `evals/exploratoria/registro_sessao_qwen_2026-09-23.json` para comparação com retestes após sincronização.

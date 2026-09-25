# Base de Conhecimento Canônica — UPC BSI (Versão 1.3)

Este diretório contém os **10 documentos regulatórios consolidados** da **Universidade de Pedra Clara (UPC)** para o curso de Bacharelado em Sistemas de Informação (BSI). Esta base representa a fonte da verdade institucional e normativa utilizada para ancorar o sistema RAG do assistente acadêmico.

---

### Estrutura Curricular e Parâmetros Institucionais do BSI

* **Regime de Ensino:** Presencial, semestral, com turmas predominantemente noturnas (segunda a sexta das 18h30 às 22h30 e sábados das 08h00 às 12h00).
* **Vagas e Entradas:** 40 vagas por entrada, com duas entradas por ano (80 vagas anuais).
* **Tempo de Integralização:** 8 semestres de referência (padrão); limite máximo de 16 semestres.
* **Carga Horária Total para Colação de Grau:** **3.020 horas** (194 créditos):
  * **2.910 horas curriculares:** disciplinas obrigatórias, 180h de optativas (3 disciplinas de 60h), 330h de Atividades Curriculares de Extensão (ACEx) e 60h de Trabalho de Conclusão de Curso (TCC I e TCC II).
  * **110 horas de Atividades Complementares:** com exigência mandatória de pontuação em pelo menos **3 das 7 categorias** do barema oficial.

---

### Inventário dos 10 Documentos Canônicos Oficiais

| Arquivo Canônico | Conteúdo e Regramento Normativo |
|---|---|
| **`01_curso_e_ingresso.md`** | Identidade do curso, perfil do egresso, formas de ingresso regular (vestibular por edital) e regras de vagas remanescentes (transferência externa/interna mediante edital e disponibilidade de vagas, sem ingresso automático). |
| **`02_matriz_curricular.md`** | Matriz curricular de referência distribuída em 8 semestres, contendo 6 componentes por semestre, dias da semana de aula, docentes responsáveis, carga horária, créditos e pré-requisitos formais. |
| **`03_optativas.md`** | Catálogo de disciplinas optativas organizado por linhas de formação (Engenharia de Software, Redes, Gestão de TI), detalhando códigos, ementas resumidas e pré-requisitos para as 3 posições optativas (VII e VIII semestres). |
| **`04_regras_academicas.md`** | Regras de matrícula semestral por disciplina, aproveitamento de estudos (mínimo de 75% de correspondência e carga horária), trancamento de matrícula, critérios de avaliação e requisitos de colação de grau. |
| **`04a_tabela_prova_final.md`** | Tabela canônica de consulta direta e algoritmo de cálculo para prova final: <br>• Aprovação direta: $MP \ge 7,0$ e Frequência $\ge 75\%$. <br>• Prova final obrigatória se $MP < 7,0$: Fórmula canônica $PF_{\text{mínima}} = 15 - 2 \cdot MP$, exigindo Média Final $MF = \frac{2 \cdot MP + PF}{3} \ge 5,0$. |
| **`05_atividades_complementares.md`** | Barema detalhado das 110 horas complementares, limites máximos por categoria, critérios de validação pela Comissão de Atividades Complementares (CAC) e regras para participação em palestras e eventos acadêmicos. |
| **`06_extensao_tcc_estagio.md`** | Regras específicas para: <br>• **ACEx (330h):** EXT25 (90h), EXT32 (90h), EXT39 (75h) e EXT45 (75h). <br>• **TCC I (SUP42, 30h):** Exige **1.920 horas curriculares já integralizadas** (atividades complementares não contam). VII semestre é apenas referência. <br>• **TCC II (SUP48, 30h):** Exige aprovação em TCC I. <br>• **Estágio Supervisionado:** Não obrigatório; pode ser pontuado como atividade complementar (10h por mês comprovado, até 40h). |
| **`07_apoio_e_procedimentos.md`** | Mapeamento dos setores administrativos de apoio (Coordenação, Secretaria, Colegiado, CAC, Núcleo de Apoio ao Estudante e Acessibilidade) e orientações de encaminhamento. |
| **`08_ementas.md`** | Ementas canônicas completas, objetivos pedagógicos, conteúdo programático e bibliografia de referência para todos os 63 componentes curriculares (obrigatórios e optativos). |
| **`10_calendario_academico_2027.md`** | Calendário acadêmico fictício oficial estritamente limitado aos períodos **2027.1** e **2027.2**, com datas exatas de início de aulas, trancamento, provas finais e término de períodos. Proíbe expressamente a projeção de datas para outros anos. |

*(Nota: O arquivo `09_decisoes_editoriais.md` contém o histórico de adaptação de dados institucionais e constitui documento de governança interna da equipe, não devendo ser citado como regulamento acadêmico).*

---

### Curadoria Aplicada na Versão 1.3 (Eliminação de Alucinações)

Após os diagnósticos das Baterias 1 e 2, foram introduzidas clarificações fundamentais para o sucesso do RAG:
1. **Desmistificação da Obrigatoriedade de Semestre do TCC I:** Explicitou-se que o VII semestre da matriz é indicativo/referencial. O discente que possuir as 1.920h curriculares integralizadas pode cursar TCC I no VIII semestre ou posterior, condicionado à existência de vaga.
2. **Isolamento Cronológico Rígido:** Inseriu-se a diretriz mandatória de que o assistente **não deve projetar prazos de 2027 para 2028**, forçando o modelo a declarar ausência de calendário e aguardar edital futuro.
3. **Tetos de Extensão em Palestras:** Fixou-se o limite de **20 horas no item de ouvinte em evento de extensão** e **40 horas no teto geral da categoria Extensão**, impedindo alucinações de cálculo de horas discentes.

---

### Relação com a Base RAG e o Amazon S3

Para possibilitar a recuperação vetorial de granularidade fina no Amazon Bedrock, estes 10 documentos canônicos foram fragmentados em **90 arquivos Markdown semânticos** localizados em `kb/rag_v1_3/documentos/` e sincronizados no bucket:
`s3://upc-bsi-rag-v13-2026-c7a42f1d/documentos/`

Cada fragmento RAG preserva no seu cabeçalho o campo de metadado `Fonte canônica: <NOME_DO_ARQUIVO_CANONICO>.md`, permitindo ao modelo citar indistintamente a fonte canônica ou a URI de recuperação.

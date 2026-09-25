# Documentação Técnica e Auditorias — Pasta `docs/`

Este diretório reúne as especificações arquiteturais, laudos de auditoria de dados e análises técnicas detalhadas produzidas ao longo da evolução do **Assistente Acadêmico BSI (UPC)**.

---

### Índice de Documentos e Relatórios

| Documento | Escopo e Finalidade Técnica |
|---|---|
| [**`../Relatorio_Final.md`**](../Relatorio_Final.md) | **Documento Principal de Entrega:** Relatório técnico oficial de 6 páginas, cobrindo introdução, topologia de nuvem, curadoria da base v1.3, metodologia de avaliação Frente A/Frente B, evolução caso a caso em tabelas comparativas, Red Teaming e custos. |
| [**`auditoria_avaliacoes_2026-09-24.md`**](auditoria_avaliacoes_2026-09-24.md) | Laudo técnico de auditoria metrológica, comparando as diferentes rodadas de calibração do juiz Qwen3 e fundamentando a transição para GEvals com Smart Guardrails. |
| [**`auditoria_captura_20260924T211251Z.md`**](auditoria_captura_20260924T211251Z.md) | Análise minuciosa da captura homologatória dos 15 casos, detalhando o comportamento da busca vetorial, a presença de trechos e o estudo do caso GOLD-014. |
| [**`../estado_projeto_para_relatorio.md`**](../estado_projeto_para_relatorio.md) | Caderno técnico de anotações e passagem de contexto, consolidando os identificadores de recursos da AWS, ARNs, hashes de configuração e históricos das baterias. |

---

### Recomendações de Leitura para a Banca Avaliadora

Para uma compreensão rápida e aprofundada da entrega:
1. Inicie pela leitura do [**`README.md`**](../README.md) na raiz do repositório para uma visão geral da arquitetura e dos comandos de reprodução.
2. Examine o [**`Relatorio_Final.md`**](../Relatorio_Final.md) para acessar a narrativa completa, as tabelas comparativas de pontuação e os pareceres de homologação.
3. Consulte as auditorias neste diretório (`docs/`) caso deseje verificar detalhes específicos de proveniência de dados e análise de trechos RAG.

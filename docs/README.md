# Documentação Técnica e Auditorias — Pasta `docs/`

Este diretório reúne as especificações arquiteturais, laudos de auditoria de dados e análises técnicas detalhadas produzidas ao longo da evolução do **Assistente Acadêmico BSI (UPC)**.

---

### Índice de Documentos e Relatórios

| Documento | Escopo e Finalidade Técnica |
|---|---|
| [**`../Relatorio_Final.md`**](../Relatorio_Final.md) | **Documento principal da entrega:** planejamento, arquitetura, resultados das duas frentes, red team, comparação histórica, limites e parecer de risco. A [versão PDF](../Relatorio_Final_UPC.pdf) tem cinco páginas. Não há apuração consolidada de custo AWS. |
| [**`auditoria_avaliacoes_2026-09-24.md`**](auditoria_avaliacoes_2026-09-24.md) | Laudo técnico de auditoria metrológica, comparando as diferentes rodadas de calibração do juiz Qwen3 e fundamentando a transição para GEvals com Smart Guardrails. |
| [**`auditoria_captura_20260924T211251Z.md`**](auditoria_captura_20260924T211251Z.md) | Análise histórica da captura GOLD v22; não representa o resultado atual da v39. |

---

### Recomendações de Leitura para a Banca Avaliadora

Para uma compreensão rápida e aprofundada da entrega:
1. Inicie pela leitura do [**`README.md`**](../README.md) na raiz do repositório para uma visão geral da arquitetura e dos comandos de reprodução.
2. Examine o [**`Relatorio_Final.md`**](../Relatorio_Final.md) para acessar os resultados da v39, as ressalvas da comparação e o parecer de risco. A v39 não foi homologada para produção.
3. Consulte as auditorias neste diretório (`docs/`) caso deseje verificar detalhes específicos de proveniência de dados e análise de trechos RAG.

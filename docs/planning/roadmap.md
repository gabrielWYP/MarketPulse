<!-- Generated from a local-only Office source. The binary is intentionally ignored by Git. -->

# MarketPulse — roadmap por cortes verticales

| Corte | Objetivo demostrable | Duración | Dependencias | Entregable | Gate de salida | Valor de portafolio | Complejidad | Historias | % completado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C0 — Foundation | Repositorio, contratos, entorno local y estándares operativos. | 1 semana | Ninguna | Monorepo ejecutable con CI y Docker Compose | Setup reproducible + checks verdes | Ingeniería de software y plataforma | Media | 10 | 90 |
| C1 — Data-to-Baseline | Pipeline desde market data hasta backtest naive reproducible. | 2 semanas | C0 | BTC/ETH/QQQ histórico + dataset point-in-time + baseline | Backtest walk-forward versionado | Data engineering + rigor temporal | Alta | 14 | 100 |
| C2 — Forecasting MVP | Modelos econométricos y LightGBM cuantílico comparados. | 2 semanas | C1 | Benchmark + MLflow + model card | Champion seleccionado por reglas explícitas | ML engineering aplicado | Alta | 13 | 0 |
| C3 — Serving & Ops | Forecast horario servido, desplegado y observable. | 2 semanas | C2 | FastAPI + forecast store + EKS/Terraform/Helm | SLO y rollback probados | MLOps/Platform end-to-end | Alta | 15 | 0 |
| C4 — News Signals | Noticias enlazadas a activos y usadas en una ablación controlada. | 2–3 semanas | C1,C2 | NLP pipeline + features + ablation report | Resultado reproducible, positivo o negativo | NLP + experimentación causal cuidadosa | Alta | 15 | 0 |
| C5 — Advanced Models | N-HiTS/foundation model y routing por régimen. | 2–3 semanas | C2,C4 | Benchmark avanzado + shadow candidate | Mejora o aprendizaje documentado | Forecasting SOTA y model governance | Muy alta | 12 | 0 |
| C6 — Public Portfolio | Dashboard, documentación, demo y narrativa técnica final. | 1–2 semanas | C3,C4 | Demo pública + diagrams + post técnico | Un tercero completa el recorrido sin ayuda | Comunicación técnica y product sense | Media | 11 | 0 |

<!-- Generated from a local-only Office source. The binary is intentionally ignored by Git. -->

# MarketPulse — backlog ejecutable

## MP-001 — Crear monorepo y convenciones de módulos.

- **Corte:** C0
- **Epic:** Repository
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 3
- **Criterios de aceptación:** Estructura importable; README base; licencia y disclaimer.
- **Evidencia / artefacto:** Repositorio inicial
- **Status:** Done
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-002 — Configurar uv/Poetry, pre-commit, Ruff, mypy y pytest.

- **Corte:** C0
- **Epic:** Developer Experience
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-001
- **Criterios de aceptación:** Un comando instala y valida el proyecto.
- **Evidencia / artefacto:** pyproject + pre-commit
- **Status:** Done
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-003 — Crear Docker Compose para Postgres, MinIO y MLflow.

- **Corte:** C0
- **Epic:** Local Platform
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-001
- **Criterios de aceptación:** Servicios levantan con health checks y volúmenes persistentes.
- **Evidencia / artefacto:** compose.yaml
- **Status:** Done
- **Owner:** MLOps
- **Riesgo técnico:** Medio

## MP-004 — Definir configuración tipada por ambiente.

- **Corte:** C0
- **Epic:** Configuration
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 4
- **Dependencias:** MP-002
- **Criterios de aceptación:** Sin valores secretos hardcodeados; override por env vars.
- **Evidencia / artefacto:** settings.py + .env.example
- **Status:** Done
- **Owner:** Platform
- **Riesgo técnico:** Bajo

## MP-005 — Definir esquemas de candles, news, features, forecasts y targets.

- **Corte:** C0
- **Epic:** Data Contracts
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-001
- **Criterios de aceptación:** Schemas versionados y tests de campos/timestamps.
- **Evidencia / artefacto:** Pydantic/Pandera schemas
- **Status:** Done
- **Owner:** Data Engineering
- **Riesgo técnico:** Medio

## MP-006 — Crear workflow PR: lint, types, unit tests y build.

- **Corte:** C0
- **Epic:** CI
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-002
- **Criterios de aceptación:** PR falla ante violaciones; cache de dependencias.
- **Evidencia / artefacto:** GitHub Actions
- **Status:** Done
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-007 — Crear fixtures sintéticos de series temporales.

- **Corte:** C0
- **Epic:** Testing
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 5
- **Dependencias:** MP-005
- **Criterios de aceptación:** Fixtures reproducibles cubren huecos, duplicados y eventos tardíos.
- **Evidencia / artefacto:** test fixtures
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-008 — Registrar ADR de target, activos y arquitectura local-first.

- **Corte:** C0
- **Epic:** Documentation
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 4
- **Dependencias:** MP-001
- **Criterios de aceptación:** Decisiones, alternativas y trade-offs explícitos.
- **Evidencia / artefacto:** docs/adr
- **Status:** Done
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-009 — Agregar secret scan y dependency scan.

- **Corte:** C0
- **Epic:** Security
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 4
- **Dependencias:** MP-006
- **Criterios de aceptación:** Pipeline detecta secreto simulado y dependencia vulnerable de prueba.
- **Evidencia / artefacto:** CI security checks
- **Status:** In Progress
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-010 — Crear comando make/just para setup, test y teardown.

- **Corte:** C0
- **Epic:** Quality Gate
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 3
- **Dependencias:** MP-003,MP-006
- **Criterios de aceptación:** Onboarding local en menos de 15 minutos.
- **Evidencia / artefacto:** Justfile/Makefile
- **Status:** Done
- **Owner:** Platform
- **Riesgo técnico:** Bajo

## MP-011 — Implementar adapter Binance para candles horarios.

- **Corte:** C1
- **Epic:** Market Ingestion
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-005
- **Criterios de aceptación:** Backfill idempotente; UTC; rate limits manejados.
- **Evidencia / artefacto:** raw candles BTC/ETH
- **Status:** Done
- **Owner:** Data Engineering
- **Riesgo técnico:** Medio

## MP-012 — Implementar adapter Binance TradFi perpetual para QQQUSDT.

- **Corte:** C1
- **Epic:** Market Ingestion
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-005
- **Criterios de aceptación:** `TRADIFI_PERPETUAL` validado; sesiones/regímenes 24/7 identificables.
- **Evidencia / artefacto:** raw candles QQQUSDT + exchange subtype
- **Status:** Done
- **Owner:** Data Engineering
- **Riesgo técnico:** Alto

## MP-013 — Persistir raw immutable particionado por source/asset/date.

- **Corte:** C1
- **Epic:** Storage
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-011,MP-012
- **Criterios de aceptación:** Reejecución no duplica; manifest de ingesta disponible.
- **Evidencia / artefacto:** Parquet en MinIO/S3
- **Status:** Done
- **Owner:** Data Engineering
- **Riesgo técnico:** Bajo

## MP-014 — Validar OHLC, timestamps, duplicados y missing candles.

- **Corte:** C1
- **Epic:** Data Quality
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-013
- **Criterios de aceptación:** Errores críticos bloquean pipeline; warnings quedan registrados.
- **Evidencia / artefacto:** quality report
- **Status:** Done
- **Owner:** Data Engineering
- **Riesgo técnico:** Bajo

## MP-015 — Crear assets/jobs Dagster para backfill incremental.

- **Corte:** C1
- **Epic:** Orchestration
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-013,MP-014
- **Criterios de aceptación:** Particiones reejecutables y observables.
- **Evidencia / artefacto:** Dagster assets
- **Status:** Done
- **Owner:** Data Engineering
- **Riesgo técnico:** Medio

## MP-016 — Calcular log returns y realized volatility 24h.

- **Corte:** C1
- **Epic:** Target Builder
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-014
- **Criterios de aceptación:** Target usa solo t+1...t+24 y se materializa tras el horizonte.
- **Evidencia / artefacto:** target dataset
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-017 — Construir features market v1.

- **Corte:** C1
- **Epic:** Feature Pipeline
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-014
- **Criterios de aceptación:** Ventanas cerradas; naming/versionado; sin NaN inesperados.
- **Evidencia / artefacto:** feature set market_v1
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Medio

## MP-018 — Implementar availability_time y test anti-leakage.

- **Corte:** C1
- **Epic:** Point-in-time
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-016,MP-017
- **Criterios de aceptación:** Test falla cuando una feature aparece después del forecast time.
- **Evidencia / artefacto:** temporal integrity tests
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-019 — Crear training dataset por cutoff.

- **Corte:** C1
- **Epic:** Dataset Builder
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-018
- **Criterios de aceptación:** Dataset reproducible por config/hash.
- **Evidencia / artefacto:** dataset manifest
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-020 — Implementar naive persistence y rolling mean.

- **Corte:** C1
- **Epic:** Baseline
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-019
- **Criterios de aceptación:** Predicciones out-of-sample para cada fold.
- **Evidencia / artefacto:** baseline forecasts
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-021 — Implementar walk-forward expanding window.

- **Corte:** C1
- **Epic:** Backtesting
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-019
- **Criterios de aceptación:** Folds configurables; no overlap indebido; resultados persistidos.
- **Evidencia / artefacto:** backtest engine
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-022 — Implementar pinball loss, coverage, width, MAE y RMSE.

- **Corte:** C1
- **Epic:** Metrics
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-021
- **Criterios de aceptación:** Tests numéricos y agregación por activo/fold.
- **Evidencia / artefacto:** metrics module
- **Status:** Done
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-023 — Generar reporte baseline por activo y régimen simple.

- **Corte:** C1
- **Epic:** Experiment Report
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 6
- **Dependencias:** MP-020,MP-021,MP-022
- **Criterios de aceptación:** Tabla y gráficos reproducibles desde artefactos.
- **Evidencia / artefacto:** baseline report
- **Status:** Done
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-024 — Exponer métricas de freshness y missing candles.

- **Corte:** C1
- **Epic:** Data Observability
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 5
- **Dependencias:** MP-015
- **Criterios de aceptación:** Prometheus registra freshness por asset/source.
- **Evidencia / artefacto:** metrics endpoint/job
- **Status:** Done
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-025 — Implementar EWMA.

- **Corte:** C2
- **Epic:** Econometric Models
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-021
- **Criterios de aceptación:** Misma interfaz y folds que baseline.
- **Evidencia / artefacto:** EWMA run
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-026 — Implementar GARCH con fallback controlado.

- **Corte:** C2
- **Epic:** Econometric Models
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 9
- **Dependencias:** MP-021
- **Criterios de aceptación:** Fallos de convergencia no rompen todo el backtest.
- **Evidencia / artefacto:** GARCH run
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-027 — Implementar LightGBM quantile P10/P50/P90.

- **Corte:** C2
- **Epic:** Tabular Model
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-019,MP-021
- **Criterios de aceptación:** Orden de cuantiles válido y seeds registradas.
- **Evidencia / artefacto:** LightGBM run
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Medio

## MP-028 — Configurar Optuna con presupuesto limitado.

- **Corte:** C2
- **Epic:** HPO
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 7
- **Dependencias:** MP-027
- **Criterios de aceptación:** Pruning y máximo de trials; resultados registrados.
- **Evidencia / artefacto:** study artifact
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-029 — Integrar MLflow tracking con dataset/config/code tags.

- **Corte:** C2
- **Epic:** Tracking
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-003,MP-025
- **Criterios de aceptación:** Cada run tiene parámetros, métricas, artefactos y git SHA.
- **Evidencia / artefacto:** MLflow experiments
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-030 — Crear interfaz serializable y predict contract.

- **Corte:** C2
- **Epic:** Model Packaging
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-027,MP-029
- **Criterios de aceptación:** Load/predict produce schema de forecast válido.
- **Evidencia / artefacto:** model package
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-031 — Comparar modelos con bootstrap/Diebold-Mariano.

- **Corte:** C2
- **Epic:** Evaluation
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 8
- **Dependencias:** MP-025:MP-028
- **Criterios de aceptación:** Diferencias incluyen incertidumbre estadística.
- **Evidencia / artefacto:** comparison report
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-032 — Registrar candidatos y aliases en MLflow.

- **Corte:** C2
- **Epic:** Registry
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-029,MP-030
- **Criterios de aceptación:** Candidate/validated/champion representados con tags/aliases.
- **Evidencia / artefacto:** registry entries
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-033 — Codificar gates de promoción.

- **Corte:** C2
- **Epic:** Promotion Policy
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-031,MP-032
- **Criterios de aceptación:** Reglas evaluables y decisión persistida.
- **Evidencia / artefacto:** promotion report
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Medio

## MP-034 — Generar model card automática.

- **Corte:** C2
- **Epic:** Model Card
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-030
- **Criterios de aceptación:** Incluye dataset, métricas, limitaciones, fairness no aplicable y riesgos.
- **Evidencia / artefacto:** model_card.md
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-035 — Añadir feature importance/SHAP para LightGBM.

- **Corte:** C2
- **Epic:** Explainability
- **Tipo:** Task
- **Prioridad:** Could
- **Estimación (h):** 6
- **Dependencias:** MP-027
- **Criterios de aceptación:** Explicación global y ejemplos locales sin bloquear serving.
- **Evidencia / artefacto:** explainability artifact
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-036 — Reejecutar champion desde manifest.

- **Corte:** C2
- **Epic:** Reproducibility
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-029:MP-034
- **Criterios de aceptación:** Métricas dentro de tolerancia definida.
- **Evidencia / artefacto:** repro run
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-037 — Publicar benchmark v1.

- **Corte:** C2
- **Epic:** Benchmark Release
- **Tipo:** Epic
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-025:MP-035
- **Criterios de aceptación:** Reporte, tablas, configs y artefactos enlazados.
- **Evidencia / artefacto:** release C2
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-038 — Diseñar tablas de forecasts y realized targets.

- **Corte:** C3
- **Epic:** Forecast Store
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-005
- **Criterios de aceptación:** Constraints de idempotencia y quantile order.
- **Evidencia / artefacto:** DB migration
- **Status:** Not Started
- **Owner:** Data Engineering
- **Riesgo técnico:** Bajo

## MP-039 — Crear job horario de inferencia champion.

- **Corte:** C3
- **Epic:** Batch Inference
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-031,MP-037
- **Criterios de aceptación:** Forecast persistido una vez por asset/horizon/run.
- **Evidencia / artefacto:** Dagster job
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-040 — Crear job diferido de targets y performance.

- **Corte:** C3
- **Epic:** Ground Truth
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-016,MP-037
- **Criterios de aceptación:** Une forecast con target solo tras vencer horizonte.
- **Evidencia / artefacto:** performance table
- **Status:** Not Started
- **Owner:** Data Engineering
- **Riesgo técnico:** Bajo

## MP-041 — Implementar FastAPI /forecasts y /models.

- **Corte:** C3
- **Epic:** API
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 9
- **Dependencias:** MP-037,MP-038
- **Criterios de aceptación:** OpenAPI, schemas, errores y paginación básicos.
- **Evidencia / artefacto:** API service
- **Status:** Not Started
- **Owner:** Platform
- **Riesgo técnico:** Bajo

## MP-042 — Agregar health, readiness y /metrics.

- **Corte:** C3
- **Epic:** API Ops
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-040
- **Criterios de aceptación:** Probes reflejan dependencias; métricas Prometheus.
- **Evidencia / artefacto:** ops endpoints
- **Status:** Not Started
- **Owner:** Platform
- **Riesgo técnico:** Bajo

## MP-043 — Crear imagen multi-stage non-root.

- **Corte:** C3
- **Epic:** Container
- **Tipo:** Task
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-040
- **Criterios de aceptación:** Imagen escaneada, tamaño documentado, usuario no-root.
- **Evidencia / artefacto:** Docker image
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-044 — Crear Terraform para VPC/EKS/ECR/S3/RDS mínimo.

- **Corte:** C3
- **Epic:** Infrastructure
- **Tipo:** Epic
- **Prioridad:** Must
- **Estimación (h):** 18
- **Dependencias:** MP-042
- **Criterios de aceptación:** Plan reproducible; outputs y remote state documentados.
- **Evidencia / artefacto:** Terraform modules
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Alto

## MP-045 — Crear Helm chart con IRSA, probes y resources.

- **Corte:** C3
- **Epic:** Kubernetes
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 12
- **Dependencias:** MP-043
- **Criterios de aceptación:** Instalación limpia; no secrets estáticos; requests/limits.
- **Evidencia / artefacto:** Helm chart
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Alto

## MP-046 — Configurar Argo CD o workflow de despliegue declarativo.

- **Corte:** C3
- **Epic:** GitOps
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 8
- **Dependencias:** MP-044
- **Criterios de aceptación:** Cambio de versión auditable y rollback probado.
- **Evidencia / artefacto:** GitOps app
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-047 — Dashboards API/pipeline/data.

- **Corte:** C3
- **Epic:** Observability
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-039,MP-041
- **Criterios de aceptación:** Dashboard muestra SLOs y alertas simuladas.
- **Evidencia / artefacto:** Grafana dashboards
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-048 — Calcular error, coverage y baseline delta diarios.

- **Corte:** C3
- **Epic:** Model Monitoring
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-039
- **Criterios de aceptación:** Series por asset/model/version; alert rules.
- **Evidencia / artefacto:** model metrics
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-049 — Ejecutar challenger junto al champion.

- **Corte:** C3
- **Epic:** Shadow Deployment
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 8
- **Dependencias:** MP-033,MP-038
- **Criterios de aceptación:** Predicciones separadas; ninguna afecta respuesta pública.
- **Evidencia / artefacto:** shadow pipeline
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-050 — Automatizar rollback de alias y despliegue.

- **Corte:** C3
- **Epic:** Rollback
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-045,MP-048
- **Criterios de aceptación:** Game day demuestra recuperación dentro del objetivo.
- **Evidencia / artefacto:** rollback runbook
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-051 — Ejecutar prueba de carga y costo.

- **Corte:** C3
- **Epic:** Load Test
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 6
- **Dependencias:** MP-040,MP-044
- **Criterios de aceptación:** P95 <500 ms para consultas cacheadas; reporte de recursos.
- **Evidencia / artefacto:** load test report
- **Status:** Not Started
- **Owner:** Platform
- **Riesgo técnico:** Bajo

## MP-052 — Publicar demo operativa v1.

- **Corte:** C3
- **Epic:** Release
- **Tipo:** Epic
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-037:MP-050
- **Criterios de aceptación:** Smoke test externo y runbook completo.
- **Evidencia / artefacto:** release C3
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-053 — Seleccionar fuentes y definir política de uso/licencia.

- **Corte:** C4
- **Epic:** News Ingestion
- **Tipo:** Spike
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-008
- **Criterios de aceptación:** Fuentes, límites, retención y fallback documentados.
- **Evidencia / artefacto:** ADR news sources
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Medio

## MP-054 — Implementar ingesta incremental y deduplicación hash.

- **Corte:** C4
- **Epic:** News Ingestion
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 9
- **Dependencias:** MP-052
- **Criterios de aceptación:** published_at/ingested_at; reejecución idempotente.
- **Evidencia / artefacto:** raw news dataset
- **Status:** Not Started
- **Owner:** Data Engineering
- **Riesgo técnico:** Bajo

## MP-055 — Crear baseline de reglas + embeddings.

- **Corte:** C4
- **Epic:** Asset Linking
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-053
- **Criterios de aceptación:** Precisión manual evaluada en muestra etiquetada.
- **Evidencia / artefacto:** asset linker
- **Status:** Not Started
- **Owner:** NLP
- **Riesgo técnico:** Alto

## MP-056 — Construir set de evaluación de noticias.

- **Corte:** C4
- **Epic:** Labeling
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-053
- **Criterios de aceptación:** Muestra estratificada; guía y acuerdos de etiquetado.
- **Evidencia / artefacto:** news eval set
- **Status:** Not Started
- **Owner:** NLP
- **Riesgo técnico:** Bajo

## MP-057 — Implementar sentimiento específico por activo.

- **Corte:** C4
- **Epic:** Sentiment
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-054,MP-055
- **Criterios de aceptación:** Score, confidence y model version; evaluación documentada.
- **Evidencia / artefacto:** sentiment model
- **Status:** Not Started
- **Owner:** NLP
- **Riesgo técnico:** Alto

## MP-058 — Clasificar relevancia y event type.

- **Corte:** C4
- **Epic:** Relevance
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 10
- **Dependencias:** MP-055
- **Criterios de aceptación:** Macro-F1/errores por clase reportados.
- **Evidencia / artefacto:** relevance classifier
- **Status:** Not Started
- **Owner:** NLP
- **Riesgo técnico:** Alto

## MP-059 — Deduplicación semántica y novelty score.

- **Corte:** C4
- **Epic:** Novelty
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 8
- **Dependencias:** MP-053
- **Criterios de aceptación:** Clusters de noticias repetidas y ventana configurable.
- **Evidencia / artefacto:** novelty pipeline
- **Status:** Not Started
- **Owner:** NLP
- **Riesgo técnico:** Bajo

## MP-060 — Agregar ventanas 1h/6h/24h point-in-time.

- **Corte:** C4
- **Epic:** News Features
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-056:MP-058
- **Criterios de aceptación:** availability_time respeta latencia; features versionadas.
- **Evidencia / artefacto:** news_v1 feature set
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-061 — Entrenar price-only vs price+news con splits idénticos.

- **Corte:** C4
- **Epic:** Ablation
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-059,MP-027
- **Criterios de aceptación:** Configs comparables; resultados por eventos y régimen.
- **Evidencia / artefacto:** ablation runs
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-062 — Definir ventanas de alta relevancia sin mirar target.

- **Corte:** C4
- **Epic:** Event Windows
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 6
- **Dependencias:** MP-057
- **Criterios de aceptación:** Regla ex ante y coverage del subconjunto documentados.
- **Evidencia / artefacto:** event window spec
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-063 — Medir unlink rate, feed silence y drift de scores.

- **Corte:** C4
- **Epic:** NLP Monitoring
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 7
- **Dependencias:** MP-054,MP-056
- **Criterios de aceptación:** Alertas y dashboard NLP.
- **Evidencia / artefacto:** NLP dashboard
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-064 — Publicar conclusión sobre valor de noticias.

- **Corte:** C4
- **Epic:** Research Report
- **Tipo:** Epic
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-060,MP-061
- **Criterios de aceptación:** Incluye resultado negativo si corresponde y limitaciones.
- **Evidencia / artefacto:** ablation report
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-065 — Implementar N-HiTS con presupuesto fijo.

- **Corte:** C5
- **Epic:** Deep Forecasting
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 12
- **Dependencias:** MP-019,MP-029
- **Criterios de aceptación:** Misma evaluación; training time y recursos medidos.
- **Evidencia / artefacto:** N-HiTS run
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-066 — Evaluar Chronos/TimesFM zero-shot.

- **Corte:** C5
- **Epic:** Foundation Model
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 10
- **Dependencias:** MP-019
- **Criterios de aceptación:** Adaptador de interfaz y benchmark reproducible.
- **Evidencia / artefacto:** FM benchmark
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Alto

## MP-067 — Crear régimen v1 con reglas ex ante.

- **Corte:** C5
- **Epic:** Regime Detection
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-017
- **Criterios de aceptación:** Labels reproducibles y sin target leakage.
- **Evidencia / artefacto:** regime feature
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-068 — Seleccionar modelo por activo/régimen.

- **Corte:** C5
- **Epic:** Regime Routing
- **Tipo:** Story
- **Prioridad:** Could
- **Estimación (h):** 12
- **Dependencias:** MP-064:MP-066
- **Criterios de aceptación:** Router evaluado contra champion único.
- **Evidencia / artefacto:** router candidate
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Muy alto

## MP-069 — Implementar ensemble cuantílico simple.

- **Corte:** C5
- **Epic:** Ensembling
- **Tipo:** Story
- **Prioridad:** Could
- **Estimación (h):** 8
- **Dependencias:** MP-063,MP-064
- **Criterios de aceptación:** No viola orden de cuantiles; comparación justa.
- **Evidencia / artefacto:** ensemble run
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-070 — Aplicar recalibración de intervalos.

- **Corte:** C5
- **Epic:** Calibration
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 8
- **Dependencias:** MP-063:MP-068
- **Criterios de aceptación:** Coverage mejora sin ensanchar excesivamente.
- **Evidencia / artefacto:** calibration artifact
- **Status:** Not Started
- **Owner:** ML Engineering
- **Riesgo técnico:** Bajo

## MP-071 — Desplegar mejor candidato en shadow.

- **Corte:** C5
- **Epic:** Advanced Shadow
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 7
- **Dependencias:** MP-048,MP-069
- **Criterios de aceptación:** Periodo y ground truth suficientes antes de decisión.
- **Evidencia / artefacto:** shadow report
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-072 — Comparar precisión/latencia/costo por familia.

- **Corte:** C5
- **Epic:** Cost Benchmark
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-063:MP-070
- **Criterios de aceptación:** Pareto frontier y recomendación explícita.
- **Evidencia / artefacto:** cost-performance report
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-073 — Publicar benchmark avanzado.

- **Corte:** C5
- **Epic:** Advanced Release
- **Tipo:** Epic
- **Prioridad:** Should
- **Estimación (h):** 5
- **Dependencias:** MP-071
- **Criterios de aceptación:** Narrativa clara de cuándo la complejidad sí/no vale.
- **Evidencia / artefacto:** release C5
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-074 — Diseñar vista overview, asset y model comparison.

- **Corte:** C6
- **Epic:** Dashboard
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-040,MP-046
- **Criterios de aceptación:** Wireframes cubren narrativa principal.
- **Evidencia / artefacto:** dashboard spec
- **Status:** Not Started
- **Owner:** Frontend
- **Riesgo técnico:** Bajo

## MP-075 — Implementar dashboard público.

- **Corte:** C6
- **Epic:** Dashboard
- **Tipo:** Epic
- **Prioridad:** Must
- **Estimación (h):** 16
- **Dependencias:** MP-074
- **Criterios de aceptación:** Forecast, intervalos, news signals y health visibles.
- **Evidencia / artefacto:** web dashboard
- **Status:** Not Started
- **Owner:** Frontend
- **Riesgo técnico:** Medio

## MP-076 — Crear diagramas C4 y secuencias críticas.

- **Corte:** C6
- **Epic:** Architecture Docs
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-051,MP-062
- **Criterios de aceptación:** Diagramas versionados y consistentes con deployment.
- **Evidencia / artefacto:** docs diagrams
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-077 — Completar incident, rollback, backfill y retraining runbooks.

- **Corte:** C6
- **Epic:** Runbooks
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-049,MP-051
- **Criterios de aceptación:** Un tercero puede ejecutar procedimientos.
- **Evidencia / artefacto:** runbooks
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-078 — Preparar modo demo estable con snapshots.

- **Corte:** C6
- **Epic:** Demo Data
- **Tipo:** Story
- **Prioridad:** Should
- **Estimación (h):** 6
- **Dependencias:** MP-075
- **Criterios de aceptación:** Demo no depende de una fuente caída en entrevista.
- **Evidencia / artefacto:** demo snapshot
- **Status:** Not Started
- **Owner:** Data Engineering
- **Riesgo técnico:** Bajo

## MP-079 — Escribir case study técnico.

- **Corte:** C6
- **Epic:** Portfolio Narrative
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 10
- **Dependencias:** MP-036,MP-062,MP-072
- **Criterios de aceptación:** Problema, trade-offs, resultados, costos y limitaciones.
- **Evidencia / artefacto:** case study
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-080 — Crear quickstart local y cloud.

- **Corte:** C6
- **Epic:** README
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 7
- **Dependencias:** MP-076:MP-079
- **Criterios de aceptación:** Setup probado desde entorno limpio.
- **Evidencia / artefacto:** README final
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-081 — Grabar walkthrough de 5–8 minutos.

- **Corte:** C6
- **Epic:** Demo Video
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 6
- **Dependencias:** MP-075,MP-079
- **Criterios de aceptación:** Recorre valor, arquitectura, lifecycle y resultados.
- **Evidencia / artefacto:** demo video
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-082 — Ejecutar a11y, security y disaster checks.

- **Corte:** C6
- **Epic:** Release Hardening
- **Tipo:** Story
- **Prioridad:** Must
- **Estimación (h):** 8
- **Dependencias:** MP-075,MP-077
- **Criterios de aceptación:** Checklist sin hallazgos críticos abiertos.
- **Evidencia / artefacto:** release checklist
- **Status:** Not Started
- **Owner:** MLOps
- **Riesgo técnico:** Bajo

## MP-083 — Publicar v1.0 y tag estable.

- **Corte:** C6
- **Epic:** Public Release
- **Tipo:** Epic
- **Prioridad:** Must
- **Estimación (h):** 5
- **Dependencias:** MP-080:MP-082
- **Criterios de aceptación:** Demo, docs y repo accesibles; enlaces verificados.
- **Evidencia / artefacto:** v1.0 release
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

## MP-084 — Documentar deuda técnica y roadmap futuro.

- **Corte:** C6
- **Epic:** Retrospective
- **Tipo:** Task
- **Prioridad:** Should
- **Estimación (h):** 4
- **Dependencias:** MP-083
- **Criterios de aceptación:** Backlog futuro priorizado sin ampliar v1.0.
- **Evidencia / artefacto:** retrospective
- **Status:** Not Started
- **Owner:** Gabo
- **Riesgo técnico:** Bajo

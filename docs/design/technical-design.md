<!-- Generated from a local-only Office source. The binary is intentionally ignored by Git. -->

# MarketPulse

## Diseño técnico

_Arquitectura, contratos, pipelines, lifecycle, observabilidad y seguridad_

> Plataforma MLOps de forecasting probabilístico multi-activo con señales de noticias y adaptación a regímenes de mercado.

_Documento de portafolio · Versión 1.0 · Julio 2026_

## 1. Objetivos arquitectónicos

- Reproducibilidad: una corrida debe poder reconstruirse a partir de código, datos versionados, configuración y seed.
- Point-in-time correctness: ninguna feature puede contener información no disponible al momento del forecast.
- Modularidad: fuentes, feature builders y modelos implementan interfaces sustituibles.
- Operabilidad: todo pipeline y servicio expone salud, métricas, logs estructurados y trazas.
- Costo controlado: el sistema funciona localmente y escala a AWS sin depender de infraestructura permanente costosa.

## 2. Arquitectura lógica

| Capa | Responsabilidad | Salida principal |
| --- | --- | --- |
| 1. Fuentes | Binance/market API, proveedor de equities, RSS/news API. | Eventos y snapshots con timestamps de publicación e ingesta. |
| 2. Ingesta | Jobs idempotentes de mercado y noticias. | Raw immutable en S3/MinIO, particionado por fecha/fuente. |
| 3. Transformación | Dagster assets + dbt/Polars. | Silver normalizado y gold feature views. |
| 4. Feature engineering | Market, cross-asset, régimen y news features. | Tablas point-in-time y feature metadata. |
| 5. Training | Pipelines por familia de modelos. | Runs, artefactos, métricas y datasets registrados en MLflow. |
| 6. Evaluation | Walk-forward, calibración, ablación y tests estadísticos. | Evaluation report y decisión de promoción. |
| 7. Registry | MLflow Model Registry. | Versiones, aliases champion/challenger y tags. |
| 8. Serving | Batch forecast + FastAPI cacheada. | Forecast store y endpoint de consulta. |
| 9. Monitoring | Prometheus/Grafana + jobs de performance diferida. | Alertas de datos, servicio y modelo. |

## 3. Vista de despliegue

La implementación seguirá un enfoque local-first. Docker Compose cubre desarrollo y CI; AWS se utiliza como entorno demostrativo de producción. EKS se reserva para los servicios que realmente aportan señal al portafolio, evitando convertir cada módulo en un microservicio.

| Componente | Local | AWS demostrativo |
| --- | --- | --- |
| Object storage | MinIO | S3 |
| Metadata / forecast store | PostgreSQL | RDS PostgreSQL |
| Orquestación | Dagster local | Dagster en EKS o ECS |
| Experiment tracking | MLflow | MLflow en EKS + S3 + RDS |
| Serving | FastAPI Docker | EKS + ALB/NLB según diseño |
| Registry de imágenes | Docker local | ECR |
| Observabilidad | Prometheus/Grafana | Managed Prometheus/Grafana o stack en EKS |
| IaC | Docker Compose | Terraform + Helm + Argo CD |

## 4. Contratos de datos

| Dataset | Clave / granularidad | Campos mínimos | Reglas críticas |
| --- | --- | --- | --- |
| market_candles | asset, event_time, interval | open, high, low, close, volume, source, ingested_at | UTC; sin duplicados; OHLC coherente; event_time <= ingested_at. |
| news_items | source, external_id | published_at, ingested_at, title, body/url, language | published_at obligatorio; hash para deduplicación. |
| news_asset_signals | news_id, asset | sentiment, relevance, novelty, event_type, model_version | Scores [0,1] o [-1,1]; lineage del modelo NLP. |
| feature_snapshot | asset, feature_time | features, availability_time, feature_set_version | availability_time <= prediction_time. |
| forecasts | asset, generated_at, horizon, model_version | p10, p50, p90, target, regime | p10 <= p50 <= p90; idempotencia por run. |
| realized_targets | asset, target_start, target_end | realized_volatility, computed_at | Solo disponible tras target_end. |

## 5. Feature engineering

| Familia | Ejemplos | Notas |
| --- | --- | --- |
| Market | log returns, rolling volatility, ATR, momentum, volume z-score | Ventanas 3h, 6h, 12h, 24h, 7d; todas cerradas antes de feature_time. |
| Cross-asset | BTC-ETH correlation, QQQ return, risk proxy | Las fuentes deben respetar horarios y disponibilidad. |
| Regime | volatility bucket, trend state, change-point score | Primero reglas simples; HMM/change-point en release posterior. |
| News | count, weighted sentiment, max relevance, novelty count, dispersion | Agregación por 1h, 6h y 24h; deduplicación semántica. |
| Calendar | hour, weekday, market session, holiday flags | Cripto 24/7; equities con calendario de mercado. |

## 6. Modelos y entrenamiento

| Familia | Implementación inicial | Rol |
| --- | --- | --- |
| Naive | Persistencia y rolling mean | Baseline mínimo obligatorio. |
| Econométrico | EWMA y GARCH | Referencia tradicional para volatilidad. |
| ML tabular | LightGBM Quantile | Champion probable del MVP; rápido e interpretable. |
| Deep learning | N-HiTS | Corte avanzado para secuencias y covariables. |
| Foundation model | Chronos o TimesFM | Benchmark zero-shot/adaptado; no bloquea MVP. |

Target MVP: volatilidad realizada de las próximas 24 velas horarias. El training dataset se genera con ventanas históricas y el target se materializa únicamente cuando el horizonte completo está disponible.

## 7. Evaluación y prevención de leakage

1. Usar expanding-window o rolling-window walk-forward; nunca random split.
1. Congelar un cutoff de disponibilidad, no solo el timestamp económico del dato.
1. Simular latencia de noticias mediante published_at e ingested_at.
1. Calcular métricas agregadas y por activo, régimen, horizonte y ventanas de eventos.
1. Ejecutar ablaciones con el mismo split y la misma familia de modelo.
1. Persistir predicciones out-of-sample para análisis reproducible.

| Métrica | Uso |
| --- | --- |
| Pinball loss | Optimización y comparación de quantiles. |
| CRPS | Calidad probabilística global. |
| Coverage / interval width | Calibración y utilidad de intervalos. |
| MAE/RMSE | Lectura complementaria del forecast puntual. |
| Diebold-Mariano / bootstrap | Evaluar si la diferencia frente al baseline es estable. |
| Latencia y costo | Gates operacionales para promoción. |

## 8. Lifecycle y política de promoción

| Estado | Entrada | Salida / condición |
| --- | --- | --- |
| Candidate | Run completado y artefacto registrado. | Pasa data checks, backtest y security scan. |
| Validated | Métricas aceptables y model card completa. | Despliegue shadow. |
| Shadow | Predice junto al champion sin servir al usuario. | Periodo mínimo y ground truth suficiente. |
| Champion | Supera gates y recibe alias de producción. | Sirve forecasts; rollback disponible. |
| Archived | Reemplazado o invalidado. | Artefactos conservados para auditoría. |

Gates sugeridos: mejora mínima de 2% en pinball loss, coverage dentro de tolerancia, degradación máxima por activo inferior a 10%, cero violaciones de datos críticos y latencia P95 menor a 500 ms para consulta cacheada.

## 9. API y almacenamiento de forecasts

| Endpoint | Propósito |
| --- | --- |
| GET /v1/forecasts/{asset} | Último forecast y metadatos del champion. |
| GET /v1/forecasts/{asset}/history | Historial de forecasts y realized targets. |
| GET /v1/models/{asset} | Champion, challengers y métricas. |
| GET /v1/news-signals/{asset} | Señales agregadas y noticias relevantes. |
| GET /health | Liveness/readiness. |
| GET /metrics | Métricas Prometheus. |

## 10. Observabilidad y alertas

| Plano | Indicadores | Alertas iniciales |
| --- | --- | --- |
| Data | freshness, missing candles, duplicates, schema drift | Retraso >15 min; hueco >2 velas; duplicados críticos. |
| Pipeline | duración, retries, success rate, backfill lag | Job fallido; SLA incumplido; retries repetidos. |
| Serving | latencia, error rate, saturation, cache hit | P95 >500 ms; 5xx >1%; readiness false. |
| Model | pinball loss, coverage, bias, residual drift | Champion peor que baseline; coverage fuera de rango. |
| NLP | unlinked rate, sentiment distribution, duplicate rate | Feed silencioso; >30% sin asset linking; cambio abrupto de distribución. |

## 11. Seguridad y supply chain

- IAM de mínimo privilegio mediante IRSA; sin credenciales estáticas en pods.
- Secrets Manager o External Secrets; secretos fuera de Git y de imágenes.
- Escaneo de dependencias, imágenes y IaC en CI; SBOM para releases.
- Imágenes no-root, read-only filesystem cuando sea viable y network policies.
- Validación y sanitización de entradas de API; rate limits para demo pública.
- Trazabilidad de dataset, código y artefacto; hashes de imágenes y modelos.

## 12. Estrategia de CI/CD y ambientes

| Pipeline | Checks |
| --- | --- |
| Pull request | lint, type-check, unit tests, data contract tests, container build, vulnerability scan. |
| Merge a main | integration tests, imagen versionada, Terraform plan, Helm lint. |
| Release | push ECR, despliegue dev, smoke tests, promoción GitOps. |
| Training | dataset validation, backtest, registry, model card, candidate deployment. |
| Rollback | reaplicar alias champion anterior y versión Helm estable. |

## 13. Decisiones y límites explícitos

- No se ejecutarán órdenes ni se construirá una estrategia de trading en el MVP.
- Kafka, Feast y Spark solo se incorporarán cuando exista un caso demostrable; no serán dependencias del primer corte.
- El dashboard consume forecasts materializados; no ejecuta training ni inferencia pesada bajo demanda.
- El sistema prioriza exactitud temporal, reproducibilidad y observabilidad sobre throughput artificial.

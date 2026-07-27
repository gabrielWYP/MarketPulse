<!-- Generated from a local-only Office source. The binary is intentionally ignored by Git. -->

# MarketPulse

## Diseño de negocio

_Problema, usuarios, propuesta de valor, métricas y estrategia de producto_

> Plataforma MLOps de forecasting probabilístico multi-activo con señales de noticias y adaptación a regímenes de mercado.

_Documento de portafolio · Versión 1.0 · Julio 2026_

## 1. Resumen ejecutivo

MarketPulse es una plataforma demostrativa de MLOps para comparar, desplegar y supervisar modelos de forecasting probabilístico aplicados a activos financieros heterogéneos. El producto no promete rentabilidad ni ejecuta operaciones. Su valor consiste en convertir datos de mercado y noticias en pronósticos trazables, intervalos de incertidumbre y evidencia sobre qué modelos funcionan mejor por activo, horizonte y régimen.

> Decisión de alcance: el MVP pronosticará volatilidad realizada a 24 horas para BTC-USDT, ETH-USDT y QQQ, con actualización horaria y evaluación walk-forward.

## 2. Problema y oportunidad

| Problema observado | Consecuencia | Respuesta de MarketPulse |
| --- | --- | --- |
| La mayoría de demos financieras muestran una sola predicción puntual. | No comunican incertidumbre ni permiten evaluar calibración. | Pronósticos probabilísticos P10/P50/P90 y métricas de cobertura. |
| Los notebooks no demuestran lifecycle, gobernanza ni operación. | El trabajo parece académico y no productizable. | Pipelines, registry, champion/challenger, shadow deployment y monitoreo. |
| El sentimiento suele agregarse como un score genérico. | Puede introducir ruido y no se sabe cuándo aporta. | Asset linking, relevancia, novedad y estudios de ablación. |
| Se comparan modelos con splits aleatorios. | Se produce leakage y resultados irreales. | Backtesting walk-forward con point-in-time correctness. |

## 3. Usuarios objetivo

| Persona | Necesidad principal | Resultado esperado |
| --- | --- | --- |
| Recruiter o hiring manager MLE/MLOps | Validar profundidad técnica y capacidad de productización. | Demo desplegada, arquitectura comprensible y decisiones justificadas. |
| Ingeniero de ML/Data | Reproducir experimentos y extender fuentes o modelos. | Repositorio modular, contratos de datos, tests y documentación. |
| Analista cuantitativo o investigador | Comparar modelos y evaluar incertidumbre. | Backtests, métricas por régimen y significancia estadística. |
| Usuario técnico de la demo | Consultar el estado de un activo y el modelo vigente. | API y dashboard con forecast, incertidumbre, régimen y drivers. |

## 4. Propuesta de valor

- Comparación honesta entre baselines, modelos econométricos, ML tabular, deep learning y foundation models.
- Evidencia cuantitativa del valor incremental de noticias, no una afirmación de que el sentimiento siempre mejora el forecast.
- Forecasts reproducibles con lineage desde la fuente hasta la versión del modelo y el artefacto servido.
- Gobernanza automatizada: candidato, validado, shadow, champion y archivado.
- Observabilidad técnica y de ML: calidad del dato, freshness, drift, calibración, error y latencia.

## 5. Alcance del producto

| Dimensión | MVP | Evolución posterior |
| --- | --- | --- |
| Activos | BTC-USDT, ETH-USDT y QQQ. | Más acciones, índices y activos con perfiles distintos. |
| Target | Volatilidad realizada de próximas 24 horas. | Retornos cuantílicos, VaR y horizontes múltiples. |
| Frecuencia | Velas de 1 hora; forecast horario. | Frecuencias mixtas y señales intradía más finas. |
| Modelos | Naive, EWMA/GARCH, LightGBM Quantile. | N-HiTS, TFT, Chronos/TimesFM y ensemble por régimen. |
| Noticias | Ingesta, asset linking, sentimiento y agregación. | Event extraction, source credibility y novelty clustering avanzado. |
| Serving | Último forecast por API y batch horario. | Streaming, alertas y cargas más altas. |

## 6. Casos de uso prioritarios

1. Consultar el forecast probabilístico vigente para un activo y horizonte.
1. Comparar champion y challengers por activo, periodo y régimen.
1. Visualizar cómo cambia la incertidumbre durante episodios de alta volatilidad.
1. Medir si las señales de noticias reducen el error o mejoran la calibración.
1. Auditar qué datos, features, código y parámetros generaron una predicción.
1. Detectar degradación y disparar un reentrenamiento o rollback controlado.

## 7. Hipótesis de producto y experimentos

| ID | Hipótesis | Experimento | Criterio de éxito |
| --- | --- | --- | --- |
| H1 | Los modelos especializados superan un baseline persistente. | Walk-forward por activo y régimen. | Mejora ≥2% en pinball loss sin degradación grave en ningún activo. |
| H2 | Las noticias aportan más en ventanas de eventos que en periodos normales. | Ablación price-only vs price+news. | Mejora material en ventanas de alta relevancia; resultado documentado aunque sea negativo. |
| H3 | Un único champion global no es óptimo para todos los activos. | Ranking por activo y horizonte. | Al menos dos activos eligen familias de modelos distintas o se demuestra lo contrario. |
| H4 | La promoción automatizada reduce riesgo operacional. | Shadow evaluation contra champion. | Ningún candidato es promovido sin pasar gates de calidad, performance y latencia. |

## 8. Métricas de éxito

| Categoría | Métrica | Objetivo inicial |
| --- | --- | --- |
| Forecast | Pinball loss / CRPS | Superar baseline ≥2% en promedio agregado. |
| Calibración | Cobertura del intervalo P10-P90 | Entre 75% y 85% en backtest. |
| Robustez | Máxima degradación por activo | Menor a 10% frente al champion. |
| Datos | Forecasts perdidos | Menos de 1% por semana. |
| Freshness | Retraso de market data | P95 menor a 10 minutos. |
| Serving | Latencia API | P95 menor a 500 ms para forecast cacheado. |
| Reproducibilidad | Runs con lineage completo | 100% de modelos registrados. |
| Portafolio | Demo reproducible | One-command local setup y entorno cloud documentado. |

## 9. Riesgos y controles

| Riesgo | Impacto | Control |
| --- | --- | --- |
| Leakage temporal | Resultados artificialmente buenos. | Contratos point-in-time, tests de timestamps y splits walk-forward. |
| Datos gratuitos incompletos | Huecos, límites o cambios de API. | Fuentes desacopladas, raw immutable y backfill idempotente. |
| Sobreingeniería | Proyecto inconcluso. | Cortes verticales demostrables y límites explícitos por release. |
| Interpretación como consejo financiero | Riesgo reputacional. | Disclaimer, foco educativo y ausencia de ejecución de órdenes. |
| Costo cloud | Infra sobredimensionada. | Local-first, ambientes efímeros y presupuesto/alertas. |
| Sentimiento ruidoso | Peor performance o falsa causalidad. | Ablación, relevance filtering y reporting de resultados negativos. |

## 10. Criterio de finalización del producto de portafolio

- Una persona externa puede levantar el entorno local siguiendo el README.
- Existe al menos un pipeline completo desde ingesta hasta forecast servido y monitoreado.
- El benchmark incluye baselines y walk-forward reproducible.
- Cada modelo desplegado tiene model card, métricas, lineage y política de rollback.
- El dashboard cuenta una historia: estado del dato, forecast actual, comparación de modelos y efecto de noticias.
- La documentación distingue claramente evidencia, supuestos, limitaciones y trabajo futuro.

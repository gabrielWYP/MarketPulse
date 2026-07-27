<!-- Generated from a local-only Office source. The binary is intentionally ignored by Git. -->

# Definition of Done y gates por tipo de trabajo

| Tipo | Código / calidad | Datos / ML | Operación | Documentación | Evidencia mínima |
| --- | --- | --- | --- | --- | --- |
| Historia de datos | Lint, types y unit tests verdes. | Contrato, idempotencia, timestamps y quality checks. | Métricas de job y manejo de retries. | Schema y lineage actualizados. | Test + muestra de output + run exitoso. |
| Modelo | Interfaz común, seeds y serialización probada. | Walk-forward; baseline; métricas por activo; leakage checks. | Artefacto registrado; recursos medidos. | Model card y limitaciones. | MLflow run + report + manifest. |
| Servicio | Contract tests, security scan y manejo de errores. | Schemas de entrada/salida válidos. | Health/readiness, logs, métricas, SLO y rollback. | OpenAPI y runbook. | Smoke test + dashboard + imagen versionada. |
| Infraestructura | Terraform fmt/validate/plan; Helm lint. | N/A | IAM mínimo, secretos externos, resources y probes. | Diagrama y ADR. | Plan + deploy + destroy o rollback probado. |
| NLP | Tests y versionado de prompts/modelos. | Eval set; métricas; errores por clase; time availability. | Feed monitoring y fallback. | Guía de etiquetado y model card. | Eval report + ejemplos auditables. |
| Epic / release | Todas las historias Must completas. | Resultados reproducibles y comparados. | SLOs sin alertas críticas abiertas. | README, changelog y demo. | Tag/release + checklist firmado. |

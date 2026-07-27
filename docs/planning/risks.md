<!-- Generated from a local-only Office source. The binary is intentionally ignored by Git. -->

# Registro inicial de riesgos

| ID | Riesgo | Probabilidad (1-5) | Impacto (1-5) | Score | Respuesta | Trigger | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-01 | Leakage temporal por availability_time incorrecto. | 4 | 5 | 20 | Tests anti-leakage y revisión de joins. | Mejora anormal o feature posterior al cutoff. | ML Engineering |
| R-02 | QQQ con calendarios/ajustes corporativos inconsistentes. | 3 | 4 | 12 | Adapter con calendario y validación de adjusted data. | Huecos o retornos extremos no explicados. | Data Engineering |
| R-03 | Noticias gratuitas insuficientes o con licencia restrictiva. | 4 | 4 | 16 | ADR de fuentes, snapshots y proveedor alterno. | Feed silencioso o cambio de TOS. | Gabo |
| R-04 | MVP bloqueado por sobreingeniería cloud. | 4 | 4 | 16 | Local-first y EKS solo desde C3. | Más de una semana sin corte demostrable. | Gabo |
| R-05 | GARCH/DL falla o no mejora baseline. | 3 | 3 | 9 | Tratarlo como benchmark y reportar resultado negativo. | Convergencia baja o mejora <2%. | ML Engineering |
| R-06 | Costos AWS superan presupuesto personal. | 3 | 4 | 12 | Ambientes efímeros, budgets y teardown automatizado. | Costo diario excede umbral definido. | MLOps |
| R-07 | Dashboard distrae del núcleo técnico. | 3 | 2 | 6 | Dashboard solo en C6 y basado en APIs estables. | Frontend inicia antes de C3 completo. | Gabo |
| R-08 | Resultados interpretados como recomendación financiera. | 2 | 5 | 10 | Disclaimer y ausencia de ejecución/retorno prometido. | Copy sugiere compra/venta. | Gabo |

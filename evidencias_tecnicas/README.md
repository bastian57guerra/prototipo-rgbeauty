# Kit de evidencias - RG Beauty Spa: sitio web, API Gateway y administracion de usuarios (Evaluacion Unidad II)

Requisitos: Python 3.10+ (solo libreria estandar). No hay que instalar nada.

## Como ejecutar (en TU computador, para que fecha y responsable sean tuyos)
    python run_sql_demo.py          # crea las 9 tablas, inserta datos ficticios, consultas y pruebas de integridad
    python run_doc_check.py         # verifica coherencia de los JSON y sus referencias al modelo relacional
    cd app && python run_pruebas.py # 22 pruebas (unitarias, integracion con modulos simulados, seguridad, rendimiento, accesibilidad)
Las salidas quedan en `salidas/`. Toma capturas de la consola con la fecha visible para el Anexo H.
(En Windows, si `python` no funciona, usa `py`.)

## Que es cada cosa
- `app/rgbeauty/`: codigo DEMOSTRATIVO (validaciones, gateway con timeout/reintento/circuit breaker, contratos, token firmado,
  login con bloqueo, recuperacion de clave, permisos por rol). No es el sistema final; existe para que las pruebas tengan algo real que ejecutar.
- `app/rgbeauty/modulos_sim.py`: SIMULADORES de los modulos de citas, ventas e inventario (los hacen otros equipos).
- `sql/`: esquema (9 tablas), datos ficticios y consultas. Disenado para PostgreSQL; la demo corre en SQLite.
- `mongo/`: documentos JSON y consultas para MongoDB.
- `diagramas/` y `prototipo/`: imagenes en alta resolucion. `salidas/`: resultados reales de la ejecucion.

## Lo que debes hacer tu (no se puede automatizar)
1. Ejecutar `sql/*.sql` en PostgreSQL (quita la linea PRAGMA del esquema; en `03_consultas.sql` cambia `substr(...)` si lo usas). Captura.
2. Cargar `mongo/*.json` en MongoDB Atlas/Compass y correr las consultas de `consultas_mongosh.js`. Captura.
3. Recrear/importar las pantallas de `prototipo/` en Figma, conectar los flujos y pegar el enlace en el informe.
4. Hacer la validacion con 3-5 personas y completar la seccion 5.6 y el Anexo D.
5. Completar los textos amarillos del Word (enlaces, tablero, Scrum Master, capturas).

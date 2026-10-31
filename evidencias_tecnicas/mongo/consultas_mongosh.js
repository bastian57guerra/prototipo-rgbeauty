// Ejecutar con: mongosh "<cadena de conexion>" consultas_mongosh.js  (o pegar en la consola de Atlas/Compass)
use("rgbeauty_sitio_demo");
db.contenido_pagina.drop(); db.eventos_integracion.drop();
db.contenido_pagina.insertMany(JSON.parse(cat("contenido_pagina.json")));
db.eventos_integracion.insertMany(JSON.parse(cat("eventos_integracion.json")));
// C1: paginas que tienen un boton hacia el modulo de citas
printjson(db.contenido_pagina.find({ "bloques.boton.destino.modulo": "citas" }, { slug: 1, version: 1 }).toArray());
// C2: eventos de integracion que fallaron (no OK), del mas reciente al mas antiguo
printjson(db.eventos_integracion.find({ resultado: { $ne: "OK" } }, { modulo: 1, resultado: 1, duracion_ms: 1 }).sort({ inicio: -1 }).toArray());
// C3: cantidad de eventos por modulo y resultado
printjson(db.eventos_integracion.aggregate([{ $group: { _id: { modulo: "$modulo", resultado: "$resultado" }, total: { $sum: 1 } } }]).toArray());

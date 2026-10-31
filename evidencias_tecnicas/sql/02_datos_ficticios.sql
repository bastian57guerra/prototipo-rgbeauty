INSERT INTO usuario (id_usuario, correo, nombres, apellidos, password_hash, activo, creado_en) VALUES
 (1,'duena@rgbeauty.test','Carolina','Reyes','pbkdf2_sha256$600000$sal01$hashficticio01',1,'2026-09-01 09:00:00'),
 (2,'asistente@rgbeauty.test','Ana','Munoz','pbkdf2_sha256$600000$sal02$hashficticio02',1,'2026-09-01 09:05:00'),
 (3,'asistente2@rgbeauty.test','Sofia','Lagos','pbkdf2_sha256$600000$sal03$hashficticio03',0,'2026-09-15 10:00:00');
INSERT INTO rol VALUES (1,'DUENA','Propietaria: todas las funciones'),(2,'ASISTENTE','Edita contenido y productos; no gestiona precios ni usuarios');
INSERT INTO permiso VALUES
 (1,'CONTENIDO_EDITAR','Crear y editar paginas en borrador'),
 (2,'CONTENIDO_PUBLICAR','Publicar o despublicar paginas'),
 (3,'PRODUCTO_EDITAR','Editar descripcion y fotos de productos (via modulo de ventas)'),
 (4,'PRECIO_EDITAR','Cambiar precios (via modulo de ventas)'),
 (5,'USUARIO_GESTIONAR','Crear, desactivar usuarios y asignar roles'),
 (6,'AUDITORIA_VER','Ver el registro de auditoria'),
 (7,'AGENDA_VER','Ver la agenda (consulta al modulo de citas)');
INSERT INTO usuario_rol VALUES (1,1),(2,2),(3,2);
INSERT INTO rol_permiso VALUES (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(2,1),(2,3),(2,7);
INSERT INTO modulo_externo VALUES
 (1,'citas','https://citas.rgbeauty.test/api/v1','v1',3000,'ACTIVO','2026-10-23 08:00:00'),
 (2,'ventas','https://ventas.rgbeauty.test/api/v1','v1',3000,'ACTIVO','2026-10-23 08:00:00'),
 (3,'inventario','https://inventario.rgbeauty.test/api/v1','v1',3000,'ACTIVO','2026-10-23 08:00:00');
INSERT INTO pagina VALUES
 (1,'inicio','Inicio','PUBLICADA',1,1,3,'2026-09-02 10:00:00','2026-10-01 12:00:00'),
 (2,'servicios','Servicios','PUBLICADA',2,1,2,'2026-09-05 11:00:00','2026-10-03 09:30:00'),
 (3,'resultados','Resultados de tratamientos','BORRADOR',2,NULL,1,'2026-10-15 16:00:00',NULL),
 (4,'ofertas-de-primavera','Ofertas de primavera','EN_REVISION',2,NULL,1,'2026-10-20 10:00:00',NULL);
INSERT INTO token_recuperacion VALUES (1,2,'a3f1c0de5b7a4c1e9d2f8b6a0c4e7d19a3f1c0de5b7a4c1e9d2f8b6a0c4e7d19',  '2026-10-22 10:30:00',1,'2026-10-22 10:00:00');
INSERT INTO auditoria VALUES
 (1,1,'CREAR_USUARIO','usuario',2,'Alta de asistente','190.0.2.10','2026-09-01 09:05:00'),
 (2,1,'PUBLICAR_PAGINA','pagina',1,'Inicio publicada v3','190.0.2.10','2026-10-01 12:00:00'),
 (3,2,'EDITAR_PAGINA','pagina',3,'Borrador de resultados','190.0.2.55','2026-10-15 16:00:00'),
 (4,NULL,'LOGIN_FALLIDO','usuario',2,'Credenciales invalidas','203.0.113.9','2026-10-22 09:58:00');

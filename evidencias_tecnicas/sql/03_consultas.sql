-- Q1. Usuarios con sus roles y cantidad de permisos
SELECT u.id_usuario AS id, u.nombres||' '||u.apellidos AS usuario, r.nombre AS rol, u.activo, COUNT(rp.id_permiso) AS permisos
FROM usuario u JOIN usuario_rol ur ON ur.id_usuario=u.id_usuario JOIN rol r ON r.id_rol=ur.id_rol
JOIN rol_permiso rp ON rp.id_rol=r.id_rol GROUP BY u.id_usuario, r.nombre ORDER BY u.id_usuario;

-- Q2. Permisos efectivos de la asistente (usuario 2)
SELECT p.codigo, p.descripcion FROM usuario_rol ur JOIN rol_permiso rp ON rp.id_rol=ur.id_rol
JOIN permiso p ON p.id_permiso=rp.id_permiso WHERE ur.id_usuario=2 ORDER BY p.id_permiso;

-- Q3. Paginas con autor, publicador y estado
SELECT pg.slug, pg.estado, a.nombres AS autor, COALESCE(b.nombres,'-') AS publicador, pg.version
FROM pagina pg JOIN usuario a ON a.id_usuario=pg.id_autor LEFT JOIN usuario b ON b.id_usuario=pg.id_publicador ORDER BY pg.id_pagina;

-- Q4. Modulos conectados y su estado
SELECT nombre, version_contrato AS contrato, timeout_ms, estado FROM modulo_externo ORDER BY id_modulo;

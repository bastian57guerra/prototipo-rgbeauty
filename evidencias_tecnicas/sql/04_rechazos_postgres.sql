-- =====================================================================
-- RG Beauty Spa - Evidencia 4.7.1: el motor rechaza datos invalidos
-- Motor: PostgreSQL. Ejecutar DESPUES de 01, 02 y 03 (consultas Q1 a Q4).
-- Intenta 10 inserciones: las 9 primeras deben ser RECHAZADAS y la 10 ACEPTADA.
-- El resultado aparece en la pestana "Messages" de pgAdmin (captura esa pestana).
-- =====================================================================
DO $$
DECLARE
  sentencias text[] := ARRAY[
    $q$INSERT INTO usuario (id_usuario,correo,nombres,apellidos,password_hash,creado_en) VALUES (9,'duena@rgbeauty.test','X','Y','h','2026-10-24 10:00:00')$q$,
    $q$INSERT INTO usuario_rol VALUES (2,99)$q$,
    $q$INSERT INTO rol_permiso VALUES (1,5)$q$,
    $q$INSERT INTO pagina VALUES (9,'inicio','Otra','BORRADOR',1,NULL,1,'2026-10-24 10:00:00',NULL)$q$,
    $q$INSERT INTO pagina VALUES (9,'x','X','ARCHIVADA',1,NULL,1,'2026-10-24 10:00:00',NULL)$q$,
    $q$INSERT INTO pagina VALUES (9,'y','Y','PUBLICADA',2,NULL,1,'2026-10-24 10:00:00',NULL)$q$,
    $q$INSERT INTO modulo_externo VALUES (9,'otro','https://x.test','v1',50000,'ACTIVO',NULL)$q$,
    $q$INSERT INTO token_recuperacion VALUES (9,2,'a3f1c0de5b7a4c1e9d2f8b6a0c4e7d19a3f1c0de5b7a4c1e9d2f8b6a0c4e7d19','2026-10-24 10:00:00',0,'2026-10-24 10:00:00')$q$,
    $q$INSERT INTO usuario (id_usuario,correo,nombres,apellidos,password_hash,intentos_fallidos,creado_en) VALUES (9,'z@x.test','Z','Z','h',-1,'2026-10-24 10:00:00')$q$,
    $q$INSERT INTO pagina VALUES (9,'preguntas-frecuentes','Preguntas frecuentes','BORRADOR',2,NULL,1,'2026-10-24 10:00:00',NULL)$q$
  ];
  motivos text[] := ARRAY[
    'correo duplicado (UNIQUE)',
    'rol 99 inexistente (FOREIGN KEY)',
    'par (rol, permiso) repetido (PRIMARY KEY)',
    'slug duplicado (UNIQUE)',
    'estado fuera del dominio (CHECK)',
    'pagina PUBLICADA sin publicador (CHECK)',
    'timeout fuera de rango (CHECK)',
    'hash de token repetido (UNIQUE)',
    'intentos_fallidos negativo (CHECK)',
    'registro valido (debe ser aceptado)'
  ];
  i int;
BEGIN
  FOR i IN 1..array_length(sentencias,1) LOOP
    BEGIN
      EXECUTE sentencias[i];
      RAISE NOTICE 'Prueba %: ACEPTADA  | %', i, motivos[i];
    EXCEPTION WHEN others THEN
      RAISE NOTICE 'Prueba %: RECHAZADA | % | %', i, motivos[i], SQLERRM;
    END;
  END LOOP;
END $$;

-- Confirmar que solo entro la prueba 10 (debe mostrar 1 fila nueva con id 9)
SELECT id_pagina, slug, estado FROM pagina WHERE id_pagina = 9;

-- LIMPIEZA: deja la base igual que en el informe (4 paginas)
DELETE FROM pagina WHERE id_pagina = 9;
SELECT COUNT(*) AS paginas_restantes FROM pagina;   -- debe dar 4

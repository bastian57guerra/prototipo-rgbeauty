-- =====================================================================
-- RG Beauty Spa - Sitio web, API Gateway y administracion de usuarios
-- Modelo logico v1 | Evaluacion Unidad II
-- Motor ejecutado en la demo: SQLite 3. Motor objetivo: PostgreSQL
-- (para PostgreSQL: quitar la linea PRAGMA).
-- =====================================================================
PRAGMA foreign_keys = ON;

CREATE TABLE usuario (
  id_usuario        INTEGER PRIMARY KEY,
  correo            VARCHAR(120) NOT NULL UNIQUE,
  nombres           VARCHAR(80)  NOT NULL,
  apellidos         VARCHAR(80)  NOT NULL,
  password_hash     VARCHAR(255) NOT NULL,
  activo            INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  intentos_fallidos INTEGER NOT NULL DEFAULT 0 CHECK (intentos_fallidos >= 0),
  bloqueado_hasta   TIMESTAMP NULL,
  ultimo_login      TIMESTAMP NULL,
  creado_en         TIMESTAMP NOT NULL
);
CREATE TABLE rol (
  id_rol      INTEGER PRIMARY KEY,
  nombre      VARCHAR(30) NOT NULL UNIQUE,
  descripcion VARCHAR(200)
);
CREATE TABLE permiso (
  id_permiso  INTEGER PRIMARY KEY,
  codigo      VARCHAR(40) NOT NULL UNIQUE,
  descripcion VARCHAR(200) NOT NULL
);
CREATE TABLE usuario_rol (
  id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario),
  id_rol     INTEGER NOT NULL REFERENCES rol(id_rol),
  PRIMARY KEY (id_usuario, id_rol)
);
CREATE TABLE rol_permiso (
  id_rol     INTEGER NOT NULL REFERENCES rol(id_rol),
  id_permiso INTEGER NOT NULL REFERENCES permiso(id_permiso),
  PRIMARY KEY (id_rol, id_permiso)
);
CREATE TABLE modulo_externo (               -- registro de modulos a los que se cuelga el sitio
  id_modulo           INTEGER PRIMARY KEY,
  nombre              VARCHAR(30) NOT NULL UNIQUE,
  base_url            VARCHAR(200) NOT NULL,
  version_contrato    VARCHAR(10) NOT NULL,
  timeout_ms          INTEGER NOT NULL CHECK (timeout_ms BETWEEN 100 AND 10000),
  estado              VARCHAR(12) NOT NULL CHECK (estado IN ('ACTIVO','DEGRADADO','INACTIVO')),
  ultima_verificacion TIMESTAMP NULL
);
CREATE TABLE pagina (                       -- metadatos de las paginas editables del sitio
  id_pagina      INTEGER PRIMARY KEY,
  slug           VARCHAR(80)  NOT NULL UNIQUE,
  titulo         VARCHAR(120) NOT NULL,
  estado         VARCHAR(12)  NOT NULL CHECK (estado IN ('BORRADOR','EN_REVISION','PUBLICADA')),
  id_autor       INTEGER NOT NULL REFERENCES usuario(id_usuario),
  id_publicador  INTEGER NULL REFERENCES usuario(id_usuario),
  version        INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
  creada_en      TIMESTAMP NOT NULL,
  publicada_en   TIMESTAMP NULL,
  CHECK (estado <> 'PUBLICADA' OR (id_publicador IS NOT NULL AND publicada_en IS NOT NULL))
);
CREATE TABLE token_recuperacion (
  id_token   INTEGER PRIMARY KEY,
  id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario),
  hash_token VARCHAR(64) NOT NULL UNIQUE,   -- solo se guarda el hash, nunca el token
  expira_en  TIMESTAMP NOT NULL,
  usado      INTEGER NOT NULL DEFAULT 0 CHECK (usado IN (0,1)),
  creado_en  TIMESTAMP NOT NULL
);
CREATE TABLE auditoria (
  id_auditoria INTEGER PRIMARY KEY,
  id_usuario   INTEGER NULL REFERENCES usuario(id_usuario),
  accion       VARCHAR(40) NOT NULL,
  entidad      VARCHAR(30) NOT NULL,
  id_entidad   INTEGER NULL,
  detalle      VARCHAR(300),
  ip_origen    VARCHAR(45),
  fecha        TIMESTAMP NOT NULL
);
CREATE INDEX ix_pagina_estado ON pagina (estado);
CREATE INDEX ix_auditoria_fecha ON auditoria (fecha);
CREATE INDEX ix_token_usuario ON token_recuperacion (id_usuario);

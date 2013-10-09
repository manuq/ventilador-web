drop table if exists inscripciones;
create table inscripciones (
    id integer primary key autoincrement,
    titulo_obra text not null,
    duracion_obra text not null,
    sinopsis_obra text not null,
    pais_obra text not null,
    es_serie_obra boolean not null,
    imagen_obra_1 text not null,
    imagen_obra_2 text not null,
    url_obra text,
    nombre_presentante text not null,
    nacionalidad_presentante text not null,
    correo_presentante text not null,
    domicilio_presentante text not null,
    web_presentante text,
    telefono_presentante text not null,
    foto_director text not null);

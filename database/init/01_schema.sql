CREATE TABLE IF NOT EXISTS estudiantes (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(120) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    semestre VARCHAR(15) NOT NULL,
    creditos INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS matriculas (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER NOT NULL
        REFERENCES estudiantes(id),
    curso_id INTEGER NOT NULL
        REFERENCES cursos(id),
    nota_final NUMERIC(4,2)
        CHECK (nota_final BETWEEN 0 AND 20),
    UNIQUE (estudiante_id, curso_id)
);

INSERT INTO estudiantes
(nombres, apellidos, correo)
VALUES
('Estudiante 01', 'Demostración',
 'estudiante01@uts.example.com'),
('Estudiante 02', 'Demostración',
 'estudiante02@uts.example.com'),
('Estudiante 03', 'Demostración',
 'estudiante03@uts.example.com'),
('Estudiante 04', 'Demostración',
 'estudiante04@uts.example.com'),
('Estudiante 05', 'Demostración',
 'estudiante05@uts.example.com'),
('Estudiante 06', 'Demostración',
 'estudiante06@uts.example.com'),
('Estudiante 07', 'Demostración',
 'estudiante07@uts.example.com'),
('Estudiante 08', 'Demostración',
 'estudiante08@uts.example.com'),
('Estudiante 09', 'Demostración',
 'estudiante09@uts.example.com'),
('Estudiante 10', 'Demostración',
 'estudiante10@uts.example.com'),
('Estudiante 11', 'Demostración',
 'estudiante11@uts.example.com'),
('Estudiante 12', 'Demostración',
 'estudiante12@uts.example.com'),
('Estudiante 13', 'Demostración',
 'estudiante13@uts.example.com'),
('Estudiante 14', 'Demostración',
 'estudiante14@uts.example.com'),
('Estudiante 15', 'Demostración',
 'estudiante15@uts.example.com'),
('Estudiante 16', 'Demostración',
 'estudiante16@uts.example.com'),
('Estudiante 17', 'Demostración',
 'estudiante17@uts.example.com'),
('Estudiante 18', 'Demostración',
 'estudiante18@uts.example.com'),
('Estudiante 19', 'Demostración',
 'estudiante19@uts.example.com'),
('Estudiante 20', 'Demostración',
 'estudiante20@uts.example.com')
ON CONFLICT (correo) DO NOTHING;

INSERT INTO cursos
(codigo, nombre, semestre, creditos)
VALUES
('WSO', 'Web Semántica y Ontologías', 'ING-VIII', 3),
('IOT', 'Internet de las Cosas y Robótica', 'ING-IX', 4),
('CC', 'Cloud Computing', 'ING-X', 4),
('EMS', 'Evolución y Mantenimiento de Software', 'ING-IX', 3),
('ST2', 'Seminario de Tesis II', 'ING-X', 4),
('CS', 'Ciberseguridad', 'ING-X', 3),
('EMPS', 'Evaluación de mejora y procesos de Software',
 'ING-VI', 3)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO matriculas
(estudiante_id, curso_id, nota_final)
SELECT
    e.id,
    c.id,
    ROUND(
        (10 + ((e.id * 7 + c.id * 3) % 11))::numeric,
        2
    )
FROM estudiantes e
CROSS JOIN cursos c
WHERE
    c.id IN (
        ((e.id - 1) % 7) + 1,
        (e.id % 7) + 1,
        ((e.id + 1) % 7) + 1
    )
AND e.correo LIKE 'estudiante%@uts.example.com'
ON CONFLICT (estudiante_id, curso_id)
DO NOTHING;

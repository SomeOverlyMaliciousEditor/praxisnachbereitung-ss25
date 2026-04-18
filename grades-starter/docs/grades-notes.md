# Notizen zum grades-starter (Aufgabe B.2 / B.3)

## 1. DB-Schema (db/init/001_schema.sql)

### Tabellen und Rollen

- **student**
  - `student_id serial primary key`
  - `matrikel text not null unique`
  - `vorname text not null`
  - `nachname text not null`
  - `programme text not null`
  - `semester int not null check (semester between 1 and 12)`
  - Rolle: Stammdaten zu Studierenden (fachliche Identität über `matrikel`).

- **module**
  - `module_id serial primary key`
  - `name text not null unique`
  - Rolle: Stammdaten zu Modulen (jeder Modulname eindeutig).

- **grade**
  - `grade_id serial primary key`
  - `student_id int not null references student(student_id) on delete cascade`
  - `module_id int not null references module(module_id) on delete cascade`
  - `grade_value text not null`
  - `graded_at timestamp not null default now()`
  - Rolle: Bewegungsdaten / Zuordnung Student–Modul–Note mit Zeitstempel.

### Wichtige Constraints

- **Primärschlüssel**
  - `student.student_id`
  - `module.module_id`
  - `grade.grade_id`

- **Eindeutigkeit (UNIQUE)**
  - `student.matrikel` ist eindeutig.
  - `module.name` ist eindeutig.

- **CHECK-Constraint**
  - `student.semester between 1 and 12`  
    → Semester muss zwischen 1 und 12 liegen.

- **Fremdschlüssel (FK)**
  - `grade.student_id → student.student_id on delete cascade`
  - `grade.module_id → module.module_id on delete cascade`
  - Fachlich: jede `grade` gehört zu genau einem `student` und einem `module`. Beim Löschen von Student oder Modul werden zugehörige Noten mit gelöscht.

### Fachliche Interpretation / ER-Modell

- Entitäten:
  - `Student`
  - `Module`
  - `Grade`

- Beziehungen:
  - `Student 1–n Grade`
  - `Module 1–n Grade`
  - Damit insgesamt: `Student` und `Module` stehen in einer n–m-Beziehung, realisiert über `Grade`.

- Domänenregeln im Schema:
  - Matrikel ist Pflichtfeld und pro Student eindeutig.
  - Modulname ist Pflichtfeld und eindeutig.
  - Semester muss im gültigen Bereich (1–12) liegen.
  - Es gibt keine Note ohne existierenden Student oder Modul (FK-Constraints).

### Seed-Daten

- `student`:
  - Drei Beispielstudierende, inkl. Matrikel, Name, Studiengang, Semester.
  - Insert mit `on conflict (matrikel) do nothing` → Script ist idempotent.

- `module`:
  - Vier Beispielmodule, Insert mit `on conflict (name) do nothing`.

- `grade`:
  - Noten werden über ein `INSERT ... SELECT` eingefügt:
    - Join auf `student` über `matrikel`
    - Join auf `module` über `name`
  - Fachlich: Seed-Zuordnung von Studierenden zu Modulen mit Noten, Zeit wird automatisch über `graded_at default now()` gesetzt.

## 2. Technische Muster im Projekt (Kurzüberblick)

> Bezug: Aufgabenstellung B).2 / B).3 (grades-starter als Referenz)

- **DB-Init**: Schema und Seed-Daten werden über SQL-Dateien unter `db/init/` definiert, nicht manuell in der DB.
- **Idempotente Seeds**: `on conflict do nothing` sorgt dafür, dass man das Init-SQL mehrfach laufen lassen kann, ohne doppelte Daten zu erzeugen.
- **Trennung von Stammdaten und Bewegungsdaten**:
  - Stammdaten: `student`, `module`
  - Bewegungsdaten: `grade`
- **Domänenlogik in der DB**:
  - Eindeutigkeiten (`UNIQUE`)
  - Wertebereiche (`CHECK`)
  - Referenzielle Integrität (`FOREIGN KEY ... on delete cascade`).

# R1 - Eindeutige Personen
Jede Person hat eine eindeutige `person_id` (PK) sowie eine eindeutige fachliche Kennung (z.B. Mitarbeiter-/Personalnummer) als UK.

# R2 - Eindeutige Geräte
Jedes Gerät hat eine eindeutige `device_id` (PK) sowie eine eindeutige fachliche Kennung (z.B. Inventarnummer oder Seriennummer) als UK.

# R3 - Eindeutige Ausleihen
Jede Ausleihe (`Assignment`) hat eine eigene `assignment_id` (PK). Die Kombination aus `person_id`, `device_id` und `start_date` ist fachlich eindeutig.

# R4 - Maximal eine aktive Ausleihe pro Gerät
Ein Gerät darf zu einem Zeitpunkt höchstens eine aktive Ausleihe haben (höchstens ein `Assignment` ohne `end_date`).

# R5 - Mehrere Geräte pro Person
Eine Person darf gleichzeitig mehrere Geräte ausgeliehen haben.

# R6 - Historie der Ausleihen
Jede neue Ausleihe erzeugt einen neuen `Assignment`-Datensatz. Bestehende Datensätze werden nicht überschrieben, sondern nur durch Setzen von `end_date` abgeschlossen.

# R7 - Fremdschlüssel für Ausleihen
Für jede Ausleihe müssen `person_id` und `device_id` auf existierende Einträge in `Person` bzw. `Device` verweisen (FK-Beziehung).

# R8 - Löschen von Geräten
Ein Gerät darf nur gelöscht werden, wenn keine zugehörigen Ausleihen (auch historische) mehr existieren. Alternativ wird ein Gerät über ein Status-Feld (z.B. `inactive`/`retired`) nur logisch stillgelegt.

# R9 - Konsistente Datumsangaben
`start_date` ist Pflichtfeld für jede Ausleihe. Wenn `end_date` gesetzt ist, muss `end_date >= start_date` gelten.

# R10 - Gerätestatus und Wertelisten
Der Status eines Geräts (z.B. `active`, `defective`, `retired`) stammt aus einer festen Werteliste. Geräte mit Status `retired` dürfen nicht neu ausgeliehen werden.

# R11 - Optionale Limitierung je Person
Für bestimmte Gerätekategorien kann die maximale Anzahl gleichzeitig ausgeliehener Geräte pro Person begrenzt werden (Geschäftsregel, nicht zwingend als DB-Constraint umgesetzt).

# R12 - Rückgabefristen
Für Ausleihen gilt eine fachliche maximale Ausleihdauer (z.B. X Tage). Überschreitungen werden in Auswertungen/Reports sichtbar gemacht.

# R13 - Nachvollziehbarkeit von Inventaränderungen
Wesentliche Änderungen am Inventar (z.B. Statuswechsel, Standortänderung) sollen nachvollziehbar sein, z.B. über eine eigene Historien-Tabelle oder ein Audit-Konzept im Zielsystem.

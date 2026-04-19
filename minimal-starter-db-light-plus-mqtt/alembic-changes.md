
# Gerät Rückgabe

## device_status

Neues Feld an device: status mit klar definierten Werten:

- ready
- software_change (Reset)
- hardware_change (Repair)
- defect (Austausch)

alter table device
  add column status text not null default 'einsatzbereit'
  check (status in ('einsatzbereit', 'software_change', 'hardware_change', 'defect'));

alembic revision -m "add status to device"

## damage_quote

Feldname: damage_note
Typ: text
Optional: ja (NULL erlaubt), weil viele Rückgaben keinen Schaden haben.

create table ... 
damage_note text, 
...

alembic revision -m "add damage_note to assignment"

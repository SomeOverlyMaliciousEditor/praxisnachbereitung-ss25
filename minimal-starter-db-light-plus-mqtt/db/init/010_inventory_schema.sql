-- 010_inventory_schema.sql
-- Inventar-Schema: department, person, device_type, location, device, assignment

create table if not exists department (
  department_id serial primary key,
  name          text not null unique
);

create table if not exists person (
  person_id     serial primary key,
  department_id int  not null references department(department_id) on delete restrict,
  first_name    text not null,
  last_name     text not null,
  email         text not null unique
);

create table if not exists device_type (
  device_type_id serial primary key,
  name           text not null unique
);

create table if not exists location (
  location_id serial primary key,
  name        text not null unique
);

create table if not exists device (
  device_id      serial primary key,
  device_type_id int  not null references device_type(device_type_id) on delete restrict,
  location_id    int  not null references location(location_id) on delete restrict,
  serial_number  text not null unique,
  inventory_code text,
  note           text
);

create table if not exists assignment (
  assignment_id serial primary key,
  device_id     int  not null references device(device_id) on delete cascade,
  person_id     int  not null references person(person_id) on delete restrict,
  issued_at     timestamp not null default now(),
  returned_at   timestamp,
  check (returned_at is null or returned_at >= issued_at)
);

-- Seed-Daten

insert into department (name) values
  ('Fakultät Informatik'),
  ('Fakultät Wirtschaft'),
  ('IT-Services')
on conflict (name) do nothing;

insert into person (department_id, first_name, last_name, email)
select d.department_id, p.first_name, p.last_name, p.email
from (values
  ('Fakultät Informatik', 'Anna',  'Koch',   'anna.koch@example.org'),
  ('Fakultät Wirtschaft', 'Ben',   'König',  'ben.koenig@example.org'),
  ('IT-Services',         'Clara', 'Meier',  'clara.meier@example.org')
) as p(dept_name, first_name, last_name, email)
join department d on d.name = p.dept_name
on conflict (email) do nothing;

insert into device_type (name) values
  ('Laptop'),
  ('Monitor'),
  ('Handscanner')
on conflict (name) do nothing;

insert into location (name) values
  ('Gebäude E'),
  ('Gebäude F'),
  ('Gebäude H')
on conflict (name) do nothing;

insert into device (device_type_id, location_id, serial_number, inventory_code, note)
select dt.device_type_id, l.location_id, d.serial_number, d.inventory_code, d.note
from (values
  ('Laptop',      'Gebäude E', 'LAP-0001', 'INV-1001', 'Entwickler-Notebook'),
  ('Monitor',     'Gebäude F', 'MON-0001', 'INV-2001', '27 Zoll Monitor'),
  ('Handscanner', 'Gebäude H', 'HAN-0001', 'INV-3001', 'Barcode-Scanner Lager')
) as d(type_name, loc_name, serial_number, inventory_code, note)
join device_type dt on dt.name = d.type_name
join location    l  on l.name  = d.loc_name
on conflict (serial_number) do nothing;

insert into assignment (device_id, person_id, issued_at, returned_at)
select dv.device_id, p.person_id, now() - interval '7 days', null
from device dv
join device_type dt on dt.device_type_id = dv.device_type_id
join person      p  on p.email = 'anna.koch@example.org'
where dv.serial_number = 'LAP-0001'
on conflict do nothing;

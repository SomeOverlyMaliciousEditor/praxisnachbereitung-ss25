create table if not exists device (
  id serial primary key,
  name text not null,
  status text not null check (status in ('in_use','in_stock','repair','retired')),
  location text not null default 'HQ'
);

insert into device (name, status, location) values
  ('Laptop-001','in_use','HQ'),
  ('Laptop-002','repair','HQ'),
  ('Monitor-003','in_stock','HQ'),
  ('Dock-004','in_use','Remote'),
  ('Printer-005','retired','HQ'),
  ('Tablet-006','in_use','Remote'),
  ('Phone-007','in_stock','HQ'),
  ('Scanner-008','repair','HQ'),
  ('Headset-009','in_use','HQ'),
  ('Router-010','in_stock','Remote');

create or replace view v_device_status as
select status, count(*) as cnt
from device
group by status;

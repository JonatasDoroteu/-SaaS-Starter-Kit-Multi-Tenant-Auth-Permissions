-- Execute once in the Supabase SQL Editor with an administrative role.
-- Replace the placeholder before executing and never commit the real password.

create role saas_app
  login
  password 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD'
  nosuperuser
  nocreatedb
  nocreaterole
  noreplication
  nobypassrls;

grant connect on database postgres to saas_app;
grant usage on schema public to saas_app;
grant select, insert, update, delete on all tables in schema public to saas_app;
grant usage, select, update on all sequences in schema public to saas_app;

alter default privileges in schema public
  grant select, insert, update, delete on tables to saas_app;
alter default privileges in schema public
  grant usage, select, update on sequences to saas_app;

-- Verify the role used by DATABASE_URL cannot bypass RLS.
select rolname, rolsuper, rolbypassrls
from pg_roles
where rolname = 'saas_app';
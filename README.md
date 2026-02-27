# Database

PostgreSQL schema and seed data for AIRA-Med.

## Setup
```bash
createdb hospitaldb
psql -U postgres -d hospitaldb -f schema.sql
psql -U postgres -d hospitaldb -f seed.sql
```

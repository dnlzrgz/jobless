## 0.10.0 (2026-02-04)

### Feat

- **db**: update schemas for better validation

## 0.9.1 (2026-02-03)

### Feat

- **app**: improve select styles

## 0.9.0 (2026-02-03)

### Feat

- **app**: add create modals for companies and applications

### Fix

- **app**: handle correctly validation errors on create

### Refactor

- **scripts**: make skills lowercase
- **db**: remove skill relationship with companies

## 0.8.0 (2026-01-24)

### Feat

- **db**: add pydantic schemas for validation

### Refactor

- **app**: apply repositories
- **db**: remove sqlmodel in favor of sqlalchemy
- **db**: remove services in favor of repositories

## 0.7.0 (2026-01-20)

### Feat

- **app**: add modal for creating contacts

### Fix

- **models**: catch validation errors

### Refactor

- **app**: rename file

## 0.6.0 (2026-01-16)

### Feat

- **app**: add custom data tables subclasses

## 0.5.0 (2026-01-15)

### Feat

- **app**: add bindings for delete and refresh actions

## 0.4.1 (2026-01-14)

### Fix

- **app**: update data tables type hints

### Refactor

- **app**: add config dict for data tables

## 0.4.0 (2026-01-13)

### Feat

- **app**: add custom data tables and header
- **scripts**: add script to populate the db
- add support for settings

## 0.3.0 (2026-01-11)

### Feat

- add schemas using dataclasses

### Refactor

- **models**: convert schemas into sqlmodel models

## 0.2.0 (2026-01-08)

### Feat

- **db**: add schemas, triggers and relationships
- init commit

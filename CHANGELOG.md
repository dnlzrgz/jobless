## 0.15.2 (2026-02-19)

### Feat

- **app**: add key bindings to jump between tables

## 0.15.1 (2026-02-19)

### Refactor

- **settings**: remove pydantic-settings for dataclass

## 0.15.0 (2026-02-18)

### Feat

- **app**: improve navigation in data tables

## 0.14.1 (2026-02-18)

### Fix

- **app,db**: fix update related functionality

## 0.14.0 (2026-02-17)

### Feat

- **db**: add numeric id to skill model
- **db**: add schemas for easier validation in app
- **app**: add update modals

### Refactor

- **app**: update application to use schemas instead of models
- **db**: decouple models from app with schemas

## 0.13.0 (2026-02-11)

### Feat

- **db**: add missing application possible statuses

## 0.12.0 (2026-02-11)

### Feat

- **db**: improve unique values listing

## 0.11.0 (2026-02-11)

### Refactor

- **app**: add registry pattern

## 0.10.2 (2026-02-06)

### Refactor

- **db**: remove pydantic schemas and update repositories

## 0.10.1 (2026-02-05)

### Feat

- **app**: add scoped sessions

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

## 0.18.0 (2026-05-12)

### Feat

- **cli**: add --force flag to delete commands

## 0.17.0 (2026-05-11)

### Feat

- **cli**: add --add-skill/--remove-skill on update application
- **cli**: add update command for skills
- **cli**: add filters to skills command
- **cli**: add view command for contacts
- **cli**: add filters to contacts command
- **cli**: manage contacts on applications
- **cli**: add view command for companies
- **cli**: add filters to companies command
- **cli**: add view command for applications
- **cli**: add format options for applications list command
- **cli**: add more options to filter applications by
- **cli**: add filters to applications command
- **cli**: add export command
- **tui**: remove tui
- **cli**: add util function for optional fields
- **cli**: add command to manage companies
- **cli**: add command to manage skills
- **cli**: add command to manage applications
- update util script
- add mapper

### Fix

- **cli**: minor typos on commands
- **repos**: return type of skill repository get method

### Refactor

- **settings**: extract settings loader
- decouple schemas and models
- extract location and status enums

## 0.16.0 (2026-03-01)

### Feat

- **cli**: add prune command
- **db**: add method to handle basic filtering
- **cli**: add export command

### Fix

- get_app_dir was not using correct parameter

## 0.15.3 (2026-02-19)

### Feat

- **app**: update grid size

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

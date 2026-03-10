# jobless

**A simple job application manager for your terminal.**

jobless is a simple, easy-to-use job application manager that lives in your terminal, built with the goal of replacing cluttered spreadsheets and infinite browser bookmarks.

![screenshot](./.github/jobless.svg)

## Features

- Manage applications, companies, and contacts all in one place.
- Navigate, create, and update without lifting your hands from the keyboard.

## Roadmap (WIP)

- Full-text search.
- Advanced filtering.
- `$EDITOR` integration.
- `import` command.
- AI-Assisted pipeline.
- Notifications.
- Statistics (maybe).

## Installation

jobless can be installed via [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv tool install --python 3.14 jobless

# or to use it without installing.
uvx --python 3.14 jobless
```

### Prefer `pipx`?

If you prefer `pipx` is as easy as to run `pipx install jobless`.

## Commands

jobless has a small CLI that allows to do certain things that would be harder to do on a TUI.

### `export`

You can export your entire database or your applications, companies, or contacts:

```bash
# Export everything into a ZIP file.
jobless export -f backup.zip

# Export only applications into a CSV file.
jobless export -f applications.csv --only applications
```

### `prune`

The `prune` command lets you remove stale applications and orphaned records. You just need to run:

```bash
# See what's stale without deleting anything.
jobless prune --days 180 --dry-run

# Cleanup
jobless prune --days 180
```

## Config

jobless looks for a config file at `~/.config/jobless/config.toml`. By default, the SQLite database will also be created in this directory.

### Theme

At the moment, you can customize the theme using any of the [built-in textual themes](https://textual.textualize.io/guide/design/). To change the theme, add the following line to your config file:

```toml
theme = "catppuccin-latte"
```

# jobless

**A job application tracker for the command line.**

Built with the idea of replacing cluttered spreadsheets and infinite browser tabs, jobless is a simple job application tracker for the terminal. Keep your applications, companies, contacts, and skills organized in a single place.

## Features

- Track job applications, companies, contacts, and skills.
- Advance filtering and sorting.

## Roadmap (WIP)

- TUI (more on this down below.)
- Full-text search.
- Notifications/Events.

## Installation

jobless can be installed via [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv tool install --python 3.14 jobless
# or
uvx --python 3.14 jobless
```

### Prefer `pipx`?

If you prefer `pipx`, it's as easy as running `pipx install jobless`.

## Commands

### Applications

```bash
jobless app <command>
```

| Command  | Description                                                                                                                            |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `add`    | Add a new application. Prompts for title and company if not provided as flags. Skills and contacts can be attached at creation time.   |
| `view`   | Show all details for an application. Pass `--web` to open the job posting URL in your browser.                                         |
| `update` | Update any field on an existing application. Add or remove individual skills and contacts without touching the rest.                   |
| `list`   | List applications with optional filters. Filter by status, location type, company, skill, applied date range, or follow-up date range. |
| `del`    | Delete one or more applications by ID.                                                                                                 |

If you need to, you can always run:

```bash
jobless app --help
# or
jobless app <command> --help
```

### Companies

```bash
jobless company <command>
```

Companies can be created automatically when adding an application, but you can also manage them directly if you want or need to.

| Command  | Description                                                                                                                   |
| -------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `add`    | Add a company manually with a name, website, and industry.                                                                    |
| `view`   | Show company details. Pass `--web` to open the company website.                                                               |
| `update` | Update the name, URL, or industry. Pass `''` to clear an optional field.                                                      |
| `list`   | List companies with optional filters, including by number of linked applications.                                             |
| `del`    | Delete one or more companies. If a company has linked applications you will be asked to confirm before everything is removed. |

### Contacts

```bash
jobless contact <command>
```

Refers to people you've talked to, recruiters, or anyone else worth keeping a record of.

| Command  | Description                                                                      |
| -------- | -------------------------------------------------------------------------------- |
| `add`    | Add a contact with a name, email, phone, and/or URL (e.g. a LinkedIn profile).   |
| `view`   | Show contact details. Pass `--web` to open the contact's URL.                    |
| `update` | Update any field. Pass `''` to clear an optional field.                          |
| `list`   | List contacts with optional filters, including by number of linked applications. |
| `del`    | Delete one or more contacts. Linked applications are not affected.               |

### Skills

```bash
jobless skill <command>
```

Skills are created automatically when you tag an application. There is no `add` command but you can rename or delete them if needed here.

| Command  | Description                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| `update` | Rename a skill.                                                                             |
| `list`   | List all skills. Filter by name or number of linked applications.                           |
| `del`    | Delete one or more skills. They will be unlinked from any applications that reference them. |

## Exporting

Every `list` command supports a `--format` flag with supports JSON. If you need to export your data, the easiest way is to:

```bash
# dump all applications to a file
jobless app list --format json > application.json

# or export only active applications (for example)
jobless app list --status applied --status interviewing --format json > active.json
```

## Where is the TUI?

For the time being I decided to remove the TUI that was the original form of jobless. The reason being that the TUI was making me slower and this tool, instead of making things easy for me, was adding a hurdle that wasn't that necessary. That said, I plan to re-add the TUI in the future, but only after I've polished a few rough edges in the current CLI.

## Using with other tools

Since jobless is a plain CLI, it fits naturally into any shell workflow. The JSON output in particular makes it easy to pipe data into tools like `jq`, scripts, or AI assistants/agents with shell access.

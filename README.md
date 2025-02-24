# Checklist Generator

A Python CLI tool that generates daily checklists by combining tasks from a markdown file with calendar events from an .ics file. The output is a formatted Typst document that can optionally be compiled to PDF.

## Features

- Generates daily checklists with German date formatting
- Parses hierarchical tasks from markdown files with support for explanatory text
- Integrates calendar events from .ics files (excluding "Tägliche Systemkontrolle" events)
- Creates professional Typst documents with:
  - Custom header with logo
  - Formatted task checkboxes
  - Calendar events section
  - Notes section with lined space
- Supports double-sided printing
- Optional direct PDF compilation

## Requirements

- Python 3
- Typst (for PDF compilation)
- Python packages:
  - typer
  - icalendar

## Usage

```bash
python checklist_generator.py  \
  <start-date> <end-date> \
  --tasks tasks.md \
  --calendar calendarfile.ics \
  --output checklist.typ \
  --compile
```

### Arguments

- `start-date`: Start date in YYYY-MM-DD format
- `end-date`: End date in YYYY-MM-DD format
- `--tasks, -t`: Path to markdown tasks file
- `--calendar, -c`: Path to ICS calendar file
- `--output, -o`: Output Typst file path
- `--compile`: Optional flag to compile to PDF

## File Structure

- `checklist_generator.py`: Main Python script
- `tasks.md`: Source markdown file containing daily tasks
- `template.typ`: Typst template for document formatting
- `logo.png`: Logo file for header
- `Hansaponik.ics`: Calendar file with events

## Task Format

Tasks in the markdown file support:
- Hierarchical structure with indentation
- Explanatory text in parentheses
- Example:
```markdown
- Main task
  - Subtask (with explanation)
```

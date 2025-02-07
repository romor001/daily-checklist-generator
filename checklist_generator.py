#!/usr/bin/env python3

import typer
from datetime import datetime, timedelta
import icalendar
import re
from pathlib import Path
from typing import Optional
import subprocess

# Configuration
HEADER_TEXT = "FH Südwestfalen - Kokerei Hansa - Gloria"
LOGO_PATH = "logo.png"  # Logo file in the same directory

# Create Typer app instance
app = typer.Typer(help="Generate daily checklist in Typst format")

# Typst document template
TYPST_TEMPLATE = '''
#import "template.typ": *

#show: project.with(
  title: "{header_text}",
  logo: "{logo_path}"
)

{pages}
'''

# Template for each page
PAGE_TEMPLATE = '''
#page[
  = {date}

  // Regular tasks
  {tasks}

  // Calendar events for the day
  == weitere Aufgaben
  {events}

  // Notes section
  == Notizen und Beobachtungen
  {notes}
]
'''

def parse_markdown_tasks(md_file: Path) -> str:
    """Parse markdown file and convert bullets to Typst checklist items."""
    try:
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Convert markdown bullet points to Typst checklist items
        tasks = []
        for line in content.split('\n'):
            if line.strip().startswith('- '):
                # Count leading spaces for indentation
                indent_spaces = len(re.match(r'^[\s]*', line).group())
                indent_level = indent_spaces // 2  # Convert spaces to indent level
                task_text = line.strip('- ').strip()
                
                # Handle explanatory text in parentheses
                if '(' in task_text and ')' in task_text:
                    main_text = task_text[:task_text.find('(')].strip()
                    explanation = task_text[task_text.find('(')+1:task_text.find(')')].strip()
                    escaped_main = escape_typst_string(main_text)
                    escaped_explanation = escape_typst_string(explanation)
                    task_line = f"#task(\"{escaped_main}\", indent: {indent_level})[*{escaped_main}* #text(weight: \"light\", style: \"italic\")[{escaped_explanation}]]"
                else:
                    escaped_text = escape_typst_string(task_text)
                    task_line = f"#task(\"{escaped_text}\", indent: {indent_level})[*{escaped_text}*]"
                
                tasks.append(task_line)
        
        return '\n'.join(tasks)
    except Exception as e:
        typer.secho(f"Error parsing markdown file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

def escape_typst_string(s: str) -> str:
    """Escape special characters for Typst string literals."""
    # Escape backslashes first, then quotes
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return s

def get_calendar_events(ics_file: Path, date: datetime.date) -> Optional[str]:
    """Get events for a specific date from ICS file."""
    try:
        with open(ics_file, 'rb') as f:
            cal = icalendar.Calendar.from_ical(f.read())
        
        events = []
        for event in cal.walk('vevent'):
            event_date = event.get('dtstart').dt
            if isinstance(event_date, datetime):
                event_date = event_date.date()
            
            if event_date == date:
                summary = str(event.get('summary'))
                escaped_summary = escape_typst_string(summary)
                events.append(f"#task(\"{escaped_summary}\")[*{escaped_summary}*]")
        
        # Return None if no events, otherwise join them with newlines
        return '\n'.join(events) if events else None
    except Exception as e:
        typer.secho(f"Error reading calendar file: {e}", fg=typer.colors.RED)
        return None

def generate_notes_section() -> str:
    """Generate lined notes section with double spacing."""
    # Return lines with extra vertical space between them
    # Reduce the number of lines to ensure everything fits on one page
    return "#line(length: 100%)\n#v(1.4em)\n" * 8

def generate_typst_document(
    start_date: datetime.date,
    end_date: datetime.date,
    tasks_md: Path,
    calendar_file: Path,
    output_file: Path
) -> None:
    """Generate the complete Typst document."""
    # Ensure output directory exists
    output_dir = output_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template.typ to output directory if it's not there
    template_source = Path(__file__).parent / "template.typ"
    template_dest = output_dir / "template.typ"
    if not template_dest.exists():
        try:
            import shutil
            shutil.copy2(template_source, template_dest)
        except Exception as e:
            typer.secho(f"Warning: Could not copy template file: {e}", fg=typer.colors.YELLOW)
            typer.echo("Please ensure template.typ is in the same directory as the output file.")
    
    # German weekday and month names
    WEEKDAYS_DE = {
        'Monday': 'Montag',
        'Tuesday': 'Dienstag',
        'Wednesday': 'Mittwoch',
        'Thursday': 'Donnerstag',
        'Friday': 'Freitag',
        'Saturday': 'Samstag',
        'Sunday': 'Sonntag'
    }
    
    MONTHS_DE = {
        'January': 'Januar',
        'February': 'Februar',
        'March': 'März',
        'April': 'April',
        'May': 'Mai',
        'June': 'Juni',
        'July': 'Juli',
        'August': 'August',
        'September': 'September',
        'October': 'Oktober',
        'November': 'November',
        'December': 'Dezember'
    }
    
    pages = []
    current_date = start_date
    
    with typer.progressbar(
        length=(end_date - start_date).days + 1,
        label="Generating pages"
    ) as progress:
        while current_date <= end_date:
            # Get English date format first
            eng_date = current_date.strftime("%A, %B %d, %Y")
            
            # Convert to German
            for eng, de in WEEKDAYS_DE.items():
                eng_date = eng_date.replace(eng, de)
            for eng, de in MONTHS_DE.items():
                eng_date = eng_date.replace(eng, de)
                
            tasks = parse_markdown_tasks(tasks_md)
            events = get_calendar_events(calendar_file, current_date)
            notes = generate_notes_section()
            
            page = PAGE_TEMPLATE.format(
                date=eng_date,
                tasks=tasks,
                events=events if events else "",
                notes=notes
            ).replace('Events', 'Termine').replace('Notes', 'Notizen')
            
            pages.append(page)
            
            current_date += timedelta(days=1)
            progress.update(1)
    
    # Complete document
    document = TYPST_TEMPLATE.format(
        header_text=HEADER_TEXT,
        logo_path=LOGO_PATH,
        pages='\n'.join(pages)
    )
    
    with open(output_file, 'w') as f:
        f.write(document)
        
    typer.secho(f"Generated Typst document: {output_file}", fg=typer.colors.GREEN)

@app.command()
def generate(
    start_date: datetime = typer.Argument(
        ...,
        help="Start date (YYYY-MM-DD)",
        formats=["%Y-%m-%d"]
    ),
    end_date: datetime = typer.Argument(
        ...,
        help="End date (YYYY-MM-DD)",
        formats=["%Y-%m-%d"]
    ),
    tasks: Path = typer.Option(
        ...,
        "--tasks", "-t",
        help="Path to markdown tasks file",
        exists=True,
        file_okay=True,
        dir_okay=False
    ),
    calendar: Path = typer.Option(
        ...,
        "--calendar", "-c",
        help="Path to ICS calendar file",
        exists=True,
        file_okay=True,
        dir_okay=False
    ),
    output: Path = typer.Option(
        ...,
        "--output", "-o",
        help="Output Typst file"
    ),
    compile: bool = typer.Option(
        False,
        "--compile",
        help="Compile to PDF after generating Typst file",
        is_flag=True
    )
) -> None:
    """Generate daily checklist in Typst format with optional PDF compilation."""
    generate_typst_document(
        start_date.date(),
        end_date.date(),
        tasks,
        calendar,
        output
    )
    
    if compile:
        try:
            output_pdf = output.with_suffix('.pdf')
            typer.echo("Compiling PDF...")
            subprocess.run(['typst', 'compile', str(output), str(output_pdf)], check=True)
            typer.secho(f"Generated PDF: {output_pdf}", fg=typer.colors.GREEN)
        except subprocess.CalledProcessError as e:
            typer.secho(f"Error compiling PDF: {e}", fg=typer.colors.RED)
            raise typer.Exit(1)
        except FileNotFoundError:
            typer.secho(
                "Error: typst command not found. Please ensure Typst is installed and in your PATH.",
                fg=typer.colors.RED
            )
            raise typer.Exit(1)

if __name__ == "__main__":
    app()
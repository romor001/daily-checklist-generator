#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta
import icalendar
import markdown
import re
from pathlib import Path

# Configuration
HEADER_TEXT = "FH Südwestfalen - Kokerei Hansa - Gloria"
LOGO_PATH = "logo.png"  # Logo file in the same directory

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

def parse_markdown_tasks(md_file):
    """Parse markdown file and convert bullets to Typst checklist items."""
    try:
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Convert markdown to HTML to parse the list structure
        html = markdown.markdown(content)
        
        # Now convert HTML list items to Typst checklist items
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
        print(f"Error parsing markdown file: {e}")
        return "Error parsing tasks"

def escape_typst_string(s):
    """Escape special characters for Typst string literals."""
    # Escape backslashes first, then quotes
    s = s.replace('\\', '\\\\').replace('"', '\\"')
    return s

def get_calendar_events(ics_file, date):
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
        print(f"Error reading calendar file: {e}")
        return None

def generate_notes_section():
    """Generate lined notes section with double spacing.
    Return a flexible number of lines that will fit on one page."""
    # Return lines with extra vertical space between them
    # Reduce the number of lines to ensure everything fits on one page
    return "#line(length: 100%)\n#v(1.4em)\n" * 8

def generate_typst_document(start_date, end_date, tasks_md, calendar_file, output_file):
    """Generate the complete Typst document."""
    # Ensure output directory exists
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template.typ to output directory if it's not there
    template_source = Path(__file__).parent / "template.typ"
    template_dest = output_dir / "template.typ"
    if not template_dest.exists():
        try:
            import shutil
            shutil.copy2(template_source, template_dest)
        except Exception as e:
            print(f"Warning: Could not copy template file: {e}")
            print("Please ensure template.typ is in the same directory as the output file.")
    
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
            events=events,
            notes=notes
        ).replace('Events', 'Termine').replace('Notes', 'Notizen')
        
        pages.append(page)
        
        current_date += timedelta(days=1)
    
    # Complete document
    document = TYPST_TEMPLATE.format(
        header_text=HEADER_TEXT,
        logo_path=LOGO_PATH,
        pages='\n'.join(pages)
    )
    
    with open(output_file, 'w') as f:
        f.write(document)
        
    print(f"Generated Typst document: {output_file}")
    print("To compile to PDF, run:")
    print(f"typst compile {output_file} {Path(output_file).stem}.pdf")

def main():
    parser = argparse.ArgumentParser(description='Generate daily checklist in Typst format')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--tasks', required=True, help='Path to markdown tasks file')
    parser.add_argument('--calendar', required=True, help='Path to ICS calendar file')
    parser.add_argument('--output', required=True, help='Output Typst file')
    parser.add_argument('--compile', action='store_true', help='Compile to PDF after generating Typst file')
    
    args = parser.parse_args()
    
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    
    generate_typst_document(start_date, end_date, args.tasks, args.calendar, args.output)
    
    if args.compile:
        try:
            import subprocess
            output_pdf = Path(args.output).stem + '.pdf'
            subprocess.run(['typst', 'compile', args.output, output_pdf], check=True)
            print(f"Generated PDF: {output_pdf}")
        except subprocess.CalledProcessError as e:
            print(f"Error compiling PDF: {e}")
        except FileNotFoundError:
            print("Error: typst command not found. Please ensure Typst is installed and in your PATH.")

if __name__ == "__main__":
    main()
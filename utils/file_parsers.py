"""File Parsers - Helper functions for reading local files (.docx, .xlsx, .ics, etc.) where a full API is overkill."""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class FileParser:
    """Parse various file formats."""

    @staticmethod
    def parse_csv(file_path: str, delimiter: str = ',') -> List[Dict]:
        """Parse CSV file into list of dictionaries."""
        import csv

        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                data = list(reader)
        except Exception as e:
            print(f"Error parsing CSV {file_path}: {e}")
        return data

    @staticmethod
    def parse_json(file_path: str) -> Dict[str, Any]:
        """Parse JSON file."""
        import json

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {}

    @staticmethod
    def parse_text(file_path: str) -> str:
        """Parse plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return ""

    @staticmethod
    def parse_excel(file_path: str) -> List[Dict]:
        """Parse Excel file (.xlsx, .xls)."""
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_dict('records')
        except ImportError:
            print("pandas not available for Excel parsing")
            return []
        except Exception as e:
            print(f"Error parsing Excel {file_path}: {e}")
            return []

    @staticmethod
    def parse_word(file_path: str) -> str:
        """Parse Word document (.docx)."""
        try:
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            print("python-docx not available for Word parsing")
            return ""
        except Exception as e:
            print(f"Error parsing Word document {file_path}: {e}")
            return ""

    @staticmethod
    def parse_ics(file_path: str) -> List[Dict]:
        """Parse iCalendar (.ics) file."""
        try:
            from icalendar import Calendar
            events = []

            with open(file_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())

            for component in cal.walk():
                if component.name == "VEVENT":
                    event = {
                        'summary': str(component.get('summary', '')),
                        'start': component.get('dtstart').dt if component.get('dtstart') else None,
                        'end': component.get('dtend').dt if component.get('dtend') else None,
                        'location': str(component.get('location', '')),
                        'description': str(component.get('description', ''))
                    }
                    events.append(event)

            return events
        except ImportError:
            print("icalendar not available for ICS parsing")
            return []
        except Exception as e:
            print(f"Error parsing ICS file {file_path}: {e}")
            return []

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detect file type based on extension."""
        _, ext = os.path.splitext(file_path.lower())
        return ext[1:] if ext else 'unknown'

    @classmethod
    def parse_file(cls, file_path: str) -> Any:
        """Auto-detect and parse file based on extension."""
        if not os.path.exists(file_path):
            return None

        file_type = cls.detect_file_type(file_path)

        if file_type == 'csv':
            return cls.parse_csv(file_path)
        elif file_type == 'json':
            return cls.parse_json(file_path)
        elif file_type in ['txt', 'md']:
            return cls.parse_text(file_path)
        elif file_type in ['xlsx', 'xls']:
            return cls.parse_excel(file_path)
        elif file_type == 'docx':
            return cls.parse_word(file_path)
        elif file_type == 'ics':
            return cls.parse_ics(file_path)
        else:
            return cls.parse_text(file_path)  # Default to text

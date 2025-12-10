"""
Professional-Grade Content Generation System
Interactive HTML presentations, Excel dashboards, Word documents, and web applications
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from jinja2 import Environment, FileSystemLoader, Template
import base64
from io import BytesIO
import zipfile
import tempfile
import logging
from datetime import datetime
import uuid

@dataclass
class ContentConfig:
    """Configuration for content generation"""
    title: str
    author: str = "AI Assistant"
    theme: str = "professional"
    output_format: str = "html"
    template_dir: str = "templates"
    assets_dir: str = "assets"
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseContentGenerator:
    """Base class for all content generators"""
    
    def __init__(self, config: ContentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.template_env = self._setup_templates()
        
    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment"""
        template_dir = os.path.join(os.path.dirname(__file__), self.config.template_dir)
        if not os.path.exists(template_dir):
            os.makedirs(template_dir, exist_ok=True)
        
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # Add custom filters
        env.filters['b64encode'] = lambda x: base64.b64encode(x).decode('utf-8')
        env.filters['timestamp'] = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return env
    
    def generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())[:8]

class PresentationGenerator(BaseContentGenerator):
    """
    Interactive HTML Presentation Generator
    Creates responsive presentations with embedded charts and animations
    """
    
    def __init__(self, config: ContentConfig):
        super().__init__(config)
        self.slides = []
        self.theme_config = self._load_theme_config()
    
    def _load_theme_config(self) -> Dict[str, Any]:
        """Load theme configuration"""
        themes = {
            "professional": {
                "primary_color": "#2c3e50",
                "secondary_color": "#3498db",
                "background_color": "#ffffff",
                "text_color": "#2c3e50",
                "font_family": "Arial, sans-serif",
                "heading_font": "Georgia, serif"
            },
            "modern": {
                "primary_color": "#1a1a1a",
                "secondary_color": "#ff6b6b",
                "background_color": "#f8f9fa",
                "text_color": "#1a1a1a",
                "font_family": "Helvetica, sans-serif",
                "heading_font": "Montserrat, sans-serif"
            },
            "creative": {
                "primary_color": "#8e44ad",
                "secondary_color": "#e74c3c",
                "background_color": "#ecf0f1",
                "text_color": "#2c3e50",
                "font_family": "Open Sans, sans-serif",
                "heading_font": "Playfair Display, serif"
            }
        }
        return themes.get(self.config.theme, themes["professional"])
    
    def add_slide(self, slide_type: str, content: Dict[str, Any], 
                  layout: str = "default", animations: List[str] = None) -> str:
        """Add a slide to the presentation"""
        slide_id = self.generate_id()
        
        slide = {
            "id": slide_id,
            "type": slide_type,
            "layout": layout,
            "content": content,
            "animations": animations or [],
            "theme": self.theme_config
        }
        
        self.slides.append(slide)
        return slide_id
    
    def add_title_slide(self, title: str, subtitle: str = "", author: str = "") -> str:
        """Add title slide"""
        content = {
            "title": title,
            "subtitle": subtitle,
            "author": author or self.config.author,
            "date": datetime.now().strftime('%B %d, %Y')
        }
        return self.add_slide("title", content, "center")
    
    def add_content_slide(self, title: str, content: Union[str, List[str]], 
                         image_url: str = None, chart_data: Dict = None) -> str:
        """Add content slide with text, images, or charts"""
        slide_content = {
            "title": title,
            "content": content if isinstance(content, list) else [content],
            "image_url": image_url,
            "chart_data": chart_data
        }
        
        layout = "image-right" if image_url else "chart" if chart_data else "default"
        return self.add_slide("content", slide_content, layout)
    
    def add_chart_slide(self, title: str, chart_type: str, data: Dict[str, Any], 
                       chart_config: Dict[str, Any] = None) -> str:
        """Add slide with interactive chart"""
        chart_data = {
            "type": chart_type,
            "data": data,
            "config": chart_config or {},
            "id": f"chart_{self.generate_id()}"
        }
        
        content = {
            "title": title,
            "chart_data": chart_data
        }
        
        return self.add_slide("chart", content, "chart")
    
    def add_comparison_slide(self, title: str, left_content: Dict, right_content: Dict) -> str:
        """Add comparison slide with two columns"""
        content = {
            "title": title,
            "left": left_content,
            "right": right_content
        }
        return self.add_slide("comparison", content, "two-column")
    
    def generate_html(self, output_path: str = None, include_navigation: bool = True) -> str:
        """Generate complete HTML presentation"""
        template_content = self._get_presentation_template()
        
        template = Template(template_content)
        
        html_content = template.render(
            title=self.config.title,
            slides=self.slides,
            theme=self.theme_config,
            include_navigation=include_navigation,
            metadata=self.config.metadata
        )
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"Presentation saved to {output_path}")
        
        return html_content
    
    def _get_presentation_template(self) -> str:
        """Get the main presentation template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: {{ theme.font_family }};
            background: {{ theme.background_color }};
            color: {{ theme.text_color }};
            overflow: hidden;
        }
        
        .presentation-container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        
        .slide {
            width: 100%;
            height: 100%;
            position: absolute;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s ease-in-out;
        }
        
        .slide.active {
            opacity: 1;
            transform: translateX(0);
        }
        
        .slide.prev {
            transform: translateX(-100%);
        }
        
        .slide h1 {
            font-family: {{ theme.heading_font }};
            font-size: 3em;
            color: {{ theme.primary_color }};
            margin-bottom: 30px;
            text-align: center;
        }
        
        .slide h2 {
            font-family: {{ theme.heading_font }};
            font-size: 2.5em;
            color: {{ theme.primary_color }};
            margin-bottom: 25px;
        }
        
        .slide h3 {
            font-size: 1.8em;
            color: {{ theme.secondary_color }};
            margin-bottom: 20px;
        }
        
        .slide p, .slide li {
            font-size: 1.3em;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .slide ul {
            list-style: none;
            padding-left: 0;
        }
        
        .slide li {
            position: relative;
            padding-left: 30px;
            margin-bottom: 10px;
        }
        
        .slide li:before {
            content: "▶";
            color: {{ theme.secondary_color }};
            position: absolute;
            left: 0;
        }
        
        .two-column {
            flex-direction: row;
            justify-content: space-between;
            align-items: flex-start;
        }
        
        .column {
            flex: 1;
            padding: 0 30px;
        }
        
        .chart-container {
            width: 80%;
            height: 60%;
            margin: 20px auto;
        }
        
        .image-container {
            max-width: 50%;
            max-height: 60%;
            margin: 20px;
        }
        
        .image-container img {
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .navigation {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 15px;
            z-index: 1000;
        }
        
        .nav-btn {
            padding: 12px 24px;
            background: {{ theme.primary_color }};
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .nav-btn:hover {
            background: {{ theme.secondary_color }};
            transform: translateY(-2px);
        }
        
        .nav-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .slide-counter {
            position: fixed;
            top: 30px;
            right: 30px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
        }
        
        .title-slide {
            text-align: center;
        }
        
        .title-slide .subtitle {
            font-size: 1.8em;
            color: {{ theme.secondary_color }};
            margin-bottom: 40px;
        }
        
        .title-slide .author {
            font-size: 1.2em;
            color: {{ theme.text_color }};
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .slide {
                padding: 30px 20px;
            }
            
            .slide h1 {
                font-size: 2.2em;
            }
            
            .slide h2 {
                font-size: 1.8em;
            }
            
            .two-column {
                flex-direction: column;
            }
            
            .chart-container {
                width: 95%;
                height: 50%;
            }
        }
    </style>
</head>
<body>
    <div class="presentation-container">
        {% for slide in slides %}
        <div class="slide {{ slide.layout }}-layout {% if loop.first %}active{% endif %}" data-slide="{{ loop.index0 }}">
            {% if slide.type == 'title' %}
                <div class="title-slide">
                    <h1>{{ slide.content.title }}</h1>
                    {% if slide.content.subtitle %}
                        <div class="subtitle">{{ slide.content.subtitle }}</div>
                    {% endif %}
                    {% if slide.content.author %}
                        <div class="author">{{ slide.content.author }}</div>
                    {% endif %}
                    {% if slide.content.date %}
                        <div class="author">{{ slide.content.date }}</div>
                    {% endif %}
                </div>
            {% elif slide.type == 'content' %}
                <h2>{{ slide.content.title }}</h2>
                {% if slide.layout == 'image-right' %}
                    <div class="two-column">
                        <div class="column">
                            {% for item in slide.content.content %}
                                <p>{{ item }}</p>
                            {% endfor %}
                        </div>
                        <div class="column">
                            {% if slide.content.image_url %}
                                <div class="image-container">
                                    <img src="{{ slide.content.image_url }}" alt="Slide image">
                                </div>
                            {% endif %}
                        </div>
                    </div>
                {% else %}
                    {% for item in slide.content.content %}
                        {% if item is string %}
                            <p>{{ item }}</p>
                        {% else %}
                            <ul>
                                {% for list_item in item %}
                                    <li>{{ list_item }}</li>
                                {% endfor %}
                            </ul>
                        {% endif %}
                    {% endfor %}
                {% endif %}
            {% elif slide.type == 'chart' %}
                <h2>{{ slide.content.title }}</h2>
                <div class="chart-container">
                    <canvas id="{{ slide.content.chart_data.id }}"></canvas>
                </div>
            {% elif slide.type == 'comparison' %}
                <h2>{{ slide.content.title }}</h2>
                <div class="two-column">
                    <div class="column">
                        <h3>{{ slide.content.left.title }}</h3>
                        {% for item in slide.content.left.items %}
                            <p>{{ item }}</p>
                        {% endfor %}
                    </div>
                    <div class="column">
                        <h3>{{ slide.content.right.title }}</h3>
                        {% for item in slide.content.right.items %}
                            <p>{{ item }}</p>
                        {% endfor %}
                    </div>
                </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    
    {% if include_navigation %}
    <div class="navigation">
        <button class="nav-btn" id="prevBtn" onclick="changeSlide(-1)">Previous</button>
        <button class="nav-btn" id="nextBtn" onclick="changeSlide(1)">Next</button>
    </div>
    
    <div class="slide-counter">
        <span id="currentSlide">1</span> / <span id="totalSlides">{{ slides|length }}</span>
    </div>
    {% endif %}
    
    <script>
        let currentSlideIndex = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.remove('active', 'prev');
                if (i === index) {
                    slide.classList.add('active');
                } else if (i < index) {
                    slide.classList.add('prev');
                }
            });
            
            document.getElementById('currentSlide').textContent = index + 1;
            document.getElementById('prevBtn').disabled = index === 0;
            document.getElementById('nextBtn').disabled = index === totalSlides - 1;
        }
        
        function changeSlide(direction) {
            const newIndex = currentSlideIndex + direction;
            if (newIndex >= 0 && newIndex < totalSlides) {
                currentSlideIndex = newIndex;
                showSlide(currentSlideIndex);
            }
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') changeSlide(-1);
            if (e.key === 'ArrowRight') changeSlide(1);
        });
        
        // Initialize charts
        {% for slide in slides %}
        {% if slide.type == 'chart' %}
        const ctx{{ loop.index }} = document.getElementById('{{ slide.content.chart_data.id }}').getContext('2d');
        new Chart(ctx{{ loop.index }}, {
            type: '{{ slide.content.chart_data.type }}',
            data: {{ slide.content.chart_data.data | tojson }},
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                ...{{ slide.content.chart_data.config | tojson }}
            }
        });
        {% endif %}
        {% endfor %}
        
        // Initialize presentation
        showSlide(0);
        
        // GSAP animations
        gsap.from('.slide.active h1, .slide.active h2', {
            duration: 1,
            y: 50,
            opacity: 0,
            ease: "power2.out"
        });
    </script>
</body>
</html>
        '''

class ExcelDashboardGenerator(BaseContentGenerator):
    """
    Excel Dashboard Generator with Live Data Connections
    Creates professional Excel files with charts and conditional formatting
    """
    
    def __init__(self, config: ContentConfig):
        super().__init__(config)
        self.workbook_data = {}
        self.charts = []
        self.conditional_formats = []
    
    def add_worksheet(self, name: str, data: pd.DataFrame, 
                     chart_configs: List[Dict] = None) -> str:
        """Add worksheet with data and optional charts"""
        worksheet_id = self.generate_id()
        
        self.workbook_data[name] = {
            "id": worksheet_id,
            "data": data,
            "charts": chart_configs or [],
            "conditional_formats": []
        }
        
        return worksheet_id
    
    def add_chart(self, worksheet_name: str, chart_type: str, 
                 data_range: str, chart_config: Dict = None) -> str:
        """Add chart to worksheet"""
        chart_id = self.generate_id()
        
        chart = {
            "id": chart_id,
            "type": chart_type,
            "data_range": data_range,
            "config": chart_config or {},
            "worksheet": worksheet_name
        }
        
        if worksheet_name in self.workbook_data:
            self.workbook_data[worksheet_name]["charts"].append(chart)
        
        return chart_id
    
    def add_conditional_formatting(self, worksheet_name: str, cell_range: str, 
                                 format_type: str, format_config: Dict) -> str:
        """Add conditional formatting to worksheet"""
        format_id = self.generate_id()
        
        conditional_format = {
            "id": format_id,
            "range": cell_range,
            "type": format_type,
            "config": format_config
        }
        
        if worksheet_name in self.workbook_data:
            self.workbook_data[worksheet_name]["conditional_formats"].append(conditional_format)
        
        return format_id
    
    def generate_excel(self, output_path: str) -> bool:
        """Generate Excel file with all worksheets and formatting"""
        try:
            import openpyxl
            from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart
            from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, IconSetRule
            from openpyxl.utils.dataframe import dataframe_to_rows
            from openpyxl.styles import PatternFill, Font, Alignment
            
            workbook = openpyxl.Workbook()
            
            # Remove default sheet
            workbook.remove(workbook.active)
            
            for sheet_name, sheet_data in self.workbook_data.items():
                worksheet = workbook.create_sheet(title=sheet_name)
                
                # Add data
                df = sheet_data["data"]
                for r in dataframe_to_rows(df, index=False, header=True):
                    worksheet.append(r)
                
                # Format headers
                for cell in worksheet[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center")
                
                # Add charts
                for chart_config in sheet_data["charts"]:
                    chart = self._create_chart(chart_config, worksheet)
                    if chart:
                        worksheet.add_chart(chart, chart_config.get("position", "H2"))
                
                # Add conditional formatting
                for cf in sheet_data["conditional_formats"]:
                    self._apply_conditional_formatting(worksheet, cf)
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            workbook.save(output_path)
            self.logger.info(f"Excel dashboard saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating Excel file: {e}")
            return False
    
    def _create_chart(self, chart_config: Dict, worksheet) -> Any:
        """Create chart based on configuration"""
        try:
            import openpyxl.chart as charts
            
            chart_type = chart_config["type"].lower()
            
            if chart_type == "bar":
                chart = charts.BarChart()
            elif chart_type == "line":
                chart = charts.LineChart()
            elif chart_type == "pie":
                chart = charts.PieChart()
            elif chart_type == "scatter":
                chart = charts.ScatterChart()
            else:
                return None
            
            # Configure chart
            chart.title = chart_config.get("title", "Chart")
            chart.x_axis.title = chart_config.get("x_title", "X Axis")
            chart.y_axis.title = chart_config.get("y_title", "Y Axis")
            
            # Add data
            data_range = chart_config["data_range"]
            chart.add_data(worksheet[data_range], titles_from_data=True)
            
            return chart
            
        except Exception as e:
            self.logger.error(f"Error creating chart: {e}")
            return None
    
    def _apply_conditional_formatting(self, worksheet, cf_config: Dict):
        """Apply conditional formatting to worksheet"""
        try:
            from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, IconSetRule
            
            cell_range = cf_config["range"]
            format_type = cf_config["type"]
            config = cf_config["config"]
            
            if format_type == "color_scale":
                rule = ColorScaleRule(
                    start_type=config.get("start_type", "min"),
                    start_color=config.get("start_color", "FF0000"),
                    end_type=config.get("end_type", "max"),
                    end_color=config.get("end_color", "00FF00")
                )
            elif format_type == "data_bar":
                rule = DataBarRule(
                    start_type=config.get("start_type", "min"),
                    end_type=config.get("end_type", "max"),
                    color=config.get("color", "0066CC")
                )
            elif format_type == "icon_set":
                rule = IconSetRule(
                    icon_style=config.get("icon_style", "3TrafficLights1"),
                    type=config.get("type", "percent")
                )
            else:
                return
            
            worksheet.conditional_formatting.add(cell_range, rule)
            
        except Exception as e:
            self.logger.error(f"Error applying conditional formatting: {e}")

class WordDocumentGenerator(BaseContentGenerator):
    """
    Word Document Generator with Complex Layouts
    Creates professional Word documents with tables and formatting
    """
    
    def __init__(self, config: ContentConfig):
        super().__init__(config)
        self.document_content = []
        self.styles = {}
    
    def add_heading(self, text: str, level: int = 1) -> str:
        """Add heading to document"""
        element_id = self.generate_id()
        
        self.document_content.append({
            "id": element_id,
            "type": "heading",
            "text": text,
            "level": level
        })
        
        return element_id
    
    def add_paragraph(self, text: str, style: str = "normal") -> str:
        """Add paragraph to document"""
        element_id = self.generate_id()
        
        self.document_content.append({
            "id": element_id,
            "type": "paragraph",
            "text": text,
            "style": style
        })
        
        return element_id
    
    def add_table(self, data: List[List[str]], headers: List[str] = None, 
                 style: str = "professional") -> str:
        """Add table to document"""
        element_id = self.generate_id()
        
        self.document_content.append({
            "id": element_id,
            "type": "table",
            "headers": headers,
            "data": data,
            "style": style
        })
        
        return element_id
    
    def add_list(self, items: List[str], list_type: str = "bullet") -> str:
        """Add list to document"""
        element_id = self.generate_id()
        
        self.document_content.append({
            "id": element_id,
            "type": "list",
            "items": items,
            "list_type": list_type
        })
        
        return element_id
    
    def generate_docx(self, output_path: str) -> bool:
        """Generate Word document"""
        try:
            from docx import Document
            from docx.shared import Inches, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.enum.table import WD_TABLE_ALIGNMENT
            
            doc = Document()
            
            # Set document title
            doc.core_properties.title = self.config.title
            doc.core_properties.author = self.config.author
            
            for element in self.document_content:
                if element["type"] == "heading":
                    heading = doc.add_heading(element["text"], level=element["level"])
                    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                elif element["type"] == "paragraph":
                    paragraph = doc.add_paragraph(element["text"])
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                
                elif element["type"] == "table":
                    self._add_table_to_doc(doc, element)
                
                elif element["type"] == "list":
                    self._add_list_to_doc(doc, element)
            
            doc.save(output_path)
            self.logger.info(f"Word document saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating Word document: {e}")
            return False
    
    def _add_table_to_doc(self, doc, table_element: Dict):
        """Add table to Word document"""
        try:
            from docx.shared import RGBColor
            from docx.enum.table import WD_TABLE_ALIGNMENT
            
            headers = table_element.get("headers", [])
            data = table_element["data"]
            
            # Create table
            rows = len(data) + (1 if headers else 0)
            cols = len(data[0]) if data else len(headers)
            table = doc.add_table(rows=rows, cols=cols)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Add headers
            if headers:
                header_row = table.rows[0]
                for i, header in enumerate(headers):
                    cell = header_row.cells[i]
                    cell.text = header
                    # Format header
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
                            run.font.color.rgb = RGBColor(255, 255, 255)
                    cell._element.get_or_add_tcPr().append(
                        cell._element.xpath('.//w:shd')[0] if cell._element.xpath('.//w:shd') 
                        else cell._element._new_child('w:shd')
                    )
            
            # Add data
            start_row = 1 if headers else 0
            for i, row_data in enumerate(data):
                row = table.rows[start_row + i]
                for j, cell_data in enumerate(row_data):
                    row.cells[j].text = str(cell_data)
            
            # Apply table style
            table.style = 'Table Grid'
            
        except Exception as e:
            self.logger.error(f"Error adding table to document: {e}")
    
    def _add_list_to_doc(self, doc, list_element: Dict):
        """Add list to Word document"""
        try:
            items = list_element["items"]
            list_type = list_element["list_type"]
            
            for item in items:
                if list_type == "bullet":
                    doc.add_paragraph(item, style='List Bullet')
                elif list_type == "number":
                    doc.add_paragraph(item, style='List Number')
                else:
                    doc.add_paragraph(f"• {item}")
                    
        except Exception as e:
            self.logger.error(f"Error adding list to document: {e}")

# Example usage
if __name__ == "__main__":
    # Example presentation generation
    config = ContentConfig(
        title="AI in Business",
        author="AI Assistant",
        theme="professional"
    )
    
    presentation = PresentationGenerator(config)
    presentation.add_title_slide("AI in Business", "Transforming the Future", "AI Assistant")
    presentation.add_content_slide("Benefits", ["Increased efficiency", "Better decision making", "Cost reduction"])
    
    # Generate chart data
    chart_data = {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{
            "label": "Revenue",
            "data": [100, 150, 200, 250],
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "borderColor": "rgba(54, 162, 235, 1)"
        }]
    }
    
    presentation.add_chart_slide("Revenue Growth", "line", chart_data)
    
    html_output = presentation.generate_html("presentation.html")
    print("Presentation generated successfully!")
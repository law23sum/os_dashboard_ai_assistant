"""
Specialized Intelligence - Quality Assurance Systems
Automated content validation, accessibility checking, and professional formatting
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import asyncio
import hashlib
import tempfile
import subprocess

import requests
import pandas as pd
from bs4 import BeautifulSoup


@dataclass
class ValidationRule:
    """Represents a validation rule"""

    name: str
    description: str
    rule_type: str  # 'regex', 'function', 'api', 'structure'
    pattern: str = None
    function: callable = None
    severity: str = "error"  # 'error', 'warning', 'info'
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of a validation check"""

    rule_name: str
    passed: bool
    message: str
    severity: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentValidator:
    """
    Advanced content validation system with multiple validation types
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_rules = {}
        self.custom_validators = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default validation rules"""

        # HTML validation rules
        self.add_rule(
            ValidationRule(
                name="html_structure",
                description="Check basic HTML structure",
                rule_type="function",
                function=self._validate_html_structure,
            )
        )

        self.add_rule(
            ValidationRule(
                name="accessibility_alt_text",
                description="Check for alt text on images",
                rule_type="function",
                function=self._validate_alt_text,
            )
        )

        self.add_rule(
            ValidationRule(
                name="element_overflow",
                description="Check for element overflow",
                rule_type="function",
                function=self._validate_element_overflow,
            )
        )

        # Content validation rules
        self.add_rule(
            ValidationRule(
                name="spelling_grammar",
                description="Check spelling and grammar",
                rule_type="function",
                function=self._validate_spelling_grammar,
            )
        )

        self.add_rule(
            ValidationRule(
                name="professional_formatting",
                description="Check professional formatting standards",
                rule_type="function",
                function=self._validate_professional_formatting,
            )
        )

        # Data validation rules
        self.add_rule(
            ValidationRule(
                name="data_consistency",
                description="Check data consistency",
                rule_type="function",
                function=self._validate_data_consistency,
            )
        )

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.validation_rules[rule.name] = rule
        self.logger.info(f"Added validation rule: {rule.name}")

    def remove_rule(self, rule_name: str):
        """Remove a validation rule"""
        if rule_name in self.validation_rules:
            del self.validation_rules[rule_name]
            self.logger.info(f"Removed validation rule: {rule_name}")

    def validate_content(
        self, content: str, content_type: str = "html", rules: List[str] = None
    ) -> List[ValidationResult]:
        """
        Validate content against specified rules
        """
        results = []

        # Use all rules if none specified
        if rules is None:
            rules = list(self.validation_rules.keys())

        for rule_name in rules:
            if rule_name not in self.validation_rules:
                continue

            rule = self.validation_rules[rule_name]

            try:
                if rule.rule_type == "regex":
                    result = self._validate_regex(content, rule)
                elif rule.rule_type == "function":
                    result = rule.function(content, content_type)
                elif rule.rule_type == "api":
                    result = self._validate_api(content, rule)
                else:
                    continue

                if isinstance(result, list):
                    results.extend(result)
                else:
                    results.append(result)

            except Exception as e:
                self.logger.error(f"Error validating rule {rule_name}: {e}")
                results.append(
                    ValidationResult(
                        rule_name=rule_name,
                        passed=False,
                        message=f"Validation error: {str(e)}",
                        severity="error",
                    )
                )

        return results

    def _validate_regex(self, content: str, rule: ValidationRule) -> ValidationResult:
        """Validate content using regex pattern"""
        if not rule.pattern:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                message="No pattern specified for regex rule",
                severity="error",
            )

        matches = re.finditer(rule.pattern, content, re.MULTILINE)
        match_count = len(list(matches))

        # Determine if validation passed based on rule metadata
        expected_matches = rule.metadata.get("expected_matches", 0)
        min_matches = rule.metadata.get("min_matches", 0)
        max_matches = rule.metadata.get("max_matches", float("inf"))

        passed = min_matches <= match_count <= max_matches
        if expected_matches > 0:
            passed = match_count == expected_matches

        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            message=f"Found {match_count} matches for pattern",
            severity=rule.severity,
        )

    def _validate_html_structure(
        self, content: str, content_type: str
    ) -> List[ValidationResult]:
        """Validate HTML structure"""
        results = []

        if content_type != "html":
            return results

        try:
            soup = BeautifulSoup(content, "html.parser")

            # Check for DOCTYPE
            if not content.strip().startswith("<!DOCTYPE"):
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=False,
                        message="Missing DOCTYPE declaration",
                        severity="warning",
                        suggestion="Add <!DOCTYPE html> at the beginning",
                    )
                )

            # Check for html tag
            if not soup.find("html"):
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=False,
                        message="Missing <html> tag",
                        severity="error",
                    )
                )

            # Check for head tag
            if not soup.find("head"):
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=False,
                        message="Missing <head> tag",
                        severity="error",
                    )
                )

            # Check for title tag
            if not soup.find("title"):
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=False,
                        message="Missing <title> tag",
                        severity="warning",
                        suggestion="Add a descriptive title",
                    )
                )

            # Check for body tag
            if not soup.find("body"):
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=False,
                        message="Missing <body> tag",
                        severity="error",
                    )
                )

            # Check for unclosed tags
            unclosed_tags = self._find_unclosed_tags(content)
            for tag in unclosed_tags:
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=False,
                        message=f"Unclosed tag: {tag}",
                        severity="error",
                        suggestion=f"Close the {tag} tag properly",
                    )
                )

            if not results:
                results.append(
                    ValidationResult(
                        rule_name="html_structure",
                        passed=True,
                        message="HTML structure is valid",
                        severity="info",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    rule_name="html_structure",
                    passed=False,
                    message=f"HTML parsing error: {str(e)}",
                    severity="error",
                )
            )

        return results

    def _validate_alt_text(
        self, content: str, content_type: str
    ) -> List[ValidationResult]:
        """Validate alt text for images"""
        results = []

        if content_type != "html":
            return results

        try:
            soup = BeautifulSoup(content, "html.parser")
            images = soup.find_all("img")

            missing_alt = []
            empty_alt = []

            for img in images:
                src = img.get("src", "unknown")
                alt = img.get("alt")

                if alt is None:
                    missing_alt.append(src)
                elif not alt.strip():
                    empty_alt.append(src)

            if missing_alt:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_alt_text",
                        passed=False,
                        message=f"Images missing alt text: {', '.join(missing_alt[:3])}{'...' if len(missing_alt) > 3 else ''}",
                        severity="error",
                        suggestion="Add descriptive alt text to all images",
                        metadata={"missing_alt_count": len(missing_alt)},
                    )
                )

            if empty_alt:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_alt_text",
                        passed=False,
                        message=f"Images with empty alt text: {len(empty_alt)}",
                        severity="warning",
                        suggestion="Provide meaningful alt text or use alt='' for decorative images",
                    )
                )

            if not missing_alt and not empty_alt and images:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_alt_text",
                        passed=True,
                        message=f"All {len(images)} images have alt text",
                        severity="info",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    rule_name="accessibility_alt_text",
                    passed=False,
                    message=f"Alt text validation error: {str(e)}",
                    severity="error",
                )
            )

        return results

    def _validate_element_overflow(
        self, content: str, content_type: str
    ) -> List[ValidationResult]:
        """Validate element overflow using headless browser simulation"""
        results = []

        if content_type != "html":
            return results

        try:
            # Simulate overflow detection (in real implementation, would use browser automation)
            soup = BeautifulSoup(content, "html.parser")

            # Check for potential overflow indicators
            overflow_indicators = [
                "width: 100vw",
                "height: 100vh",
                "position: fixed",
                "position: absolute",
            ]

            style_content = ""
            style_tags = soup.find_all("style")
            for style in style_tags:
                style_content += style.get_text()

            # Check inline styles
            elements_with_styles = soup.find_all(attrs={"style": True})
            for element in elements_with_styles:
                style_content += element.get("style", "")

            potential_overflow = False
            for indicator in overflow_indicators:
                if indicator in style_content:
                    potential_overflow = True
                    break

            # Check for large fixed dimensions
            large_dimension_pattern = r"(width|height):\s*(\d{4,}px|\d{3,}vw|\d{3,}vh)"
            if re.search(large_dimension_pattern, style_content):
                potential_overflow = True

            if potential_overflow:
                results.append(
                    ValidationResult(
                        rule_name="element_overflow",
                        passed=False,
                        message="Potential element overflow detected",
                        severity="warning",
                        suggestion="Check element dimensions and positioning",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        rule_name="element_overflow",
                        passed=True,
                        message="No obvious overflow issues detected",
                        severity="info",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    rule_name="element_overflow",
                    passed=False,
                    message=f"Overflow validation error: {str(e)}",
                    severity="error",
                )
            )

        return results

    def _validate_spelling_grammar(
        self, content: str, content_type: str
    ) -> ValidationResult:
        """Validate spelling and grammar (simplified implementation)"""
        try:
            # Extract text content
            if content_type == "html":
                soup = BeautifulSoup(content, "html.parser")
                text_content = soup.get_text()
            else:
                text_content = content

            # Simple spelling check (in real implementation, would use proper spell checker)
            common_misspellings = {
                "teh": "the",
                "recieve": "receive",
                "seperate": "separate",
                "occured": "occurred",
                "definately": "definitely",
            }

            issues_found = []
            words = re.findall(r"\b\w+\b", text_content.lower())

            for word in words:
                if word in common_misspellings:
                    issues_found.append(
                        f"'{word}' should be '{common_misspellings[word]}'"
                    )

            if issues_found:
                return ValidationResult(
                    rule_name="spelling_grammar",
                    passed=False,
                    message=f"Spelling issues found: {', '.join(issues_found[:3])}{'...' if len(issues_found) > 3 else ''}",
                    severity="warning",
                    suggestion="Review and correct spelling errors",
                    metadata={"issues_count": len(issues_found)},
                )
            else:
                return ValidationResult(
                    rule_name="spelling_grammar",
                    passed=True,
                    message="No obvious spelling issues detected",
                    severity="info",
                )

        except Exception as e:
            return ValidationResult(
                rule_name="spelling_grammar",
                passed=False,
                message=f"Spelling validation error: {str(e)}",
                severity="error",
            )

    def _validate_professional_formatting(
        self, content: str, content_type: str
    ) -> List[ValidationResult]:
        """Validate professional formatting standards"""
        results = []

        try:
            if content_type == "html":
                soup = BeautifulSoup(content, "html.parser")

                # Check for consistent heading hierarchy
                headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
                if headings:
                    heading_levels = [int(h.name[1]) for h in headings]

                    # Check for skipped heading levels
                    for i in range(1, len(heading_levels)):
                        if heading_levels[i] - heading_levels[i - 1] > 1:
                            results.append(
                                ValidationResult(
                                    rule_name="professional_formatting",
                                    passed=False,
                                    message="Heading hierarchy skips levels",
                                    severity="warning",
                                    suggestion="Use consecutive heading levels (h1, h2, h3...)",
                                )
                            )
                            break

                # Check for proper paragraph structure
                paragraphs = soup.find_all("p")
                short_paragraphs = [
                    p for p in paragraphs if len(p.get_text().strip()) < 20
                ]

                if len(short_paragraphs) > len(paragraphs) * 0.5:
                    results.append(
                        ValidationResult(
                            rule_name="professional_formatting",
                            passed=False,
                            message="Many paragraphs are very short",
                            severity="warning",
                            suggestion="Consider combining short paragraphs for better readability",
                        )
                    )

                # Check for consistent spacing
                style_content = ""
                style_tags = soup.find_all("style")
                for style in style_tags:
                    style_content += style.get_text()

                # Look for inconsistent margin/padding values
                margin_pattern = r"margin[^:]*:\s*(\d+(?:\.\d+)?(?:px|em|rem))"
                margins = re.findall(margin_pattern, style_content)

                if len(set(margins)) > 5:  # Too many different margin values
                    results.append(
                        ValidationResult(
                            rule_name="professional_formatting",
                            passed=False,
                            message="Inconsistent spacing values detected",
                            severity="warning",
                            suggestion="Use consistent spacing values throughout the document",
                        )
                    )

            if not results:
                results.append(
                    ValidationResult(
                        rule_name="professional_formatting",
                        passed=True,
                        message="Professional formatting standards met",
                        severity="info",
                    )
                )

        except Exception as e:
            results.append(
                ValidationResult(
                    rule_name="professional_formatting",
                    passed=False,
                    message=f"Formatting validation error: {str(e)}",
                    severity="error",
                )
            )

        return results

    def _validate_data_consistency(
        self, content: str, content_type: str
    ) -> ValidationResult:
        """Validate data consistency"""
        try:
            if content_type == "json":
                data = json.loads(content)

                # Check for consistent data types
                if isinstance(data, list) and data:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        keys = set(first_item.keys())

                        inconsistent_items = []
                        for i, item in enumerate(data[1:], 1):
                            if not isinstance(item, dict) or set(item.keys()) != keys:
                                inconsistent_items.append(i)

                        if inconsistent_items:
                            return ValidationResult(
                                rule_name="data_consistency",
                                passed=False,
                                message=f"Inconsistent data structure in items: {inconsistent_items[:5]}",
                                severity="warning",
                                suggestion="Ensure all data items have the same structure",
                            )

            return ValidationResult(
                rule_name="data_consistency",
                passed=True,
                message="Data consistency check passed",
                severity="info",
            )

        except Exception as e:
            return ValidationResult(
                rule_name="data_consistency",
                passed=False,
                message=f"Data consistency validation error: {str(e)}",
                severity="error",
            )

    def _find_unclosed_tags(self, html_content: str) -> List[str]:
        """Find unclosed HTML tags"""
        # Simplified implementation - in practice, would use proper HTML parser
        self_closing_tags = {
            "img",
            "br",
            "hr",
            "input",
            "meta",
            "link",
            "area",
            "base",
            "col",
            "embed",
            "source",
            "track",
            "wbr",
        }

        # Find all opening and closing tags
        opening_tags = re.findall(r"<(\w+)(?:\s[^>]*)?>(?!</)", html_content)
        closing_tags = re.findall(r"</(\w+)>", html_content)

        # Filter out self-closing tags
        opening_tags = [
            tag for tag in opening_tags if tag.lower() not in self_closing_tags
        ]

        # Count occurrences
        from collections import Counter

        opening_count = Counter(opening_tags)
        closing_count = Counter(closing_tags)

        unclosed = []
        for tag, count in opening_count.items():
            if closing_count.get(tag, 0) < count:
                unclosed.append(tag)

        return unclosed

    def _validate_api(self, content: str, rule: ValidationRule) -> ValidationResult:
        """Validate content using external API"""
        # Placeholder for API validation
        return ValidationResult(
            rule_name=rule.name,
            passed=True,
            message="API validation not implemented",
            severity="info",
        )


class BatchValidator:
    """
    Batch validation system for processing multiple files
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.validator = ContentValidator()
        self.logger = logging.getLogger(__name__)

    def validate_files(
        self,
        file_paths: List[str],
        content_types: Dict[str, str] = None,
        rules: List[str] = None,
    ) -> Dict[str, List[ValidationResult]]:
        """
        Validate multiple files in batch
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {}

            for file_path in file_paths:
                content_type = self._detect_content_type(file_path, content_types)
                future = executor.submit(
                    self._validate_single_file, file_path, content_type, rules
                )
                future_to_file[future] = file_path

            for future in future_to_file:
                file_path = future_to_file[future]
                try:
                    results[file_path] = future.result()
                except Exception as e:
                    self.logger.error(f"Error validating {file_path}: {e}")
                    results[file_path] = [
                        ValidationResult(
                            rule_name="batch_validation",
                            passed=False,
                            message=f"Validation failed: {str(e)}",
                            severity="error",
                        )
                    ]

        return results

    def _validate_single_file(
        self, file_path: str, content_type: str, rules: List[str] = None
    ) -> List[ValidationResult]:
        """Validate a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self.validator.validate_content(content, content_type, rules)

        except Exception as e:
            return [
                ValidationResult(
                    rule_name="file_validation",
                    passed=False,
                    message=f"Error reading file: {str(e)}",
                    severity="error",
                )
            ]

    def _detect_content_type(
        self, file_path: str, content_types: Dict[str, str] = None
    ) -> str:
        """Detect content type from file extension"""
        if content_types and file_path in content_types:
            return content_types[file_path]

        extension = Path(file_path).suffix.lower()

        type_mapping = {
            ".html": "html",
            ".htm": "html",
            ".json": "json",
            ".txt": "text",
            ".md": "markdown",
            ".css": "css",
            ".js": "javascript",
        }

        return type_mapping.get(extension, "text")

    def generate_report(
        self,
        validation_results: Dict[str, List[ValidationResult]],
        output_path: str = None,
    ) -> str:
        """Generate validation report"""
        report_lines = []
        report_lines.append("# Validation Report")
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # Summary
        total_files = len(validation_results)
        total_issues = sum(
            len([r for r in results if not r.passed])
            for results in validation_results.values()
        )

        report_lines.append("## Summary")
        report_lines.append(f"- Files validated: {total_files}")
        report_lines.append(f"- Total issues found: {total_issues}")
        report_lines.append("")

        # Detailed results
        for file_path, results in validation_results.items():
            report_lines.append(f"## {file_path}")

            errors = [r for r in results if r.severity == "error" and not r.passed]
            warnings = [r for r in results if r.severity == "warning" and not r.passed]
            info = [r for r in results if r.severity == "info"]

            if errors:
                report_lines.append("### Errors")
                for result in errors:
                    report_lines.append(f"- **{result.rule_name}**: {result.message}")
                    if result.suggestion:
                        report_lines.append(f"  - Suggestion: {result.suggestion}")
                report_lines.append("")

            if warnings:
                report_lines.append("### Warnings")
                for result in warnings:
                    report_lines.append(f"- **{result.rule_name}**: {result.message}")
                    if result.suggestion:
                        report_lines.append(f"  - Suggestion: {result.suggestion}")
                report_lines.append("")

            if not errors and not warnings:
                report_lines.append("✅ No issues found")
                report_lines.append("")

        report_content = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            self.logger.info(f"Validation report saved to {output_path}")

        return report_content


class AccessibilityChecker:
    """
    Specialized accessibility checker for web content
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_accessibility(self, html_content: str) -> List[ValidationResult]:
        """
        Comprehensive accessibility check
        """
        results = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Check for alt text on images
        results.extend(self._check_image_alt_text(soup))

        # Check for proper heading structure
        results.extend(self._check_heading_structure(soup))

        # Check for form labels
        results.extend(self._check_form_labels(soup))

        # Check for color contrast (simplified)
        results.extend(self._check_color_contrast(soup))

        # Check for keyboard navigation
        results.extend(self._check_keyboard_navigation(soup))

        return results

    def _check_image_alt_text(self, soup: BeautifulSoup) -> List[ValidationResult]:
        """Check image alt text accessibility"""
        results = []
        images = soup.find_all("img")

        for img in images:
            src = img.get("src", "unknown")
            alt = img.get("alt")

            if alt is None:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_image_alt",
                        passed=False,
                        message=f"Image missing alt attribute: {src}",
                        severity="error",
                        suggestion="Add alt attribute with descriptive text",
                    )
                )
            elif len(alt.strip()) == 0:
                # Empty alt is acceptable for decorative images
                results.append(
                    ValidationResult(
                        rule_name="accessibility_image_alt",
                        passed=True,
                        message=f"Image has empty alt (decorative): {src}",
                        severity="info",
                    )
                )
            elif len(alt) > 125:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_image_alt",
                        passed=False,
                        message=f"Alt text too long ({len(alt)} chars): {src}",
                        severity="warning",
                        suggestion="Keep alt text under 125 characters",
                    )
                )

        return results

    def _check_heading_structure(self, soup: BeautifulSoup) -> List[ValidationResult]:
        """Check heading structure for accessibility"""
        results = []
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        if not headings:
            results.append(
                ValidationResult(
                    rule_name="accessibility_headings",
                    passed=False,
                    message="No headings found",
                    severity="warning",
                    suggestion="Add headings to structure content",
                )
            )
            return results

        # Check for h1
        h1_count = len(soup.find_all("h1"))
        if h1_count == 0:
            results.append(
                ValidationResult(
                    rule_name="accessibility_headings",
                    passed=False,
                    message="No h1 heading found",
                    severity="error",
                    suggestion="Add one h1 heading as the main page title",
                )
            )
        elif h1_count > 1:
            results.append(
                ValidationResult(
                    rule_name="accessibility_headings",
                    passed=False,
                    message=f"Multiple h1 headings found ({h1_count})",
                    severity="warning",
                    suggestion="Use only one h1 heading per page",
                )
            )

        # Check heading hierarchy
        heading_levels = [int(h.name[1]) for h in headings]
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i - 1] > 1:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_headings",
                        passed=False,
                        message="Heading hierarchy skips levels",
                        severity="warning",
                        suggestion="Use consecutive heading levels",
                    )
                )
                break

        return results

    def _check_form_labels(self, soup: BeautifulSoup) -> List[ValidationResult]:
        """Check form label accessibility"""
        results = []

        # Find form inputs
        inputs = soup.find_all(["input", "select", "textarea"])
        inputs = [
            inp
            for inp in inputs
            if inp.get("type") not in ["hidden", "submit", "button"]
        ]

        for inp in inputs:
            input_id = inp.get("id")
            input_type = inp.get("type", "text")

            # Check for associated label
            label = None
            if input_id:
                label = soup.find("label", attrs={"for": input_id})

            # Check for wrapping label
            if not label:
                parent = inp.parent
                if parent and parent.name == "label":
                    label = parent

            if not label:
                results.append(
                    ValidationResult(
                        rule_name="accessibility_form_labels",
                        passed=False,
                        message=f"Input missing label: {input_type}",
                        severity="error",
                        suggestion="Associate input with a label element",
                    )
                )

        return results

    def _check_color_contrast(self, soup: BeautifulSoup) -> List[ValidationResult]:
        """Check color contrast (simplified implementation)"""
        results = []

        # This is a simplified check - real implementation would calculate actual contrast ratios
        style_content = ""
        style_tags = soup.find_all("style")
        for style in style_tags:
            style_content += style.get_text()

        # Look for potential low contrast combinations
        low_contrast_patterns = [
            r"color:\s*#[a-f0-9]{6}.*background.*#[a-f0-9]{6}",
            r"background.*#[a-f0-9]{6}.*color:\s*#[a-f0-9]{6}",
        ]

        for pattern in low_contrast_patterns:
            if re.search(pattern, style_content, re.IGNORECASE):
                results.append(
                    ValidationResult(
                        rule_name="accessibility_color_contrast",
                        passed=False,
                        message="Potential color contrast issue detected",
                        severity="warning",
                        suggestion="Verify color contrast meets WCAG guidelines (4.5:1 for normal text)",
                    )
                )
                break

        return results

    def _check_keyboard_navigation(self, soup: BeautifulSoup) -> List[ValidationResult]:
        """Check keyboard navigation accessibility"""
        results = []

        # Check for interactive elements without proper focus handling
        interactive_elements = soup.find_all(
            ["a", "button", "input", "select", "textarea"]
        )

        elements_without_focus = []
        for element in interactive_elements:
            # Check if element has tabindex or is naturally focusable
            if element.name in ["input", "select", "textarea", "button"]:
                continue  # Naturally focusable

            if element.name == "a" and element.get("href"):
                continue  # Links with href are focusable

            if element.get("tabindex") is not None:
                continue  # Has explicit tabindex

            elements_without_focus.append(element.name)

        if elements_without_focus:
            results.append(
                ValidationResult(
                    rule_name="accessibility_keyboard_navigation",
                    passed=False,
                    message=f"Interactive elements may not be keyboard accessible: {set(elements_without_focus)}",
                    severity="warning",
                    suggestion="Ensure all interactive elements are keyboard accessible",
                )
            )

        return results


# Example usage
if __name__ == "__main__":
    # Example HTML content validation
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Main Title</h1>
        <img src="test.jpg" alt="Test image">
        <p>This is a test paragraph.</p>
    </body>
    </html>
    """

    validator = ContentValidator()
    results = validator.validate_content(html_content, "html")

    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.rule_name}: {result.message}")

    # Accessibility check
    accessibility_checker = AccessibilityChecker()
    accessibility_results = accessibility_checker.check_accessibility(html_content)

    print("\nAccessibility Results:")
    for result in accessibility_results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.rule_name}: {result.message}")

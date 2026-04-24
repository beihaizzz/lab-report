"""Tests for parse_pdf.py."""
import json
from pathlib import Path

import pytest

from scripts.parse_pdf import parse_pdf


class TestParseNormalPdf:
    def test_parse_normal_pdf(self, sample_pdf):
        result = parse_pdf(sample_pdf)
        assert result["page_count"] > 0, "page_count should be > 0"
        assert result["is_scanned"] is False, "normal PDF should not be scanned"
        assert result["markdown"], "markdown should have content"
        assert "error" not in result, f"unexpected error: {result.get('error')}"


class TestDetectScannedPdf:
    def test_detect_scanned_pdf(self, sample_scanned_pdf):
        result = parse_pdf(sample_scanned_pdf)
        assert result["is_scanned"] is True, "should detect as scanned"
        assert result["warning"] == "SCANNED_PDF_DETECTED", "should set warning"


class TestJsonOutput:
    def test_json_output(self, sample_pdf):
        result = parse_pdf(sample_pdf, output_format="json")
        assert "error" not in result, f"unexpected error: {result.get('error')}"
        assert "page_count" in result
        assert "markdown" in result
        assert "is_scanned" in result


class TestMarkdownOutput:
    def test_markdown_output(self, sample_pdf):
        result = parse_pdf(sample_pdf, output_format="markdown")
        assert "error" not in result, f"unexpected error: {result.get('error')}"
        assert "# " in result["markdown"] or "## " in result["markdown"], \
            "markdown output should contain headings"


class TestFileNotFound:
    def test_file_not_found(self):
        result = parse_pdf(Path("nonexistent_file.pdf"))
        assert "error" in result, "should return error for nonexistent file"

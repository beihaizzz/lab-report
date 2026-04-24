"""Tests for parse_pptx.py."""
from pathlib import Path

from scripts.parse_pptx import parse_pptx


class TestSlideCount:
    def test_slide_count(self, sample_pptx):
        result = parse_pptx(sample_pptx, output_format="json")
        assert "error" not in result, f"unexpected error: {result.get('error')}"
        assert result["slide_count"] >= 5, \
            f"expected >=5 slides, got {result['slide_count']}"


class TestJsonOutput:
    def test_json_output(self, sample_pptx):
        result = parse_pptx(sample_pptx, output_format="json")
        assert "error" not in result, f"unexpected error: {result.get('error')}"
        assert "slide_count" in result
        assert "slides" in result
        assert len(result["slides"]) == result["slide_count"]
        # At least one slide should have content
        slides_with_content = [
            s for s in result["slides"]
            if s.get("title") or s.get("content")
        ]
        assert len(slides_with_content) > 0, "at least one slide should have content"


class TestFileNotFound:
    def test_file_not_found(self):
        result = parse_pptx(Path("nonexistent_file.pptx"))
        assert "error" in result, "should return error for nonexistent file"

"""Unit tests for the PDF merge logic."""
import io

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_merger import MergeError, merge_pdfs


def make_pdf(num_pages: int) -> bytes:
    """Build an in-memory PDF with the given number of blank A4 pages."""
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=595, height=842)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def page_count(pdf_bytes: bytes) -> int:
    return len(PdfReader(io.BytesIO(pdf_bytes)).pages)


def test_merge_two_pdfs_sums_pages():
    merged = merge_pdfs([make_pdf(2), make_pdf(3)])
    assert page_count(merged) == 5


def test_merge_three_pdfs():
    merged = merge_pdfs([make_pdf(1), make_pdf(1), make_pdf(1)])
    assert page_count(merged) == 3


def test_merge_accepts_streams():
    merged = merge_pdfs([io.BytesIO(make_pdf(2)), io.BytesIO(make_pdf(2))])
    assert page_count(merged) == 4


def test_single_file_raises():
    with pytest.raises(MergeError):
        merge_pdfs([make_pdf(1)])


def test_no_files_raises():
    with pytest.raises(MergeError):
        merge_pdfs([])


def test_invalid_pdf_raises():
    with pytest.raises(MergeError):
        merge_pdfs([make_pdf(1), b"this is not a pdf"])

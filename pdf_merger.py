"""Core logic for merging PDF files.

Kept separate from the web layer so it can be unit-tested in isolation
and reused from a CLI or other front-ends if needed.
"""
from __future__ import annotations

import io
from typing import BinaryIO, Iterable, Union

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError, PdfStreamError

# Anything pypdf can read from: a file path, bytes, or an open binary stream.
PdfSource = Union[str, bytes, BinaryIO]


class MergeError(Exception):
    """Raised when one or more inputs cannot be merged into a valid PDF."""


def _as_stream(source: PdfSource) -> BinaryIO:
    """Normalise a source into a binary stream that pypdf can read."""
    if isinstance(source, bytes):
        return io.BytesIO(source)
    return source  # str path or already a file-like object


def merge_pdfs(sources: Iterable[PdfSource]) -> bytes:
    """Merge several PDFs (in the given order) into a single PDF.

    Args:
        sources: An ordered iterable of PDF sources. Each item may be a file
            path, raw ``bytes``, or an open binary stream. At least two
            sources are required.

    Returns:
        The bytes of the merged PDF document.

    Raises:
        MergeError: If fewer than two sources are given, or if any source is
            not a readable PDF.
    """
    sources = list(sources)
    if len(sources) < 2:
        raise MergeError("Sono necessari almeno 2 file PDF da unire.")

    writer = PdfWriter()
    try:
        for index, source in enumerate(sources, start=1):
            try:
                reader = PdfReader(_as_stream(source))
                if not reader.pages:
                    raise MergeError(f"Il file numero {index} non contiene pagine.")
                for page in reader.pages:
                    writer.add_page(page)
            except (PdfReadError, PdfStreamError, OSError) as exc:
                raise MergeError(
                    f"Il file numero {index} non è un PDF valido o è danneggiato."
                ) from exc

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()
    finally:
        writer.close()

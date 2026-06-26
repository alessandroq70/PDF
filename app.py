"""Flask web application that merges 2+ PDF files into one.

Run with:  python app.py
Then open http://127.0.0.1:5000 in your browser.
"""
from __future__ import annotations

import io

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from pdf_merger import MergeError, merge_pdfs

app = Flask(__name__)

# Reject very large uploads early (200 MB total). Adjust if you routinely
# merge bigger documents.
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024


@app.route("/")
def index():
    """Serve the single-page interface."""
    return render_template("index.html")


@app.route("/merge", methods=["POST"])
def merge():
    """Merge the uploaded PDFs and return the resulting file.

    Files are read from the ``files`` multipart field, in the exact order the
    browser sent them, so the front-end controls the merge order.
    """
    uploads = request.files.getlist("files")

    if len(uploads) < 2:
        return jsonify(error="Seleziona almeno 2 file PDF."), 400

    for upload in uploads:
        name = (upload.filename or "").lower()
        if not name.endswith(".pdf"):
            return jsonify(
                error=f"'{upload.filename}' non è un file PDF."
            ), 400

    streams = [io.BytesIO(upload.read()) for upload in uploads]

    try:
        merged_bytes = merge_pdfs(streams)
    except MergeError as exc:
        return jsonify(error=str(exc)), 400

    return send_file(
        io.BytesIO(merged_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="documenti-uniti.pdf",
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(_exc):
    return jsonify(error="I file caricati superano il limite di 200 MB."), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

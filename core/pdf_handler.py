import fitz  # PyMuPDF
from pathlib import Path


class PDFHandler:
    """Handles opening, saving, and basic PDF operations."""

    def __init__(self):
        self.doc: fitz.Document | None = None
        self.file_path: str | None = None
        self.modified = False

    def open(self, path: str) -> fitz.Document:
        if self.doc:
            self.close()
        self.doc = fitz.open(path)
        self.file_path = path
        self.modified = False
        return self.doc

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None
            self.file_path = None
            self.modified = False

    def save(self, path: str | None = None):
        if not self.doc:
            raise RuntimeError("Kein PDF geoeffnet")
        target = path or self.file_path
        if target == self.file_path:
            self.doc.saveIncr()
        else:
            self.doc.save(target, garbage=4, deflate=True)
        self.file_path = target
        self.modified = False

    def save_as(self, path: str):
        if not self.doc:
            raise RuntimeError("Kein PDF geoeffnet")
        self.doc.save(path, garbage=4, deflate=True)
        self.file_path = path
        self.modified = False

    def page_count(self) -> int:
        return self.doc.page_count if self.doc else 0

    def get_page(self, index: int) -> fitz.Page:
        if not self.doc:
            raise RuntimeError("Kein PDF geoeffnet")
        return self.doc[index]

    def get_page_pixmap(self, index: int, zoom: float = 1.0) -> fitz.Pixmap:
        page = self.get_page(index)
        mat = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=mat, alpha=False)

    def rotate_page(self, index: int, angle: int):
        page = self.get_page(index)
        page.set_rotation((page.rotation + angle) % 360)
        self.modified = True

    def delete_page(self, index: int):
        if not self.doc:
            raise RuntimeError("Kein PDF geoeffnet")
        self.doc.delete_page(index)
        self.modified = True

    def move_page(self, from_idx: int, to_idx: int):
        if not self.doc:
            raise RuntimeError("Kein PDF geoeffnet")
        self.doc.move_page(from_idx, to_idx)
        self.modified = True

    def insert_pages_from(self, other_path: str, at_index: int = -1):
        if not self.doc:
            raise RuntimeError("Kein PDF geoeffnet")
        other = fitz.open(other_path)
        if at_index < 0:
            at_index = self.doc.page_count
        self.doc.insert_pdf(other, start_at=at_index)
        other.close()
        self.modified = True

    def file_size(self) -> int:
        if self.file_path and Path(self.file_path).exists():
            return Path(self.file_path).stat().st_size
        return 0

    def export_page_as_image(self, index: int, path: str, zoom: float = 2.0):
        pix = self.get_page_pixmap(index, zoom)
        pix.save(path)

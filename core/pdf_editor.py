import fitz
from pathlib import Path


class PDFEditor:
    """Text and image editing operations on PDF pages."""

    @staticmethod
    def add_text(page: fitz.Page, x: float, y: float, text: str,
                 fontsize: float = 12, color: tuple = (0, 0, 0),
                 fontname: str = "helv"):
        point = fitz.Point(x, y)
        rc = page.insert_text(point, text, fontsize=fontsize,
                              fontname=fontname, color=color)
        return rc

    @staticmethod
    def redact_and_replace(page: fitz.Page, rect: fitz.Rect,
                           new_text: str, fontsize: float = 11,
                           color: tuple = (0, 0, 0)):
        page.add_redact_annot(rect, new_text, fontsize=fontsize,
                              text_color=color)
        page.apply_redactions()

    @staticmethod
    def insert_image(page: fitz.Page, rect: fitz.Rect, image_path: str):
        page.insert_image(rect, filename=image_path)

    @staticmethod
    def remove_image(page: fitz.Page, xref: int):
        """Remove an image by its xref number."""
        page.delete_image(xref)

    @staticmethod
    def get_images(page: fitz.Page) -> list:
        return page.get_images(full=True)

    @staticmethod
    def add_highlight(page: fitz.Page, rect: fitz.Rect):
        annot = page.add_highlight_annot(rect)
        return annot

    @staticmethod
    def add_comment(page: fitz.Page, point: fitz.Point, text: str):
        annot = page.add_text_annot(point, text)
        return annot

    @staticmethod
    def add_freehand(page: fitz.Page, points: list[fitz.Point],
                     color: tuple = (1, 0, 0), width: float = 2.0):
        annot = page.add_ink_annot([points])
        annot.set_border(width=width)
        annot.set_colors(stroke=color)
        annot.update()
        return annot

    @staticmethod
    def get_text_blocks(page: fitz.Page) -> list:
        return page.get_text("blocks")

    @staticmethod
    def insert_signature_image(page: fitz.Page, rect: fitz.Rect,
                               image_path: str):
        """Insert a signature image (PNG/JPG) into the page."""
        page.insert_image(rect, filename=image_path, overlay=True)

    @staticmethod
    def insert_signature_bytes(page: fitz.Page, rect: fitz.Rect,
                               image_bytes: bytes):
        """Insert a signature from raw PNG bytes into the page."""
        page.insert_image(rect, stream=image_bytes, overlay=True)

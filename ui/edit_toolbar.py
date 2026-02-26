from PyQt6.QtWidgets import (QToolBar, QColorDialog, QInputDialog,
                              QFileDialog, QMessageBox, QWidget)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import pyqtSignal
import fitz


class EditToolbar(QToolBar):
    """Toolbar for PDF editing operations."""

    text_add_requested = pyqtSignal()
    image_add_requested = pyqtSignal()
    highlight_requested = pyqtSignal()
    draw_requested = pyqtSignal()
    comment_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Bearbeiten", parent)
        self._setup_actions()

    def _setup_actions(self):
        self.act_add_text = QAction("Text einfuegen", self)
        self.act_add_text.setToolTip("Text an Position einfuegen")
        self.act_add_text.triggered.connect(self.text_add_requested)
        self.addAction(self.act_add_text)

        self.act_add_image = QAction("Bild einfuegen", self)
        self.act_add_image.setToolTip("Bild in Seite einbetten")
        self.act_add_image.triggered.connect(self.image_add_requested)
        self.addAction(self.act_add_image)

        self.addSeparator()

        self.act_highlight = QAction("Hervorheben", self)
        self.act_highlight.triggered.connect(self.highlight_requested)
        self.addAction(self.act_highlight)

        self.act_comment = QAction("Kommentar", self)
        self.act_comment.triggered.connect(self.comment_requested)
        self.addAction(self.act_comment)

        self.act_draw = QAction("Zeichnen", self)
        self.act_draw.triggered.connect(self.draw_requested)
        self.addAction(self.act_draw)

    def add_text_to_page(self, page: fitz.Page, parent_widget: QWidget):
        text, ok = QInputDialog.getMultiLineText(
            parent_widget, "Text einfuegen", "Text eingeben:")
        if not ok or not text:
            return False
        x, ok_x = QInputDialog.getDouble(
            parent_widget, "Position", "X-Position:", 50, 0, 10000, 1)
        if not ok_x:
            return False
        y, ok_y = QInputDialog.getDouble(
            parent_widget, "Position", "Y-Position:", 50, 0, 10000, 1)
        if not ok_y:
            return False
        size, ok_s = QInputDialog.getInt(
            parent_widget, "Schriftgroesse", "Groesse:", 12, 4, 200)
        if not ok_s:
            return False

        from core.pdf_editor import PDFEditor
        PDFEditor.add_text(page, x, y, text, fontsize=size)
        return True

    def add_image_to_page(self, page: fitz.Page, parent_widget: QWidget):
        path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Bild auswaehlen", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not path:
            return False
        x, ok_x = QInputDialog.getDouble(
            parent_widget, "Position", "X-Position:", 50, 0, 10000, 1)
        if not ok_x:
            return False
        y, ok_y = QInputDialog.getDouble(
            parent_widget, "Position", "Y-Position:", 50, 0, 10000, 1)
        if not ok_y:
            return False
        w, ok_w = QInputDialog.getDouble(
            parent_widget, "Groesse", "Breite:", 200, 10, 10000, 1)
        if not ok_w:
            return False
        h, ok_h = QInputDialog.getDouble(
            parent_widget, "Groesse", "Hoehe:", 200, 10, 10000, 1)
        if not ok_h:
            return False

        rect = fitz.Rect(x, y, x + w, y + h)
        from core.pdf_editor import PDFEditor
        PDFEditor.insert_image(page, rect, path)
        return True

    def add_comment_to_page(self, page: fitz.Page, parent_widget: QWidget):
        text, ok = QInputDialog.getMultiLineText(
            parent_widget, "Kommentar", "Kommentartext:")
        if not ok or not text:
            return False
        x, ok_x = QInputDialog.getDouble(
            parent_widget, "Position", "X-Position:", 50, 0, 10000, 1)
        if not ok_x:
            return False
        y, ok_y = QInputDialog.getDouble(
            parent_widget, "Position", "Y-Position:", 50, 0, 10000, 1)
        if not ok_y:
            return False

        from core.pdf_editor import PDFEditor
        PDFEditor.add_comment(page, fitz.Point(x, y), text)
        return True

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget,
                              QListWidgetItem, QAbstractItemView, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData
from PyQt6.QtGui import QPixmap, QImage, QIcon, QDrag
import fitz


class ThumbnailBar(QWidget):
    """Sidebar showing page thumbnails with drag & drop reorder."""

    page_selected = pyqtSignal(int)
    pages_reordered = pyqtSignal(int, int)  # from, to
    page_delete_requested = pyqtSignal(int)
    page_rotate_requested = pyqtSignal(int, int)  # index, angle

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 160))
        self.list_widget.setSpacing(4)
        self.list_widget.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        self.list_widget.model().rowsMoved.connect(self._on_rows_moved)
        self.list_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(
            self._show_context_menu)

        self.setFixedWidth(150)
        layout.addWidget(self.list_widget)

    def set_document(self, doc: fitz.Document):
        self.doc = doc
        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        if not self.doc:
            return
        for i in range(self.doc.page_count):
            page = self.doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2), alpha=False)
            img = QImage(pix.samples, pix.width, pix.height,
                         pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            item = QListWidgetItem(QIcon(pixmap), f"Seite {i + 1}")
            item.setSizeHint(QSize(130, 140))
            self.list_widget.addItem(item)

    def select_page(self, index: int):
        self.list_widget.blockSignals(True)
        self.list_widget.setCurrentRow(index)
        self.list_widget.blockSignals(False)

    def _on_row_changed(self, row):
        if row >= 0:
            self.page_selected.emit(row)

    def _on_rows_moved(self, parent, start, end, dest, row):
        self.pages_reordered.emit(start, row if row < start else row - 1)

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        idx = self.list_widget.row(item)
        menu = QMenu(self)
        rot_90 = menu.addAction("90° drehen")
        rot_180 = menu.addAction("180° drehen")
        rot_270 = menu.addAction("270° drehen")
        menu.addSeparator()
        delete_action = menu.addAction("Seite loeschen")

        action = menu.exec(self.list_widget.mapToGlobal(pos))
        if action == rot_90:
            self.page_rotate_requested.emit(idx, 90)
        elif action == rot_180:
            self.page_rotate_requested.emit(idx, 180)
        elif action == rot_270:
            self.page_rotate_requested.emit(idx, 270)
        elif action == delete_action:
            self.page_delete_requested.emit(idx)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QScrollArea, QPushButton, QSpinBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
import fitz


class ViewerWidget(QWidget):
    """PDF page viewer with zoom and navigation."""

    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        self._drawing = False
        self._draw_points = []
        self._annotations_overlay = []
        self._tool_mode = None  # None, "text", "draw", "highlight"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Navigation bar
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Zurueck")
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next = QPushButton("Weiter ▶")
        self.btn_next.clicked.connect(self.next_page)

        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setPrefix("Seite ")
        self.page_spin.valueChanged.connect(self._on_spin_changed)

        self.page_label = QLabel("/ 0")

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        self.zoom_label = QLabel("100%")

        nav.addWidget(self.btn_prev)
        nav.addWidget(self.page_spin)
        nav.addWidget(self.page_label)
        nav.addWidget(self.btn_next)
        nav.addStretch()
        nav.addWidget(QLabel("Zoom:"))
        nav.addWidget(self.zoom_slider)
        nav.addWidget(self.zoom_label)

        layout.addLayout(nav)

        # Scroll area for page display
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_label_img = QLabel()
        self.page_label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.page_label_img)

        layout.addWidget(self.scroll)

    def set_document(self, doc: fitz.Document):
        self.doc = doc
        self.current_page = 0
        self.page_spin.setMaximum(max(1, doc.page_count))
        self.page_label.setText(f"/ {doc.page_count}")
        self.render_page()

    def render_page(self):
        if not self.doc or self.doc.page_count == 0:
            self.page_label_img.clear()
            return
        page = self.doc[self.current_page]
        mat = fitz.Matrix(self.zoom * 1.5, self.zoom * 1.5)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(pix.samples, pix.width, pix.height,
                     pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.page_label_img.setPixmap(pixmap)
        self.page_label_img.resize(pixmap.size())
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(self.current_page + 1)
        self.page_spin.blockSignals(False)
        self.page_changed.emit(self.current_page)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        if self.doc and self.current_page < self.doc.page_count - 1:
            self.current_page += 1
            self.render_page()

    def go_to_page(self, index: int):
        if self.doc and 0 <= index < self.doc.page_count:
            self.current_page = index
            self.render_page()

    def _on_spin_changed(self, val):
        self.go_to_page(val - 1)

    def _on_zoom_changed(self, val):
        self.zoom = val / 100.0
        self.zoom_label.setText(f"{val}%")
        self.render_page()

    def refresh(self):
        self.render_page()

    def set_tool_mode(self, mode):
        self._tool_mode = mode

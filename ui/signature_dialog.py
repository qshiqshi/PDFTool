from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QFileDialog, QTabWidget, QWidget,
                              QSpinBox, QGroupBox, QFormLayout, QMessageBox,
                              QColorDialog)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import (QPainter, QPen, QColor, QPixmap, QImage,
                          QPainterPath, QFont)
import io


class SignatureCanvas(QWidget):
    """Canvas for drawing a freehand signature."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 200)
        self.setMaximumHeight(250)
        self._pen_color = QColor(0, 0, 50)
        self._pen_width = 3
        self._paths = []
        self._current_path = []
        self._drawing = False
        self.setStyleSheet("background: white; border: 2px solid #ccc; border-radius: 4px;")
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_pen_color(self, color: QColor):
        self._pen_color = color

    def set_pen_width(self, width: int):
        self._pen_width = width

    def clear(self):
        self._paths.clear()
        self._current_path.clear()
        self.update()

    def is_empty(self) -> bool:
        return len(self._paths) == 0 and len(self._current_path) == 0

    def to_pixmap(self) -> QPixmap:
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._draw_paths(painter)
        painter.end()
        return self._crop_to_content(pixmap)

    def to_bytes(self) -> bytes:
        pixmap = self.to_pixmap()
        img = pixmap.toImage()
        buf = io.BytesIO()
        ba = img.convertToFormat(QImage.Format.Format_ARGB32)
        # Save via QImage -> PNG bytes
        from PyQt6.QtCore import QBuffer, QIODevice
        qbuf = QBuffer()
        qbuf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(qbuf, "PNG")
        return bytes(qbuf.data())

    def _crop_to_content(self, pixmap: QPixmap) -> QPixmap:
        img = pixmap.toImage()
        min_x, min_y = img.width(), img.height()
        max_x, max_y = 0, 0
        for path in self._paths:
            for pt in path:
                min_x = min(min_x, pt.x() - 5)
                min_y = min(min_y, pt.y() - 5)
                max_x = max(max_x, pt.x() + 5)
                max_y = max(max_y, pt.y() + 5)
        if max_x <= min_x or max_y <= min_y:
            return pixmap
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(img.width(), max_x)
        max_y = min(img.height(), max_y)
        padding = 10
        rect = QRect(
            int(min_x - padding), int(min_y - padding),
            int(max_x - min_x + 2 * padding), int(max_y - min_y + 2 * padding)
        )
        return pixmap.copy(rect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        # Baseline hint
        y_mid = self.height() * 0.7
        painter.setPen(QPen(QColor(220, 220, 220), 1, Qt.PenStyle.DashLine))
        painter.drawLine(20, int(y_mid), self.width() - 20, int(y_mid))
        # Hint text
        if self.is_empty():
            painter.setPen(QColor(180, 180, 180))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Hier unterschreiben...")
        # Signature strokes
        self._draw_paths(painter)
        painter.end()

    def _draw_paths(self, painter: QPainter):
        pen = QPen(self._pen_color, self._pen_width,
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        for path in self._paths:
            if len(path) < 2:
                continue
            for i in range(1, len(path)):
                painter.drawLine(path[i - 1], path[i])
        if len(self._current_path) >= 2:
            for i in range(1, len(self._current_path)):
                painter.drawLine(self._current_path[i - 1],
                                 self._current_path[i])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawing = True
            self._current_path = [event.position().toPoint()]

    def mouseMoveEvent(self, event):
        if self._drawing:
            self._current_path.append(event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drawing:
            self._drawing = False
            if len(self._current_path) > 1:
                self._paths.append(self._current_path)
            self._current_path = []
            self.update()


class SignatureDialog(QDialog):
    """Dialog for creating/loading a signature and placing it on a PDF page."""

    def __init__(self, page_count: int = 1, current_page: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Digitale Unterschrift")
        self.setMinimumSize(600, 520)
        self._page_count = page_count
        self._current_page = current_page
        self._loaded_image_path = None
        self._result_pixmap = None
        self._result_mode = None  # "draw" or "image"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("Unterschrift erstellen oder laden")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 4px;")
        layout.addWidget(header)

        # Tabs: Draw / Load image
        self.tabs = QTabWidget()

        # --- Draw tab ---
        draw_tab = QWidget()
        draw_layout = QVBoxLayout(draw_tab)

        self.canvas = SignatureCanvas()
        draw_layout.addWidget(self.canvas)

        draw_btns = QHBoxLayout()
        self.btn_clear = QPushButton("Neu zeichnen")
        self.btn_clear.clicked.connect(self.canvas.clear)
        self.btn_pen_color = QPushButton("Stiftfarbe")
        self.btn_pen_color.clicked.connect(self._pick_pen_color)
        draw_btns.addWidget(self.btn_clear)
        draw_btns.addWidget(self.btn_pen_color)
        draw_btns.addStretch()
        draw_layout.addLayout(draw_btns)

        self.tabs.addTab(draw_tab, "Zeichnen")

        # --- Image tab ---
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)

        self.image_preview = QLabel("Kein Bild geladen")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(150)
        self.image_preview.setStyleSheet(
            "background: white; border: 2px solid #ccc; border-radius: 4px;")
        image_layout.addWidget(self.image_preview)

        self.btn_load_image = QPushButton("Bild laden (PNG/JPG)")
        self.btn_load_image.clicked.connect(self._load_image)
        image_layout.addWidget(self.btn_load_image)

        hint = QLabel("Tipp: Unterschrift auf weissem Papier, abfotografieren/scannen.\n"
                       "PNG mit transparentem Hintergrund funktioniert am besten.")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        image_layout.addWidget(hint)

        self.tabs.addTab(image_tab, "Bild laden")

        layout.addWidget(self.tabs)

        # --- Placement options ---
        place_group = QGroupBox("Platzierung auf der Seite")
        place_layout = QFormLayout(place_group)

        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setMaximum(self._page_count)
        self.spin_page.setValue(self._current_page + 1)
        place_layout.addRow("Seite:", self.spin_page)

        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, 2000)
        self.spin_x.setValue(50)
        self.spin_x.setSuffix(" pt")
        place_layout.addRow("X-Position:", self.spin_x)

        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, 2000)
        self.spin_y.setValue(700)
        self.spin_y.setSuffix(" pt")
        place_layout.addRow("Y-Position:", self.spin_y)

        self.spin_w = QSpinBox()
        self.spin_w.setRange(20, 1000)
        self.spin_w.setValue(200)
        self.spin_w.setSuffix(" pt")
        place_layout.addRow("Breite:", self.spin_w)

        self.spin_h = QSpinBox()
        self.spin_h.setRange(10, 500)
        self.spin_h.setValue(80)
        self.spin_h.setSuffix(" pt")
        place_layout.addRow("Hoehe:", self.spin_h)

        layout.addWidget(place_group)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_apply = QPushButton("Unterschrift einfuegen")
        self.btn_apply.setStyleSheet(
            "background-color: #1565C0; color: white; font-size: 14px; "
            "padding: 8px 20px; border-radius: 4px;")
        self.btn_apply.clicked.connect(self._apply)
        self.btn_cancel = QPushButton("Abbrechen")
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

    def _pick_pen_color(self):
        color = QColorDialog.getColor(QColor(0, 0, 50), self, "Stiftfarbe")
        if color.isValid():
            self.canvas.set_pen_color(color)

    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Unterschrift-Bild laden", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)")
        if not path:
            return
        self._loaded_image_path = path
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Fehler", "Bild konnte nicht geladen werden.")
            return
        scaled = pixmap.scaled(
            QSize(460, 180), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.image_preview.setPixmap(scaled)

    def _apply(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # Draw
            if self.canvas.is_empty():
                QMessageBox.warning(self, "Fehler",
                                    "Bitte zuerst eine Unterschrift zeichnen!")
                return
            self._result_mode = "draw"
            self._result_pixmap = self.canvas.to_pixmap()
        else:  # Image
            if not self._loaded_image_path:
                QMessageBox.warning(self, "Fehler",
                                    "Bitte zuerst ein Bild laden!")
                return
            self._result_mode = "image"
            self._result_pixmap = QPixmap(self._loaded_image_path)

        self.accept()

    def get_result(self) -> dict | None:
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        return {
            "mode": self._result_mode,
            "pixmap": self._result_pixmap,
            "image_path": self._loaded_image_path,
            "page": self.spin_page.value() - 1,
            "x": self.spin_x.value(),
            "y": self.spin_y.value(),
            "width": self.spin_w.value(),
            "height": self.spin_h.value(),
        }

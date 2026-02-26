from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QComboBox, QFileDialog, QMessageBox,
                              QProgressBar, QGroupBox, QRadioButton,
                              QButtonGroup)
from PyQt6.QtCore import Qt
from pathlib import Path

from core.pdf_compressor import PDFCompressor


class CompressDialog(QDialog):
    """Dialog for PDF compression."""

    def __init__(self, input_path: str = None, parent=None):
        super().__init__(parent)
        self.input_path = input_path
        self.setWindowTitle("PDF komprimieren")
        self.setMinimumWidth(450)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # File selection
        file_group = QGroupBox("Datei")
        file_layout = QHBoxLayout(file_group)
        self.file_label = QLabel(
            Path(self.input_path).name if self.input_path else "Keine Datei")
        self.btn_select = QPushButton("Andere PDF waehlen")
        self.btn_select.clicked.connect(self._select_file)
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(self.btn_select)
        layout.addWidget(file_group)

        if self.input_path:
            size = Path(self.input_path).stat().st_size
            self.size_label = QLabel(f"Aktuelle Groesse: {self._fmt(size)}")
        else:
            self.size_label = QLabel("")
        layout.addWidget(self.size_label)

        # Quality selection
        quality_group = QGroupBox("Komprimierungsstufe")
        q_layout = QVBoxLayout(quality_group)

        self.radio_simple = QRadioButton(
            "Nur aufraumen (Garbage Collection + Deflate)")
        self.radio_low = QRadioButton("Niedrig (starke Komprimierung, Qualitaetsverlust)")
        self.radio_mid = QRadioButton("Mittel (guter Kompromiss)")
        self.radio_mid.setChecked(True)
        self.radio_high = QRadioButton("Hoch (wenig Komprimierung, gute Qualitaet)")

        q_layout.addWidget(self.radio_simple)
        q_layout.addWidget(self.radio_low)
        q_layout.addWidget(self.radio_mid)
        q_layout.addWidget(self.radio_high)
        layout.addWidget(quality_group)

        # Result
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 14px; margin: 8px;")
        layout.addWidget(self.result_label)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_compress = QPushButton("Komprimieren")
        self.btn_compress.setStyleSheet(
            "background-color: #FF9800; color: white; font-size: 14px; "
            "padding: 8px 16px; border-radius: 4px;")
        self.btn_compress.clicked.connect(self._do_compress)
        self.btn_close = QPushButton("Schliessen")
        self.btn_close.clicked.connect(self.close)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_compress)
        btn_row.addWidget(self.btn_close)
        layout.addLayout(btn_row)

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "PDF auswaehlen", "", "PDF (*.pdf)")
        if path:
            self.input_path = path
            self.file_label.setText(Path(path).name)
            size = Path(path).stat().st_size
            self.size_label.setText(f"Aktuelle Groesse: {self._fmt(size)}")

    def _do_compress(self):
        if not self.input_path:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst eine PDF auswaehlen!")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Komprimierte PDF speichern als",
            str(Path(self.input_path).parent /
                (Path(self.input_path).stem + "_komprimiert.pdf")),
            "PDF (*.pdf)")
        if not path:
            return

        try:
            self.btn_compress.setEnabled(False)
            self.btn_compress.setText("Komprimiere...")

            if self.radio_simple.isChecked():
                old, new = PDFCompressor.simple_compress(self.input_path, path)
            else:
                quality = "mittel"
                if self.radio_low.isChecked():
                    quality = "niedrig"
                elif self.radio_high.isChecked():
                    quality = "hoch"
                old, new = PDFCompressor.compress(
                    self.input_path, path, quality)

            saved = old - new
            pct = (saved / old * 100) if old > 0 else 0
            self.result_label.setText(
                f"Vorher: {self._fmt(old)}  →  Nachher: {self._fmt(new)}\n"
                f"Gespart: {self._fmt(saved)} ({pct:.1f}%)")
            QMessageBox.information(
                self, "Fertig",
                f"PDF komprimiert!\n"
                f"Vorher: {self._fmt(old)}\n"
                f"Nachher: {self._fmt(new)}\n"
                f"Gespart: {self._fmt(saved)} ({pct:.1f}%)")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
        finally:
            self.btn_compress.setEnabled(True)
            self.btn_compress.setText("Komprimieren")

    @staticmethod
    def _fmt(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

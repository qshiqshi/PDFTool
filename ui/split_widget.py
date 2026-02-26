from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QFileDialog, QMessageBox, QRadioButton,
                              QButtonGroup, QLineEdit, QSpinBox, QGroupBox,
                              QFormLayout)
from PyQt6.QtCore import Qt
from pathlib import Path

from core.pdf_splitter import PDFSplitter


class SplitWidget(QWidget):
    """Tab for splitting PDFs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_path = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("PDF aufteilen")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin: 8px;")
        layout.addWidget(header)

        # File selection
        file_row = QHBoxLayout()
        self.file_label = QLabel("Keine Datei ausgewaehlt")
        self.btn_select = QPushButton("PDF auswaehlen")
        self.btn_select.clicked.connect(self._select_file)
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(self.btn_select)
        layout.addLayout(file_row)

        # Split mode
        mode_group = QGroupBox("Modus")
        mode_layout = QVBoxLayout(mode_group)

        self.radio_all = QRadioButton("In einzelne Seiten aufteilen")
        self.radio_all.setChecked(True)
        self.radio_ranges = QRadioButton("An bestimmten Bereichen aufteilen")
        self.radio_extract = QRadioButton("Seitenbereich extrahieren")

        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.radio_all, 0)
        self.btn_group.addButton(self.radio_ranges, 1)
        self.btn_group.addButton(self.radio_extract, 2)

        mode_layout.addWidget(self.radio_all)
        mode_layout.addWidget(self.radio_ranges)

        self.ranges_input = QLineEdit()
        self.ranges_input.setPlaceholderText("z.B. 1-3, 4-7, 8-12")
        self.ranges_input.setEnabled(False)
        mode_layout.addWidget(self.ranges_input)

        mode_layout.addWidget(self.radio_extract)

        extract_row = QHBoxLayout()
        self.spin_from = QSpinBox()
        self.spin_from.setPrefix("Von Seite: ")
        self.spin_from.setMinimum(1)
        self.spin_from.setEnabled(False)
        self.spin_to = QSpinBox()
        self.spin_to.setPrefix("Bis Seite: ")
        self.spin_to.setMinimum(1)
        self.spin_to.setEnabled(False)
        extract_row.addWidget(self.spin_from)
        extract_row.addWidget(self.spin_to)
        mode_layout.addLayout(extract_row)

        layout.addWidget(mode_group)

        self.btn_group.idToggled.connect(self._on_mode_changed)

        self.btn_split = QPushButton("Aufteilen")
        self.btn_split.setStyleSheet(
            "background-color: #2196F3; color: white; font-size: 14px; "
            "padding: 8px 16px; border-radius: 4px;")
        self.btn_split.clicked.connect(self._do_split)
        layout.addWidget(self.btn_split)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _on_mode_changed(self, id_, checked):
        if not checked:
            return
        self.ranges_input.setEnabled(id_ == 1)
        self.spin_from.setEnabled(id_ == 2)
        self.spin_to.setEnabled(id_ == 2)

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "PDF auswaehlen", "", "PDF (*.pdf)")
        if path:
            self.input_path = path
            self.file_label.setText(Path(path).name)
            import fitz
            doc = fitz.open(path)
            pages = doc.page_count
            doc.close()
            self.spin_from.setMaximum(pages)
            self.spin_to.setMaximum(pages)
            self.spin_to.setValue(pages)

    def _do_split(self):
        if not self.input_path:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst eine PDF auswaehlen!")
            return

        output_dir = QFileDialog.getExistingDirectory(
            self, "Zielordner auswaehlen")
        if not output_dir:
            return

        mode = self.btn_group.checkedId()
        try:
            if mode == 0:
                files = PDFSplitter.split_all_pages(
                    self.input_path, output_dir)
                self.status_label.setText(f"{len(files)} Dateien erstellt")
                QMessageBox.information(
                    self, "Fertig",
                    f"PDF in {len(files)} einzelne Seiten aufgeteilt!")

            elif mode == 1:
                ranges_text = self.ranges_input.text().strip()
                if not ranges_text:
                    QMessageBox.warning(self, "Fehler",
                                        "Bitte Seitenbereiche eingeben!")
                    return
                ranges = []
                for part in ranges_text.split(","):
                    part = part.strip()
                    if "-" in part:
                        s, e = part.split("-", 1)
                        ranges.append((int(s.strip()), int(e.strip())))
                    else:
                        p = int(part)
                        ranges.append((p, p))
                files = PDFSplitter.split_at_ranges(
                    self.input_path, output_dir, ranges)
                self.status_label.setText(f"{len(files)} Dateien erstellt")
                QMessageBox.information(
                    self, "Fertig",
                    f"PDF in {len(files)} Teile aufgeteilt!")

            elif mode == 2:
                s = self.spin_from.value()
                e = self.spin_to.value()
                stem = Path(self.input_path).stem
                out_path = str(Path(output_dir) / f"{stem}_S{s}-{e}.pdf")
                PDFSplitter.extract_range(self.input_path, out_path, s, e)
                self.status_label.setText(f"Seiten {s}-{e} extrahiert")
                QMessageBox.information(
                    self, "Fertig",
                    f"Seiten {s}-{e} extrahiert!")

        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

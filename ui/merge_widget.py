from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QListWidget, QAbstractItemView, QFileDialog,
                              QMessageBox, QLabel, QProgressBar)
from PyQt6.QtCore import Qt
from pathlib import Path

from core.pdf_merger import PDFMerger


class MergeWidget(QWidget):
    """Tab for merging multiple PDFs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.merger = PDFMerger()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("PDFs zusammenfuegen")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin: 8px;")
        layout.addWidget(header)

        desc = QLabel("Dateien per Drag & Drop oder Button hinzufuegen.\n"
                       "Reihenfolge per Drag & Drop aendern.")
        desc.setStyleSheet("color: #666; margin-bottom: 8px;")
        layout.addWidget(desc)

        self.file_list = QListWidget()
        self.file_list.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove)
        self.file_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.file_list.setAcceptDrops(True)
        self.file_list.setMinimumHeight(200)
        layout.addWidget(self.file_list)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Dateien hinzufuegen")
        self.btn_add.clicked.connect(self._add_files)
        self.btn_remove = QPushButton("Entfernen")
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_clear = QPushButton("Alle entfernen")
        self.btn_clear.clicked.connect(self._clear_all)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_remove)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.btn_merge = QPushButton("Zusammenfuegen")
        self.btn_merge.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 14px; "
            "padding: 8px 16px; border-radius: 4px;")
        self.btn_merge.clicked.connect(self._do_merge)
        layout.addWidget(self.btn_merge)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "PDF-Dateien auswaehlen", "", "PDF (*.pdf)")
        for f in files:
            self.merger.add_file(f)
            self.file_list.addItem(Path(f).name + f"  [{f}]")

    def _remove_selected(self):
        row = self.file_list.currentRow()
        if row >= 0:
            self.merger.remove_file(row)
            self.file_list.takeItem(row)

    def _clear_all(self):
        self.merger.clear()
        self.file_list.clear()

    def _do_merge(self):
        if len(self.merger.files) < 2:
            QMessageBox.warning(self, "Fehler",
                                "Mindestens 2 PDF-Dateien hinzufuegen!")
            return
        # Sync order from list widget
        self.merger.files.clear()
        for i in range(self.file_list.count()):
            text = self.file_list.item(i).text()
            path = text.split("[")[-1].rstrip("]")
            self.merger.files.append(path)

        path, _ = QFileDialog.getSaveFileName(
            self, "Zusammengefuegt speichern als", "zusammengefuegt.pdf",
            "PDF (*.pdf)")
        if not path:
            return
        try:
            pages = self.merger.merge(path)
            self.status_label.setText(
                f"Erfolgreich! {len(self.merger.files)} Dateien → "
                f"{pages} Seiten → {Path(path).name}")
            QMessageBox.information(self, "Fertig",
                                    f"PDF zusammengefuegt!\n{pages} Seiten gespeichert.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QMenuBar, QStatusBar, QFileDialog,
                              QMessageBox, QSplitter, QToolBar, QPushButton,
                              QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from pathlib import Path

from core.pdf_handler import PDFHandler
from ui.viewer_widget import ViewerWidget
from ui.thumbnail_bar import ThumbnailBar
from ui.edit_toolbar import EditToolbar
from ui.merge_widget import MergeWidget
from ui.split_widget import SplitWidget
from ui.compress_widget import CompressDialog
from ui.signature_dialog import SignatureDialog


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.handler = PDFHandler()
        self.setWindowTitle("PDF Tool")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self._setup_menubar()
        self._setup_toolbar()
        self._setup_central()
        self._setup_statusbar()

    def _setup_menubar(self):
        mb = self.menuBar()

        # Datei
        file_menu = mb.addMenu("Datei")
        act_open = file_menu.addAction("Oeffnen")
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self._open_file)

        act_save = file_menu.addAction("Speichern")
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self._save_file)

        act_save_as = file_menu.addAction("Speichern unter...")
        act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        act_save_as.triggered.connect(self._save_as)

        file_menu.addSeparator()

        act_export_img = file_menu.addAction("Seite als Bild exportieren")
        act_export_img.triggered.connect(self._export_page_image)

        file_menu.addSeparator()

        act_exit = file_menu.addAction("Beenden")
        act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        act_exit.triggered.connect(self.close)

        # Bearbeiten
        edit_menu = mb.addMenu("Bearbeiten")
        act_rotate_90 = edit_menu.addAction("Seite 90° drehen")
        act_rotate_90.triggered.connect(lambda: self._rotate_current(90))
        act_rotate_180 = edit_menu.addAction("Seite 180° drehen")
        act_rotate_180.triggered.connect(lambda: self._rotate_current(180))

        edit_menu.addSeparator()
        act_del_page = edit_menu.addAction("Seite loeschen")
        act_del_page.triggered.connect(self._delete_current_page)

        edit_menu.addSeparator()
        act_insert_pages = edit_menu.addAction("Seiten aus PDF einfuegen...")
        act_insert_pages.triggered.connect(self._insert_pages_from_file)

        # Ansicht
        view_menu = mb.addMenu("Ansicht")
        act_zoom_in = view_menu.addAction("Vergroessern")
        act_zoom_in.setShortcut(QKeySequence("Ctrl++"))
        act_zoom_in.triggered.connect(
            lambda: self.viewer.zoom_slider.setValue(
                self.viewer.zoom_slider.value() + 25))
        act_zoom_out = view_menu.addAction("Verkleinern")
        act_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        act_zoom_out.triggered.connect(
            lambda: self.viewer.zoom_slider.setValue(
                self.viewer.zoom_slider.value() - 25))

        # Werkzeuge
        tools_menu = mb.addMenu("Werkzeuge")
        act_sign = tools_menu.addAction("Unterschreiben...")
        act_sign.triggered.connect(self._sign_pdf)
        tools_menu.addSeparator()
        act_compress = tools_menu.addAction("Komprimieren...")
        act_compress.triggered.connect(self._show_compress)

    def _setup_toolbar(self):
        tb = QToolBar("Werkzeugleiste")
        tb.setMovable(False)
        self.addToolBar(tb)

        btn_open = QPushButton("Oeffnen")
        btn_open.clicked.connect(self._open_file)
        tb.addWidget(btn_open)

        btn_save = QPushButton("Speichern")
        btn_save.clicked.connect(self._save_file)
        tb.addWidget(btn_save)

        tb.addSeparator()

        self.edit_toolbar = EditToolbar(self)
        self.edit_toolbar.text_add_requested.connect(self._add_text)
        self.edit_toolbar.image_add_requested.connect(self._add_image)
        self.edit_toolbar.comment_requested.connect(self._add_comment)
        self.addToolBar(self.edit_toolbar)

        tb.addSeparator()

        btn_rotate = QPushButton("Drehen")
        btn_rotate.clicked.connect(lambda: self._rotate_current(90))
        tb.addWidget(btn_rotate)

        btn_sign = QPushButton("Unterschreiben")
        btn_sign.clicked.connect(self._sign_pdf)
        tb.addWidget(btn_sign)

        btn_compress = QPushButton("Komprimieren")
        btn_compress.clicked.connect(self._show_compress)
        tb.addWidget(btn_compress)

    def _setup_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        # Viewer tab
        viewer_tab = QWidget()
        viewer_layout = QHBoxLayout(viewer_tab)
        viewer_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.thumbnail_bar = ThumbnailBar()
        self.viewer = ViewerWidget()

        self.thumbnail_bar.page_selected.connect(self.viewer.go_to_page)
        self.viewer.page_changed.connect(self.thumbnail_bar.select_page)
        self.thumbnail_bar.pages_reordered.connect(self._on_pages_reordered)
        self.thumbnail_bar.page_delete_requested.connect(
            self._delete_page_at)
        self.thumbnail_bar.page_rotate_requested.connect(
            self._rotate_page_at)

        self.splitter.addWidget(self.thumbnail_bar)
        self.splitter.addWidget(self.viewer)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([150, 850])

        viewer_layout.addWidget(self.splitter)
        self.tabs.addTab(viewer_tab, "Viewer")

        # Merge tab
        self.merge_widget = MergeWidget()
        self.tabs.addTab(self.merge_widget, "Zusammenfuegen")

        # Split tab
        self.split_widget = SplitWidget()
        self.tabs.addTab(self.split_widget, "Aufteilen")

        layout.addWidget(self.tabs)

    def _setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Bereit")

    def _update_status(self):
        if self.handler.doc:
            page = self.viewer.current_page + 1
            total = self.handler.page_count()
            size = self.handler.file_size()
            size_str = f"{size / (1024*1024):.2f} MB" if size > 0 else ""
            name = Path(self.handler.file_path).name if self.handler.file_path else ""
            mod = " *" if self.handler.modified else ""
            self.status.showMessage(
                f"{name}{mod}  |  Seite {page}/{total}  |  {size_str}")
            self.setWindowTitle(f"PDF Tool - {name}{mod}")
        else:
            self.status.showMessage("Bereit")
            self.setWindowTitle("PDF Tool")

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "PDF oeffnen", "", "PDF (*.pdf);;Alle Dateien (*)")
        if not path:
            return
        try:
            doc = self.handler.open(path)
            self.viewer.set_document(doc)
            self.thumbnail_bar.set_document(doc)
            self._update_status()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Konnte PDF nicht oeffnen:\n{e}")

    def _save_file(self):
        if not self.handler.doc:
            return
        try:
            if self.handler.file_path:
                self.handler.save()
            else:
                self._save_as()
            self._update_status()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def _save_as(self):
        if not self.handler.doc:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Speichern unter", "", "PDF (*.pdf)")
        if path:
            try:
                self.handler.save_as(path)
                self._update_status()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def _export_page_image(self):
        if not self.handler.doc:
            QMessageBox.warning(self, "Fehler", "Kein PDF geoeffnet!")
            return
        idx = self.viewer.current_page
        path, _ = QFileDialog.getSaveFileName(
            self, "Seite als Bild speichern",
            f"seite_{idx + 1}.png",
            "PNG (*.png);;JPG (*.jpg)")
        if path:
            try:
                self.handler.export_page_as_image(idx, path)
                QMessageBox.information(self, "Fertig",
                                        f"Seite {idx + 1} als Bild gespeichert!")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _rotate_current(self, angle):
        if not self.handler.doc:
            return
        idx = self.viewer.current_page
        self._rotate_page_at(idx, angle)

    def _rotate_page_at(self, idx, angle):
        self.handler.rotate_page(idx, angle)
        self.viewer.refresh()
        self.thumbnail_bar.refresh()
        self._update_status()

    def _delete_current_page(self):
        if not self.handler.doc:
            return
        self._delete_page_at(self.viewer.current_page)

    def _delete_page_at(self, idx):
        if not self.handler.doc:
            return
        reply = QMessageBox.question(
            self, "Seite loeschen",
            f"Seite {idx + 1} wirklich loeschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.handler.delete_page(idx)
        if self.viewer.current_page >= self.handler.page_count():
            self.viewer.current_page = max(0, self.handler.page_count() - 1)
        self.viewer.page_spin.setMaximum(max(1, self.handler.page_count()))
        self.viewer.page_label.setText(f"/ {self.handler.page_count()}")
        self.viewer.refresh()
        self.thumbnail_bar.refresh()
        self._update_status()

    def _on_pages_reordered(self, from_idx, to_idx):
        self.handler.move_page(from_idx, to_idx)
        self.viewer.refresh()
        self._update_status()

    def _insert_pages_from_file(self):
        if not self.handler.doc:
            QMessageBox.warning(self, "Fehler", "Zuerst ein PDF oeffnen!")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "PDF zum Einfuegen auswaehlen", "", "PDF (*.pdf)")
        if not path:
            return
        pos, ok = QInputDialog.getInt(
            self, "Position", "Nach welcher Seite einfuegen?",
            self.viewer.current_page + 1, 0, self.handler.page_count())
        if not ok:
            return
        self.handler.insert_pages_from(path, pos)
        self.viewer.page_spin.setMaximum(self.handler.page_count())
        self.viewer.page_label.setText(f"/ {self.handler.page_count()}")
        self.viewer.refresh()
        self.thumbnail_bar.refresh()
        self._update_status()

    def _add_text(self):
        if not self.handler.doc:
            QMessageBox.warning(self, "Fehler", "Kein PDF geoeffnet!")
            return
        page = self.handler.get_page(self.viewer.current_page)
        if self.edit_toolbar.add_text_to_page(page, self):
            self.handler.modified = True
            self.viewer.refresh()
            self._update_status()

    def _add_image(self):
        if not self.handler.doc:
            QMessageBox.warning(self, "Fehler", "Kein PDF geoeffnet!")
            return
        page = self.handler.get_page(self.viewer.current_page)
        if self.edit_toolbar.add_image_to_page(page, self):
            self.handler.modified = True
            self.viewer.refresh()
            self._update_status()

    def _add_comment(self):
        if not self.handler.doc:
            QMessageBox.warning(self, "Fehler", "Kein PDF geoeffnet!")
            return
        page = self.handler.get_page(self.viewer.current_page)
        if self.edit_toolbar.add_comment_to_page(page, self):
            self.handler.modified = True
            self.viewer.refresh()
            self._update_status()

    def _sign_pdf(self):
        if not self.handler.doc:
            QMessageBox.warning(self, "Fehler", "Kein PDF geoeffnet!")
            return
        dlg = SignatureDialog(
            page_count=self.handler.page_count(),
            current_page=self.viewer.current_page,
            parent=self)
        dlg.exec()
        result = dlg.get_result()
        if not result:
            return
        try:
            import fitz
            from core.pdf_editor import PDFEditor
            page = self.handler.get_page(result["page"])
            rect = fitz.Rect(result["x"], result["y"],
                             result["x"] + result["width"],
                             result["y"] + result["height"])
            if result["mode"] == "image" and result["image_path"]:
                PDFEditor.insert_signature_image(page, rect, result["image_path"])
            else:
                png_bytes = result["pixmap"]
                # Convert QPixmap to PNG bytes
                from PyQt6.QtCore import QBuffer, QIODevice
                buf = QBuffer()
                buf.open(QIODevice.OpenModeFlag.WriteOnly)
                result["pixmap"].save(buf, "PNG")
                png_data = bytes(buf.data())
                buf.close()
                PDFEditor.insert_signature_bytes(page, rect, png_data)
            self.handler.modified = True
            self.viewer.go_to_page(result["page"])
            self.viewer.refresh()
            self.thumbnail_bar.refresh()
            self._update_status()
            QMessageBox.information(self, "Fertig",
                                    f"Unterschrift auf Seite {result['page'] + 1} eingefuegt!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler",
                                 f"Unterschrift konnte nicht eingefuegt werden:\n{e}")

    def _show_compress(self):
        path = self.handler.file_path
        dlg = CompressDialog(path, self)
        dlg.exec()

    def closeEvent(self, event):
        if self.handler.modified:
            reply = QMessageBox.question(
                self, "Ungespeicherte Aenderungen",
                "Es gibt ungespeicherte Aenderungen. Trotzdem schliessen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        self.handler.close()
        event.accept()

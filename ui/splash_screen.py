from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QLinearGradient


class SplashScreen(QSplashScreen):
    """Splash screen showing app features on startup."""

    def __init__(self):
        pixmap = self._create_pixmap()
        super().__init__(pixmap)
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint)

    def _create_pixmap(self) -> QPixmap:
        w, h = 560, 420
        pixmap = QPixmap(w, h)
        pixmap.fill(QColor(0, 0, 0, 0))

        p = QPainter(pixmap)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(30, 30, 60))
        grad.setColorAt(0.5, QColor(45, 25, 80))
        grad.setColorAt(1.0, QColor(20, 20, 50))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, h, 16, 16)

        # Border
        p.setPen(QColor(120, 80, 200, 100))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(1, 1, w - 2, h - 2, 16, 16)

        # Title
        title_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        p.setFont(title_font)
        p.setPen(QColor(255, 255, 255))
        p.drawText(0, 40, w, 50, Qt.AlignmentFlag.AlignCenter, "PDF Tool")

        # Subtitle
        sub_font = QFont("Segoe UI", 11)
        p.setFont(sub_font)
        p.setPen(QColor(180, 160, 220))
        p.drawText(0, 80, w, 30, Qt.AlignmentFlag.AlignCenter,
                   "Dein PDF-Werkzeugkasten")

        # Feature list
        features = [
            ("Anzeigen & Navigieren",
             "PDFs oeffnen, zoomen, Seiten durchblaettern"),
            ("Bearbeiten",
             "Text & Bilder einfuegen, Kommentare, Hervorhebungen"),
            ("Unterschreiben",
             "Digital unterschreiben – zeichnen oder Bild laden"),
            ("Seiten verwalten",
             "Drehen, loeschen, neu anordnen per Drag & Drop"),
            ("Zusammenfuegen",
             "Mehrere PDFs zu einem Dokument kombinieren"),
            ("Aufteilen",
             "PDF in einzelne Seiten oder Bereiche splitten"),
            ("Komprimieren",
             "Dateigroesse reduzieren mit einstellbarer Qualitaet"),
        ]

        y = 125
        icon_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        desc_font = QFont("Segoe UI", 9)

        for title, desc in features:
            # Bullet point
            p.setPen(QColor(140, 100, 240))
            p.setFont(icon_font)
            p.drawText(40, y, 20, 20, Qt.AlignmentFlag.AlignCenter, "●")

            # Feature title
            p.setPen(QColor(255, 255, 255))
            p.setFont(icon_font)
            p.drawText(65, y, 200, 20, Qt.AlignmentFlag.AlignLeft, title)

            # Description
            p.setPen(QColor(160, 160, 190))
            p.setFont(desc_font)
            p.drawText(65, y + 18, 460, 20,
                       Qt.AlignmentFlag.AlignLeft, desc)

            y += 40

        # Footer
        footer_font = QFont("Segoe UI", 8)
        p.setFont(footer_font)
        p.setPen(QColor(120, 120, 150))
        p.drawText(0, h - 30, w, 20, Qt.AlignmentFlag.AlignCenter,
                   "AKKD  •  Andreas Kuschner Kommunikationsdesign")

        p.end()
        return pixmap

    def show_with_timeout(self, ms: int = 3000):
        self.show()
        QApplication.processEvents()
        QTimer.singleShot(ms, self.close)

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Tool")
    app.setOrganizationName("AKKD")

    # Apply dark-ish modern style
    app.setStyleSheet("""
        QMainWindow, QWidget {
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        QToolBar {
            spacing: 6px;
            padding: 4px;
        }
        QToolBar QPushButton {
            padding: 4px 10px;
            border: 1px solid #ccc;
            border-radius: 3px;
            background: #f5f5f5;
        }
        QToolBar QPushButton:hover {
            background: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
        }
        QTabBar::tab {
            padding: 6px 16px;
            margin-right: 2px;
            border: 1px solid #ccc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            background: #f0f0f0;
        }
        QTabBar::tab:selected {
            background: white;
            font-weight: bold;
        }
        QStatusBar {
            background: #f5f5f5;
            border-top: 1px solid #ddd;
        }
        QListWidget {
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QScrollArea {
            background: #e8e8e8;
        }
    """)

    # Splash screen
    from ui.splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    from ui.main_window import MainWindow
    window = MainWindow()

    splash.finish(window)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

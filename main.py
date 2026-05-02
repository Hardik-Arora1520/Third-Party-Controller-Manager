"""
Cosmic Byte Ares Controller Manager
Main entry point
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cosmic Byte Ares Manager")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

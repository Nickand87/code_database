from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QPoint


class EnterLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.focusNextPrevChild(True)
        else:
            super().keyPressEvent(event)


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title_bar_height=30, button_width=30):
        super().__init__(parent)
        self.title_label = None
        self.layout = None
        self.close_button = None
        self.minimize_button = None
        self.maximize_button = None
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self.initializeUI(title_bar_height, button_width)

    def initializeUI(self, title_bar_height, button_width):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setupLabels()
        self.setupButtons(title_bar_height, button_width)
        self.setFixedHeight(title_bar_height)

    def setupLabels(self):
        self.title_label = QLabel("Game Tools")
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()

    def setupButtons(self, title_bar_height, button_width):
        self.close_button = QPushButton("X")
        self.minimize_button = QPushButton("-")
        self.maximize_button = QPushButton("[]")

        for btn in [self.minimize_button, self.maximize_button, self.close_button]:
            btn.setFixedSize(button_width, title_bar_height)
            self.layout.addWidget(btn)

        self.minimize_button.clicked.connect(self.parent().showMinimized)
        self.maximize_button.clicked.connect(self.toggleMaximizeRestore)
        self.close_button.clicked.connect(self.parent().close)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = event.globalPos() - self.drag_start_position
            self.drag_start_position = event.globalPos()
            self.parent().move(self.parent().pos() + delta)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def toggleMaximizeRestore(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setText("[]")
        else:
            self.parent().showMaximized()
            self.maximize_button.setText("_")

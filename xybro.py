import sys
from PyQt5.QtCore import Qt, QUrl, QSize, QRectF
from PyQt5.QtGui import QIcon, QPixmap, QPainterPath, QColor, QPalette, QPainter
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QTabWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QProgressBar,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem, QWebEnginePage


class SquarcicleButton(QPushButton):
    def __init__(self, light_icon_path, dark_icon_path):
        super().__init__()
        self.setFixedSize(32, 32)
        self.setStyleSheet("border-radius: 8px;")
        self.light_icon_path = light_icon_path
        self.dark_icon_path = dark_icon_path
        self.setIcon(QIcon(light_icon_path))
        self.setIconSize(QSize(24, 24))
        self.setGraphicsEffect(QGraphicsDropShadowEffect(self))
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(8)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)

    def enterEvent(self, event):
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self.shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 8.0, 8.0)

        painter.setClipPath(path)
        super().paintEvent(event)

    def set_dark_mode(self, dark_mode):
        if dark_mode:
            self.setIcon(QIcon(self.dark_icon_path))
        else:
            self.setIcon(QIcon(self.light_icon_path))


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("xyBro")
        self.setGeometry(100, 100, 1280, 720)

        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout()
        title_bar.setLayout(title_layout)

        # Create title label
        self.title_label = QLabel("xyBro")
        self.title_label.setStyleSheet("font-size: 20px; padding: 5px; color: #F8F8F2;")
        title_layout.addWidget(self.title_label)

        # Create toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar.setLayout(toolbar_layout)

        # Create buttons
        back_button = SquarcicleButton("icons/light/back.png", "icons/dark/back.png")
        back_button.clicked.connect(self.back)
        toolbar_layout.addWidget(back_button)

        forward_button = SquarcicleButton("icons/light/forward.png", "icons/dark/forward.png")
        forward_button.clicked.connect(self.forward)
        toolbar_layout.addWidget(forward_button)

        refresh_button = SquarcicleButton("icons/light/refresh.png", "icons/dark/refresh.png")
        refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(refresh_button)

        self.dark_mode_button = SquarcicleButton("icons/light/theme.png", "icons/dark/theme.png")
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        toolbar_layout.addWidget(self.dark_mode_button)

        download_button = SquarcicleButton("icons/light/download.png", "icons/dark/download.png")
        download_button.clicked.connect(self.start_download)
        toolbar_layout.addWidget(download_button)

        new_tab_button = SquarcicleButton("icons/light/new_tab.png", "icons/dark/new_tab.png")
        new_tab_button.clicked.connect(self.create_new_tab)
        toolbar_layout.addWidget(new_tab_button)

        title_layout.addWidget(toolbar)

        # Create URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search query...")
        self.url_bar.setStyleSheet("border: none; border-radius: 8px; padding: 4px;")
        self.url_bar.returnPressed.connect(self.load_url)
        title_layout.addWidget(self.url_bar)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Add initial tab
        self.create_new_tab()

        # Add title bar and tab widget to main layout
        layout.addWidget(title_bar)
        layout.addWidget(self.tab_widget)

        # Create central widget and set layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set dark mode by default
        self.dark_mode = True
        self.set_dark_mode()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.set_dark_mode()

    def set_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #252526;
                    color: #F8F8F2;
                }
                QTabWidget::pane {
                    border-top: 1px solid #808080;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: #252526;
                    color: #F8F8F2;
                    padding: 8px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #3E3E40;
                }
                QTabBar::tab:hover {
                    background-color: #3E3E40;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                QLineEdit {
                    background-color: #373737;
                    color: #F8F8F2;
                    border: none;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #373737;
                    color: #F8F8F2;
                    border: none;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: #3E3E40;
                }
                QPushButton:pressed {
                    background-color: #454545;
                }
                """
            )
        else:
            self.setStyleSheet("")

        # Update icons in the toolbar
        for button in self.findChildren(SquarcicleButton):
            button.set_dark_mode(self.dark_mode)

        # Update title label color
        self.set_dark_mode_title()

    def set_dark_mode_title(self):
        if self.dark_mode:
            self.title_label.setStyleSheet("font-size: 20px; padding: 5px; color: #F8F8F2;")
        else:
            self.title_label.setStyleSheet("font-size: 20px; padding: 5px; color: #000000;")

    def create_new_tab(self):
        # Create web view
        web_view = QWebEngineView()
        web_view.page().profile().downloadRequested.connect(self.handle_download_request)
        web_view.page().setBackgroundColor(Qt.transparent)

        # Create progress bar
        progress_bar = QProgressBar()
        progress_bar.setTextVisible(False)
        progress_bar.setMaximumHeight(2)
        progress_bar.setStyleSheet("QProgressBar { background-color: transparent; } QProgressBar::chunk { background-color: #64B5F6; }")

        # Create tab layout
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(web_view)
        tab_layout.addWidget(progress_bar)

        # Create tab widget
        tab_widget = QWidget()
        tab_widget.setLayout(tab_layout)

        # Add tab widget to tab widget
        index = self.tab_widget.addTab(tab_widget, "")
        self.tab_widget.setCurrentIndex(index)

        # Set tab as current tab
        self.tab_widget.setCurrentWidget(tab_widget)

        # Set tab title
        self.set_tab_title(index, "New Tab")

        # Load homepage
        self.load_homepage(index)

        # Connect web view signals
        web_view.urlChanged.connect(lambda url: self.update_url_bar(url, index))
        web_view.titleChanged.connect(lambda title: self.set_tab_title(index, title))
        web_view.loadProgress.connect(progress_bar.setValue)

    def close_tab(self, index):
        if self.tab_widget.count() == 1:
            # Don't allow closing the last tab
            return

        # Remove tab and delete its web view
        widget = self.tab_widget.widget(index)
        widget.deleteLater()
        self.tab_widget.removeTab(index)

    def load_url(self):
        url = self.url_bar.text()
        self.load_url_in_current_tab(url)

    def load_url_in_current_tab(self, url):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index).layout().itemAt(0).widget()
        web_view.load(QUrl(url))

    def load_homepage(self, index):
        # Load your homepage URL here
        homepage_url = "https://www.google.com"
        web_view = self.tab_widget.widget(index).layout().itemAt(0).widget()
        web_view.load(QUrl(homepage_url))

    def back(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index).layout().itemAt(0).widget()
        web_view.back()

    def forward(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index).layout().itemAt(0).widget()
        web_view.forward()

    def refresh(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index).layout().itemAt(0).widget()
        web_view.reload()

    def update_url_bar(self, url, index):
        if index == self.tab_widget.currentIndex():
            self.url_bar.setText(url.toString())

    def set_tab_title(self, index, title):
        if index == self.tab_widget.currentIndex():
            self.setWindowTitle(title)

        if title == "":
            title = "New Tab"

        self.tab_widget.setTabText(index, title)

    def start_download(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index).layout().itemAt(0).widget()
        url = web_view.url().toString()

        if url:
            # Show save file dialog
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)

            if file_path:
                # Start download
                web_view.page().profile().downloadRequested.disconnect(self.handle_download_request)
                download_item = web_view.page().profile().downloadRequested.connect(lambda download: self.handle_download(download, file_path))
                web_view.page().profile().download(download_item, url)

    def handle_download_request(self, download):
        # Show save file dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_path:
            # Start download
            download.finished.connect(lambda: self.download_finished(download))
            download.setPath(file_path)
            download.accept()

    def handle_download(self, download, file_path):
        download.finished.connect(lambda: self.download_finished(download))
        download.setPath(file_path)

    def download_finished(self, download):
        QMessageBox.information(self, "Download Complete", f"File {download.path()} has been downloaded successfully!")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BrowserWindow()
    window.show()

    sys.exit(app.exec_())

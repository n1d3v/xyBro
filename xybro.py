import sys
from PyQt5.QtCore import Qt, QUrl, QSize
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
    QMenu,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEngineProfile,
    QWebEngineDownloadItem,
)


class ButtonWithShadow(QPushButton):
    def __init__(self, icon_path):
        super().__init__()
        self.setFixedSize(32, 32)
        self.setStyleSheet("border-radius: 16px;")
        self.setIcon(QIcon(icon_path))
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


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("xyBro")
        self.setGeometry(100, 100, 800, 600)

        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout()
        title_bar.setLayout(title_layout)

        # Create title label
        title_label = QLabel("xyBro")
        title_label.setStyleSheet("font-size: 20px; padding: 5px;")
        title_layout.addWidget(title_label)

        # Create toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar.setLayout(toolbar_layout)

        # Create buttons
        back_button = ButtonWithShadow("icons/back.png")
        back_button.clicked.connect(self.back)
        toolbar_layout.addWidget(back_button)

        forward_button = ButtonWithShadow("icons/forward.png")
        forward_button.clicked.connect(self.forward)
        toolbar_layout.addWidget(forward_button)

        refresh_button = ButtonWithShadow("icons/refresh.png")
        refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(refresh_button)

        new_tab_button = ButtonWithShadow("icons/new_tab.png")
        new_tab_button.clicked.connect(self.create_new_tab)
        toolbar_layout.addWidget(new_tab_button)

        download_button = ButtonWithShadow("icons/download.png")
        download_button.clicked.connect(self.download_manager)
        toolbar_layout.addWidget(download_button)

        # Create URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search query...")
        self.url_bar.setStyleSheet("border: none;")
        self.url_bar.returnPressed.connect(self.load_url)
        toolbar_layout.addWidget(self.url_bar)

        title_layout.addWidget(toolbar)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabBar().setStyleSheet("border: none;")
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(title_bar)
        layout.addWidget(self.tab_widget)

        # Create initial tab
        self.create_new_tab()

        # Set layout to central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Download manager window
        self.download_manager_window = DownloadManagerWindow()

        # Create a profile for handling downloads
        self.download_profile = QWebEngineProfile.defaultProfile()
        self.download_profile.downloadRequested.connect(self.handle_download)

    def load_url(self):
        url_bar = self.sender()
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index)
        text = url_bar.text().strip()

        # Check if the input is a URL
        if not text.startswith("http://") and not text.startswith("https://"):
            # Treat as a Google search query
            url = f"https://www.google.com/search?q={text}"
        else:
            url = text

        web_view.load(QUrl(url))

    def create_new_tab(self):
        web_view = QWebEngineView()
        web_view.load(QUrl("https://www.google.com"))
        web_view.titleChanged.connect(self.update_tab_title)
        web_view.urlChanged.connect(self.update_url_bar)
        web_view.contextMenuEvent = self.context_menu_event
        self.tab_widget.addTab(web_view, "New Tab")
        current_index = self.tab_widget.indexOf(web_view)
        self.tab_widget.setCurrentIndex(current_index)

    def update_tab_title(self, title):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(current_index, title)

    def update_url_bar(self, url):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index)
        self.url_bar.setText(url.toString())

    def close_tab(self, index):
        if index != -1:
            self.tab_widget.removeTab(index)

    def back(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index)
        web_view.back()

    def forward(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index)
        web_view.forward()

    def refresh(self):
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.widget(current_index)
        web_view.reload()

    def handle_download(self, download_item):
        download_item.finished.connect(self.download_finished)
        download_item.downloadProgress.connect(self.update_download_progress)
        self.download_manager_window.add_download(download_item)

    def download_finished(self):
        download_item = self.sender()
        if download_item.state() == QWebEngineDownloadItem.DownloadCompleted:
            QMessageBox.information(
                self,
                "Download Completed",
                f"{download_item.fileName()} has been downloaded successfully.",
            )

    def update_download_progress(self, bytes_received, bytes_total):
        download_item = self.sender()
        if download_item.state() == QWebEngineDownloadItem.DownloadInProgress:
            self.download_manager_window.update_download_progress(
                download_item, bytes_received, bytes_total
            )

    def download_manager(self):
        self.download_manager_window.show()

    def context_menu_event(self, event):
        web_view = self.sender()
        menu = QMenu(self)

        save_image_action = menu.addAction("Save Image")
        save_image_action.triggered.connect(lambda: self.save_image(web_view, event))

        menu.exec_(event.globalPos())

    def save_image(self, web_view, event):
        if web_view.page() is None:
            return

        hit_test_result = web_view.page().hitTestContent(event.pos())
        if hit_test_result.isContentSelected():
            # Save the selected content as an image
            image_url = hit_test_result.imageUrl()
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setFileMode(QFileDialog.AnyFile)
            file_dialog.setDefaultSuffix("png")
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                download_item = web_view.page().profile().downloadImage(image_url)
                download_item.finished.connect(lambda: self.save_selected_image(download_item, file_path))
        else:
            # Save the entire page as an image
            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setFileMode(QFileDialog.AnyFile)
            file_dialog.setDefaultSuffix("png")
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                web_view.grab().save(file_path)

    def save_selected_image(self, download_item, file_path):
        if download_item.state() == QWebEngineDownloadItem.DownloadCompleted:
            file_extension = QFileInfo(file_path).suffix()
            if file_extension == "":
                file_extension = "png"
                file_path += ".png"
            download_item.downloadProgress.connect(lambda bytes_received, bytes_total: self.update_save_progress(download_item, bytes_received, bytes_total, file_path))
            download_item.save(file_path, file_extension)

    def update_save_progress(self, download_item, bytes_received, bytes_total, file_path):
        if download_item.state() == QWebEngineDownloadItem.DownloadInProgress:
            progress = bytes_received * 100 / bytes_total
            self.download_manager_window.update_save_progress(download_item, progress, file_path)


class DownloadManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Download Manager")
        self.setGeometry(100, 100, 600, 400)

        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create list widget
        self.download_list = QListWidget()
        layout.addWidget(self.download_list)

        # Set layout to central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_download(self, download_item):
        item = QListWidgetItem(download_item.fileName())
        item.setData(Qt.UserRole, download_item)
        self.download_list.addItem(item)

    def update_download_progress(self, download_item, bytes_received, bytes_total):
        for row in range(self.download_list.count()):
            item = self.download_list.item(row)
            if item.data(Qt.UserRole) == download_item:
                progress = bytes_received * 100 / bytes_total
                item.setText(f"{download_item.fileName()} - {progress:.2f}%")

    def update_save_progress(self, download_item, progress, file_path):
        for row in range(self.download_list.count()):
            item = self.download_list.item(row)
            if item.data(Qt.UserRole) == download_item:
                item.setText(f"{download_item.fileName()} - {progress:.2f}% - Saving...")

                if progress == 100:
                    QMessageBox.information(
                        self,
                        "Save Completed",
                        f"{download_item.fileName()} has been saved to {file_path} successfully.",
                    )
                    self.download_list.takeItem(row)
                    break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec_())

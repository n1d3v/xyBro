import sys
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineCore import *


class DarkWebEnginePage(QWebEnginePage):
    def userAgentForUrl(self, url):
        return f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 xyBro"


class xyBro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("xyBro")
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QVBoxLayout())
        self.tab_widget = QTabWidget()
        self.centralWidget().layout().addWidget(self.tab_widget)
        self.add_new_tab(QUrl("https://www.google.com"))

        self.setStyleSheet("""
            QMainWindow, QLineEdit, QTabWidget, QTabBar::tab {
                font-family: Arial;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabBar::tab {
                padding: 10px;
            }
            QTabBar::tab:selected {
                background-color: #3b3b3b;
            }
        """)

    def add_new_tab(self, url=None):
        if url is None:
            url = QUrl("")

        web_view = QWebEngineView()
        web_view.setPage(DarkWebEnginePage(self))
        web_view.setUrl(url)
        web_view.urlChanged.connect(self.update_urlbar)

        index = self.tab_widget.addTab(web_view, "New Tab")
        self.tab_widget.setCurrentIndex(index)

        web_view.loadFinished.connect(lambda: self.tab_widget.setTabText(index, web_view.page().title()))

        urlbar = QLineEdit()
        urlbar.returnPressed.connect(lambda: web_view.setUrl(QUrl.fromUserInput(urlbar.text())))
        web_view.urlChanged.connect(lambda url: urlbar.setText(url.toString()))
        self.centralWidget().layout().addWidget(urlbar)

    def update_urlbar(self, q):
     self.tab_widget.setTabText(self.tab_widget.currentIndex(), q.toString())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("xyBro")
    app.setOrganizationName("xyBro")
    app.setOrganizationDomain("xyBro")

    main_window = xyBro()
    main_window.show()

    sys.exit(app.exec_())
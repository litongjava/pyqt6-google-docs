import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
                             QPushButton, QLineEdit, QHBoxLayout, QSizePolicy, QTabBar)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

default_url = "https://docs.google.com"
title = 'Google Docs'


class FixedTabBar(QTabBar):
    def tabSizeHint(self, index):
        return QSize(200, 40)  # 这里设置标签的大小


class BrowserTab(QWebEngineView):
    def __init__(self, tab_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 创建自定义的 QWebEngineProfile
        self.custom_profile = QWebEngineProfile("google docs", self)
        self.custom_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.custom_profile.setCachePath('./web_cache')
        self.custom_profile.setPersistentStoragePath('./web_storage')

        self.setPage(QWebEnginePage(self.custom_profile, self))

        self.tab_widget = tab_widget
        self.load(QUrl(default_url))
        self.titleChanged.connect(self.update_title)

    def update_title(self, title):
        index = self.tab_widget.indexOf(self)
        if index != -1:
            self.tab_widget.setTabText(index, title)


class SimplifiedMultiTabBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(title)
        self.setGeometry(100, 30, 1500, 1000)
        self.showMaximized()

        layout = QVBoxLayout()

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabBar(FixedTabBar())
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        layout.addWidget(self.tabs)

        # Add New Tab button in the right corner of the tab bar
        self.addTabButton = QPushButton("Add New Tab", self)
        self.addTabButton.clicked.connect(self.add_tab)
        self.tabs.setCornerWidget(self.addTabButton, Qt.Corner.TopRightCorner)

        # Navigation bar
        nav_layout = QHBoxLayout()

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.navigate_back)
        nav_layout.addWidget(self.back_button)

        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.navigate_forward)
        nav_layout.addWidget(self.forward_button)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.address_bar)

        layout.addLayout(nav_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.add_tab()

    def navigate_back(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.back()

    def navigate_forward(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.forward()

    def navigate_to_url(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.load(QUrl(self.address_bar.text()))

    def tab_changed(self, index):
        current_tab = self.tabs.widget(index)
        if current_tab:
            url = current_tab.url().toString()
            self.address_bar.setText(url)

    def add_tab(self):
        new_tab = BrowserTab(self.tabs)
        new_tab.urlChanged.connect(self.tab_url_changed)
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        tab = self.tabs.widget(index)
        tab.deleteLater()
        self.tabs.removeTab(index)

    def tab_url_changed(self, qurl):
        self.address_bar.setText(qurl.toString())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            is_visible = self.back_button.isVisible()
            self.back_button.setVisible(not is_visible)
            self.forward_button.setVisible(not is_visible)
            self.address_bar.setVisible(not is_visible)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimplifiedMultiTabBrowser()
    window.show()
    sys.exit(app.exec())

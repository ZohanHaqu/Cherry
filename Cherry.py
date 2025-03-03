import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QMessageBox, QFileDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QDialogButtonBox, QMenu, QMenuBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon


class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About Cherry")
        self.setGeometry(500, 300, 400, 200)

        layout = QVBoxLayout()

        about_message = QLabel("""
        Cherry 1.0

        We don't know if Cherry is based on Chromium or PyQt5, but we do know it's a unique and feature-rich browser
        that's built for both speed and simplicity. 

        Thanks for using Cherry Browser!
        """)

        layout.addWidget(about_message)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout.addWidget(button_box)

        self.setLayout(layout)


class CherryBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cherry Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("cherry.ico"))

        # Show the Welcome Page when the browser starts
        self.show_welcome_page()

        # Create the main tab widget and set it as central widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create a button for opening a new tab
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(self.add_new_tab)

        # Create a layout for the top bar and add the new tab button
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Create a horizontal layout for the toolbar with the new tab button
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.new_tab_btn)
        toolbar_layout.addStretch(1)  # This adds space between the new tab button and the close button

        # Create a QWidget to hold the layout and add it to the toolbar
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)
        navbar.addWidget(toolbar_widget)

        # Create the first tab with a default new tab page
        self.add_new_tab()

        # Create navigation toolbar
        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.navigate_back)
        self.navbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.navigate_forward)
        self.navbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        self.tabs.currentChanged.connect(self.update_url)

        # Create the menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_window)
        file_menu.addAction(about_action)

    def show_welcome_page(self):
        """Show the welcome page when the browser starts"""
        welcome_window = WelcomePage()
        welcome_window.exec_()

    def add_new_tab(self):
        """Add a new tab with the default page"""
        new_tab = QWidget()
        tab_layout = QVBoxLayout()

        # Create a layout for the tab to include the close button
        tab_header_layout = QHBoxLayout()

        # Create a close button for each tab
        close_btn = QPushButton("X")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(lambda: self.close_tab())

        # Add the close button to the header layout and align it to the right
        tab_header_layout.addWidget(close_btn, alignment=Qt.AlignRight)

        # Add the header layout (with close button) to the tab layout
        tab_layout.addLayout(tab_header_layout)

        browser = QWebEngineView()

        # Set the default new tab page with the absolute path to newtab.html
        browser.setUrl(QUrl("file:///C:/Users/zohan/Downloads/Cherry/newtab.html"))

        # Add the browser to the layout
        tab_layout.addWidget(browser)

        new_tab.setLayout(tab_layout)

        # Add the new tab to the QTabWidget
        tab_index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(tab_index)

        # Save the browser object as an attribute so it can be accessed later
        new_tab.browser = browser

        # Connect the download request signal after the QWebEngineView is created
        browser.page().profile().downloadRequested.connect(self.on_download_requested)

    def close_tab(self):
        """Close the current tab"""
        current_index = self.tabs.currentIndex()
        self.tabs.removeTab(current_index)

    def current_browser(self):
        """Returns the current browser (QWebEngineView)"""
        current_widget = self.tabs.currentWidget()
        return current_widget.browser if hasattr(current_widget, 'browser') else None

    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.current_browser().setUrl(QUrl(url))

    def update_url(self):
        current_browser = self.current_browser()
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def on_download_requested(self, download: QWebEngineDownloadItem):
        """Handle download requests"""
        file_name = download.path().split("/")[-1]

        # Open a file dialog to select the download location
        download_location = QFileDialog.getSaveFileName(self, "Select Download Location", file_name)[0]

        if download_location:
            # Show message box asking for confirmation and display the chosen path
            reply = QMessageBox.question(self, "Confirm Download", 
                                         f"Are you sure to install {file_name}?\nDownload Location: {download_location}", 
                                         QMessageBox.Yes | QMessageBox.No, 
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                download.setPath(download_location)
                download.accept()
            else:
                download.cancel()

    def show_about_window(self):
        """Show the About window with Cherry details"""
        about_window = AboutWindow()
        about_window.exec_()

    # Navigation functions:
    def navigate_back(self):
        """Navigate back"""
        current_browser = self.current_browser()
        if current_browser and current_browser.history().canGoBack():
            current_browser.back()

    def navigate_forward(self):
        """Navigate forward"""
        current_browser = self.current_browser()
        if current_browser and current_browser.history().canGoForward():
            current_browser.forward()

    def reload_page(self):
        """Reload the current page"""
        current_browser = self.current_browser()
        if current_browser:
            current_browser.reload()


class WelcomePage(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Welcome to Cherry Browser")
        self.setGeometry(500, 300, 400, 200)

        layout = QVBoxLayout()

        welcome_message = QLabel("""
        Welcome to Cherry Browser!

        Since the close tab button isn't aligned properly, we have reduced the height of the browser content
        to prevent this issue.

        Other features of Cherry include a custom tab management system and enhanced download capabilities.

        Enjoy browsing with Cherry!
        """)

        layout.addWidget(welcome_message)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout.addWidget(button_box)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CherryBrowser()
    window.show()
    sys.exit(app.exec_())

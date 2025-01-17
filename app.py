import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QMessageBox, QWidget, QDialog, QDialogButtonBox, QFormLayout, QFileDialog
)
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt
from uploader import upload_file_to_s3

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class AWSCredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter AWS Credentials")

        self.access_key_input = QLineEdit()
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.region_input = QLineEdit()
        self.region_input.setText("us-east-1")

        form_layout = QFormLayout()
        form_layout.addRow("Access Key:", self.access_key_input)
        form_layout.addRow("Secret Key:", self.secret_key_input)
        form_layout.addRow("Region:", self.region_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

        self.apply_styles()

    def apply_styles(self):
        font_path = resource_path("fonts/AlbertSans-Regular.ttf")
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            return

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
            return

        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if not font_families:
            print(f"No font families found for font ID: {font_id}")
            return

        font_family = font_families[0]

        bold_font_path = resource_path("fonts/Sora-Medium.ttf")
        if not os.path.exists(bold_font_path):
            print(f"Font file not found: {bold_font_path}")
            return

        bold_font_id = QFontDatabase.addApplicationFont(bold_font_path)
        if bold_font_id == -1:
            print(f"Failed to load font: {bold_font_path}")
            return

        bold_font_families = QFontDatabase.applicationFontFamilies(bold_font_id)
        if not bold_font_families:
            print(f"No font families found for font ID: {bold_font_id}")
            return

        bold_font_family = bold_font_families[0]

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #1d1f21;
                font-family: '{font_family}';
                color: #ffffff;
            }}
            QLineEdit {{
                padding: 10px;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                font-size: 16px;
                font-family: '{bold_font_family}';
                background-color: #2c2f33;
                color: #ffffff;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.12), inset 0 1px 2px rgba(0, 0, 0, 0.24);
                transition: all 0.3s ease;
            }}
            QLineEdit:focus {{
                border-color: #505AAF;
                box-shadow: 0 0 5px rgba(80, 90, 175, 0.5);
            }}
            QLabel {{
                font-size: 16px;
                margin-bottom: 5px;
                font-family: '{bold_font_family}';
                color: #ffffff;
            }}
            QPushButton {{
                background-color: #505AAF;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
                font-family: '{font_family}';
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: #404A9E;
                box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: #303A8E;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                transform: translateY(2px);
            }}
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AWS S3 Large File Uploader")
        self.setGeometry(100, 100, 500, 400)

        self.aws_access_key = None
        self.aws_secret_key = None
        self.aws_region = "us-east-1"

        layout = QVBoxLayout()

        self.aws_config_button = QPushButton("Set AWS Credentials")
        self.aws_config_button.clicked.connect(self.set_aws_credentials)
        layout.addWidget(self.aws_config_button)

        self.bucket_label = QLabel("S3 Bucket Name:")
        self.bucket_input = QLineEdit()
        self.bucket_input.setPlaceholderText("Enter S3 bucket name")
        layout.addWidget(self.bucket_label)
        layout.addWidget(self.bucket_input)

        self.file_label = QLabel("File to Upload:")
        layout.addWidget(self.file_label)
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Enter file path or click 'Select File'")
        layout.addWidget(self.file_input)

        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_file_button)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.apply_styles()

    def apply_styles(self):
        font_path = resource_path("fonts/AlbertSans-Regular.ttf")
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            return

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_path}")
            return

        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if not font_families:
            print(f"No font families found for font ID: {font_id}")
            return

        font_family = font_families[0]

        bold_font_path = resource_path("fonts/Sora-Medium.ttf")
        if not os.path.exists(bold_font_path):
            print(f"Font file not found: {bold_font_path}")
            return

        bold_font_id = QFontDatabase.addApplicationFont(bold_font_path)
        if bold_font_id == -1:
            print(f"Failed to load font: {bold_font_path}")
            return

        bold_font_families = QFontDatabase.applicationFontFamilies(bold_font_id)
        if not bold_font_families:
            print(f"No font families found for font ID: {bold_font_id}")
            return

        bold_font_family = bold_font_families[0]

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #1d1f21;
                font-family: '{font_family}';
                color: #ffffff;
            }}
            QMessageBox {{
                background-color: #1d1f21;
                font-family: '{font_family}';
                color: #ffffff;
            }}
            QPushButton {{
                background-color: #505AAF;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
                font-family: '{font_family}';
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: #404A9E;
                box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: #303A8E;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                transform: translateY(2px);
            }}
            QLineEdit {{
                padding: 10px;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                font-size: 16px;
                font-family: '{bold_font_family}';
                background-color: #2c2f33;
                color: #ffffff;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.12), inset 0 1px 2px rgba(0, 0, 0, 0.24);
                transition: all 0.3s ease;
            }}
            QLineEdit:focus {{
                border-color: #505AAF;
                box-shadow: 0 0 5px rgba(80, 90, 175, 0.5);
            }}
            QLabel {{
                font-size: 16px;
                margin-bottom: 5px;
                font-family: '{bold_font_family}';
                color: #ffffff;
            }}
        """)

    def set_aws_credentials(self):
        dialog = AWSCredentialsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            access_key, secret_key, region = dialog.get_credentials()
            if not access_key or not secret_key:
                QMessageBox.warning(self, "Error", "AWS Access Key and Secret Key are required.")
                return
            self.aws_access_key = access_key
            self.aws_secret_key = secret_key
            self.aws_region = region
            QMessageBox.information(self, "Success", "AWS credentials set successfully.")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_input.setText(file_path)

    def upload_file(self):
        bucket = self.bucket_input.text().strip()
        file_path = self.file_input.text().strip()

        if not bucket:
            QMessageBox.warning(self, "Error", "Please specify an S3 bucket.")
            return
        if not os.path.isfile(file_path):
            QMessageBox.warning(self, "Error", "Please select a valid file.")
            return
        if not self.aws_access_key or not self.aws_secret_key:
            QMessageBox.warning(self, "Error", "Please set AWS credentials first.")
            return

        self.status_label.setText("Uploading...")
        try:
            upload_file_to_s3(
                file_path=file_path,
                bucket_name=bucket,
                aws_access_key=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region=self.aws_region
            )
            QMessageBox.information(self, "Success", "File uploaded successfully.")
            self.status_label.setText("Upload complete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
            self.status_label.setText("Upload failed.")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QWidget
)
from uploader import upload_file_to_s3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AWS S3 Large File Uploader")
        self.setGeometry(100, 100, 400, 300)

        # Layout
        layout = QVBoxLayout()

        # AWS Configuration Button
        self.aws_config_button = QPushButton("Set AWS Credentials")
        self.aws_config_button.clicked.connect(self.set_aws_credentials)
        layout.addWidget(self.aws_config_button)

        # Bucket input
        self.bucket_label = QLabel("S3 Bucket Name:")
        self.bucket_input = QLineEdit()
        self.bucket_input.setPlaceholderText("Enter S3 bucket name")
        layout.addWidget(self.bucket_label)
        layout.addWidget(self.bucket_input)

        # File selection and upload
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

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_aws_credentials(self):
        """Prompt the user to enter AWS credentials and store them in a .env file."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Set AWS Credentials")
        dialog.setGeometry(150, 150, 300, 200)

        layout = QVBoxLayout()

        # AWS Access Key ID
        access_key_label = QLabel("AWS Access Key ID:")
        access_key_input = QLineEdit()
        layout.addWidget(access_key_label)
        layout.addWidget(access_key_input)

        # AWS Secret Access Key
        secret_key_label = QLabel("AWS Secret Access Key:")
        secret_key_input = QLineEdit()
        secret_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(secret_key_label)
        layout.addWidget(secret_key_input)

        # AWS Region
        region_label = QLabel("AWS Region:")
        region_input = QLineEdit()
        region_input.setPlaceholderText("us-east-1")
        layout.addWidget(region_label)
        layout.addWidget(region_input)

        # Save Button
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_aws_credentials(
            access_key_input.text(),
            secret_key_input.text(),
            region_input.text(),
            dialog
        ))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    def save_aws_credentials(self, access_key, secret_key, region, dialog):
        """Save the provided AWS credentials to a .env file."""
        if not access_key or not secret_key:
            QMessageBox.warning(self, "Error", "Access Key and Secret Key cannot be empty.")
            return

        region = region.strip() if region else "us-east-1"

        with open(".env", "w") as env_file:
            env_file.write(f"AWS_ACCESS_KEY_ID={access_key}\n")
            env_file.write(f"AWS_SECRET_ACCESS_KEY={secret_key}\n")
            env_file.write(f"AWS_REGION={region}\n")

        QMessageBox.information(self, "Success", "AWS credentials saved successfully.")
        dialog.accept()

    def select_file(self):
        """Open a file dialog to select a file."""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_input.setText(file_path)

    def upload_file(self):
        """Upload the selected file to the specified S3 bucket."""
        bucket = self.bucket_input.text().strip()
        file_path = self.file_input.text().strip()

        if not bucket:
            QMessageBox.warning(self, "Error", "Please specify an S3 bucket.")
            return
        if not os.path.isfile(file_path):
            QMessageBox.warning(self, "Error", "Please select a valid file.")
            return

        self.status_label.setText("Uploading...")
        try:
            upload_file_to_s3(file_path, bucket)
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

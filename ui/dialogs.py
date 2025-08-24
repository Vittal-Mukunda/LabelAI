from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QFileDialog

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setFixedSize(400, 150)

        self.projectName = QLineEdit(self)
        self.projectPath = QLineEdit(self)
        self.projectPath.setReadOnly(True)

        browseButton = QPushButton("Browse...")
        browseButton.clicked.connect(self.browse_path)

        createButton = QPushButton("Create", self)
        createButton.clicked.connect(self.accept)

        layout = QFormLayout(self)
        layout.addRow("Project Name:", self.projectName)
        layout.addRow("Project Location:", self.projectPath)
        layout.addWidget(browseButton)
        layout.addWidget(createButton)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Location")
        if path:
            self.projectPath.setText(path)

    def get_project_data(self):
        return {
            "name": self.projectName.text(),
            "path": self.projectPath.text()
        }

import sys
import pandas as pd
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)
from PyQt5.QtCore import Qt
import json


class TextLabelingTool(QMainWindow):
    def __init__(self, df, save_path="labeled_data.csv"):
        super().__init__()
        self.df = df
        self.save_path = save_path
        self.current_index = 0

        self.setWindowTitle("Text Labeling Tool")
        self.setGeometry(500, 100, 800, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.comment_label = QLabel("", self)
        self.comment_label.setWordWrap(True)
        self.layout.addWidget(self.comment_label)

        self.index_label = QLabel("", self)
        self.layout.addWidget(self.index_label)

        self.current_label = QLabel("Current Label: ", self)
        self.layout.addWidget(self.current_label)

        self.rating_label = QLabel("Rating: ", self)
        self.layout.addWidget(self.rating_label)

        self.radio_group = QButtonGroup(self)
        self.positive_radio = QRadioButton("positive")
        self.negative_radio = QRadioButton("negative")
        self.neutral_radio = QRadioButton("neutral")

        self.radio_group.addButton(self.positive_radio)
        self.radio_group.addButton(self.negative_radio)
        self.radio_group.addButton(self.neutral_radio)

        self.layout.addWidget(self.positive_radio)
        self.layout.addWidget(self.negative_radio)
        self.layout.addWidget(self.neutral_radio)

        self.button_layout = QHBoxLayout()
        self.previous_button = QPushButton("Previous (←)", self)
        self.previous_button.clicked.connect(self.previous_comment)
        self.previous_button.setEnabled(False)

        self.next_button = QPushButton("Next (→)", self)
        self.next_button.clicked.connect(self.skip_comment)

        self.save_button = QPushButton("Save and Next (S)", self)
        self.save_button.clicked.connect(self.save_label)

        self.close_button = QPushButton("Close (Esc)", self)
        self.close_button.clicked.connect(self.close)

        self.button_layout.addWidget(self.previous_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.close_button)
        self.layout.addLayout(self.button_layout)

        # Thêm hộp nhập vị trí hàng và nút Go
        self.jump_layout = QHBoxLayout()
        self.jump_input = QLineEdit(self)
        self.jump_input.setPlaceholderText("Enter row number")
        self.jump_button = QPushButton("Go", self)
        self.jump_button.clicked.connect(self.jump_to_index)

        self.jump_layout.addWidget(self.jump_input)
        self.jump_layout.addWidget(self.jump_button)
        self.layout.addLayout(self.jump_layout)

        # Load current index from progress file if it exists
        self.load_progress()
        self.update_ui()

    def load_progress(self):
        progress_path = self.save_path.replace(".csv", "_progress.json")
        if os.path.isfile(progress_path):
            try:
                with open(progress_path, "r") as f:
                    data = json.load(f)
                    if "current_index" in data and 0 <= data["current_index"] < len(
                        self.df
                    ):
                        self.current_index = data["current_index"]
                        print(f"Resumed at index {self.current_index}")
            except Exception as e:
                print(f"Error loading progress file: {e}")

    def update_ui(self):
        if 0 <= self.current_index < len(self.df):
            row = self.df.iloc[self.current_index]
            self.comment_label.setText(f"Comment:\n{row['comment']}")
            self.current_label.setText(f"Current Label: {row['label']}")
            self.rating_label.setText(f"Rating: {row['rating']}")

            # Hiển thị số hàng hiện tại
            self.index_label.setText(f"Row: {self.current_index + 1}/{len(self.df)}")

            current_label = row["label"]
            if current_label == "positive":
                self.positive_radio.setChecked(True)
            elif current_label == "negative":
                self.negative_radio.setChecked(True)
            elif current_label == "neutral":
                self.neutral_radio.setChecked(True)
            else:
                self.radio_group.setExclusive(False)
                self.positive_radio.setChecked(False)
                self.negative_radio.setChecked(False)
                self.neutral_radio.setChecked(False)
                self.radio_group.setExclusive(True)

            self.previous_button.setEnabled(self.current_index > 0)
        else:
            self.comment_label.setText("Labeling completed!")
            self.index_label.setText(f"Row: {len(self.df)}/{len(self.df)}")
            self.current_label.setText("Current Label: None")
            self.rating_label.setText("Rating: None")
            self.save_button.setEnabled(False)
            self.next_button.setEnabled(False)

    def save_label(self):
        if self.current_index < len(self.df):
            new_label = None
            if self.positive_radio.isChecked():
                new_label = "positive"
            elif self.negative_radio.isChecked():
                new_label = "negative"
            elif self.neutral_radio.isChecked():
                new_label = "neutral"

            if new_label:
                new_row = self.df.iloc[self.current_index].copy()
                new_row["label"] = new_label

                file_exists = os.path.isfile(self.save_path)
                pd.DataFrame([new_row]).to_csv(
                    self.save_path, mode="a", header=not file_exists, index=False
                )

                print(
                    f"Saved new label at index {self.current_index}: {new_label}",
                    flush=True,
                )

            self.current_index += 1
            self.update_ui()

    def skip_comment(self):
        """Bỏ qua comment hiện tại, không lưu nhãn"""
        self.current_index += 1
        self.update_ui()

    def previous_comment(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_ui()

    def jump_to_index(self):
        """Nhảy đến hàng được nhập trong ô"""
        try:
            index = int(self.jump_input.text()) - 1
            if 0 <= index < len(self.df):
                self.current_index = index
                self.update_ui()
            else:
                print("Invalid index")
        except ValueError:
            print("Please enter a valid number")

    def keyPressEvent(self, event):
        """Xử lý sự kiện bàn phím"""
        if event.key() == Qt.Key_S:
            print("Shortcut S pressed")  # Debug kiểm tra phím
            self.save_label()
        elif event.key() == Qt.Key_Left:
            self.previous_comment()
        elif event.key() == Qt.Key_Right:
            self.skip_comment()
        elif event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        """Tự động lưu current_index khi cửa sổ đóng"""
        progress_path = self.save_path.replace(".csv", "_progress.json")
        with open(progress_path, "w") as f:
            json.dump({"current_index": self.current_index}, f)
        print(f"Saved current index to {progress_path}")
        super().closeEvent(event)


if __name__ == "__main__":
    unsure_labels_path = "../data/unsure-labels/phone_ratings_unsure_part1.csv"
    output_path = "../data/result_from_labelling_tool/data_part1.csv"

    double_check_data = pd.read_csv(unsure_labels_path, encoding="utf-8")

    app = QApplication(sys.argv)
    window = TextLabelingTool(double_check_data, output_path)
    window.show()
    sys.exit(app.exec_())

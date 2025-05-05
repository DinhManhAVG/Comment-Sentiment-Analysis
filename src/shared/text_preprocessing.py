import inspect
from pathlib import Path
import pandas as pd
import string
import re
import json
import py_vncorenlp
import os


def get_project_root() -> Path: # Nên trả về đối tượng Path
    """Lấy thư mục cha chứa file Python đang chạy."""
    # __file__ là một biến đặc biệt chứa đường dẫn đến file hiện tại
    current_file_path = Path(__file__).resolve()

    print("Current file path:", current_file_path.parent.parent.parent)

    # .parent sẽ lấy thư mục chứa file đó
    return current_file_path.parent.parent.parent

# Ghi nhớ thư mục gốc ngay từ đầu
PROJECT_ROOT = get_project_root()
print("Thu mục gốc:", PROJECT_ROOT)

# Đường dẫn đến thư mục chứa mô hình vncorenlp
ABSOLUTE_MODEL_PATH = os.path.join(PROJECT_ROOT, "attribute_extractor", "vncorenlp")
print("Using model path:", ABSOLUTE_MODEL_PATH)

# Khởi tạo model từ thư mục local
vncorenlp_model = py_vncorenlp.VnCoreNLP(save_dir=ABSOLUTE_MODEL_PATH, max_heap_size="-Xmx2g")

class VietnamesePreprocessingWithoutSpellCheck:
    def __init__(self):
        # Load Vietnamese stopwords
        pd_stopword = pd.read_csv(os.path.join(PROJECT_ROOT, "data/stopword/new_vietnamese_stopwords.csv"))
        self.stop_words = set(pd_stopword[pd_stopword["is_stopword"] == 1]["word"].tolist())
        with open("../../data/vi-abbreviations.json", "r", encoding="utf-8") as file:
            self.abbreviations = json.load(file)
            
            # Sort the abbreviations by length in descending order
            self.abbreviations = dict(sorted(self.abbreviations.items(), key=lambda item: len(item[0]), reverse=True))
        self.vncorenlp_model = vncorenlp_model

    def clean(self, x: str) -> str:
        """Clean the text by removing unwanted characters or patterns."""
        x = re.sub(r"\s+", " ", x) # replace multiple spaces with a single space

        # Replace '10d', '10đ', '10 điểm' to 'tốt' if > 8, 'khá' if > 5, 'tệ' if <= 5 (0-5)
        x = re.sub(r"\b(\d{1,2})(d|đ)\b", lambda match: "tốt" if int(match.group(1)) > 8 else "tạm" if int(match.group(1)) > 4 else "tệ", x) 

        # Loại bỏ ngày dd/mm/yyyy,...
        x = re.sub(r"\b\d{1,2}\s*[/-]\s*\d{1,2}(?:\s*[/-]\s*\d{2,4})?\b", "", x)
        x = re.sub(r"\b\d{1,2}\s*/\s*\d{4}\b", "", x)

        x = re.sub(r"\b0", "", x)  # remove digit 0 at the beginning

        # Remove phone number
        x = re.sub(r"(\d{10})", "", x) # remove phone number vietnam like 0954223654, 0856452325, 0123456789
        x = re.sub(r"(xx\s*){2,}", "", x) # remove phone number vietnam like xxx223654 hay 0905***654
        x = re.sub(r"(\*\s*)+", "", x)
        x = re.sub(r"\b\d+[xX\*]+\d+\b", "", x)  # Xoá các dãy số có chứa x hoặc *

        x = re.sub(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "", x) # remove email
        x = re.sub(r"\b\d+\b", lambda match: "" if int(match.group(0)) >= 100 else match.group(0), x) # remove number stand alone
        
        x = re.sub(r"\b\d+(?:\.\d+)?(tr\d+|tr|k)\b", "", x) # Remove numbers >= 100 or numbers with 'tr' or 'k' (1tr5, 130k, 11940k)
        x = re.sub(r"\b\d+(?:\.\d+)?tr\d+(?:\.\d+)?k\b", "", x) # Remove like that 11tr990k

        x = self.normalize_time_units(x)  # Normalize time units

        # Loại bỏ x% hay x %
        x = re.sub(r"\b\d+\s*%", "", x)
        x = re.sub(r"\s+", " ", x) # replace multiple spaces with a single space
        x = x.strip()  # Remove leading/trailing spaces
        return x
    
    def normalize_time_units(self, x: str) -> str:
        # Bước 1: Chuẩn hóa 30p, 2h, 10h30p → thêm khoảng trắng nếu cần
        x = re.sub(r"(\d+)([ph])\b", r"\1 \2", x)

        # Bước 2: Thay thế các đơn vị viết tắt thành đầy đủ
        x = re.sub(r"\b\d+\s*(p|phút)\b", "phút", x)
        x = re.sub(r"\b\d+\s*(h|giờ|tiếng)\b", "giờ", x)
        x = re.sub(r"\b\d+\s*(giây)\b", "giây", x)
        x = re.sub(r"\b\d+\s*(ngày)\b", "ngày", x)
        x = re.sub(r"\b\d+\s*(tháng)\b", "tháng", x)
        x = re.sub(r"\b\d+\s*(năm)\b", "năm", x)

        return x

    def to_lower(self, x: str) -> str:
        """Convert all text to lowercase."""
        return x.lower()

    def delete_punctuation(self, x: str) -> str:
        """Replace punctuation with space to avoid sticking words."""
        return re.sub(rf"[{re.escape(string.punctuation)}]", " ", x)

    def tokenize_text(self, x: str) -> list:
        """Tokenize the text into words."""
        return " ".join(vncorenlp_model.word_segment(x))

    def delete_stop_words(self, x: str) -> str:
        """Remove stopwords from the text."""
        return " ".join([word for word in x.split() if word not in self.stop_words])
    
    def replace_long_abbreviations(self, x: str) -> str:
        """Chủ yếu là replace các từ ghép không dấu thành từ ghép có dấu."""
        for key, value in self.abbreviations.items():
            if len(key.split()) > 1:
                pattern = re.compile(r"(?<!\w)" + re.escape(key) + r"(?!\w)")
                x = pattern.sub(value, x)
        return x

    def replace_abbreviations(self, x: str) -> str:
        """Replace abbreviations in the text using the loaded dictionary."""
        return  " ".join([self.abbreviations.get(word, word) for word in x.split()])
    
    def special_case(self, x: str) -> str:
        """Replace special cases in the text."""
        # Replace "mọi người" with "mọi_người"
        x = x.replace("mọi người", "mọi_người")
        return x

    def __call__(self, x: str):
        """Apply the preprocessing pipeline to the input text."""
        before_x = x
        x = self.clean(x)
        x = self.to_lower(x)
        x = self.replace_long_abbreviations(x)
        x = self.replace_abbreviations(x)
        x = self.delete_punctuation(x)
        x = self.tokenize_text(x)
        x = self.replace_abbreviations(x)
        x = self.special_case(x)

        x = self.delete_stop_words(x)
        return x
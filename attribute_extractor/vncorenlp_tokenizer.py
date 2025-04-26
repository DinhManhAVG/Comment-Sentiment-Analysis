import py_vncorenlp
import os

ABSOLUTE_MODEL_PATH = os.path.abspath("vncorenlp")
print("Using model path:", ABSOLUTE_MODEL_PATH)

# Khởi tạo model từ thư mục local
model = py_vncorenlp.VnCoreNLP(save_dir=ABSOLUTE_MODEL_PATH, max_heap_size="-Xmx2g")

while True:
    example = input("Nhập câu (hoặc 'exit' để thoát): ")
    if example.lower() == "exit":
        break
    result = model.word_segment(example)
    print("Kết quả:", result)
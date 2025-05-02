- % pin nên loại không
- sản phẩm 10 đ, khác gì với sản phẩm 3/5 điểm => Chưa giải quyết được => Cần đảo lại thứ tự 
- sản phẩm này "được"?? từ "được" xử lý sao??
- Các csv trong thư mục unsure-labels: chưa chắc chắn về label nên cần xem lại bằng cách chạy tool đánh nhãn
- File labeled_phone_rating_sure.csv: đã được đánh nhãn chắc chắn

## Note về preprocessing:
+ Replace punctuation nhưng chưa thay bằng khoảng trắng
+ Đang replace số kiểu gì vậy mà có chỗ có số chỗ không?
+ Từ "ngày", "tháng", "năm" có nên xem là stopword không?
+ EX: Mình thấy dt xài ổn, đáp ứng tiêu chí cơ bản là nghe gọi. Nghe mọi người nói 1 ngày hết pin, có thể do mọi người chưa tắt GPS và kết nối bluetooth đi, nên hao pin. Mình xài 4 5 ngày mới phải sạc lại. -> Câu này nên đánh label là [1,0] vì phần không tốt là nêu ra ý kiến `người khác` -> Xem "mọi người" có nên là stopword không?
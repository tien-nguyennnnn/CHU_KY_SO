Một ứng dụng web được xây dựng bằng Flask (Python) để cho phép người dùng tải lên, tải xuống và xác minh tính toàn vẹn của các file thông qua chữ ký số.

Tính năng chính





Tải lên file: Người dùng có thể tải file lên hệ thống với giới hạn kích thước 16MB.



Tải xuống file: Liệt kê và tải về các file đã được tải lên.



Xác minh chữ ký số: Tạo và kiểm tra chữ ký số bằng thuật toán SHA-256 để đảm bảo tính toàn vẹn của file



Bảo mật: Sử dụng CSRF protection, giới hạn kích thước file, và xử lý tên file an toàn.



Thông báo: Hiển thị thông báo thành công/lỗi rõ ràng cho người dùng.

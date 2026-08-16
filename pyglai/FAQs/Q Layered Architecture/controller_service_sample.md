Dưới đây là ví dụ thực tế bằng ngôn ngữ **Python** , sử dụng framework **FastAPI** (hoặc Flask) để minh họa rõ ràng sự phân tách giữa **Controller** và **Service** cho chức năng Tạo tài khoản người dùng (`Create User`). [[1](https://lp.jetbrains.com/python-unplugged), [2](https://medium.com/pythoneers/building-apis-in-python-basics-1815c6d4b5a4)]

1\. File Service (Xử lý Logic Nghiệp Vụ)

Service hoàn toàn không biết gì về HTTP request, header hay JSON. Nó chỉ nhận dữ liệu thô, thực hiện tính toán, kiểm tra logic nghiệp vụ và lưu vào database. [[1](https://www.tuvoc.com/blog/step-by-step-guide-to-python-web-development/), [2](https://blackboard.github.io/rest-apis/learn/examples/python-demo), [3](https://www.datanovia.com/learn/programming/python/additional-tutorials/file-io.html)]

python
    
    
    # services/user_service.py
    from datetime import datetime
    
    class UserService:
        def __init__(self, user_repository):
            self.user_repo = user_repository
    
        def register_user(self, email: str, password_raw: str) -> dict:
            # 1. Logic nghiệp vụ: Kiểm tra email đã tồn tại chưa
            if self.user_repo.find_by_email(email):
                raise ValueError("Email này đã được sử dụng!")
    
            # 2. Logic nghiệp vụ: Mã hóa mật khẩu (giả định)
            hashed_password = f"secure_hash_{password_raw}"
    
            # 3. Tạo cấu trúc dữ liệu người dùng mới
            new_user = {
                "email": email,
                "password": hashed_password,
                "created_at": datetime.now()
            }
    
            # 4. Gọi Repository để lưu vào database
            return self.user_repo.save(new_user)
    

Hãy thận trọng khi sử dụng mã.

2\. File Controller (Điều Phối Giao Tiếp)

Controller chịu trách nhiệm tiếp nhận HTTP Request, bắt lỗi (Exception) từ Service để chuyển thành mã lỗi HTTP tương ứng (400, 500) và trả về cho Client.

python
    
    
    # controllers/user_controller.py
    from fastapi import APIRouter, HTTPException, status
    from pydantic import BaseModel, EmailStr
    from services.user_service import UserService
    
    router = APIRouter()
    # Giả định user_service đã được khởi tạo và inject vào đây
    user_service = UserService(user_repository=...)
    
    # Định nghĩa cấu trúc dữ liệu đầu vào (Validation cơ bản)
    class RegisterRequest(BaseModel):
        email: EmailStr
        password: str
    
    @router.post("/register", status_code=status.HTTP_201_CREATED)
    def register(request_data: RegisterRequest):
        try:
            # Controller chuyển tiếp dữ liệu đã validate cơ bản cho Service xử lý
            result = user_service.register_user(
                email=request_data.email, 
                password_raw=request_data.password
            )
            
            # Controller định dạng lại kết quả trả về cho Client (Ẩn password đi)
            return {
                "status": "success",
                "data": {
                    "email": result["email"],
                    "created_at": result["created_at"]
                }
            }
            
        except ValueError as e:
            # Controller bắt lỗi nghiệp vụ từ Service và chuyển thành mã lỗi HTTP thích hợp
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(e)
            )
    

Hãy thận trọng khi sử dụng mã.

* * *

Điểm mấu chốt bạn có thể thấy qua code Python:

  * **Controller** xử lý các khái niệm của Web: `@router.post`, `HTTPException`, `status.HTTP_21_CREATED`. Nếu bạn chuyển ứng dụng từ Web sang chạy bằng dòng lệnh (CLI), file Controller này sẽ bị vứt bỏ hoàn toàn.
  * **Service** xử lý các khái niệm của Doanh nghiệp: Kiểm tra trùng email, mã hóa mật khẩu. Nếu bạn chuyển từ Web sang CLI, file `UserService` này **vẫn giữ nguyên 100%** và tái sử dụng được ngay.



Bạn có muốn áp dụng cấu trúc này vào một dự án **FastAPI, Flask** hay **Django** cụ thể nào không? Tôi có thể hướng dẫn bạn cách tổ chức **thư mục dự án** chuẩn cho kiến trúc này.


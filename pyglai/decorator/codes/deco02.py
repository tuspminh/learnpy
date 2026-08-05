def create_pw(init_pw):
    login_count = 0

    def login(pw):
        nonlocal login_count   
        if login_count >= 3:
            return f'pw invalid, your ac locked'
        
        if pw == init_pw:
            return f'login successful'
            login_count = 0
        else: 
            login_count += 1
            return f'pw invalid'

    return login

dang_nhap = create_pw("Admin123")

print(dang_nhap("12244"))
print(dang_nhap("dsdsf"))
print(dang_nhap("Admin123"))
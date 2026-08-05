
# enclosing
def outer():
    encloing_var = 50
    def inner():
        print(f"{encloing_var}")
    
    inner()

outer()

def tang_so():
    count:int = 0

    def dem():
        nonlocal count
        count += 1
        print(f'{count}')

    return dem

bo_dem = tang_so()

bo_dem()
bo_dem()
bo_dem()



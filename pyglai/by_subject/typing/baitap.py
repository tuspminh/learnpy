# he thong quan ly vi dien tu
from typing import Final, Literal

type LoaiGiaoDich = Literal["nap tien", "rut tien", "chuyen khoan"]
type LichSuGiaoDich = list[LoaiGiaoDich | int | None]
type CountryCode = Literal["VN", "US", "JP"]
DANH_SACH_MA_QUOC_GIA = Final[list[CountryCode]]


def xu_ly_vi(giaodich: LichSuGiaoDich) -> list[int] | None:
    list_money = [money for money in giaodich if isinstance(money, int)]
    return list_money if list_money else None


if __name__ == "__main__":
    giaodich = ["nap tien", 5000, "rut tien", 2000, "chuyen khoan", 500]
    print(xu_ly_vi(giaodich))
    giaodich = ["nap tien", "rut tien", "chuyen khoan"]
    print(xu_ly_vi(giaodich))

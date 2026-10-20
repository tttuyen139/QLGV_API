from decimal import Decimal


def format_vnd(so_tien) -> str:
    """Hiển thị VNĐ; giữ phần lẻ MONEY nếu có, không cắt số tiền."""
    text = format(Decimal(str(so_tien)), ',.4f')
    integer, fraction = text.split('.')
    fraction = fraction.rstrip('0')
    return integer.replace(',', '.') + (',' + fraction if fraction else '') + ' VNĐ'

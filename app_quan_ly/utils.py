def format_vnd(so_tien) -> str:
    """Định dạng tiền VNĐ, ví dụ 2250000 -> '2.250.000 VNĐ'"""
    return f"{int(so_tien):,} VNĐ".replace(',', '.')

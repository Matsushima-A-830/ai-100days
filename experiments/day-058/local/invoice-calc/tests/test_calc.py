from invoice_calc import total_with_tax


def test_basic():
    assert total_with_tax(100) == 110.0


def test_rounding():
    assert total_with_tax(19.99) == 21.99


def test_custom_rate():
    assert total_with_tax(50, rate=0.08) == 54.0

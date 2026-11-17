from hypothesis import given, strategies as st
from processor import decode_promo_voucher, calculate_seat_tier_price, parse_attendee_badge


@given(st.text() | st.none())
def test_decode_promo_voucher_no_crash(s):
    try:
        result = decode_promo_voucher(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"decode_promo_voucher crashed with: {e!r}"


@given(st.text() | st.none())
def test_calculate_seat_tier_price_safe(s):
    try:
        result = calculate_seat_tier_price(s)
        assert isinstance(result, (str, float))
    except Exception as e:
        assert False, f"calculate_seat_tier_price crashed with: {e!r}"


@given(st.text() | st.none())
def test_parse_attendee_badge_safe(s):
    try:
        result = parse_attendee_badge(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"parse_attendee_badge crashed with: {e!r}"

"""EI-02, EF-G2 : analyse des trames."""
import pytest
from gateway.frame import parse_frame, FrameError, crc16_ccitt_false, check_crc

def signed(payload: str) -> str:
    """Ajoute le membre crc à un objet JSON (sans crc)."""
    crc = crc16_ccitt_false(payload.encode())
    return payload[:-1] + f',"crc":"{crc:04X}"}}'

VALID = signed('{"id":"TN01","seq":12,"t":1700000000,"temp":25.50,"state":"NORMAL"}')

def test_EI02_crc_check_value_123456789_is_29B1():
    assert crc16_ccitt_false(b"123456789") == 0x29B1

def test_EI02_valid_frame_is_parsed():
    f = parse_frame(VALID)
    assert (f.node_id, f.seq, f.state) == ("TN01", 12, "NORMAL")
    assert f.temp == pytest.approx(25.5, abs=0.01)

def test_EI02_negative_temperature_is_parsed():
    f = parse_frame(signed('{"id":"TN01","seq":1,"t":0,"temp":-3.25,"state":"NORMAL"}'))
    assert f.temp == pytest.approx(-3.25)

@pytest.mark.parametrize("bad", [
    pytest.param(VALID.replace(VALID[-6:-2], "0000"), id="crc_wrong"),
    pytest.param(signed('{"id":"TN01","seq":12,"t":1700000000,"state":"NORMAL"}'), id="temp_missing"),
    pytest.param("{not json", id="syntax"),
    pytest.param(signed('{"id":"TN01","seq":12,"t":1700000000,"temp":"25.50","state":"NORMAL"}'), id="temp_string"),
    pytest.param(signed('{"id":"TN01","seq":-1,"t":1700000000,"temp":25.5,"state":"NORMAL"}'), id="seq_negative"),
    pytest.param(signed('{"id":"TN01","seq":1,"t":1,"temp":25.5,"state":"BOOM"}'), id="state_unknown"),
    pytest.param(signed('{"id":"TN01","seq":true,"t":1,"temp":25.5,"state":"NORMAL"}'), id="seq_bool"),
    pytest.param(signed('[1,2,3]'), id="not_object"),
    pytest.param("x" * 300, id="too_long"),
    pytest.param(VALID[:-8], id="truncated"),
])
def test_EI02_invalid_frames_are_rejected(bad):
    with pytest.raises(FrameError):
        parse_frame(bad)

def test_EI02_check_crc_without_member_is_false():
    assert check_crc('{"id":"TN01"}') is False



def test_EI02_invalid_json_with_valid_crc_reports_a_syntax_error():
    with pytest.raises(FrameError, match="^json:"):
        parse_frame(signed('{"id":}'))


def test_EI02_array_with_a_valid_crc_is_rejected():
    crc = crc16_ccitt_false(b'[{"id":"TN01"}]')
    text = f'[{{"id":"TN01","crc":"{crc:04X}"}}]'
    assert check_crc(text)
    with pytest.raises(FrameError, match="^format$"):
        parse_frame(text)


@pytest.mark.parametrize(("field", "value", "reason"), [
    ("id", '"TN 01"', "id"),
    ("t", "-1", "t"),
])
def test_EI02_rejects_invalid_identifier_and_timestamp(field, value, reason):
    fields = {"id": '"TN01"', "seq": "1", "t": "1", "temp": "25.5", "state": '"NORMAL"'}
    fields[field] = value
    payload = "{" + ",".join(f'"{key}":{item}' for key, item in fields.items()) + "}"
    with pytest.raises(FrameError, match=f"^{reason}$"):
        parse_frame(signed(payload))

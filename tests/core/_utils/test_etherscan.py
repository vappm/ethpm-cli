import pytest

from ethpm_cli._utils.etherscan import is_etherscan_uri


@pytest.mark.parametrize(
    "uri,expected",
    (
        ("etherscan://6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/1", True),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/1", True),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/3", True),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/4", True),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/5", True),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/42", True),
        ("etherscan:///1", False),
        ("etherscan://invalid/1", False),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729", False),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/", False),
        ("etherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/10", False),
        ("://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/1", False),
        ("xetherscan://0x6b5DA3cA4286Baa7fBaf64EEEE1834C7d430B729/1", False),
    ),
)
def test_is_etherscan_uri(uri, expected):
    actual = is_etherscan_uri(uri)
    assert actual == expected

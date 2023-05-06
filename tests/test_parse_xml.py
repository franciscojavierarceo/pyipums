from unittest import TestCase
from src.pypums.parse_xml import (
    read_ipums_ddi,
    _to_int,
    remove_namespace,
)

class TryTesting(TestCase):
    expected = ""

    def test__to_int(self):
        self.assertEqual(_to_int('1'), 1)

    def test_remove_namespace(self):
        self.assertEqual(
            remove_namespace(
                "{ddi:codebook:2_5}it works",
            ),
        "it works",
        )
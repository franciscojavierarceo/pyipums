import os
from unittest import TestCase
import xml.etree.ElementTree as ET
from src.pyipums.parse_xml import (
    read_ipums_ddi,
    _to_int,
    remove_namespace,
    get_file_metadata,
    get_field_metadata,
)


class TestParseMetaDataXML(TestCase):
    def test__to_int(self):
        self.assertEqual(_to_int("1"), 1)

    def test_remove_namespace(self):
        self.assertEqual(
            remove_namespace(
                "{ddi:codebook:2_5}it works",
            ),
            "it works",
        )

    def test_get_file_metadata(self):
        metadata = {}
        absolute_path = os.path.dirname(__file__)
        full_path = os.path.join(absolute_path, "./metadata_example.xml")
        root = ET.parse(os.path.expanduser(full_path))
        codebook = root.getroot()
        ddi_fields = [
            "column_metadata",
            "columns",
            "column_types",
            "column_specs",
            "column_dtypes",
        ]
        metadata["file_metadata"] = get_file_metadata(codebook)

        self.assertEqual(
            len(metadata["file_metadata"]),
            10,
        )
        metadata = get_field_metadata(codebook, metadata)
        for field in ddi_fields:
            self.assertGreater(len(metadata.get(field)), 0)

        self.assertEqual(
            metadata.get("column_specs")[0],
            (0, 4),
        )

        self.assertEqual(
            metadata.get("column_metadata")[0],
            ("YEAR", "discrete"),
        )

        self.assertEqual(
            metadata.get("column_dtypes")[0],
            str,
        )
        self.assertEqual(
            len(metadata.get("columns")),
            149,
        )

import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.data.io import load_table


class TestDataIo(unittest.TestCase):
    def test_load_table_reads_csv_with_read_csv(self):
        expected = pd.DataFrame([{"a": 1}])
        input_path = Path("input.csv")

        with patch("src.data.io.pd.read_csv", return_value=expected) as read_csv:
            actual = load_table(input_path)

        read_csv.assert_called_once_with(input_path)
        self.assertTrue(actual.equals(expected))

    def test_load_table_reads_ods_with_read_excel(self):
        expected = pd.DataFrame([{"a": 1}])
        input_path = Path("input.ods")

        with patch("src.data.io.pd.read_excel", return_value=expected) as read_excel:
            actual = load_table(input_path)

        read_excel.assert_called_once_with(input_path)
        self.assertTrue(actual.equals(expected))

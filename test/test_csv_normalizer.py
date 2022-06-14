import os
import shutil
import unittest

from app.normalizer import parse_args, normalize_csv_data, NormalizedRow


class ArgumentParserTestCase(unittest.TestCase):
    def test_accepts_input_and_output_file_args(self):
        args = parse_args(["input.csv", "output.csv"])
        self.assertTrue(args.input_file == "input.csv")
        self.assertTrue(args.output_file == "output.csv")


class CSVNormalizerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir("./data/outputs")

    def test_csv_normalizer(self):
        normalize_csv_data("./data/sample.csv", "./data/outputs/output.csv")

    def tearDown(self) -> None:
        shutil.rmtree("./data/outputs")


class MassageDataTestCase(unittest.TestCase):
    def test_convert_to_rcf_3339(self):
        timestamp = "4/1/11 11:00:00 AM"
        result = NormalizedRow().convert_to_rcf_3339(timestamp)

        self.assertEqual("2011-04-01T14:00:00", result)


if __name__ == "__main__":
    unittest.main()

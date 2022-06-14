import sys
import argparse
from csv import DictReader, DictWriter
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass(order=True)
class NormalizedRow:
    timestamp: str
    address: str
    zip_code: str
    full_name: str
    foo_duration: float
    bar_duration: float
    total_duration: float
    notes: str

    def __init__(
        self,
        timestamp: str,
        address: str,
        zip_code: str,
        full_name: str,
        foo_duration: str,
        bar_duration: str,
        notes: str,
    ):
        self.timestamp = self.convert_to_rcf_3339(self.encode(timestamp))
        self.address = self.encode(address)
        self.zip_code = self.encode(zip_code).zfill(5)
        self.full_name = self.encode(full_name).upper()
        self.foo_duration = self.to_seconds(foo_duration)
        self.bar_duration = self.to_seconds(bar_duration)
        self.total_duration = self.foo_duration + self.bar_duration
        self.notes = self.encode(notes)

        self.data = asdict(self)

    def __getitem__(self, item):
        return self.data[item]

    def encode(self, string: str, encoding: str = "utf-8") -> str:
        return string.encode(encoding, errors="replace").decode()

    def apply_map(self, column_order, column_mapping, newline: str = "\n"):
        line = str()
        row = dict()
        for column in column_order:
            row[column] = self[column_mapping[column]]

        return row

    def to_seconds(self, time_string: str) -> float:
        hours, minutes, rest = time_string.split(":")
        seconds, microseconds = rest.split(".")

        return timedelta(
            hours=int(hours),
            minutes=int(minutes),
            seconds=int(seconds),
            microseconds=int(microseconds),
        ).total_seconds()

    def convert_to_rcf_3339(self, timestamp: str) -> str:
        """
        Converts a timestamp string with format '%m/%d/%y %H:%M:%S %p' to RCF 3339
        :param timestamp: a date time string
        :return:
        """
        format = "%m/%d/%y %H:%M:%S %p"
        pacific_to_eastern = timedelta(hours=3)  # Difference between EST and PDT
        pacific_time = datetime.strptime(timestamp, format)
        return (pacific_time + pacific_to_eastern).isoformat()


def normalize_csv_data(input_csv_path: str, output_csv_path: str) -> None:

    # Maps column names from source to normalized
    raw_to_normalized_map = {
        "Timestamp": "timestamp",
        "Address": "address",
        "ZIP": "zip_code",
        "FullName": "full_name",
        "FooDuration": "foo_duration",
        "BarDuration": "bar_duration",
        "TotalDuration": "total_duration",
        "Notes": "notes",
    }

    with open(input_csv_path, mode="r") as read_obj:
        with open(output_csv_path, mode="w", encoding="utf-8", newline="\n") as write_obj:
            csv_dict_reader = DictReader(read_obj)
            column_names = csv_dict_reader.fieldnames
            csv_dict_writer = DictWriter(write_obj, fieldnames=column_names)
            csv_dict_writer.writeheader()
            normalized_rows = list()
            for row in csv_dict_reader:
                try:
                    normal_row = NormalizedRow(
                        timestamp=row["Timestamp"],
                        address=row["Address"],
                        zip_code=row["ZIP"],
                        full_name=row["FullName"],
                        foo_duration=row["FooDuration"],
                        bar_duration=row["BarDuration"],
                        notes=row["Notes"],
                    )

                    normalized_rows.append(
                        normal_row.apply_map(
                            column_order=column_names,
                            column_mapping=raw_to_normalized_map,
                        )
                    )

                except UnicodeEncodeError as exp:
                    print(exp, sys.exc_info())

            print(f"Number of rows written to '{output_csv_path}': {len(normalized_rows)}")
            csv_dict_writer.writerows(normalized_rows)


# TODO: Consider making this a factory method which takes a parser config
def parse_args(arguments: list) -> dict:
    parser = argparse.ArgumentParser(description="A program to parse CSV data!")
    parser.add_argument(
        "input_file",
        help="Path to the input file where data to be normalized is stored",
    )
    parser.add_argument(
        "output_file",
        help="The path to the output file where normalized data will be written",
    )

    return parser.parse_args(arguments)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])  # Sends args after "normalizer.py"
    normalize_csv_data(args.input_file, args.output_file)

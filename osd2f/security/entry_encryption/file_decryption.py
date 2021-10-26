import abc
import csv
import json
import pathlib
from typing import Any, Dict, Iterable, List

from ...definitions.submissions import (
    EncryptedEntry,
    EncryptedSubmission,
    OutputSubmission,
)
from ...logger import logger
from ...security.entry_encryption.secure_entry_singleton import SecureEntry


class EntryFile(abc.ABC):
    def __init__(self, filename: pathlib.Path, read_mode: bool):
        self.read_mode = read_mode
        if not read_mode and pathlib.Path(filename).exists():
            raise Exception(f"File {filename} already exists!")

        parent_dir = pathlib.Path(filename).parent
        if not pathlib.Path(parent_dir).exists():
            pathlib.Path(parent_dir).mkdir(parents=True, exist_ok=True)

        if read_mode:
            self.file_obj = open(filename)
        else:
            self.file_obj = open(filename, "w+")

    def __del__(self):
        if hasattr(self, "file_obj") and not self.file_obj.closed:
            self.file_obj.close()

    def __exit__(self):
        if hasattr(self, "file_obj") and not self.file_obj.closed:
            self.file_obj.close()
        self.__del__()

    @abc.abstractmethod
    def read_entries(self) -> Iterable[OutputSubmission]:
        return dict()

    @abc.abstractmethod
    def append(self, entry: OutputSubmission) -> None:
        return


class JSONFile(EntryFile):
    def __init__(self, filename: pathlib.Path, read_mode: bool):
        self.entries: List[Dict[str, Any]] = []
        super().__init__(filename, read_mode)

    def read_entries(self) -> Iterable[OutputSubmission]:
        for raw_submission in json.load(self.file_obj):
            submission = EncryptedSubmission.parse_obj(raw_submission)
            try:
                EncryptedEntry.parse_obj(submission.entry)
            except ValueError:
                logger.warning("Encountered an unencrypted entry!")
                yield OutputSubmission.parse_obj(raw_submission)
            decrypted_sub = OutputSubmission.parse_obj(raw_submission)
            decrypted_sub.entry = SecureEntry.read_entry_field(decrypted_sub.entry)
            yield decrypted_sub

    def append(self, entry: OutputSubmission) -> None:
        self.entries.append(entry.dict())

    def __del__(self):
        if (
            hasattr(self, "file_obj")
            and not self.file_obj.closed
            and not self.read_mode
        ):
            json.dump(self.entries, self.file_obj)
        self.entries = []
        return super().__del__()


class CSVFile(EntryFile):
    def __init__(self, filename: pathlib.Path, read_mode: bool):
        super().__init__(filename, read_mode)
        if not read_mode:
            headers = OutputSubmission.__fields__.keys()
            self.writer = csv.DictWriter(self.file_obj, fieldnames=headers)
            self.writer.writeheader()

    def read_entries(self) -> Iterable[OutputSubmission]:
        line = self.file_obj.readline().strip()
        header = line.split(csv.excel.delimiter)
        reader = csv.DictReader(self.file_obj, fieldnames=header)
        for e in reader:
            re: Dict[str, Any] = {k: v for k, v in e.items() if k != "entry"}
            re["entry"] = SecureEntry.read_entry_field(eval(e["entry"]))
            yield OutputSubmission.parse_obj(re)

    def append(self, entry: OutputSubmission) -> None:

        self.writer.writerow(entry.dict())


def decrypt_file(input_path: pathlib.Path, output_path: pathlib.Path) -> int:

    input_file: EntryFile

    if input_path.suffix == ".json":
        input_file = JSONFile(input_path, read_mode=True)

    elif input_path.suffix == ".csv":
        input_file = CSVFile(input_path, read_mode=True)
    else:
        raise NotImplementedError(
            f"Unknown INPUT file type {input_path.suffix}, "
            "make sure you unzipped the file."
        )

    output_file: EntryFile

    if output_path.suffix == ".json":
        output_file = JSONFile(output_path, read_mode=False)
    elif output_path.suffix == ".csv":
        output_file = CSVFile(output_path, read_mode=False)
    else:
        raise NotImplementedError(
            f"Unknown OUTPUT file type {output_path.suffix}, "
            "output should end with `.csv` or `.json`."
        )

    touched_entries = 0
    for entry in input_file.read_entries():
        output_file.append(entry)
        touched_entries += 1

    return touched_entries

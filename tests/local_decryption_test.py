import csv
import os
import shutil

from aiounittest.case import AsyncTestCase

from osd2f.definitions.submissions import OutputSubmission, Submission, SubmissionList


class test_local_decryption(AsyncTestCase):
    """Set of end-to-end tests of local decryption"""

    def setUp(self) -> None:
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")
        return os.makedirs("tmp", exist_ok=True)

    def tearDown(self) -> None:
        return shutil.rmtree("tmp")

    async def test_json_files(self):
        from osd2f.security.entry_encryption.file_decryption import decrypt_file
        import json
        from osd2f.database import (
            initialize_database,
            stop_database,
            get_submissions,
            insert_submission_list,
        )
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry
        import pathlib

        subs = SubmissionList(
            __root__=[
                Submission(
                    submission_id=f"s_{i}",
                    filename=f"file_{i}",
                    n_deleted=i,
                    entries=[{"content": f"value_{i}.{ii}"} for ii in range(10)],
                )
                for i in range(10)
            ]
        )

        await initialize_database("sqlite://:memory:")

        SecureEntry.set_secret("secret")

        # turn off decryption on reads so the retrieved subs keep their encryption
        SecureEntry.decrypt_on_read(must_decrypt_on_read=False)

        await insert_submission_list(subs)

        esubs = await get_submissions()

        encrypted_file = pathlib.Path("tmp/enc.json")
        decrypted_file = pathlib.Path("tmp/decr.json")

        json.dump(esubs, open(encrypted_file, "w"))

        # enable decryption again
        SecureEntry.decrypt_on_read(must_decrypt_on_read=True)
        decrypt_file(encrypted_file, decrypted_file)

        decrypted_subs = [
            OutputSubmission.parse_obj(s) for s in json.load(open(decrypted_file))
        ]

        original_values = {
            entry["content"] for sub in subs.__root__ for entry in sub.entries
        }
        decrypted_values = {s.entry["content"] for s in decrypted_subs}

        self.assertFalse(original_values.difference(decrypted_values))

        await stop_database()

    async def test_csv_files(self):
        from osd2f.security.entry_encryption.file_decryption import decrypt_file
        from osd2f.database import (
            initialize_database,
            stop_database,
            get_submissions,
            insert_submission_list,
        )
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry
        import pathlib

        subs = SubmissionList(
            __root__=[
                Submission(
                    submission_id=f"s_{i}",
                    filename=f"file_{i}",
                    n_deleted=i,
                    entries=[{"content": f"value_{i}.{ii}"} for ii in range(10)],
                )
                for i in range(10)
            ]
        )

        await initialize_database("sqlite://:memory:")

        SecureEntry.set_secret("secret")

        # turn off decryption on reads so the retrieved subs keep their encryption
        SecureEntry.decrypt_on_read(must_decrypt_on_read=False)

        await insert_submission_list(subs)

        esubs = await get_submissions()

        encrypted_file = pathlib.Path("tmp/enc.csv")
        decrypted_file = pathlib.Path("tmp/decr.csv")

        with open(encrypted_file, "w") as f:
            dr = csv.DictWriter(f, fieldnames=OutputSubmission.__fields__.keys())
            dr.writeheader()
            dr.writerows(esubs)

        # enable decryption again
        SecureEntry.decrypt_on_read(must_decrypt_on_read=True)
        decrypt_file(encrypted_file, decrypted_file)

        with open(decrypted_file) as f:
            h = f.readline().strip().split(csv.excel.delimiter)
            decrypted_subs = []
            for s in csv.DictReader(f, fieldnames=h):
                s["entry"] = eval(s["entry"])
                decrypted_subs.append(OutputSubmission.parse_obj(s))

        original_values = {
            entry["content"] for sub in subs.__root__ for entry in sub.entries
        }
        decrypted_values = {s.entry["content"] for s in decrypted_subs}

        self.assertFalse(original_values.difference(decrypted_values))

        await stop_database()

    async def test_json_to_csv_files(self):
        from osd2f.security.entry_encryption.file_decryption import decrypt_file
        import json
        from osd2f.database import (
            initialize_database,
            stop_database,
            get_submissions,
            insert_submission_list,
        )
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry
        import pathlib

        subs = SubmissionList(
            __root__=[
                Submission(
                    submission_id=f"s_{i}",
                    filename=f"file_{i}",
                    n_deleted=i,
                    entries=[{"content": f"value_{i}.{ii}"} for ii in range(10)],
                )
                for i in range(10)
            ]
        )

        await initialize_database("sqlite://:memory:")

        SecureEntry.set_secret("secret")

        # turn off decryption on reads so the retrieved subs keep their encryption
        SecureEntry.decrypt_on_read(must_decrypt_on_read=False)

        await insert_submission_list(subs)

        esubs = await get_submissions()

        encrypted_file = pathlib.Path("tmp/enc.json")
        decrypted_file = pathlib.Path("tmp/decr.csv")

        json.dump(esubs, open(encrypted_file, "w"))

        # enable decryption again
        SecureEntry.decrypt_on_read(must_decrypt_on_read=True)
        decrypt_file(encrypted_file, decrypted_file)

        with open(decrypted_file) as f:
            h = f.readline().strip().split(csv.excel.delimiter)
            decrypted_subs = []
            for s in csv.DictReader(f, fieldnames=h):
                s["entry"] = eval(s["entry"])
                decrypted_subs.append(OutputSubmission.parse_obj(s))

        original_values = {
            entry["content"] for sub in subs.__root__ for entry in sub.entries
        }
        decrypted_values = {s.entry["content"] for s in decrypted_subs}

        self.assertFalse(original_values.difference(decrypted_values))

        await stop_database()

    async def test_csv_to_json_files(self):
        from osd2f.security.entry_encryption.file_decryption import decrypt_file
        import json
        from osd2f.database import (
            initialize_database,
            stop_database,
            get_submissions,
            insert_submission_list,
        )
        from osd2f.security.entry_encryption.secure_entry_singleton import SecureEntry
        import pathlib

        subs = SubmissionList(
            __root__=[
                Submission(
                    submission_id=f"s_{i}",
                    filename=f"file_{i}",
                    n_deleted=i,
                    entries=[{"content": f"value_{i}.{ii}"} for ii in range(10)],
                )
                for i in range(10)
            ]
        )

        await initialize_database("sqlite://:memory:")

        SecureEntry.set_secret("secret")

        # turn off decryption on reads so the retrieved subs keep their encryption
        SecureEntry.decrypt_on_read(must_decrypt_on_read=False)

        await insert_submission_list(subs)

        esubs = await get_submissions()

        encrypted_file = pathlib.Path("tmp/enc.csv")
        decrypted_file = pathlib.Path("tmp/decr.json")

        with open(encrypted_file, "w") as f:
            dr = csv.DictWriter(f, fieldnames=OutputSubmission.__fields__.keys())
            dr.writeheader()
            dr.writerows(esubs)

        # enable decryption again
        SecureEntry.decrypt_on_read(must_decrypt_on_read=True)
        decrypt_file(encrypted_file, decrypted_file)

        decrypted_subs = [
            OutputSubmission.parse_obj(s) for s in json.load(open(decrypted_file))
        ]

        original_values = {
            entry["content"] for sub in subs.__root__ for entry in sub.entries
        }
        decrypted_values = {s.entry["content"] for s in decrypted_subs}

        self.assertFalse(original_values.difference(decrypted_values))

        await stop_database()

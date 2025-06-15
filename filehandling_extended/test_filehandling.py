# test_fielhandling.py

import filecmp
import pathlib
import shutil
import unittest
from filehandling import *


# Define class to test the program
class TestFilehandling(unittest.TestCase):

    if platform.system() == "Windows":
        _test_path = pathlib.Path("C:/temp")
    else:
        _test_path = pathlib.Path("./unittest_testdir")

    def setUp(self) -> None:
        """Set up the test environment."""
        # Create a test directory if it doesn't exist
        if not os.path.exists(self._test_path):
            os.makedirs(self._test_path)

    def tearDown(self) -> None:
        """Clean up the test environment."""
        # Remove the test directory and its contents
        if os.path.exists(self._test_path):
            shutil.rmtree(self._test_path)

    def _create_test_file(self, filename: pathlib.Path) -> None:
        """Helper function to create a test file with given content."""
        with open(filename, "w") as f:
            for i in range(1_000_000):
                content = f"{i:4n} This is a test file for file handling.\n"
                f.write(content)

    def test_copy_with_callback(self) -> None:
        callback_called = False

        def callback(copied: int, filesize: int) -> int:
            """Callback function to track progress."""
            nonlocal callback_called
            callback_called = True
            # print(f"Copied {copied*100//filesize:3} % of the file.")
            return 1  # No cancellation

        source_file = self._test_path / "test_source.txt"
        destination_file = self._test_path / "test_destination.txt"
        # Create a test source file
        self._create_test_file(source_file)
        copy_file(source_file, destination_file, callback, 4 * 1024)
        self.assertTrue(callback_called, "Callback was not called during file copy.")
        # Check if the destination file exists and has the correct content
        self.assertTrue(os.path.isfile(destination_file))
        self.assertTrue(filecmp.cmp(source_file, destination_file, False), "Files do not match after copying.")
        # Clean up test files
        os.remove(destination_file)

    def test_copy_with_callback_canceling(self) -> None:
        callback_called = 0

        def callback(copied: int, filesize: int) -> int:
            """Callback function to track progress."""
            nonlocal callback_called
            callback_called += 1
            # print(f"Copied {copied*100//filesize:3} % of the file.")
            return 1 if callback_called < 3 else 0

        source_file = self._test_path / "test_source.txt"
        destination_file = self._test_path / "test_destination.txt"
        self._create_test_file(source_file)
        copy_file(source_file, destination_file, callback, 4 * 1024)
        self.assertTrue(callback_called > 0, "Callback was not called during file copy.")
        self.assertTrue(not os.path.isfile(destination_file))

    def test_copy_with_no_callback(self) -> None:
        source_file = self._test_path / "test_source.txt"
        destination_file = self._test_path / "test_destination.txt"
        self._create_test_file(source_file)
        copy_file(source_file, destination_file, None, 4 * 1024)
        self.assertTrue(filecmp.cmp(source_file, destination_file), "Files do not match after copying.")

    def test_copy_with_callback_no_src(self) -> None:
        source_file = self._test_path / "test_source_not_exist.txt"
        destination_file = self._test_path / "test_destination.txt"
        with self.assertRaises(FileNotFoundError):
            copy_file(source_file, destination_file, None, 4 * 1024)
        # Check if the destination file exists and has the correct content
        self.assertTrue(not os.path.isfile(destination_file))

    def test_copy_with_callback_not_callable(self) -> None:
        source_file = self._test_path / "test_source.txt"
        destination_file = self._test_path / "test_destination.txt"
        self._create_test_file(source_file)
        with self.assertRaises(TypeError):
            copy_file(source_file, destination_file, destination_file, 4 * 1024)  # type: ignore
        # Check if the destination file exists and has the correct content
        self.assertTrue(not os.path.isfile(destination_file))

    def test_copy_with_callback_no_destination(self) -> None:
        source_file = self._test_path / "test_source.txt"
        destination_file = self._test_path / "test_destination.txt"
        self._create_test_file(source_file)
        with self.assertRaises(TypeError):
            copy_file(source_file, None, None, 4 * 1024)  # type: ignore
        # Check if the destination file exists and has the correct content
        self.assertTrue(not os.path.isfile(destination_file))

    def test_copy_with_callback_dest_is_dir(self) -> None:
        source_file = self._test_path / "test_source.txt"
        destination_file = self._test_path / "test_destination_dir"
        destination_file.mkdir(exist_ok=True)

        self._create_test_file(source_file)
        copy_file(source_file, destination_file, None, 4 * 1024)  # type: ignore
        # Check if the destination file exists and has the correct content
        destination_file = destination_file / source_file.name
        self.assertTrue(os.path.isfile(destination_file))
        self.assertTrue(filecmp.cmp(source_file, destination_file), "Files do not match after copying.")

    def test_compare_filenames(self) -> None:
        file1 = self._test_path / "file1.txt"
        file2 = self._test_path / "file2.txt"
        file3 = self._test_path / "file3.txt"

        self.assertEqual(compare_filenames(str(file1), str(file2)), -1)
        self.assertEqual(compare_filenames(str(file2), str(file1)), 1)
        self.assertEqual(compare_filenames(str(file1), str(file1)), 0)
        self.assertEqual(compare_filenames(str(file2), str(file3)), -1)

    def test_compare_filenames_case_insensitive(self) -> None:
        file1 = self._test_path / "file1.txt"
        file2 = self._test_path / "FILE1.TXT"
        if platform.system() == "Windows":
            self.assertEqual(compare_filenames(str(file1), str(file2)), 0)
            self.assertEqual(compare_filenames(str(file2), str(file1)), 0)
        else:
            self.assertEqual(compare_filenames(str(file1), str(file2)), 1)
            self.assertEqual(compare_filenames(str(file2), str(file1)), -1)

    def test_compare_filenames_different_extensions(self) -> None:
        file1 = self._test_path / "file1.txt"
        file2 = self._test_path / "file2.md"

        self.assertEqual(compare_filenames(str(file1), str(file2)), -1)
        self.assertEqual(compare_filenames(str(file2), str(file1)), 1)

    def test_compare_filenames_empty(self) -> None:
        file1 = self._test_path / "file1.txt"
        file2 = self._test_path / "file2.txt"

        self.assertEqual(compare_filenames("", str(file2)), -1)
        self.assertEqual(compare_filenames(str(file1), ""), 1)
        self.assertEqual(compare_filenames("", ""), 0)

    def test_compare_filenames_unicode(self) -> None:
        file1 = self._test_path / "file_1.txt"
        file2 = self._test_path / "file_1_ü.txt"

        self.assertEqual(compare_filenames(str(file1), str(file2)), -1)
        self.assertEqual(compare_filenames(str(file2), str(file1)), 1)
        self.assertEqual(compare_filenames(str(file1), str(file1)), 0)
        self.assertEqual(compare_filenames(str(file2), str(file2)), 0)

    def test_compare_filenames_with_path(self) -> None:
        file1 = self._test_path / "subdir" / "file1.txt"
        file2 = self._test_path / "subdir" / "file2.txt"

        self.assertEqual(compare_filenames(str(file1), str(file2)), -1)
        self.assertEqual(compare_filenames(str(file2), str(file1)), 1)
        self.assertEqual(compare_filenames(str(file1), str(file1)), 0)
        self.assertEqual(compare_filenames(str(file2), str(file2)), 0)

    def test_set_filetime(self) -> None:
        filename = self._test_path / "test_filetime.txt"
        self._create_test_file(filename)

        # Set file times
        creation_time = datetime.datetime(2020, 1, 1, 12, 0, 0)
        modify_time = datetime.datetime(2021, 1, 1, 12, 0, 0)
        access_time = datetime.datetime(2022, 1, 1, 12, 0, 0)

        if platform.system() == "Windows":
            set_filetime(str(filename), creation_time, modify_time, access_time)
        else:
            # On Linux, creation time is not supported, so we pass None
            set_filetime(str(filename), None, modify_time, access_time)

        # Check if the file times were set correctly
        stat_info = os.stat(filename)
        if platform.system() == "Windows":
            self.assertEqual(stat_info.st_birthtime, creation_time.timestamp()) # type: ignore
        else:
            # On Linux, creation time is not available, so we skip this check
            pass
        self.assertEqual(stat_info.st_mtime, modify_time.timestamp())
        self.assertEqual(stat_info.st_atime, access_time.timestamp())

    def test_set_filetime_no_creation_time(self) -> None:
        filename = self._test_path / "test_filetime_no_creation.txt"
        self._create_test_file(filename)

        # Set file times without creation time
        modify_time = datetime.datetime(2021, 1, 1, 12, 0, 0)
        access_time = datetime.datetime(2022, 1, 1, 12, 0, 0)

        set_filetime(str(filename), None, modify_time, access_time)

        # Check if the file times were set correctly
        stat_info = os.stat(filename)
        self.assertEqual(stat_info.st_mtime, modify_time.timestamp())
        self.assertEqual(stat_info.st_atime, access_time.timestamp())

    def test_set_filetime_no_modify_time(self) -> None:
        filename = self._test_path / "test_filetime_no_modify.txt"
        self._create_test_file(filename)

        # Set file times without modify time
        creation_time = datetime.datetime(2020, 1, 1, 12, 0, 0)
        access_time = datetime.datetime(2022, 1, 1, 12, 0, 0)

        set_filetime(str(filename), creation_time, None, access_time)

        # Check if the file times were set correctly
        stat_info = os.stat(filename)
        if platform.system() == "Windows":
            self.assertEqual(stat_info.st_ctime, creation_time.timestamp())
        self.assertEqual(stat_info.st_atime, access_time.timestamp())

    def test_set_filetime_no_access_time(self) -> None:
        filename = self._test_path / "test_filetime_no_access.txt"
        self._create_test_file(filename)

        # Set file times without access time
        creation_time = datetime.datetime(2020, 1, 1, 12, 0, 0)
        modify_time = datetime.datetime(2021, 1, 1, 12, 0, 0)

        set_filetime(str(filename), creation_time, modify_time, None)

        # Check if the file times were set correctly
        stat_info = os.stat(filename)
        if platform.system() == "Windows":
            self.assertEqual(stat_info.st_ctime, creation_time.timestamp())
        self.assertEqual(stat_info.st_mtime, modify_time.timestamp())

    def test_set_filetime_all_none(self) -> None:
        filename = self._test_path / "test_filetime_all_none.txt"
        self._create_test_file(filename)

        # Set file times to None
        set_filetime(str(filename), None, None, None)

        # Check if the file times were not changed
        stat_info = os.stat(filename)
        self.assertNotEqual(stat_info.st_ctime, 0)
        self.assertNotEqual(stat_info.st_mtime, 0)
        self.assertNotEqual(stat_info.st_atime, 0)

    def test_set_filetime_invalid_file(self) -> None:
        filename = self._test_path / "invalid_file.txt"

        # Attempt to set file times on a non-existent file
        set_filetime(str(filename), None, None, None)

    def test_set_filetime_invalid_datetime(self) -> None:
        filename = self._test_path / "test_filetime_invalid_datetime.txt"
        self._create_test_file(filename)

        # Attempt to set file times with an invalid datetime
        if platform.system() == "Windows":
             with self.assertRaises(OSError):
                set_filetime(str(filename), "invalid", None, None) # type: ignore
        else:
            set_filetime(str(filename), "invalid", None, None) # type: ignore

    def test_get_volumelabel(self) -> None:
        volumelabel = get_volumelabel(self._test_path)
        # Check if the volumelabel is not empty
        self.assertNotEqual(volumelabel, "???", "Volumelabel should not be '???'")
        if platform.system() == "Linux":
            self.assertEqual(volumelabel, "root", "Volumelabel should be 'root'")
        else:
            self.assertEqual(volumelabel, "WinDrive", "Volumelabel should be 'WinDrive' if set in Windows!")

    def test_get_volumelabel_usb_drive(self) -> None:
        if platform.system() == "Windows":
            path = pathlib.Path("E:\\SH")
        else:
            path = pathlib.Path("/media/heribert/DASI_Linux/SH_L")
        if not path.exists():
            self.skipTest(f"Test path {path} does not exist. Skipping test.")
        # Assuming the test path is a USB drive, we can check the volumelabel
        volumelabel = get_volumelabel(path)
        # Check if the volumelabel is not empty
        self.assertTrue(volumelabel, "Volumelabel should not be empty.")
        self.assertNotEqual(volumelabel, "???", "Volumelabel should not be '???'")
        if platform.system() == "Linux":
            self.assertEqual(volumelabel, "DASI_Linux", "Volumelabel should be 'DASI_Linux'")
        else:
            self.assertEqual(volumelabel, "DaSi", "Volumelabel should be 'DaSi'")

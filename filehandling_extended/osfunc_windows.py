"""
OS specific functions for filehandling_extended
WINDOWS

Author: Heribert Füchtenhans
Version: 2025.6.18
"""

import contextlib
import datetime
import os
import pathlib
import stat
from typing import Any, Callable, Optional

from ctypes import windll, wintypes, byref  # type: ignore
import pywintypes
import win32api
import win32file


def get_volumelabel(pathname: pathlib.Path) -> str:
    """Get the volumelabel of the given directory and returns ist."""
    # pylint: disable=c-extension-no-member
    volumelabel = "???"
    pathname_str = str(pathname.absolute())
    if len(pathname_str) >= 3:
        drive = pathname_str[:3]
        with contextlib.suppress(pywintypes.error):  # pylint: disable=no-member
            volumelabel = str(win32api.GetVolumeInformation(drive)[0])
    return volumelabel

def set_filetime(
    filename: str,
    creationtime: Optional[datetime.datetime],
    modifytime: Optional[datetime.datetime],
    accesstime: Optional[datetime.datetime],
) -> None:
    """
    Changes creation and/or modification time of a file.
    Aktually only works under Windows
    filename: name of the file to change
    creationtime: new creation time
    modifytime: new modified time
    accesstime: last access time
    """
    handle = windll.kernel32.CreateFileW(filename, 256, 0, None, 3, 128, None)
    # Call Win32 API to modify the file creation date
    # Convert Unix timestamp to Windows FileTime using some magic numbers
    # See documentation: https://support.microsoft.com/en-us/help/167296
    ctime = mtime = atime = wintypes.FILETIME(0, 0)
    if creationtime:
        ctime = _extracted_from_set_filetime(creationtime)
    if modifytime:
        mtime = _extracted_from_set_filetime(modifytime)
    if accesstime:
        atime = _extracted_from_set_filetime(accesstime)
    windll.kernel32.SetFileTime(
        handle,
        byref(ctime) if creationtime else None,
        byref(atime) if accesstime else None,
        byref(mtime) if modifytime else None,
    )
    windll.kernel32.CloseHandle(handle)


def _extracted_from_set_filetime(arg0: datetime.datetime):
    """Create the filetime"""
    try:
        epoch = arg0.timestamp()
        timestamp = int((epoch * 10000000) + 116444736000000000)
        return wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)
    except AttributeError as err:
        raise OSError from err


def compare(file1: str, file2: str) -> int:
    """Compares to filenames in a system independent way.
    return +1 if name of file1 is greate then file2 name
           -1 if name of file1 is smaller the file2 name
           0 if both are euqal"""
    fi1 = file1.lower()
    fi2 = file2.lower()
    if fi1 > fi2:
        return 1
    if fi1 < fi2:
        return -1
    return 0


PROGRESS_CANCEL = win32file.PROGRESS_CANCEL  # pylint: disable=c-extension-no-member
PROGRESS_CONTINUE = win32file.PROGRESS_CONTINUE  # pylint: disable=c-extension-no-member


def copy_file(
    srcfile: str | pathlib.Path,
    destfile: str | pathlib.Path,
    callback: Callable[[int, int], int] | None,
    filesize: int,
    _: int,  # No used, but required for compatibility
) -> None:
    """Copy one file with windows API copy.
    Creates the directory if it doesn't exist
    Exceptions: OSError"""

    def win_callback(_: int, total_bytes_transferred: int, *__: Any) -> int:
        """Internal callback to translate windows callback to our own one"""
        if callback is not None:
            rwert = callback(total_bytes_transferred, filesize)
            return PROGRESS_CONTINUE if rwert == 1 else PROGRESS_CANCEL
        return PROGRESS_CONTINUE

    destination = str(destfile)
    source = str(srcfile)
    try:
        if callback is not None:
            win32file.CopyFileEx(source, destination, win_callback)  # type: ignore  # pylint: disable=c-extension-no-member
        else:
            win32file.CopyFileW(source, destination, False)  # type: ignore   # pylint: disable=c-extension-no-member
    except pywintypes.error as err:  # pylint: disable=no-member
        # The next line is commented out because I don't know why I inserted it
        if os.path.exists(destination):
            os.remove(destination)
        if err.winerror != 1235:    # 1235 is Copy was canceled
            raise OSError from err

def test_for_system_attribute(path: pathlib.Path) -> bool:
    """Test if the path has system attribute.
    Path must exist and not be mounted"""
    if not os.path.exists(path):
        return False
    return (path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM) != 0

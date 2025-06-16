"""
Some extended file functions

Author: Heribert Füchtenhans

Version: 2025.6.16

On Windows we need pywin32 as requirement to use some of the functions.
"""

import datetime
import os
import pathlib
import platform
from typing import Callable

if platform.system() == "Windows":
    import filehandling_extended.osfunc_windows as osfunc
else:
    import filehandling_extended.osfunc_linux as osfunc  # type: ignore


def compare_filenames(file1: str, file2: str) -> int:
    """Compares two filenames in a system independent way.

    Args:
        file1: Name of the first file
        file2: Name of the second file

    Returns:
        +1 if name of file1 is greate then file2 name
        -1 if name of file1 is smaller the file2 name
        0 if both are equal
    """
    return osfunc.compare(file1, file2)


def copy_file(
    src: str | pathlib.Path,
    dest: str | pathlib.Path,
    callback: Callable[[int, int], int] | None = None,
    buffer_size: int = 4_194_304,  # 4MB
) -> pathlib.Path | None:
    """Copy one file with a callback.<br>
    The function copies all meta data of a file.<br>
    Under Windows it uses the Windows API to copy the file.<br>
    Under Linux it uses the shutil.copy2 function when no callback is given else
    it implements a custom copy function that calls the callback

    Args:
        src: Source filename, must exist
        dest: Path to the destination.
            If dest is a directory the src filename will be used as destination name.
            If it's a filename, it will be used as destination name.
            Existing files will be overwritten.
        callback: On Linux will be call when buffer_size bytes are copied. On Windows
            the callback will be called when the Windows API calls the callback.
            The parameter for callback are (total_bytes_copied, filesize)
            callback should return a value:
                0: Cancel the copy and delete the already copied file
                1: Continue copying
            Example:
                def my_callback(total_bytes_copied: int, filesize: int) -> int:
        buffer_size: How many bytes to copy before each call to the callback, default = 4MB
            Only used on Linux, Windows uses an internal buffer size

    Returns:
        Full path to destination file or None if transfer was canceled

    Exceptions:
        FileNotFoundError: If src doesn't exist
        TypeError: If callback is not callable
        OSError: If copying fails, e.g. if src and dest are the same file
    """

    srcfile = pathlib.Path(src)
    if not srcfile.is_file():
        raise FileNotFoundError(f"src file `{src}` doesn't exist")
    if callback is not None and not callable(callback):
        raise TypeError("callback must be a callable function")
    destpath = pathlib.Path(dest)
    destfile = destpath / srcfile.name if destpath.is_dir() else destpath
    if destfile.exists() and srcfile.samefile(destfile):
        raise OSError(f"source file `{src}` and destinaton file `{dest}` are the same file")

    os.makedirs(destfile.parent, exist_ok=True)
    filesize = srcfile.stat().st_size
    osfunc.copy_file(srcfile, destfile, callback, filesize, buffer_size)
    return destfile if destfile.exists() else None


def get_volumelabel(pathname: pathlib.Path) -> str:
    """Get the volumelabel of the given directory and returns ist.

    Args:
        pathname: Path to the directory or file to get the volumelabel from.

    Returns:
        The volumelabel of the given directory or file."""
    return osfunc.get_volumelabel(pathname)


def set_filetime(
    filename: str | pathlib.Path,
    creationtime: datetime.datetime | None,
    modifytime: datetime.datetime | None,
    accesstime: datetime.datetime | None,
) -> None:
    """
    Changes creation and/or modification and/or accesstime time of a file.

    Args:
        filename: Name of the file to change
        creationtime: New creation time
            Note: On Linux, this should be None, as linux has no creation time for files.
        modifytime: New modified time
        accesstime: New last access time

    Exceptions:
        OSError: If something went wrong
    """
    osfunc.set_filetime(str(filename), creationtime, modifytime, accesstime)

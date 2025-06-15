"""
OS specific functions for filehandling_extended
WINDOWS

Author: Heribert Füchtenhans
Version: 2025.6.15

"""

import datetime
import os
import pathlib
import shutil
from typing import IO, Any, Callable, Optional


def get_volumelabel(pathname: pathlib.Path) -> str:
    """Get the volumelabel of the given directory and returns ist."""
    volumelabel = "???"
    pathname_str = str(pathname.absolute())
    with open("/proc/mounts", "r") as mounts:
        split_mounts = [s.split() for s in mounts.read().splitlines()]
    # sort splitmounts by length of mount point, longest first
    split_mounts.sort(key=lambda x: len(x[1]), reverse=True)
    for mount in split_mounts:
        if pathname_str.startswith(mount[1]):
            volumelabel = os.path.basename(mount[1])
            if volumelabel == "":
                volumelabel = "root"
            break
    return volumelabel


def set_filetime(
    filename: str,
    creationtime: Optional[datetime.datetime],
    modifytime: Optional[datetime.datetime],
    accesstime: Optional[datetime.datetime],
) -> None:
    """
    Changes creation and/or modification time of a file.
    filename: name of the file to change
    creationtime: new creation time
        as linux has no creation time for files, this should be none
    modifytime: new modified time
    accesstime: last access time
    """
    if accesstime and modifytime:
        os.utime(filename, times=(accesstime.timestamp(), modifytime.timestamp()))
    elif modifytime:
        stat = os.stat(filename)
        atime = stat.st_atime
        os.utime(filename, times=(atime, modifytime.timestamp()))
    elif accesstime:
        stat = os.stat(filename)
        mtime = stat.st_mtime
        os.utime(filename, times=(accesstime.timestamp(), mtime))


def compare(file1: str, file2: str) -> int:
    """Compares to filenames in a system independent way.
    return +1 if name of file1 is greate then file2 name
           -1 if name of file1 is smaller the file2 name
           0 if both are euqal"""
    fi1 = file1
    fi2 = file2
    if fi1 > fi2:
        return 1
    if fi1 < fi2:
        return -1
    return 0


def copy_file(
    srcfile: str | pathlib.Path,
    destfile: str | pathlib.Path,
    callback: Callable[[int, int], int] | None,
    filesize: int,
    buffer_size: int,
) -> None:
    """Copy one file with python copy
    Exceptions: OSError when srcfile doesn't exist or destfile can't be written"""
    try:
        if callback is None:
            shutil.copy2(srcfile, destfile)
        else:
            with open(srcfile, "rb") as fsrc:
                with open(destfile, "wb") as fdest:
                    ret = _copyfileobj(fsrc, fdest, callback=callback, filesize=filesize, length=buffer_size)
            if ret == 0:
                if os.path.exists(destfile):
                    os.remove(destfile)
                return  # copying was canceld in callback
        # copy file metadata
        st = os.stat(srcfile)
        os.chown(destfile, st.st_uid, st.st_gid)
    except (FileNotFoundError, PermissionError) as err:
        raise OSError from err


def _copyfileobj(
    fsrc: IO[Any],
    fdest: IO[Any],
    callback: Callable[[int, int], int],
    filesize: int,
    length: int,
) -> int:
    """copy from fsrc to fdest

    Args:
        fsrc: filehandle to source file
        fdest: filehandle to destination file
        callback: callable callback that will be called after every length bytes copied
        length: how many bytes to copy at once (between calls to callback)
    return:
        0: cancel copying and delete file
        1: continue normal procedure
    """
    copied = 0
    while True:
        buf = fsrc.read(length)
        if not buf:
            break
        fdest.write(buf)
        copied += len(buf)
        if callback(copied, filesize) == 0:
            return 0
    return 1

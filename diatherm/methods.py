"""The MethodFile class."""
import re
from io import BytesIO
from pathlib import Path

import olefile

from . import utils


class MethodFile:
    """Read a Thermo instrument method file summary.

    These files are OLE2 files, with multiple streams.

    Parameters
    ----------
    template_file : str or Path
        A Thermo method file to use as a template for the DIA method.
        This should at least contain a tMS2 experiment for editing.
    """

    def __init__(self, method_file):
        """Initialize the MethodFile"""
        self._data = {}
        self.method_file = Path(method_file)
        self._load_data()
        self._n_dependent_scans = None

    @property
    def data(self):
        """The method summary data"""
        return self._data

    @property
    def summary(self):
        """A nice summary view of the method"""
        summary = []
        for section, data in self.data.items():
            summary.append(f"SECTION: {section}")
            summary.append("-" * (9 + len(section)))
            summary += data

        return "\n".join(summary)

    @property
    def n_dependent_scans(self):
        """The number of dependent scans"""
        if self._n_dependent_scans is None:
            for lines in self.data.values():
                for line in lines:
                    scan_line = re.search(
                        r"\w*Number of Dependent Scans.*= (\d)", line
                    )
                    return int(scan_line.group(1))

        return None

    def _load_data(self):
        """Load the template method data.

        Returns
        -------
        stream : str
            The OLE2 stream that contained the instrument method.
        data : str
            The parsed instrument method.
        """
        with olefile.OleFileIO(self.method_file) as ole:
            for stream in ole.listdir():
                if len(stream) == 2 and stream[1] == "Text":
                    data = ole.openstream(stream).read().decode("utf16")
                    self._data[stream[0]] = data.splitlines()

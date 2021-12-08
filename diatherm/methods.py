"""The MethodFile class.

This class does the heavy lifting in the diatherm package.
"""
import re
from io import BytesIO
from pathlib import Path

import olefile

from . import utils


class MethodFile:
    """Read and modify a Thermo instrument method file.

    These files are OLE2 files, with multiple streams.

    Parameters
    ----------
    template_file : str or Path
        A Thermo method file to use as a template for the DIA method.
        This should at least contain a tMS2 experiment for editing.
    """

    isolation_window_key = "\t\t\tIsolation Window (m/z) = "
    n_windows_key = "\t\t\tN (Number of Spectra) = "
    mass_list_start_key = ">>>>>>>>>>>>> Mass List Table <<<<<<<<<<<<<<\r\n"
    mass_list_end_key = ">>>>>>>>>>>>> End Mass List Table <<<<<<<<<<<<<<\r\n"

    def __init__(self, template_file):
        """Initialize the MethodFile"""
        self.template_file = Path(template_file)
        with template_file.open() as fobj:
            self._file_obj = fobj.read()

        self._stream, self.data = self._load_data()

    def _load_data(self):
        """Load the template method data.

        Returns
        -------
        stream : str
            The OLE2 stream that contained the instrument method.
        data : str
            The parsed instrument method.
        """
        with olefile.OleFileIO(BytesIO(self._file_obj)) as ole:
            stream = [
                s for s in ole.listdir() if len(s) == 2 and s[1] == "Text"
            ][0]
            # TODO: This currently only works for Exploris instruments...
            assert stream[0] == "TNG-Merkur"
            data = ole.openstream(stream).read().decode("utf16")

        return stream, data

    def update_windows(self, mass, charge=3, isolation_width=4):
        """Update the DIA windows.

        Parameters
        ----------
        mass : float or list of float
            The center m/z of the DIA isolation windows.
        charge : int or list of int
            The assumed charge state for each DIA window. If an an int,
            the charge is used for all windows.
        isolation_width : float
            The m/z width of the isolation windows.
        """
        lines = self.data.splitlines(True)
        mass = utils.listify(mass)
        charge = utils.listify(charge)

        # Find the experiment
        ms2_idx = lines.index("\tExperiment Name = tMS2\r\n")
        mass_start = lines.index(self.mass_list_start_key) + 1
        mass_end = lines.index(self.mass_list_end_key)

        if len(mass) > (mass_end - mass_start):
            raise ValueError(
                "The number of windows exceeds that in the template."
            )

        new_lines = lines[:ms2_idx]
        for line in lines[ms2_idx:mass_start]:
            # Update the isolation window width:
            if line.starts_with(self.isolation_window_key):
                line = re.sub(
                    f"({self.isolation_window_key}).+(\r\n)",
                    "\0" + str(isolation_width) + "\1",
                    line,
                )

            # Update the number of DIA scans:
            if line.starts_with(self.n_windows_key):
                line = re.sub(
                    f"({self.n_windows_key}).+(\r\n)",
                    "\0" + str(len(mass)) + "\1",
                    line,
                )

            new_lines.append(line)

        # Update the mass list table.
        if len(charge) == 1:
            charge = charge * len(mass)

        new_lines += [_make_row(mz, z) for mz, z in zip(mass, charge)]

        # Finish it:
        new_lines += lines[mass_end:]
        new_data = "".join(new_lines)
        self.data = new_data.ljust(len(self.data))

    def save(self, filename):
        """Save the updated method file.

        Parameters
        ----------
        filename : str or Path
            The method file to write.

        Returns
        -------
        Path
            The output file.
        """
        filename = Path(filename)
        with filename.open("w+") as out:
            out.write(self._file_obj)

        with olefile.OleFileIO(filename, write_mode=True) as ole:
            ole.write_stream(self._stream, self.data)

        return filename


def _make_row(mass, charge):
    """Create a row for the mass list table.

    Parameters
    ----------
    mass : float
        The ceter m/z of the isolation window.
    charge : int
        The assumed charge state.

    Returns
    -------
    str
        One formatted row for the table.
    """
    prefix = "               |               |    (no adduct)"
    mass = f"{mass:15.4f}"
    charge = f"{charge:15d}"
    suffix = "\r\n"
    return "|".join([prefix, mass, charge, suffix])

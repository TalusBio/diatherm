"""The command line entry point for diatherm"""
import random
import logging
from pathlib import Path
from argparse import ArgumentParser

from . import modifications
from . import utils

LOGGER = logging.getLogger(__name__)

def create_random_methods(
        n_windows,
        charge=3,
        width=4,
        min_mz=399,
        max_mz=1000,
        n_methods=1,
        file_root="diatherm",
        output_dir="diatherm-out",
        overwrite=False,
):
    """Create the XML modification file for random DIA windows.

    This requires a template file that contains single Inclusion
    List experiment. Note that this function will generate the XML file
    needed for the modification, but will not actually create the method.
    For that you need the XmlMethodChanger from:
    https://github.com/thermofisherlsms/meth-modifications

    Parameters
    ----------
    n_windows : int
        The number of random isolation windows to select.
    charge : int or list of int, optional
        The assumed charge state for each DIA window. If an an int,
        the charge is used for all windows.
    width : int, optional
        The integer m/z width of the isolation windows. This is converted
        to a more precise width to avoid 'forbidden zones'
    min_mz : float, optional
        The minimum DIA window edge m/z.
    max_mz : float, optional
        The maximum DIA window edge m/z.
    n_methods : int, optional
        The number of methods to create.
    file_root : str, optional
        The prefix to use for all of the output files.
    output_dir : str, optional
        The output directory.
    overwrite : bool, optional
        If False, this function will only write to a new output directory.

    Returns
    -------
    Path
        The new XML file for modifications.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=overwrite)

    # Constants:
    spacing = 1.00045475
    offset = 0.25

    # Calculate window centers:
    width = (width // spacing + 1) * spacing
    min_win = offset + spacing * ((min_mz - offset) // spacing) + width / 2
    n_total = int((max_mz - min_win - width / 2) // width + 2)
    windows = [min_win + i * width for i in range(n_total)]

    LOGGER.info("DIA window width: %.6f m/z", width)
    LOGGER.info("Center of first window: m/z %.6f", windows[0])
    LOGGER.info("Center of last window: m/z %.6f", windows[-1])
    LOGGER.info("Selecting %i random windows...", n_windows)

    output_files = []
    padding = len(str(int(n_methods)))
    for idx in range(1, n_methods + 1):
        if n_methods == 1:
            suffix = ""
        else:
            suffix = "_" + str(idx).zfill(padding)

        suffix += ".xml"
        output_file = output_dir / (file_root + suffix)

        # Sample random windows:
        selected = random.sample(windows, n_windows)
        mod_xml = modifications.add_windows(selected, charge)
        mod_xml.write(output_file)
        output_files.append(output_file)

    if n_methods == 1:
        return output_files[0]

    return output_files


def main():
    """The command line function"""
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(message)s"
    )

    desc = """
    Create the XML modification file for random DIA windows.

    This requires a template file that contains single Inclusion
    List experiment. Note that this function will generate the XML file
    needed for the modification, but will not actually create the method.
    For that you need the XmlMethodChanger from:
    https://github.com/thermofisherlsms/meth-modifications
    """
    parser = ArgumentParser(description=desc)
    parser.add_argument(
        "n_windows",
        type=int,
        help="The number fo randome isolations windows to select",
    )

    parser.add_argument(
        "--charge",
        type=str,
        default="3",
        help="""
        The assumed precursor charge for each DIA window. If all should be the
        same, this parameter should be an integer. Otherwise, a this should be
        a comma separated list specifying the charge for each DIA window, such
        as '2,3,2,2'.
        """,
    )

    parser.add_argument(
        "--width",
        type=int,
        default=4,
        help="""
        The integer m/z width of the isolation windows. This is converted
        to a more precise width to avoid 'forbidden zones'
        """,
    )

    parser.add_argument(
        "--min_mz",
        type=float,
        default=399.0,
        help="The minimum DIA window edge m/z.",
    )

    parser.add_argument(
        "--max_mz",
        type=float,
        default=1000.0,
        help="The maximum DIA window edge m/z.",
    )

    parser.add_argument(
        "--n_methods",
        type=int,
        default=1,
        help="The number of methods to create.",
    )

    parser.add_argument(
        "--file_root",
        type=str,
        default="diatherm",
        help="The prefix to use for all of the output files.",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="diatherm-out",
        help="The output directory.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow diatherm to write files to an existing directory."
    )

    args = parser.parse_args()
    charge = [int(z.strip()) for z in args.charge.split(",")]

    output_files = create_random_methods(
        n_windows=args.n_windows,
        charge=charge,
        width=args.width,
        min_mz=args.min_mz,
        max_mz=args.max_mz,
        n_methods=args.n_methods,
        file_root=args.file_root,
        output_dir=args.output_dir,
        overwrite=args.overwrite,
    )

    logging.info("Wrote:")
    for output_file in utils.listify(output_files):
        logging.info("  %s", str(output_file))

    logging.info("DONE!")


if __name__ == "__main__":
    main()

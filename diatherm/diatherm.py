"""The command line entry point for diatherm"""
import logging
from argparse import ArgumentParser

from .methods import MethodFile


def create_dia_method(template_file, output_file, mass, charge=3, width=4.0):
    """Create a Thermo DIA method from a template method file.

    This function requires that the template file contains one and only one
    "tMS2" experiment, which it will edit. Additionally, the number of DIA
    windows specified in the template file must be more than the number of
    windows specified in this function. This is due to a restriction on one
    of our underlying dependencies, which doesn't let us grow the file.

    Parameters
    ----------
    template_file : str or Path
        The DIA template method file.
    mass : float or list of float
        The center m/z of the DIA isolation windows.
    charge : int or list of int
        The assumed charge state for each DIA window. If an an int,
        the charge is used for all windows.
    width : float
        The m/z width of the isolation windows.

    Returns
    -------
    Path
        The new method file.
    """
    method_file = MethodFile(template_file)
    method_file.update_windows(mass, charge, width)
    return method_file.save(output_file)


def main():
    """The command line function"""
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(message)s"
    )

    desc = """Create a Thermo DIA method from a template method file.

    This utility requires that the template file contains one and only one
    "tMS2" experiment, which it will edit. Additionally, the number of DIA
    windows specified in the template file must be more than the number of
    windows specified in this function. This is due to a restriction on one
    of our underlying dependencies, which doesn't let us grow the file.
    """
    parser = ArgumentParser(description=desc)
    parser.add_argument(
        "template_file",
        type=str,
        help="The DIA template method file.",
    )

    parser.add_argument(
        "output_file", type=str, help="The new DIA method file."
    )

    parser.add_argument(
        "--mass",
        required=True,
        type=str,
        help="""
        The center m/z of the DIA isolation windows. Specify these as a comma
        separated list, such as '400,404,408,412'.
        """,
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
        type=float,
        default=4.0,
        help="The m/z width of the isolation windows.",
    )

    args = parser.parse_args()
    mass = [float(m.strip()) for m in args.mass.split(",")]
    charge = [int(z.strip()) for z in args.charge.split(",")]
    out_file = create_dia_method(
        args.template_file,
        args.output_file,
        mass,
        charge,
        args.width,
    )

    logging.info("Wrote %s", out_file)


if __name__ == "__main__":
    main()

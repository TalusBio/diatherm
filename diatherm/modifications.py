"""Create the XML for DIA windows"""
import xml.etree.ElementTree as ET
from pathlib import Path

from . import utils

TEMPLATE = Path(__file__).parent / "data" / "template.xml"


def add_windows(m_over_z, charge):
    """Add DIA windows

    Parameters
    ----------
    m_over_z : float or array of float
        The center m/z of the DIA windows.
    charge : int or array of int
        The assumed charge for the DIA windows.

    Returns
    -------
    xml.etree.ElementTree.
        The modification XML document.
    """
    m_over_z = utils.listify(m_over_z)
    charge = utils.listify(charge)

    if len(charge) == 1:
        charge *= len(m_over_z)

    tree = ET.parse(TEMPLATE)
    root = tree.getroot()
    mass_list = root.find(".//MassList")

    for idx, (mz_val, charge_val) in enumerate(zip(m_over_z, charge)):
        # Create the tree:
        record = ET.SubElement(mass_list, "MassListRecord")
        name = ET.SubElement(record, "CompoundName")
        formula = ET.SubElement(record, "Formula")
        mz_element = ET.SubElement(record, "MOverZ")
        z_element = ET.SubElement(record, "Z")

        # Assign values:
        name.text = f"DIA {idx+1}"
        formula.text = ""
        mz_element.text = str(mz_val)
        z_element.text = str(charge_val)

    return tree

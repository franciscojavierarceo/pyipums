import os
import xml.etree.ElementTree as ET
from typing import Dict

def read_ipums_ddi(file_path: str) -> Dict:
    """
    :param file_path:
    :return:
        List of 13
        $ file_name       : chr "usa_00003.dat"
        $ file_path       : chr "/Users/franciscojavierarceo/Downloads"
        $ file_type       : chr "rectangular"
        $ ipums_project   : chr "IPUMS USA"
        $ extract_date    : Date[1:1], format: "2023-03-22"
        $ extract_notes   : chr "User-provided description:  Revision of (2021 educational demo data)\n\nThis extract is a revision of the user'"| __truncated__
        $ rectypes        : NULL
        $ rectype_idvar   : NULL
        $ rectypes_keyvars: NULL
        $ var_info        : tibble [149 × 10] (S3: tbl_df/tbl/data.frame)
        ..$ var_name  : chr [1:149] "YEAR" "SAMPLE" "SERIAL" "CBSERIAL" ...
        ..$ var_label : chr [1:149] "Census year" "IPUMS sample identifier" "Household serial number" "Original Census Bureau household serial number" ...
        ..$ var_desc  : chr [1:149] "YEAR reports the four-digit year when the household was enumerated or included in the census, the ACS, and the "| __truncated__ "SAMPLE identifies the IPUMS sample from which the case is drawn. Each sample receives a unique 6-digit code. Th"| __truncated__ "SERIAL is an identifying number unique to each household record in a given sample. All person records are assig"| __truncated__ "CBSERIAL is the unique, original identification number assigned to each household record in a given sample by t"| __truncated__ ...
        ..$ val_labels:List of 149
    """
    ddi_dict = {}
    tree = ET.parse(file_path)
    # The codebook element is the root
    codebook = tree.getroot()

    # Handle namespaces
    namespaces = {'ddi': 'ddi:codebook:2_5'}

    # Extract the data file information
    file_desc = codebook.find("ddi:fileDscr", namespaces)
    file_id = file_desc.get("ID")
    file_title = file_desc.findtext("ddi:titlStmt/ddi:titl", namespaces=namespaces)

    # Extract variable information
    variables = []
    for var_elem in codebook.findall("ddi:dataDscr/ddi:var", namespaces):
        var = {
            "name": var_elem.get("name"),
            "label": var_elem.get("labl"),
            "categories": []
        }

        # Extract category information
        for cat_elem in var_elem.findall("ddi:catgry", namespaces):
            cat = {
                "code": cat_elem.findtext("ddi:catValu", namespaces=namespaces),
                "label": cat_elem.get("labl")
            }
            var["categories"].append(cat)

        variables.append(var)

    # Create the DDI object
    ddi = {
        "file_id": file_id,
        "file_title": file_title,
        "variables": variables
    }
    return ddi

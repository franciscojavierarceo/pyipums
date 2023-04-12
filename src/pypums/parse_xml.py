import os
import xml.etree.ElementTree as ET
from typing import Dict

_DEFAULT_NAMESPACE_ = '{ddi:codebook:2_5}'

def remove_namespace(x: str) -> str:
    if x:
        return x.replace(_DEFAULT_NAMESPACE_,"")

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
    file_metadata = {"codebook_id": codebook.get("ID")}
    for element in codebook.findall("ddi:docDscr/ddi:citation/ddi:titlStmt/", namespaces=namespaces):
        element_key = remove_namespace(element.tag)
        file_metadata[element_key] = element.text

    for element in codebook.findall("ddi:fileDscr/ddi:fileTxt/", namespaces=namespaces):
        element_key = remove_namespace(element.tag)
        file_metadata[element_key] = element.text

    ddi_dict['file_metadata'] = file_metadata
    # Extract variable information
    var_elements = codebook.findall("ddi:dataDscr/ddi:var", namespaces)
    for var_elem in var_elements:
        var_dict = {
            "name": var_elem.get("ID"),
            "field_type": var_elem.get("intrvl"),
            "tag": remove_namespace(var_elem.tag),
            "text": remove_namespace(var_elem.text),
            "files": var_elem.get("files"),
        }
        field_metadata = []
        # now get child stuff
        for child in list(var_elem):
            if remove_namespace(child.tag) == var_dict['name']:
                var_dict['description'] = remove_namespace(child.text)

            if remove_namespace(child.tag) == 'varFormat':
                field_metadata.append({
                    "tag": remove_namespace(child.tag),
                    "text": remove_namespace(child.text),
                    "schema": child.attrib.get("schema"),
                    "data_type": child.attrib.get("type"),
                })
            if remove_namespace(child.tag) == 'catgry':
                field_metadata.append({
                    'category_value':  child.findtext("ddi:catValu", namespaces=namespaces),
                    'category_label':  child.findtext("ddi:labl", namespaces=namespaces),
                })
            else:
                field_metadata.append({
                    'tag': remove_namespace(child.tag),
                    'text': remove_namespace(child.text),
                })

            var_dict['field_metadata'] = field_metadata

        ddi_dict['metadata'] = var_dict

    return ddi_dict




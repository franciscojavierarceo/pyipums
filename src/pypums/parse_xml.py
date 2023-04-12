import os
import xml.etree.ElementTree as ET
from typing import Dict

# Handle namespaces
DEFAULT_NAMESPACE = '{ddi:codebook:2_5}'
NAMESPACES = {'ddi': 'ddi:codebook:2_5'}
TITLE_XPATH = "ddi:docDscr/ddi:citation/ddi:titlStmt/"
FILE_TEXT_XPATH = "ddi:fileDscr/ddi:fileTxt/"

def remove_namespace(x: str) -> str:
    if x:
        return x.replace(DEFAULT_NAMESPACE,"")

def get_file_metadata(xml_object, metadata: Dict={}):
    # Extract the data file information
    metadata = {"codebook_id": metadata.get("ID")}
    for element in xml_object.findall(TITLE_XPATH, namespaces=NAMESPACES):
        element_key = remove_namespace(element.tag)
        metadata[element_key] = element.text

    for element in xml_object.findall(FILE_TEXT_XPATH, namespaces=NAMESPACES):
        element_key = remove_namespace(element.tag)
        metadata[element_key] = element.text

    return metadata

def get_field_metadata():
    return None

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

    ddi_dict['file_metadata'] = get_file_metadata(codebook)

    # Extract variable information
    var_elements = codebook.findall("ddi:dataDscr/ddi:var", namespaces=NAMESPACES)
    column_metadata = []
    for var_elem in var_elements:
        var_dict = {
            "name": var_elem.get("ID"),
            "field_type": var_elem.get("intrvl"),
            "files": var_elem.get("files"),
        }
        field_metadata = []
        # now get child stuff
        for child in list(var_elem):
            if remove_namespace(child.tag) == 'txt':
                var_dict['description'] = remove_namespace(child.text)

            elif remove_namespace(child.tag) == 'labl':
                var_dict['label'] = remove_namespace(child.text)

            elif remove_namespace(child.tag) == 'varFormat':
                var_dict['schema'] = child.attrib.get("schema")
                var_dict['data_type'] = child.attrib.get("type")

            elif remove_namespace(child.tag) == 'catgry':
                field_metadata.append({
                    'category_value':  child.findtext("ddi:catValu", namespaces=NAMESPACES),
                    'category_label':  child.findtext("ddi:labl", namespaces=NAMESPACES),
                })

            elif remove_namespace(child.tag) == 'location':
                var_dict['location_end_pos'] = child.attrib.get("EndPos")
                var_dict['location_start_pos'] = child.attrib.get("StartPos")
                var_dict['location_width'] = child.attrib.get("width")

            elif remove_namespace(child.tag) == 'concept':
                var_dict['concept'] = remove_namespace(child.text)

            else:
                field_metadata.append({
                    'tag': remove_namespace(child.tag),
                    'text': remove_namespace(child.text),
                })

        var_dict['field_metadata'] = field_metadata

        ddi_dict[var_dict['name']] = var_dict
        column_metadata.append(
                (var_dict['name'], var_dict['field_type'])
            )

    ddi_dict['column_metadata'] = column_metadata
    ddi_dict['columns'] = [r[0] for r in column_metadata]
    ddi_dict['column_types'] = [r[1] for r in column_metadata]

    return ddi_dict




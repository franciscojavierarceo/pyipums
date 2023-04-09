import os
import pandas as pd
import xml.etree.ElementTree as ET

def read_ipums_ddi(file_path):
    tree = ET.parse(os.path.expanduser(file_path))
    root = tree.getroot()

    # Handle namespaces
    namespaces = {'ddi': 'ddi:codebook:2_5'}

    # Find the codebook element
    codebook = root

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

def read_ipums_micro(ddi, data_file_path, n_max=None):
    # Extract column information from the DDI metadata
    col_specs = []
    col_names = []
    for var in ddi["variables"]:
        col_specs.append((int(var["categories"][0]["code"]) - 1, int(var["categories"][-1]["code"])))
        col_names.append(var["name"])

    # Read the fixed-width data file using the extracted column information
    df = pd.read_fwf(
        data_file_path,
        colspecs=col_specs,
        header=None,
        names=col_names,
        nrows=n_max,
        compression='gzip',
    )
    
    return df


def main():
    # Example usage
    ddi_file_path = "~/Downloads/usa_00003.xml"
    cps_ddi = read_ipums_ddi(ddi_file_path)
    data_file_path = "~/Downloads/usa_00003.dat.gz"
    cps_data = read_ipums_micro(cps_ddi, data_file_path, n_max=1000)
    print(cps_data.head())

if __name__ == '__main__':
    main()

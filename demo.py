import json
import pandas as pd
from src.pyipums.parse_xml import read_ipums_ddi
from ipumspy import readers, ddi


def read_ipums_micro(ddi, data_file_path, n_max=None):
    # Read the fixed-width data file using the extracted column information
    df = pd.read_fwf(
        data_file_path,
        dtypes=ddi["column_dtypes"],
        colspecs=ddi["column_specs"],
        header=None,
        names=ddi["columns"],
        nrows=n_max,
        compression="gzip",
    )

    return df


def main():
    # Example usage
    ddi_file_path = "./usa_00003.xml"
    data_file_path = "./usa_00003.dat.gz"
    cps_ddi = read_ipums_ddi(ddi_file_path)
    ddi_codebook = readers.read_ipums_ddi(ddi_file_path)
    ipums_df = readers.read_microdata(
        ddi_codebook,
        data_file_path,
        nrows=100,
    )
    print(ipums_df)
    print(json.dumps(cps_ddi["file_metadata"], indent=2))
    cps_data = read_ipums_micro(cps_ddi, data_file_path, n_max=100)
    print(cps_data.head())


if __name__ == "__main__":
    main()

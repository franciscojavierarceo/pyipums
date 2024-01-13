import os
from unittest import TestCase

import pandas as pd
from ipumspy import readers, ddi
from src.pyipums.parse_xml import read_ipums_ddi
from src.pyipums.clean_data import (
    IpumsAsecCleaner,
    IpumsAcsCleaner,
    ASEC_EDUC_ATTAINMENT,
    ACS_EDUC_ATTAINMENT,
)

xvars = [
    "AGE",
    "ADJGINC",
    "ASECWT",
    "ASECWTH",
    "ASIAN",
    "ASECFWT",
    "STATEFIP",
    "TAXINC",
    "UHRSWORK1",
    "RACE",
    "SEX",
    "SRCWELFR",
    "YEAR",
    "FOODSTAMP",
    "STAMPVAL",
    "WTFINL",
    "BPL",
    "HISPAN",
    "EMPSTAT",
    "LABFORCE",
    "OCC",
    "OCC2010",
    "MARST",
    "VETSTAT",
    "CITIZEN",
    "NATIVITY",
    "CLASSWKR",
    "WKSTAT",
    "EDUC",
    "OFFPOV",
    "EARNWT",
    "INCWAGE",
    "INCBUS",
    "INCFARM",
    "INCSS",
    "INCWELFR",
    "INCRETIR",
    "INCSSI",
    "INCINT",
    "INCUNEMP",
    "INCWKCOM",
    "INCVET",
    "INCSURV",
    "INCDISAB",
    "INCDIVID",
    "INCRENT",
    "INCEDUC",
    "INCCHILD",
    "INCASIST",
    "INCOTHER",
    "INCRANN",
    "INCPENS",
    "INCTOT",
    "STATECENSUS",
]


class TestReadASECData(TestCase):
    def test_read(self):
        absolute_path = os.path.dirname(__file__)
        ddi_file_path = "metadata_cps.xml"
        data_file_path = "cps_sample_data.csv.gz"
        full_ddi_path = os.path.join(absolute_path, ddi_file_path)
        full_data_path = os.path.join(absolute_path, data_file_path)

        ddi_codebook = readers.read_ipums_ddi(full_ddi_path)
        ipums_df = pd.read_csv(full_data_path, compression="gzip")

        df = IpumsAsecCleaner(ipums_df, ddi_codebook).clean_data()
        self.assertEqual(
            set(df["Educational Attainment"].unique()),
            set(ASEC_EDUC_ATTAINMENT.values()),
        )


class TestReadACSData(TestCase):
    def test_read(self):
        absolute_path = os.path.dirname(__file__)
        ddi_file_path = "metadata_acs.xml"
        data_file_path = "acs_sample_data.csv.gz"
        full_ddi_path = os.path.join(absolute_path, ddi_file_path)
        full_data_path = os.path.join(absolute_path, data_file_path)

        ddi_codebook = readers.read_ipums_ddi(full_ddi_path)
        ipums_df = pd.read_csv(full_data_path, compression="gzip")

        df = IpumsAcsCleaner(ipums_df, ddi_codebook).clean_data()
        self.assertEqual(
            set(df["Educational Attainment"].unique()),
            set(ACS_EDUC_ATTAINMENT.values()),
        )

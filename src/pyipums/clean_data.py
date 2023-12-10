import pandas as pd
import numpy as np
from ipumspy import readers, ddi

INCOME_COLUMN = "INC"
EDUC_LT_HS = "Less than High School Diploma"
EDUC_HS = "High school diploma or equivalent"
EDUC_VOC = "Vocational Degree"
EDUC_BS = "Bachelor's degree"
EDUC_GRAD = "Graduate degree"
EDUC_ATTAINMENT = {
    "NIU or blank": "Missing",
    "Grades 1, 2, 3, or 4": EDUC_LT_HS,
    "Grades 5 or 6": EDUC_LT_HS,
    "Grades 7 or 8": EDUC_LT_HS,
    "Grade 9": EDUC_LT_HS,
    "Grade 10": EDUC_LT_HS,
    "Grade 11": EDUC_LT_HS,
    "12th grade, no diploma": EDUC_LT_HS,
    "None or preschool": EDUC_LT_HS,
    "High school diploma or equivalent": EDUC_HS,
    "Associate's degree, academic program": EDUC_HS,
    "Associate's degree, occupational/vocational program": EDUC_VOC,
    "Some college but no degree": EDUC_HS,
    "Bachelor's degree": EDUC_BS,
    "Master's degree": EDUC_GRAD,
    "Doctorate degree": EDUC_GRAD,
    "Professional school degree": EDUC_GRAD,
}


def map_codes(ddi: ddi.Codebook, xdf: pd.DataFrame, xvar: str):
    g = {v: k for k, v in ddi.get_variable_info(xvar).codes.items()}
    res = xdf[xvar].apply(lambda x: g.get(x, None))
    return res


class IpumsCleaner:
    def __init__(self, df: pd.DataFrame, ddi_codebook: ddi.Codebook):
        self.df = df
        self.ddi_codebook = ddi_codebook

    def clean_cps_income(self):
        invalid_cols = [col for col in self.df.columns if INCOME_COLUMN in col]
        for col in invalid_cols:
            invalid_values = [999999, 999999.0]
            if self.df[col].dtype == pd.Int64Dtype():
                invalid_values.extend([99999999, 999999999, 999999])

            self.df[f"{col}"] = self.df[col].replace(invalid_values, np.nan)

        self.df["INCTOT"] = self.df["INCTOT"].astype(float)

    def clean_educ_attainment(self):
        self.df["Educational Attainment"] = (
            self.df["Education"].apply(lambda x: EDUC_ATTAINMENT.get(x)).astype(str)
        )

    def clean_variables(self):
        self.df["Occupation"] = map_codes(self.ddi_codebook, self.df, "OCC2010")
        self.df["Education"] = map_codes(self.ddi_codebook, self.df, "EDUC")
        self.df["Birthplace"] = map_codes(self.ddi_codebook, self.df, "BPL")
        self.df["Marital_Status"] = map_codes(self.ddi_codebook, self.df, "MARST")
        self.df["Nativity"] = map_codes(self.ddi_codebook, self.df, "NATIVITY")
        self.df["Class_of_worker"] = map_codes(self.ddi_codebook, self.df, "CLASSWKR")
        self.df["Hispanic"] = map_codes(self.ddi_codebook, self.df, "HISPAN")
        self.df['Hispanic or Not'] = np.where(self.df['Hispanic'] != 'Not Hispanic', 'Hispanic', 'Not Hispanic')
        self.df["Asian"] = map_codes(self.ddi_codebook, self.df, "ASIAN")
        self.df["Race"] = map_codes(self.ddi_codebook, self.df, "RACE")
        self.df["Veteran_Status"] = map_codes(self.ddi_codebook, self.df, "VETSTAT")
        self.df["Age"] = self.df["AGE"].astype(float)
        self.df["Age Bucket"] = ""
        self.df.loc[(self.df["Age"] < 15), "Age Bucket"] = "<15"
        self.df.loc[
            (self.df["Age"] >= 15) & (self.df["Age"] <= 24), "Age Bucket"
        ] = "15-24"
        self.df.loc[
            (self.df["Age"] >= 25) & (self.df["Age"] <= 54), "Age Bucket"
        ] = "25-54"
        self.df.loc[
            (self.df["Age"] >= 55) & (self.df["Age"] <= 64), "Age Bucket"
        ] = "55-64"
        self.df.loc[(self.df["Age"] >= 65), "Age Bucket"] = "65+"

    def clean_wages(self):
        # Aggregating Wages
        income_buckets = {
            "INCSS": "Government",
            "INCWELFR": "Government",
            "INCRETIR": "Investment",
            "INCSSI": "Government",
            "INCINT": "Investment",
            "INCUNEMP": "Government",
            "INCWKCOM": "Wage",
            "INCVET": "Government",
            "INCSURV": "Government",
            "INCDISAB": "Government",
            "INCDIVID": "Investment",
            "INCRENT": "Investment",
            "INCEDUC": "Government",
            "INCCHILD": "Government",
            "INCASIST": "Government",
            "INCOTHER": "Unknown",
            "INCRANN": "Investment",
            "INCPENS": "Wage",
            "INCWAGE": "Wage",
            "INCBUS": "Wage",
            "INCFARM": "Wage",
        }

        column_to_bucket_map = {}
        for bucket in set([income_buckets[k] for k in income_buckets]):
            for k in income_buckets:
                if income_buckets[k] == bucket:
                    if bucket not in column_to_bucket_map:
                        column_to_bucket_map[bucket] = [f"{k}"]
                    else:
                        column_to_bucket_map[bucket].append(f"{k}")

        for k in column_to_bucket_map:
            self.df[f"{k} Income"] = self.df[column_to_bucket_map[k]].sum(axis=1)

        self.df["Investment Income as Percent of Total Income"] = np.where(
            self.df["INCTOT"] == 0,
            0,
            self.df["Investment Income"].astype(float)
            / self.df["INCTOT"].astype(float),
        )

        self.df["Government Income as Percent of Total Income"] = np.where(
            self.df["INCTOT"] == 0,
            0,
            self.df["Government Income"].astype(float)
            / self.df["INCTOT"].astype(float),
        )

        self.df["Wage Income as Percent of Total Income"] = np.where(
            self.df["INCTOT"] == 0,
            0,
            self.df["Wage Income"].astype(float) / self.df["INCTOT"].astype(float),
        )

        self.df.loc[
            self.df["Investment Income as Percent of Total Income"] < 0,
            "Investment Income as Percent of Total Income",
        ] = 0.0
        self.df.loc[
            self.df["Investment Income as Percent of Total Income"] > 1,
            "Investment Income as Percent of Total Income",
        ] = 1
        self.df.loc[
            self.df["Government Income as Percent of Total Income"] < 0,
            "Government Income as Percent of Total Income",
        ] = 0.0
        self.df.loc[
            self.df["Government Income as Percent of Total Income"] > 1,
            "Government Income as Percent of Total Income",
        ] = 1
        self.df.loc[
            self.df["Wage Income as Percent of Total Income"] < 0,
            "Wage Income as Percent of Total Income",
        ] = 0.0
        self.df.loc[
            self.df["Wage Income as Percent of Total Income"] > 1,
            "Wage Income as Percent of Total Income",
        ] = 1

        self.df["Weighted Total Income"] = self.df["INCTOT"] * self.df["ASECWT"]
        self.df["Weighted Government Income"] = (
            self.df["Government Income"] * self.df["ASECWT"]
        )
        self.df["Weighted Investment Income"] = (
            self.df["Investment Income"] * self.df["ASECWT"]
        )
        self.df["Weighted Wage Income"] = self.df["Wage Income"] * self.df["ASECWT"]

        self.df["Weighted Government Income as Percent of Total Income"] = (
            self.df["Government Income as Percent of Total Income"] * self.df["ASECWT"]
        )
        self.df["Weighted Investment Income as Percent of Total Income"] = (
            self.df["Investment Income as Percent of Total Income"] * self.df["ASECWT"]
        )
        self.df["Weighted Wage Income as Percent of Total Income"] = (
            self.df["Wage Income as Percent of Total Income"] * self.df["ASECWT"]
        )

    def clean_data(self):
        self.clean_variables()
        self.clean_cps_income()
        self.clean_educ_attainment()
        self.clean_wages()
        return self.df

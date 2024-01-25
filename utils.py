import json
import numpy as np
import pandas as pd
import seaborn as sns
from src.pyipums.parse_xml import read_ipums_ddi
from src.pyipums.clean_data import IpumsAsecCleaner
from ipumspy import readers, ddi
from matplotlib import pyplot as plt
import matplotlib as mpl
from IPython.core.display import display
import plotly
import plotly.io as pio


plt.rcParams["figure.figsize"] = 12, 8  # Set figure size for the notebook
sns.set(style="whitegrid")  # set seaborn whitegrid theme

plotly.offline.init_notebook_mode(connected=True)

acs_xvars = [
    'YEAR',
    'SAMPLE',
    'SERIAL',
    'CBSERIAL',
    'HHWT',
    'CLUSTER',
    'STATEICP',
    'STATEFIP',
    'METRO',
    'CITY',
    'STRATA',
    'GQ',
    'PERNUM',
    'CBPERNUM',
    'PERWT',
    'SLWT',
    'RELATE',
    'RELATED',
    'SEX',
    'AGE',
    'BIRTHQTR',
    'MARST',
    'BIRTHYR',
    'MARRNO',
    'MARRINYR',
    'YRMARR',
    'DIVINYR',
    'WIDINYR',
    'FERTYR',
    'RACE',
    'RACED',
    'HISPAN',
    'HISPAND',
    'BPL',
    'BPLD',
    'ANCESTR1',
    'ANCESTR1D',
    'ANCESTR2',
    'ANCESTR2D',
    'CITIZEN',
    'YRNATUR',
    'YRIMMIG',
    'YRSUSA1',
    'YRSUSA2',
    'LANGUAGE',
    'LANGUAGED',
    'SPEAKENG',
    'TRIBE',
    'TRIBED',
    'RACAMIND',
    'RACASIAN',
    'RACBLK',
    'RACPACIS',
    'RACWHT',
    'RACOTHER',
    'RACNUM',
    'SCHOOL',
    'EDUC',
    'EDUCD',
    'GRADEATT',
    'GRADEATTD',
    'SCHLTYPE',
    'DEGFIELD',
    'DEGFIELDD',
    'DEGFIELD2',
    'DEGFIELD2D',
    'EMPSTAT',
    'EMPSTATD',
    'LABFORCE',
    'CLASSWKR',
    'CLASSWKRD',
    'OCC',
    'OCC1950',
    'OCC1990',
    'OCC2010',
    'OCCSOC',
    'IND',
    'IND1950',
    'IND1990',
    'INDNAICS',
    'WKSWORK1',
    'WKSWORK2',
    'UHRSWORK',
    'ABSENT',
    'LOOKING',
    'AVAILBLE',
    'WRKRECAL',
    'WORKEDYR',
    'INCTOT',
    'FTOTINC',
    'INCWAGE',
    'INCBUS00',
    'INCSS',
    'INCWELFR',
    'INCINVST',
    'INCRETIR',
    'INCSUPP',
    'INCOTHER',
    'INCEARN',
    'POVERTY',
    'OCCSCORE',
    'PRESGL',
    'DIFFREM',
    'DIFFPHYS',
    'DIFFMOB',
    'DIFFCARE',
    'DIFFSENS',
    'DIFFEYE',
    'DIFFHEAR',
    'VETSTAT',
    'VETSTATD',
    'PWSTATE2',
]

ipums_xvars = [
    'AGE', 
    'ADJGINC', 
    'ASECWT', 
    'ASECWTH', 
    'ASIAN', 
    'ASECFWT', 
    'STATEFIP', 
    'TAXINC', 
    'UHRSWORK1', 
    'RACE', 
    'SEX', 
    'SRCWELFR', 
    'YEAR',
    'FOODSTAMP', 
    'STAMPVAL', 
    'WTFINL', 
    'BPL', 
    'HISPAN', 
    'EMPSTAT', 
    'LABFORCE', 
    'OCC', 
    'OCC2010',
    'MARST',
    'VETSTAT',
    'CITIZEN',
    'NATIVITY',
    'CLASSWKR',
    'WKSTAT',
    'EDUC',
    'OFFPOV',
    'EARNWT',
    'INCWAGE',
    'INCBUS',
    'INCFARM',
    'INCSS',
    'INCWELFR',
    'INCRETIR',
    'INCSSI',
    'INCINT',
    'INCUNEMP',
    'INCWKCOM',
    'INCVET',
    'INCSURV',
    'INCDISAB',
    'INCDIVID',
    'INCRENT',
    'INCEDUC',
    'INCCHILD',
    'INCASIST',
    'INCOTHER',
    'INCRANN',
    'INCPENS',
    'INCTOT',
    'STATECENSUS',
]


def cdf_plot_by_x(
    ddi_codebook,
    xdf,
    groupbyvar,
    xvar,
    wvar,
    k=None,
    bbox=(0.5, -0.1),
    legend_ncol=3,
    max_percentile=1.0,
):
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    if k is not None:
        sdf = xdf[groupbyvar].value_counts()
        top_k = sdf[0 : (k - 1)].index.tolist()
        xdfss = xdf[
            xdf.eval(f'{groupbyvar} == "' + f'" | {groupbyvar} == "'.join(top_k) + '"')
        ].reset_index(drop=True)
        print(f"reducing records from {xdf.shape[0]} to {xdfss.shape[0]}")
        print(f"reducing groups from {xdf[groupbyvar].nunique()} to {k}")
    else:
        xdfss = xdf

    max_percentile_value = xdfss[xvar].quantile(max_percentile)
    xdfss = xdfss[xdfss[xvar] < max_percentile_value]
    groups = xdfss[groupbyvar].unique()
    pal = sns.color_palette("bright", len(groups))
    sns.ecdfplot(
        data=xdfss,
        weights=wvar,
        x=xvar,
        hue=groupbyvar,
        alpha=0.8,
        ax=ax,
        palette=pal,
    ).set(title=f"Cumulative Distribution of Total Income by {groupbyvar}")
    label = (
        ddi_codebook.get_variable_info(xvar.replace("_2", ""))
        .label.title()
        .replace("'S", "'s")
    )
    ax.set_xlabel(f"{label}")
    ax.set_ylabel(f"Cumulative Percent of ASEC Data")
    ax.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.2f}"))
    ax.get_xaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("${x:,.0f}"))
    ax.get_legend().set_visible(False)
    fig.legend(labels=groups, loc="lower center", bbox_to_anchor=bbox, ncol=legend_ncol)
    fig.show()


def den_cdf_plot_by_x(
    ddi_codebook,
    xdf,
    groupbyvar,
    xvar,
    wvar,
    k=None,
    bbox=(0.5, -0.1),
    legend_ncol=3,
    max_percentile=1.0,
    den_title=None,
):
    fig, (ax1, ax) = plt.subplots(1, 2, figsize=(16, 8))
    if k is not None:
        sdf = xdf[groupbyvar].value_counts()
        top_k = sdf[0 : (k - 1)].index.tolist()
        xdfss = xdf[
            xdf.eval(f'{groupbyvar} == "' + f'" | {groupbyvar} == "'.join(top_k) + '"')
        ].reset_index(drop=True)
        print(f"reducing records from {xdf.shape[0]} to {xdfss.shape[0]}")
        print(f"reducing groups from {xdf[groupbyvar].nunique()} to {k}")
    else:
        xdfss = xdf

    if den_title is None:
        den_title = f"Estimated Density Function of Total Income by {groupbyvar}"
    max_percentile_value = xdfss[xvar].quantile(max_percentile)
    xdfss = xdfss[xdfss[xvar] < max_percentile_value]
    groups = xdfss[groupbyvar].unique()
    pal = sns.color_palette("bright", len(groups))

    sns.kdeplot(
        data=xdfss,
        weights=wvar,
        x=xvar,
        hue=groupbyvar,
        cut=0,
        fill=True,
        common_norm=False,
        alpha=0.2,
        ax=ax1,
        palette=pal,
    ).set(title=den_title)
    try:
        label = (
            ddi_codebook.get_variable_info(xvar.replace("_2", ""))
            .label.title()
            .replace("'S", "'s")
        )
    except:
        label = xvar
    ax1.set_xlabel(f"{label}")
    ax1.set_ylabel(f"Percent of ASEC Data")
    ax1.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.2f}"))
    ax1.get_xaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("${x:,.0f}"))
    ax1.get_legend().set_visible(False)

    sns.ecdfplot(
        data=xdfss,
        weights=wvar,
        x=xvar,
        hue=groupbyvar,
        alpha=0.8,
        ax=ax,
        palette=pal,
    ).set(title=f"Cumulative Distribution of Total Income by {groupbyvar}")
    label = (
        ddi_codebook.get_variable_info(xvar.replace("_2", ""))
        .label.title()
        .replace("'S", "'s")
    )
    ax.set_xlabel(f"{label}")
    ax.set_ylabel(f"Cumulative Percent of ASEC Data")
    ax.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.3f}"))
    ax.get_xaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("${x:,.0f}"))
    ax.get_legend().set_visible(False)
    fig.legend(labels=groups, loc="lower center", bbox_to_anchor=bbox, ncol=legend_ncol)
    fig.show()


def denbyplot(df, colname, byvar, weightvar):
    f, ax = plt.subplots(1, figsize=(12, 8))
    groups = df[byvar].unique()
    labels = []
    for i, g in enumerate(groups):
        f = (df[colname].isnull() == False) & (df[byvar] == g)
        ax = df[f][f"{colname}_2"].plot(
            weight=df[f][weightvar], kind="density", grid=True
        )
        ax.set_xticklabels(["${:,}".format(int(x)) for x in ax.get_xticks().tolist()])
        #     ax.set_xlim([0, 1e6])
        label = (
            ddi_codebook.get_variable_info(colname.replace("_2", ""))
            .label.title()
            .replace("'S", "'s")
        )
        labels.append(label)
        ax.set_xlabel(f"{label}")

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.set_ylabel(f"Percentage of ASEC Data")
    ax.legend(
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        shadow=True,
        ncol=2,
    )
    plt.show()


def den_plot_by_x(
    ddi_codebook,
    xdf,
    groupbyvar,
    xvar,
    wvar,
    k=None,
    bbox=(0.5, -0.1),
    legend_ncol=3,
    max_percentile=1.0,
    addvline=False,
    den_title=None,
    format_axis_dollars=True,
):
    fig, ax1 = plt.subplots(1, 1, figsize=(16, 8))
    if k is not None:
        sdf = xdf[groupbyvar].value_counts()
        top_k = sdf[0 : (k - 1)].index.tolist()
        xdfss = xdf[
            xdf.eval(f'{groupbyvar} == "' + f'" | {groupbyvar} == "'.join(top_k) + '"')
        ].reset_index(drop=True)
        print(f"reducing records from {xdf.shape[0]} to {xdfss.shape[0]}")
        print(f"reducing groups from {xdf[groupbyvar].nunique()} to {k}")
    else:
        xdfss = xdf

    if den_title is None:
        den_title = f"Estimated Density Function of Total Income by {groupbyvar}"
    max_percentile_value = xdfss[xvar].quantile(max_percentile)
    xdfss = xdfss[xdfss[xvar] < max_percentile_value]
    groups = xdfss[groupbyvar].unique()
    pal = sns.color_palette("bright", len(groups))

    sns.kdeplot(
        data=xdfss,
        weights=wvar,
        x=xvar,
        hue=groupbyvar,
        cut=0,
        fill=True,
        common_norm=False,
        alpha=0.2,
        ax=ax1,
        palette=pal,
    ).set(title=den_title)
    try:
        label = (
            ddi_codebook.get_variable_info(xvar.replace("_2", ""))
            .label.title()
            .replace("'S", "'s")
        )
    except:
        label = xvar

    ax1.set_xlabel(f"{label}")
    ax1.set_ylabel(f"Percent of ASEC Data")
    if format_axis_dollars:
        ax1.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.2f}"))
        ax1.get_xaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("${x:,.0f}"))
    ax1.get_legend().set_visible(False)
    fig.legend(labels=groups, loc="lower center", bbox_to_anchor=bbox, ncol=legend_ncol)
    if addvline:
        tmp = xdfss[[xvar, groupbyvar, wvar]]
        tmp["XWEIGHT"] = xdfss[xvar] * xdfss[wvar]
        x = (
            tmp[[groupbyvar, "XWEIGHT", wvar]]
            .groupby(by=groupbyvar)
            .agg({"XWEIGHT": [len, np.sum, np.mean], wvar: [np.sum]}, as_index=False)
        )

        x.columns = ["_".join([y for y in j if y != ""]) for j in x.columns]
        x["final"] = x["XWEIGHT_sum"] / x[f"{wvar}_sum"]
        display(x[["final"]].sort_values(by="final", ascending=False))
        for i, xval in enumerate(x["final"]):
            ax1.axvline(x=xval, ymin=0, color=pal[i], ymax=1, linestyle="--")

    fig.show()


def clean_dollars(x: str) -> str:
    y = x.split(", ")
    left = round(float(y[0].replace("(", "")))
    right = round(float(y[1].replace("]", "")))
    output = f"(\${left:,}, \${right:,}]"
    return output


def pt(ddi, df: pd.DataFrame, xvar: str, wvar: str = None) -> pd.DataFrame:
    if ddi:
        codex = pd.DataFrame.from_dict(
            ddi.get_variable_info(xvar).codes, orient="index", columns=["code"]
        )
        codex.reset_index(inplace=True)
        codex.rename({"index": xvar}, axis=1, inplace=True)
    if wvar:
        aggdf = (
            df[[xvar, wvar]].groupby(by=xvar, as_index=False).agg({wvar: [np.sum, len]})
        )
        aggdf.columns = ["_".join([y for y in j if y != ""]) for j in aggdf.columns]
        aggdf.rename(
            {xvar: "code", f"{wvar}_sum": "count", f"{wvar}_len": "raw_count"},
            inplace=True,
            axis=1,
        )
        aggdf["raw_percent"] = aggdf["raw_count"] / aggdf["raw_count"].sum()
    else:
        aggdf = pd.DataFrame(df[xvar].value_counts().reset_index()).rename(
            {"index": "code", xvar: "count"}, axis=1
        )

    aggdf["Percent"] = aggdf["count"] / aggdf["count"].sum()
    if ddi:
        outdf = aggdf.merge(codex, how="left", left_on="code", right_on="code")
    else:
        outdf = aggdf.rename({"code": xvar}, axis=1)
    outdf.sort_values(by="count", ascending=False, inplace=True)
    outdf.reset_index(drop=True, inplace=True)
    if ddi:
        outdf = outdf[[xvar] + outdf.columns[0:-1].to_list()]
    return outdf


def ptbarplot(ddi, df, xvar, wvar, color="blue", out=False, xlabel="Percent of ASEC Sample", ylabel=None, title=None):
    x = pt(ddi, df, xvar, wvar)
    if not ylabel:
        try:
            ylabel = ddi.get_variable_info(xvar).label.title()
        except:
            ylabel = xvar
    x["Percent"] = (x["Percent"] * 100.0).round(2)

    y = (
        x[["Percent", xvar]]
        .sort_values(by="Percent", ascending=False)
        .reset_index(drop=True)
        .loc[0:30]
    )
    ax = y.sort_values(by="Percent").plot.barh(x=xvar, color=color, figsize=(12, 8))

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f%%", padding=2)

    if title:
        plt.title(title) 
    plt.legend(loc="lower right")
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()
    if out:
        return x


def ptbarplot2(ddi, df, xvar, wvar, color="blue", out=False, xlabel="Percent of ASEC Sample"):
    x = pt(ddi, df, xvar, wvar)
    try:
        ylabel = ddi.get_variable_info(xvar).label.title()
    except:
        ylabel = xvar
    x["Percent"] = (x["Percent"] * 100.0).round(2)

    y = (
        x[["Percent", xvar]]
        .sort_values(by="Percent", ascending=False)
        .reset_index(drop=True)
        .loc[0:30]
    )
    ax = y.sort_values(by="Percent").plot.barh(x=xvar, color=color, figsize=(12, 8))

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f%%", padding=2)

    plt.legend(loc="lower right")
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.show()
    if out:
        return x


def gen_state_df(ddi, xdf, gvar, wvar, xvar):
    t1 = pt(ddi=ddi, df=xdf, xvar=gvar, wvar=xvar)
    t2 = pt(ddi=ddi, df=xdf, xvar=gvar, wvar=wvar)
    t3 = t1.merge(t2, on=gvar)
    t3["avg_x"] = t3["count_x"] / t3["count_y"]
    t3["STATE_ABBREV"] = [us_state_to_abbrev[r] for r in t3[gvar]]
    return t3


def den_plot_by_x(
    ddi_codebook,
    xdf,
    groupbyvar,
    xvar,
    wvar,
    k=None,
    bbox=(0.5, -0.1),
    legend_ncol=3,
    max_percentile=1.0,
    addvline=False,
    den_title=None,
    format_axis_dollars=True,
):
    fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))
    if k is not None:
        sdf = xdf[groupbyvar].value_counts()
        top_k = sdf[0 : (k - 1)].index.tolist()
        xdfss = xdf[
            xdf.eval(f'{groupbyvar} == "' + f'" | {groupbyvar} == "'.join(top_k) + '"')
        ].reset_index(drop=True)
        print(f"reducing records from {xdf.shape[0]} to {xdfss.shape[0]}")
        print(f"reducing groups from {xdf[groupbyvar].nunique()} to {k}")
    else:
        xdfss = xdf

    if den_title is None:
        den_title = f"Estimated Density Function of Total Income by {groupbyvar}"
    max_percentile_value = xdfss[xvar].quantile(max_percentile)
    xdfss = xdfss[xdfss[xvar] < max_percentile_value]
    groups = xdfss[groupbyvar].unique().tolist()
    pal = sns.color_palette("bright", len(groups))

    if addvline:
        tmp = xdfss[[xvar, groupbyvar, wvar]]
        tmp["XWEIGHT"] = xdfss[xvar] * xdfss[wvar]
        x = (
            tmp[[groupbyvar, "XWEIGHT", wvar]]
            .groupby(by=groupbyvar)
            .agg({"XWEIGHT": [len, np.sum, np.mean], wvar: [np.sum]}, as_index=False)
        )
        x.columns = ["_".join([y for y in j if y != ""]) for j in x.columns]
        x["final"] = x["XWEIGHT_sum"] / x[f"{wvar}_sum"]

    test = sns.kdeplot(
        data=xdfss,
        weights=wvar,
        x=xvar,
        hue=groupbyvar,
        hue_order=x.index.tolist(),
        cut=0,
        fill=True,
        common_norm=False,
        alpha=0.2,
        # ax=ax1,
        palette=pal,
    ).set(title=den_title)

    try:
        label = (
            ddi_codebook.get_variable_info(xvar.replace("_2", ""))
            .label.title()
            .replace("'S", "'s")
        )
    except:
        label = xvar

    ax1.set_xlabel(f"{label}")
    ax1.set_ylabel(f"Percent of ASEC Data")
    if format_axis_dollars:
        ax1.get_yaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.5f}"))
        ax1.get_xaxis().set_major_formatter(mpl.ticker.StrMethodFormatter("${x:,.0f}"))
    if addvline:
        display(x[["final"]].rename({"final": xvar}, axis=1))
        for i, xval in enumerate(x["final"]):
            ax1.axvline(x=xval, ymin=0, color=pal[i], ymax=1, linestyle="--")
    fig.show()

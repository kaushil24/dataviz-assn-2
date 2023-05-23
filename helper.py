import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import janitor
import typing
import numpy as np

DATE='Date'
BUILDING='Building'
WASTE_TYPE='Waste Type'
SUBSTREAM='Substream'
DISPOSED_IN='Disposed In'
VOL='Volume'
WEIGHT='Weight'
NOTES='Notes'

CLR_REC_BLD='#451AFF'
CLR_LFILL_BLD='#828282'
CLR_CMP_BLD='#00B600'
CLR_REU_BLD='#ffa500'
CLR_REU_MIL='#ffe148'
CLR_REC_MIL='#4A62FF'
CLR_LFILL_MIL='#AFAFAF'
CLR_CMP_MIL='#7AE288'

clr_map_bld = {
    'Recycling': CLR_REC_BLD,
    'Reusables': CLR_REU_BLD,
    'Compost': CLR_CMP_BLD,
    'Landfill': CLR_LFILL_BLD
}

clr_map_mld = {
    'Recycling': CLR_REC_MIL,
    'Reusables': CLR_REU_MIL,
    'Compost': CLR_CMP_MIL,
    'Landfill': CLR_LFILL_MIL
}

emoji_waste = {
    'Compost': "🍃",
    'Landfill': "🕳️",
    'Recycling': "♼",
    'Reusables': "♲",
}

style_waste = {
    'Compost': f"<b style='color:{clr_map_bld['Compost']};'>Compost</b> <b>🍃</b>",
    'Landfill': f"<b style='color:{clr_map_bld['Landfill']};'>Landfill</b> 🕳️",
    'Recycling': f"<b style='color:{clr_map_bld['Recycling']};'>Recycling</b> ♼",
    'Reusables': f"<b style='color:{clr_map_bld['Reusables']};'>Reusables</b> ♲",

}

style_waste_st = {
    'Compost': f':green[Compost]',
    'Landfill': f'Landfill',
    'Recycling': f':blue[Recycling]',
    'Reusables': f':yellow[Reusable]',
}



def _stylize_words(tempdf, col_name, emoji: bool=False) -> pd.DataFrame:
    """
    Returns df containing stylized colname
    """
    col_name_style = f'{col_name}_style'
    tempdf[col_name_style] = tempdf[col_name].copy()
    if emoji:
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Compost', f"<b style='color:{clr_map_bld['Compost']};'>Compost</b> <b>🍃</b>")
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Landfill', 'Landfill 🕳️')
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Recycling', 'Recycling ♻️')
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Reusable', 'Reusable 🔃')
    else:
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Compost', f"<b style='color:{clr_map_bld['Compost']};'>Compost</b> <b>🍃</b>")
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Landfill', f"<b style='color:{clr_map_bld['Landfill']};'>Landfill</b> 🕳️")
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Recycling', f"<b style='color:{clr_map_bld['Recycling']};'>Recycling</b> ♼")
        tempdf[col_name_style] = tempdf[col_name_style].str.replace('Reusable', f"<b style='color:{clr_map_bld['Reusables']};'>Reusables</b> ♲")

    return tempdf, col_name_style

def get_misclassif_perc(df: pd.DataFrame, level: str, building: str = None):
    """
    level: waste_type: columns contain waste_type, weight and %age
            substream: contains waste_type, substream, weight and %age
            disposed_in: contains waste_type, substream, disposed_in, weight and %page
    building: Building 
    """
    temp_df = df.loc[:] if not building else df.loc[df[BUILDING]==building, :]
    TOTAL_DISCLASSIFIED_WEIGHT = temp_df.loc[temp_df[WASTE_TYPE]!=temp_df[DISPOSED_IN]][WEIGHT].sum()
    
    if level=='waste_type':
        wgt = temp_df.loc[temp_df[WASTE_TYPE]!=temp_df[DISPOSED_IN]].groupby([WASTE_TYPE]).agg({WEIGHT: 'sum'})
        wgt['%'] = wgt[WEIGHT] / TOTAL_DISCLASSIFIED_WEIGHT * 100
    elif level=='substream':
        wgt = temp_df.loc[temp_df[WASTE_TYPE]!=temp_df[DISPOSED_IN]].groupby([WASTE_TYPE, SUBSTREAM]).agg({WEIGHT: 'sum'})#.reset_index()
        wgt['%'] = wgt[WEIGHT] / wgt.groupby([WASTE_TYPE])[WEIGHT].transform('sum') * 100
    elif level=='disposed_in':
        wgt = temp_df.loc[temp_df[WASTE_TYPE]!=temp_df[DISPOSED_IN]].groupby([WASTE_TYPE, SUBSTREAM, DISPOSED_IN]).agg({WEIGHT: 'sum'})
        wgt['%'] =  wgt[WEIGHT] / wgt.groupby([WASTE_TYPE, SUBSTREAM])[WEIGHT].transform('sum') * 100
    return wgt

def plot_disposed_in_graph(df: pd.DataFrame, keys):
    """
    df should be a multi-indexed df having (WASTETYPE, SUBSTREAM, DISPOSED) as the index
    keys should be a list of tuples. Each tuple has 2 element representing: (WasteType, Substream).
    It represents which waste types to display on the grpah
    """
    wtdf: pd.DataFrame = df.select_rows(keys)
    wtdf = wtdf.reset_index()
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(
        go.Bar(
            y=[wtdf[WASTE_TYPE].tolist(), wtdf[SUBSTREAM].tolist(), wtdf[DISPOSED_IN].tolist()],
            x=wtdf[WEIGHT],
            customdata=wtdf[DISPOSED_IN].tolist(),# wtdf['%'].tolist()]),
            orientation='h',
            marker={'color': [clr_map_mld[clr] for clr in wtdf[DISPOSED_IN].tolist()]},
            hovertext=wtdf[DISPOSED_IN].tolist(),
            hovertemplate=
            "<b>Disposed In</b><br><br>%{customdata}: %{x} pound(s)"
        )
    )

    # title = f'Different of types of waste wrongly thrown into the <b style="color:{clr_map_bld[bin_name]};">{bin_name}</b> bin '
    # title+= f'for <b>{building_name}</b> building' if building_name else ''
    fig.update_xaxes(title_text='Weight (in pounds)')
    fig.update_yaxes(title_text='Waste Types')
    fig.update_layout(title="Waste Types, Substreams and how they're <b>Wrongly</b> Disposed In different bins")
    return fig, wtdf

def get_wrong_waste_agg_df(df: pd.DataFrame, bin_name: str, building_name: str = None):
    if not building_name:
        group_df = df.loc[df[WASTE_TYPE]!=df[DISPOSED_IN], :].groupby([DISPOSED_IN,WASTE_TYPE, SUBSTREAM]).agg({WEIGHT: 'sum'})[WEIGHT].reset_index()
    else:
        group_df = df.loc[(df[WASTE_TYPE]!=df[DISPOSED_IN]) & (df[BUILDING]==building_name), :].groupby([DISPOSED_IN,WASTE_TYPE, SUBSTREAM]).agg({WEIGHT: 'sum'})[WEIGHT].reset_index()
    group_df
    wtdf = group_df.loc[group_df[DISPOSED_IN]==bin_name] # waste type df
    return wtdf


def plot_waste_division(df, bin_name: str, building_name: str = None):
    wtdf = get_wrong_waste_agg_df(df, bin_name, building_name)
    per_bin_max_elements=5

    # ------ optional code to select only top n rows within each group -------
    idx2keep = []
    for wt in wtdf[WASTE_TYPE].unique():
        idx2keep.extend(wtdf.loc[wtdf[WASTE_TYPE]==wt, :].sort_values(WEIGHT, ascending=False)[:per_bin_max_elements].index.tolist())

    wtdf = wtdf.loc[idx2keep, :]
    # ----------------------------------------------------------------------

    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(
        go.Bar(
            y=[wtdf[WASTE_TYPE].tolist(), wtdf[SUBSTREAM].tolist()],
            x=wtdf[WEIGHT],
            orientation='h',
            marker={'color': [clr_map_mld[clr] for clr in wtdf[WASTE_TYPE].tolist()]},
        )
    )

    title = f'Different of types of waste wrongly thrown into the <b style="color:{clr_map_bld[bin_name]};">{bin_name}</b> bin '
    title+= f'for <b>{building_name}</b> building' if building_name else ''
    fig.update_xaxes(title_text='Weight (in pounds)')
    fig.update_yaxes(title_text='Waste Type')
    fig.update_layout(title=title)

    return fig

import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from helper import *
import streamlit as st
from PIL import Image


df = pd.read_csv("assign2_wastedata.csv")

# DATE='Date'
# BUILDING='Building'
# WASTE_TYPE='Waste Type'
# SUBSTREAM='Substream'
# DISPOSED_IN='Disposed In'
# VOL='Volume'
# WEIGHT='Weight'
# NOTES='Notes'

# CLR_REC_BLD='#451AFF'
# CLR_LFILL_BLD='#828282'
# CLR_CMP_BLD='#00B600'
# CLR_REU_BLD='#ffa500'
# CLR_REU_MIL='#ffe148'
# CLR_REC_MIL='#4A62FF'
# CLR_LFILL_MIL='#AFAFAF'
# CLR_CMP_MIL='#7AE288'

# clr_map_bld = {
#     'Recycling': CLR_REC_BLD,
#     'Reusables': CLR_REU_BLD,
#     'Compost': CLR_CMP_BLD,
#     'Landfill': CLR_LFILL_BLD
# }

# clr_map_mld = {
#     'Recycling': CLR_REC_MIL,
#     'Reusables': CLR_REU_MIL,
#     'Compost': CLR_CMP_MIL,
#     'Landfill': CLR_LFILL_MIL
# }

## ----- Pre-processing and cleaning steps --------

# --- Separating Stream into Waste Type and Disposed In
def split_stream(stream: str):
    resp = stream.split(" in ")
    if len(resp) == 1:
        return resp[0].strip(), resp[0].strip()
    return resp[0].strip(), resp[1].strip()

df = df.join(pd.DataFrame(df['Stream'].apply(split_stream).tolist(), columns=["Waste Type", "Disposed In"])).drop('Stream', axis=1)
df = df[[DATE, BUILDING, WASTE_TYPE, SUBSTREAM, DISPOSED_IN,  VOL, WEIGHT, NOTES]]

#  --- Renaming WasteType==Food Waste to Compost. ---
# Since Waste_typw==Food Waste has a miniscule amount (only has 8.1 pounds of total data, i.e. 0.2%)
# we're not loosing much information.
# it is safe to club as Compost waste.
df[WASTE_TYPE] = df[WASTE_TYPE].str.replace('Food Waste', 'Compost', regex=False)


# --- Clubbing Substreams wherever possible ---
df['Substream'] = df['Substream'].str.capitalize()
# rename str mapper
rename_str = {
    'Aseptic containers': ['Aseptic/tetra-pak'],
    'Electronic & universal waste': ['E-/universal waste'],
    'Plastic 1-7': ['Film plastic', 'Plastics #1-7', 'Plastic film'],
    'Food/organic waste': ['Food waste (edible)'],
    'Metal': ['Metal & aluminum'],
    'Paperboard': ['Paperboard rolls'],
}

for key, val in rename_str.items():
    for i in val:
        df[SUBSTREAM] = df[SUBSTREAM].str.replace(i, key, regex=False)


st.title("How is SCU disposing its waste?")
st.text("Understanding how correctly are we disposing our waste and how can we improve?\nA story through graphs..")

# ------------ Bird's eye view ---------
st.header("Bird's eye view")
fig = px.treemap(df, path=[BUILDING, WASTE_TYPE, SUBSTREAM], values=WEIGHT, color_discrete_map=clr_map_mld, color=WASTE_TYPE)
fig.update_layout(title='Waste Characterization of individual building at SCU')
st.plotly_chart(fig, theme=None)

# ----------- intermediate stage -------------
building = None
building = st.selectbox('Building', df[BUILDING].unique().tolist() + ['SCU'])
building = None if building == 'SCU' else building
subdf = df.loc[df[BUILDING] == building, :] if building else df

# ----------- How are we doing with disposig waste corredctly -----------
st.header('How good are we doing disposing waste correctly?')

total_disclassified = subdf.loc[subdf[WASTE_TYPE]!=subdf[DISPOSED_IN]][WEIGHT].sum() / subdf[WEIGHT].sum() * 100
st.subheader('Overall...')
st.metric('Total weight of waste generated (in pounds)', subdf[WEIGHT].sum())
st.metric('Total weight of waste misclassified (in pounds)', subdf.loc[subdf[WASTE_TYPE]!=subdf[DISPOSED_IN]][WEIGHT].sum())
st.metric('Total %age of misclassified waste', total_disclassified)

# ---------- level" waste_type ---------
st.subheader('So what type of waste is misclassified the most?')
tempdf = get_misclassif_perc(subdf, 'waste_type', building)
tempdf.sort_values(WEIGHT, inplace=True, ascending=False)
tempdf1 = tempdf.reset_index()
# col1, col2 = st.columns([1,1])
# with col1:
#     fig = go.Figure()
#     fig.add_trace(
#         go.Bar(
#             x=tempdf1[WASTE_TYPE].tolist(),
#             y=tempdf1[WEIGHT].tolist(),
#             marker={'color': [clr_map_mld[clr] for clr in tempdf1[WASTE_TYPE].tolist()]}
#         )
#     )
#     st.plotly_chart(fig)#, theme=None)
# with col2:
#     st.write(tempdf)
fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=tempdf1[WASTE_TYPE].tolist(),
        y=tempdf1[WEIGHT].tolist(),
        customdata=tempdf1['%'].tolist(),
        marker={'color': [clr_map_mld[clr] for clr in tempdf1[WASTE_TYPE].tolist()]},
        hovertemplate="Percentage: %{customdata:.2f} % <br> Weight: %{y} pound(s)"
    )
)
fig.update_xaxes(title_text='Waste Type')
fig.update_yaxes(title_text='Weight (in pounds)')
st.plotly_chart(fig, theme=None)

wts = tempdf1.loc[0:2, WASTE_TYPE]
wgs = tempdf1.loc[0:2, WEIGHT]
percs = tempdf1.loc[0:2, '%']
# st.caption(
#     f'* **{style_waste_st[wts[0]]}** {emoji_waste[wts[0]]} is the most misclassified waste type ammounting for **{wgs[0]} pounds** that is **{percs[0]:.2f}%**',
#     unsafe_allow_html=False
# )
# st.caption(
#     f'* **{style_waste_st[wts[1]]}** {emoji_waste[wts[1]]} is the second most misclassified waste type ammounting for **{wgs[1]} pounds** that is **{percs[1]:.2f}%**',
#     unsafe_allow_html=False
# )

# ------- level: substream -----------
st.subheader('What Substream of waste are we throwing wrongly? And frequent misclassifications.')
tdf = get_misclassif_perc(subdf, 'substream', building)
# st.write(tdf)
tdf.sort_values(WEIGHT, inplace=True, ascending=False)
TOP_N = 10
tdf = tdf.head(TOP_N)
tdf1 = tdf.reset_index()
fig = go.Figure()
fig.add_trace(
    go.Bar(
        y=[tdf1[WASTE_TYPE],tdf1[SUBSTREAM].tolist()],
        x=tdf1[WEIGHT].tolist(),
        orientation='h',
        marker={'color': [clr_map_mld[clr] for clr in tdf1[WASTE_TYPE].tolist()]},
        showlegend=False,
        # name=WASTE_TYPE
        # name=tdf1[WASTE_TYPE].tolist()r #].tolist()
    )
)
fig.update_xaxes(title='Weight (in pounds)')
fig.update_yaxes(title='Waste Type')
fig.update_layout(title=f"Top {len(tdf)} misclassified substreams of waste (by weight)")
st.plotly_chart(fig)
st.caption(
    f"Following are the top 3 most wrongly disposed substreams of waste \n"  +
    f"1. **{tdf1.loc[0, SUBSTREAM]}** -> {style_waste_st[tdf1.loc[0, WASTE_TYPE]]}{emoji_waste[tdf1.loc[0, WASTE_TYPE]]}\n"
    f"2. **{tdf1.loc[1, SUBSTREAM]}** -> {style_waste_st[tdf1.loc[1, WASTE_TYPE]]}{emoji_waste[tdf1.loc[1, WASTE_TYPE]]}\n"
    f"3. **{tdf1.loc[2, SUBSTREAM]}** -> {style_waste_st[tdf1.loc[2, WASTE_TYPE]]}{emoji_waste[tdf1.loc[2, WASTE_TYPE]]}"
    )

# ---------- level: disposed in -----------

st.subheader('Where are we going wrong?')
st.markdown("Now that we know what substreams are frequently wrongly disposed, let's figure out **WHERE** are we wrongly disposing them?")
tdf = get_misclassif_perc(subdf, 'disposed_in', building)
tdf1 = tdf.reset_index()
wt_substream_mapper = {wt: tdf1.loc[tdf1[WASTE_TYPE]==wt, :][SUBSTREAM].unique().tolist() for wt in tdf1[WASTE_TYPE].unique()}
# wts
col1, col2 = st.columns([1,1])
with col1:
    st.subheader("Step 1 ➡️")
    st.caption("Select type(s) of waste types you want to analyse further")
    wts = st.multiselect('Waste Type', options=wt_substream_mapper.keys(), format_func=lambda x: x + ' '+ emoji_waste[x])
with col2:
    st.subheader("Step 2")
    st.caption("Select substream(s)")
    optns = []
    for wt in wts:
        optns.extend(list(map(lambda x: f'{wt} {emoji_waste[wt]}: {x}', wt_substream_mapper[wt])))

    substreams = st.multiselect('Substreams', options=optns)
    # converting substreams to tuple of (Waste Type, Substream)
    keys = []
    ss: str
    for ss in substreams:
        wtype, subst = ss.split(":")
        wtype = wtype.split(" ")[0]
        subst = subst.strip()
        keys.append((wtype, subst))

if wts and optns:
    fig, dfr = plot_disposed_in_graph(tdf, keys)
    st.plotly_chart(fig)
    dfr.sort_values(WEIGHT, ascending=False, inplace=True)
    dfr.reset_index(inplace=True)
    st.caption("Breaking it down")
    op_str = ''
    for i in range(min(len(dfr), 3)):
        # op_str+=f'{i+1}. {dfr.loc[i, SUBSTREAM]} is disposed in {style_waste_st[dfr.loc[i, DISPOSED_IN]]} {dfr.loc[i, "%"]:10f}%.\n' 
        op_str+=f'{i+1}. **{dfr.loc[i, "%"]:.2f}%** of **{dfr.loc[i, SUBSTREAM]}** is wrongly disposed in **{style_waste_st[dfr.loc[i, DISPOSED_IN]]}** {emoji_waste[dfr.loc[i, DISPOSED_IN]]}\n'

    st.caption(op_str)

    st.markdown(f"We need to educate people at **{'SCU' if not building else building}** that:")
    op_str=''
    total_perc = 0
    total_weight = 0
    for i in range(min(len(dfr), 3)):
        # op_str+=f'{i+1}. {dfr.loc[i, SUBSTREAM]} is disposed in {style_waste_st[dfr.loc[i, DISPOSED_IN]]} {dfr.loc[i, "%"]:10f}%.\n' 
        op_str+=f'{i+1}. **{dfr.loc[i, SUBSTREAM]}** goes in the **{style_waste_st[dfr.loc[i, WASTE_TYPE]]} {emoji_waste[dfr.loc[i, WASTE_TYPE]]}** bin\n'
        total_perc+=dfr.loc[i, '%']
        total_weight+=dfr.loc[i, WEIGHT]
    st.markdown(op_str)
    st.markdown('And this would reduce waste mis-categorization by')
    col1, col2 = st.columns([1,1])
    with col1:
        st.metric('Percentage', f'{round(total_weight * 100 / subdf[WEIGHT].sum(), 3)}%')
    with col2:
        st.metric('Weight', f'{subdf[WEIGHT].sum()} pounds')

    st.text('So, how do we do that?')
# ------------- Solution --------------
st.title('Solution')
st.markdown("### So **how** do we educate people?")
st.markdown("Let's understand the proportion of different waste types in each bins.")
# ÷col0, col1, col2 = st.columns([3,3,3])
fig = plot_waste_division(subdf, 'Compost', building)#, 'Facilities')
st.plotly_chart(fig, use_container_width=True)
fig = plot_waste_division(subdf, 'Landfill', building)#, 'Facilities')
st.plotly_chart(fig, use_container_width=True)
fig = plot_waste_division(subdf, 'Recycling', building)#, 'Facilities')
st.plotly_chart(fig, use_container_width=True)

st.markdown("Now that we know the different types of waste that are wrongly thrown in the different bins;")
st.markdown("We can create personalized posters for each building depicting the most frequently occuring substream mis-characterinzation for each bin.")


bld_img_map = {
   'Facilities': 'fc',
   'Swig': 'sw', 
   'Vari Hall and Lucas Hall': 'vh',
   'Malley': 'ml',
    'University Villas': 'uv',
    'Graham': 'gm',
    'Benson Center': 'bc',
    'Learning Commons': 'lc',
}

image = Image.open(f'Media/DO NOT THROW/{bld_img_map.get(building, "SCU")}.png')

st.image(image, caption='Sunrise by the mountains')
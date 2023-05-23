import streamlit as st
from helper import style_waste_st, clr_map_bld
import pandas as pd

st.title("Report: Assignment 2 Interactive Visualization")

st.markdown(
    "**Story**: The purpose of my visualization can be broken down into two primary objectives:\n" + 
    "1. **Root causing:** Answering the _'what'_ and _'where'_ of waste miscategorization.\n" + 
    "2. **Solutions**: Answering _'how'_ to prevent waste miscategorization by actionable steps."
    )

st.header("Visualizations")

st.subheader("Multi-index bar plot")
st.markdown("Multi-index barplots help compare multiple waste types on the same axis. It becomes easy to categorize different substreams as they’re grouped into the same group and it becomes easy to compare multiple substreams that are on different waste types (since each bar is on the same axis).")

st.subheader("Stacked Multi-index bar plot")
st.markdown("Adding upon all the pros of a multi-index bar plot, a stacked multi index bar plot adds another dimension of comparison by representing the different categories that make up the bar."
)

st.subheader("Treemap")
st.markdown("Here, treemap is used to get a high level overview of the dataset. There are multiple attributes to the dataset that are relavent for our waste miscategorization discovery. Tree map is effective in\n" + 
            "* Representing different categories\n\t* Eg: Different buildings have their individual block\n\t* Different waste types have their individual blocks\n\t* Waste substreams have their individual block\n" + 
            "* Understanding magniture of these different categories. As each block is sized based on the weight that the block holds (eg. Benson Center block is relatively lareger sized than Learning Commons because former has more weight of waste collected), it becomes easy to visually compare and contrast them.\n" + 
            "* Hierarcy: As each block encompases multiple other blocks, this visual gives a notion of an implict hierarchy that exists. Eg:\n\t* Each building (holds) -> Multiple wast types\n\t* Each waste type within (holds) -> Multiple waste substreams"
)

st.subheader("Visual Elements")
st.markdown(
    "Each Waste Type text and graph is color coded. Represented by\n" +
    f"* {style_waste_st['Compost']} -> Green\n" + 
    f"* {style_waste_st['Landfill']} -> Grey\n" + 
    f"* {style_waste_st['Recycling']} -> Blue\n"
)
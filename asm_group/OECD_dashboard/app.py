import streamlit as st
from sections import intro
#, environment, area, water, energy, advanced, summary
st.set_page_config(page_title="OECD Dashboard", layout="wide")

section = st.sidebar.radio("📊 Select Section", [
    "1. Introduction",
    "2. Environmental Impact",
    "3. Land Use",
    "4. Water Use",
    "5. Energy Use",
    "6. Advanced Analysis",
    "7. Summary"
])

if section == "1. Introduction":
    intro.section_intro()
elif section == "2. Environmental Impact":
    environment.section_environment()
elif section == "3. Land Use":
    area.section_area()
elif section == "4. Water Use":
    water.section_water()
elif section == "5. Energy Use":
    energy.section_energy()
elif section == "6. Advanced Analysis":
    advanced.section_advanced()
elif section == "7. Summary":
    summary.section_summary()
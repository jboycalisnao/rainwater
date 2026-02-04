import streamlit as st
import pandas as pd
from load_and_clean import load_and_clean
from wet_dry_classification import classify_wet_dry
from spell_analysis import extract_spells
from rainfall_statistics import rainfall_intensity_stats
from synthetic_rainfall_generator import generate_synthetic
from harvest_summary import compute_harvest, summarize_harvest
from reference_table_builder import build_reliability_table
from export_results import export_results_to_json

st.set_page_config(page_title="MCS – Rainwater Harvesting Decision Support Tool", layout="wide")
st.title("MCS – Rainwater Harvesting Decision Support Tool")

# --- File Upload ---
st.header("1. Upload Raw Rainfall CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# --- Parameters ---
st.header("2. School Parameters")
col1, col2, col3, col4 = st.columns(4)
roof = col1.number_input("Roof area / classroom (m²)", value=63.0)
cls = col2.number_input("Number of classrooms", value=4, step=1)
studs = col3.number_input("Students / classroom", value=40, step=1)
demand = col4.number_input("Demand (L / student / day)", value=5.0)

run_analysis = st.button("3. Compute Harvest & Tank Reliability")

if uploaded_file is not None:
    try:
        raw_df = load_and_clean(uploaded_file)
        st.success("Rainfall data loaded successfully.")
    except Exception as e:
        st.error(f"File Error: {e}")
        raw_df = None
else:
    raw_df = None

if run_analysis and raw_df is not None:
    with st.spinner("Running analysis..."):
        try:
            # Synthetic Rainfall
            hist = classify_wet_dry(raw_df)
            spells = extract_spells(hist)
            intensity = rainfall_intensity_stats(hist)
            synth = generate_synthetic(spells, intensity)

            # Harvest
            harvest_df = compute_harvest(
                synth,
                roof_area=roof,
                classrooms=cls,
                runoff_coeff=0.9,
                gutter_eff=0.95,
                first_flush=2.0,
            )
            harvest = summarize_harvest(harvest_df)

            # Display Harvest
            st.subheader("Harvest Potential")
            st.write(f"Annual Harvest: {harvest['annual_L']:,.0f} L / year")
            st.write("Monthly Harvest (L):")
            st.write(pd.DataFrame(list(harvest["monthly_L"].items()), columns=["Month", "Liters"]))

            # Tank Reliability
            daily_demand = cls * studs * demand
            table = build_reliability_table(
                harvest_df,
                tank_sizes=range(500, 30001, 500),
                daily_demand_L=daily_demand,
            )
            st.subheader("Tank Reliability (Top 20)")
            st.dataframe(table.head(20))

            # Export Results
            st.session_state["harvest_df"] = harvest_df
            st.session_state["harvest_summary"] = harvest
            st.session_state["reliability_table"] = table
        except Exception as e:
            st.error(f"Processing Error: {e}")

if (
    "harvest_df" in st.session_state and
    "harvest_summary" in st.session_state and
    "reliability_table" in st.session_state
):
    if st.button("4. Export Results to JSON"):
        try:
            metadata = {
                "roof_area_per_class_m2": roof,
                "number_of_classrooms": cls,
                "students_per_class": studs,
                "demand_L_per_student_per_day": demand,
                "simulation_years": int(st.session_state["harvest_df"]["synthetic_year"].nunique()),
            }
            json_path = export_results_to_json(
                output_path=".",
                metadata=metadata,
                harvest_summary=st.session_state["harvest_summary"],
                reliability_table=st.session_state["reliability_table"],
            )
            st.success(f"Results exported to: {json_path}")
        except Exception as e:
            st.error(f"Export Error: {e}")

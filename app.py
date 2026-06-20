"""CorrosionLab — High-Temperature Oxidation Kinetics Analyzer."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "oxidation_data.csv"


@st.cache_data
def load_oxidation_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def main() -> None:
    st.set_page_config(page_title="CorrosionLab", page_icon="🧪", layout="wide")
    st.title("CorrosionLab")
    st.caption("High-Temperature Oxidation Kinetics Analyzer")

    df = load_oxidation_data()
    st.subheader("Oxidation data (Table 9.1)")
    st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()

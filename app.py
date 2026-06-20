"""CorrosionLab — High-Temperature Oxidation Kinetics Analyzer."""

from __future__ import annotations

import streamlit as st

from corrosionlab.constants import (
    DEFAULT_CONTROL_COLUMN,
    M_AL2O3,
    M_O,
    M_REF,
    RHO_AL2O3,
    S_REF,
    SAMPLE_METADATA,
    TIME_COLUMN,
)
from corrosionlab.expert import UserPreferences, recommend_coating
from corrosionlab.export import (
    build_text_report_pdf,
    combine_results_csv,
    figure_to_pdf_bytes,
    figure_to_svg_bytes,
)
from corrosionlab.fitting import fit_kinetic_model
from corrosionlab.io import (
    DataValidationError,
    get_sample_columns,
    load_csv,
    load_default_data,
    load_template_bytes,
)
from corrosionlab.kinetics import AnalysisConfig, analyze_all
from corrosionlab.plots import (
    plot_fit_extrapolation,
    plot_mass_change,
    plot_protective_effectiveness,
    plot_spallation,
)
from corrosionlab.spallation import detect_spallation_all


@st.cache_data
def cached_analyze(df_bytes: bytes, config_dict: dict) -> dict:
    """Cache analysis results for identical inputs."""
    import pandas as pd
    from io import BytesIO

    df = load_csv(BytesIO(df_bytes))
    config = AnalysisConfig(**config_dict)
    result = analyze_all(df, config)
    alerts = detect_spallation_all(df, config.sample_columns or get_sample_columns(df))
    return {
        "df": df,
        "result": result,
        "alerts": alerts,
    }


def render_sidebar(df) -> AnalysisConfig:
    """Render sidebar controls and return analysis configuration."""
    st.sidebar.header("Konfiguracja")

    sample_cols = get_sample_columns(df)
    control_col = st.sidebar.selectbox(
        "Kolumna referencyjna (niepokryty stop)",
        options=sample_cols,
        index=sample_cols.index(DEFAULT_CONTROL_COLUMN)
        if DEFAULT_CONTROL_COLUMN in sample_cols
        else 0,
    )

    available = [c for c in sample_cols if c != control_col]
    selected = st.sidebar.multiselect(
        "Próbki do analizy",
        options=available,
        default=available,
    )

    st.sidebar.subheader("Stałe fizykochemiczne")
    m_al2o3 = st.sidebar.number_input("M_Al₂O₃ [g/mol]", value=M_AL2O3, format="%.2f")
    m_o = st.sidebar.number_input("M_O [g/mol]", value=M_O, format="%.2f")
    rho = st.sidebar.number_input("ρ_Al₂O₃ [g/cm³]", value=RHO_AL2O3, format="%.2f")
    m_ref = st.sidebar.number_input("Masa referencyjna [g]", value=M_REF, format="%.5f")
    s_ref = st.sidebar.number_input("Powierzchnia referencyjna [cm²]", value=S_REF, format="%.1f")

    all_samples = [control_col, *selected]
    return AnalysisConfig(
        control_column=control_col,
        sample_columns=all_samples,
        m_al2o3=m_al2o3,
        m_o=m_o,
        rho_al2o3=rho,
        m_ref=m_ref,
        s_ref=s_ref,
    )


def main() -> None:
    st.set_page_config(
        page_title="CorrosionLab",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("CorrosionLab")
    st.caption("Analizator kinetyki korozji wysokotemperaturowej — FeCrAl / powłoki zol-żel")

    uploaded = st.sidebar.file_uploader("Wgraj plik CSV", type=["csv"])
    if uploaded is not None:
        try:
            raw_df = load_csv(uploaded.getvalue())
            df_source = uploaded.getvalue()
        except DataValidationError as exc:
            st.error(str(exc))
            st.stop()
    else:
        raw_df = load_default_data()
        df_source = raw_df.to_csv(index=False).encode("utf-8")
        st.sidebar.info("Używane są dane demo (Tabela 9.1 z pracy magisterskiej).")

    config = render_sidebar(raw_df)
    payload = cached_analyze(df_source, config.__dict__)
    df = payload["df"]
    result = payload["result"]
    alerts = payload["alerts"]

    coated_samples = [c for c in config.sample_columns or [] if c != config.control_column]

    tab_dash, tab_analysis, tab_spall, tab_fit, tab_expert = st.tabs(
        [
            "Dashboard",
            "Analiza kinetyczna",
            "Spallation Alert",
            "Ekstrapolacja",
            "Doradca powłok",
        ]
    )

    with tab_dash:
        st.subheader("Teoria i dane wejściowe")
        st.markdown(
            """
            **Prawo Tammanna** opisuje paraboliczną kinetykę utleniania metali: \\(x^2 = k \\cdot t\\),
            gdzie \\(x\\) to np. przyrost masy lub grubość zgorzeliny. CorrosionLab automatyzuje
            obliczenia z równań (9.1)–(9.4) pracy magisterskiej:

            - **9.1** — względna zmiana masy Δm/m₀ [%]
            - **9.2** — skuteczność ochronna Sₖ względem niepokrytego stopu
            - **9.3** — grubość zgorzeliny h [μm]
            - **9.4** — stała paraboliczna kₚ
            """
        )
        st.download_button(
            "Pobierz wzorcowy plik template.csv",
            data=load_template_bytes(),
            file_name="template.csv",
            mime="text/csv",
        )
        st.subheader("Podgląd danych")
        st.dataframe(df, use_container_width=True)

    with tab_analysis:
        st.subheader("Wyniki obliczeń")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Tabela 9.3 — Δm/m₀ [%]**")
            st.dataframe(result.mass_change_pct, use_container_width=True)
        with col2:
            st.markdown("**Tabela 9.4 — Sₖ [%]**")
            st.dataframe(result.protective_effectiveness_pct, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**Tabela 9.5 — grubość zgorzeliny h [μm]**")
            st.dataframe(result.scale_thickness_um, use_container_width=True)
        with col4:
            st.markdown("**Tabela 9.6 — stała paraboliczna kₚ**")
            st.dataframe(result.parabolic_rate, use_container_width=True)

        fig_mass = plot_mass_change(result.mass_change_pct, coated_samples + [config.control_column])
        st.plotly_chart(fig_mass, use_container_width=True)

        if coated_samples:
            fig_sk = plot_protective_effectiveness(result.protective_effectiveness_pct, coated_samples)
            st.plotly_chart(fig_sk, use_container_width=True)

        st.subheader("Eksport wyników")
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            st.download_button(
                "Eksport CSV (wszystkie tabele)",
                data=combine_results_csv(
                    result.mass_change_pct,
                    result.protective_effectiveness_pct,
                    result.scale_thickness_um,
                    result.parabolic_rate,
                ),
                file_name="corrosionlab_results.csv",
                mime="text/csv",
            )
        with exp_col2:
            try:
                st.download_button(
                    "Eksport wykresu SVG",
                    data=figure_to_svg_bytes(fig_mass),
                    file_name="kinetics_mass_change.svg",
                    mime="image/svg+xml",
                )
            except Exception as exc:
                st.caption(f"SVG niedostępny: {exc}")
        with exp_col3:
            try:
                st.download_button(
                    "Eksport wykresu PDF",
                    data=figure_to_pdf_bytes(fig_mass),
                    file_name="kinetics_mass_change.pdf",
                    mime="application/pdf",
                )
            except Exception as exc:
                st.caption(f"PDF niedostępny: {exc}")

        try:
            report_pdf = build_text_report_pdf(
                "CorrosionLab — Raport analizy",
                [
                    f"Próbki: {', '.join(config.sample_columns or [])}",
                    f"Kolumna referencyjna: {config.control_column}",
                    f"Liczba alertów odprysków: {len(alerts)}",
                ],
                {
                    "Delta m/m0 [%]": result.mass_change_pct,
                    "Skutecznosc Sk [%]": result.protective_effectiveness_pct,
                },
            )
            st.download_button(
                "Eksport raportu PDF",
                data=report_pdf,
                file_name="corrosionlab_report.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.caption(f"Raport PDF niedostępny: {exc}")

    with tab_spall:
        st.subheader("Detektor odprysków zgorzeliny")
        st.markdown(
            "Algorytm analizuje pierwszą różnicę masy między kolejnymi cyklami. "
            "Ujemny przyrost masy wskazuje potencjalny odprysk (np. TM4B, TM5A @ 96 h)."
        )
        if alerts.empty:
            st.success("Nie wykryto odprysków w wybranych próbkach.")
        else:
            st.warning(f"Wykryto {len(alerts)} potencjalnych punktów odprysku.")
            st.dataframe(alerts, use_container_width=True)

        fig_spall = plot_spallation(
            result.mass_change_pct,
            alerts,
            coated_samples + [config.control_column],
        )
        st.plotly_chart(fig_spall, use_container_width=True)

    with tab_fit:
        st.subheader("Symulator i ekstrapolacja")
        if not coated_samples:
            st.info("Wybierz próbki do analizy w panelu bocznym.")
        else:
            fit_sample = st.selectbox("Próbka", options=coated_samples)
            fit_model = st.selectbox(
                "Model kinetyczny",
                options=["parabolic", "linear", "paralinear"],
                format_func=lambda x: {
                    "linear": "Liniowy (y = a·t)",
                    "parabolic": "Paraboliczny (y = a·√t)",
                    "paralinear": "Paraliniowy (y = a·√t + b·t)",
                }[x],
            )
            max_time = float(df[TIME_COLUMN].max())
            extrap_hours = st.slider(
                "Horyzont ekstrapolacji [h]",
                min_value=int(max_time + 12),
                max_value=int(max_time + 240),
                value=int(max_time + 120),
                step=12,
            )

            mass_table = result.mass_change_pct
            time_arr = mass_table[TIME_COLUMN].to_numpy()
            y_arr = mass_table[fit_sample].to_numpy()

            try:
                fit_result = fit_kinetic_model(
                    time_arr,
                    y_arr,
                    model=fit_model,
                    extrapolation_hours=[extrap_hours],
                )
                st.metric("R² dopasowania", f"{fit_result.r_squared:.4f}")
                fig_fit = plot_fit_extrapolation(fit_result, fit_sample)
                st.plotly_chart(fig_fit, use_container_width=True)
                st.markdown(
                    f"**Predykcja @ {extrap_hours} h:** "
                    f"Δm/m₀ ≈ {float(fit_result.extrapolation[-1]):.2f}%"
                    if len(fit_result.extrapolation)
                    else ""
                )
            except ValueError as exc:
                st.error(str(exc))

    with tab_expert:
        st.subheader("System ekspercki — doradca powłok")
        st.markdown(
            "Rekomendacje oparte na wnioskach z pracy magisterskiej (rozdz. 11, str. 49–50)."
        )

        priority = st.radio(
            "Priorytet główny",
            options=["max_protection", "min_spallation", "low_cost", "multi_layer", "balanced"],
            format_func=lambda x: {
                "max_protection": "Maksymalna ochrona",
                "min_spallation": "Minimalny odprysk",
                "low_cost": "Niska cena / prosta aplikacja",
                "multi_layer": "Powłoka wielowarstwowa",
                "balanced": "Kompromis (zbalansowany)",
            }[x],
            horizontal=True,
        )
        layer_pref = st.selectbox(
            "Preferowana liczba warstw",
            options=["flexible", "single", "five"],
            format_func=lambda x: {
                "flexible": "Elastycznie (zależnie od priorytetu)",
                "single": "Jedna warstwa",
                "five": "Pięć warstw",
            }[x],
        )
        budget = st.selectbox(
            "Budżet",
            options=["low", "medium", "high"],
            format_func=lambda x: {"low": "Niski", "medium": "Średni", "high": "Wysoki"}[x],
        )
        avoid_spallation = st.checkbox("Unikaj powłok podatnych na odpryski", value=True)

        prefs = UserPreferences(
            priority=priority,
            layer_preference=layer_pref,
            budget=budget,
            avoid_spallation=avoid_spallation,
        )
        rec = recommend_coating(prefs)

        st.success(f"**{rec.title}**")
        st.markdown(rec.description)
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        meta_col1.metric("Kod próbki", rec.sample_code)
        meta_col2.metric("Oczekiwane Sₖ", rec.expected_sk_pct)
        meta_col3.metric("Liczba warstw", rec.layers)

        st.markdown(f"**Nanonapełniacz:** {rec.nanoparticle}")
        with st.expander("Zastosowane reguły"):
            for rule in rec.rules_applied:
                st.markdown(f"- {rule}")

        st.subheader("Baza wiedzy — wszystkie próbki badawcze")
        meta_rows = [
            {
                "Kod": code,
                "Nanonapełniacz": meta.nanoparticle,
                "Warstwy": meta.layers,
                "Sₖ @ 120 h": meta.sk_at_120h,
                "Ryzyko odprysku": "tak" if meta.spallation_prone else "nie",
            }
            for code, meta in SAMPLE_METADATA.items()
        ]
        st.dataframe(meta_rows, use_container_width=True)


if __name__ == "__main__":
    main()

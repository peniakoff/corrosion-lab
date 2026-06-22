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
from corrosionlab.i18n import (
    SUPPORTED_LOCALES,
    LocalizedError,
    detect_browser_locale,
    format_error,
    get_locale,
    t,
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


def init_locale() -> None:
    """Initialize locale from browser on first session load."""
    if "locale" not in st.session_state:
        st.session_state.locale = detect_browser_locale()


def render_locale_selector() -> None:
    """Render language selector in the sidebar."""
    current = get_locale()
    st.sidebar.selectbox(
        t("sidebar.language"),
        options=SUPPORTED_LOCALES,
        format_func=lambda loc: t(f"locale_names.{loc}", locale=loc),
        index=SUPPORTED_LOCALES.index(current),
        key="locale",
    )


def render_sidebar(df) -> AnalysisConfig:
    """Render sidebar controls and return analysis configuration."""
    locale = get_locale()
    st.sidebar.header(t("sidebar.config", locale=locale))

    sample_cols = get_sample_columns(df)
    control_col = st.sidebar.selectbox(
        t("sidebar.control_column", locale=locale),
        options=sample_cols,
        index=sample_cols.index(DEFAULT_CONTROL_COLUMN)
        if DEFAULT_CONTROL_COLUMN in sample_cols
        else 0,
    )

    available = [c for c in sample_cols if c != control_col]
    selected = st.sidebar.multiselect(
        t("sidebar.samples", locale=locale),
        options=available,
        default=available,
    )

    st.sidebar.subheader(t("sidebar.phys_constants", locale=locale))
    m_al2o3 = st.sidebar.number_input("M_Al₂O₃ [g/mol]", value=M_AL2O3, format="%.2f")
    m_o = st.sidebar.number_input("M_O [g/mol]", value=M_O, format="%.2f")
    rho = st.sidebar.number_input("ρ_Al₂O₃ [g/cm³]", value=RHO_AL2O3, format="%.2f")
    m_ref = st.sidebar.number_input(
        t("sidebar.ref_mass", locale=locale),
        value=M_REF,
        format="%.5f",
    )
    s_ref = st.sidebar.number_input(
        t("sidebar.ref_area", locale=locale),
        value=S_REF,
        format="%.1f",
    )

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

    init_locale()
    render_locale_selector()
    locale = get_locale()

    st.title("CorrosionLab")
    st.caption(t("page.caption", locale=locale))

    uploaded = st.sidebar.file_uploader(t("sidebar.upload_csv", locale=locale), type=["csv"])
    if uploaded is not None:
        try:
            raw_df = load_csv(uploaded.getvalue())
            df_source = uploaded.getvalue()
        except DataValidationError as exc:
            st.error(format_error(exc, locale=locale))
            st.stop()
    else:
        raw_df = load_default_data()
        df_source = raw_df.to_csv(index=False).encode("utf-8")
        st.sidebar.info(t("sidebar.demo_data", locale=locale))

    config = render_sidebar(raw_df)
    payload = cached_analyze(df_source, config.__dict__)
    df = payload["df"]
    result = payload["result"]
    alerts = payload["alerts"]

    coated_samples = [c for c in config.sample_columns or [] if c != config.control_column]

    tab_dash, tab_analysis, tab_spall, tab_fit, tab_expert = st.tabs(
        [
            t("tabs.dashboard", locale=locale),
            t("tabs.kinetics", locale=locale),
            t("tabs.spallation", locale=locale),
            t("tabs.extrapolation", locale=locale),
            t("tabs.expert", locale=locale),
        ]
    )

    with tab_dash:
        st.subheader(t("dashboard.theory_header", locale=locale))
        st.markdown(t("dashboard.theory_body", locale=locale))
        st.download_button(
            t("dashboard.download_template", locale=locale),
            data=load_template_bytes(),
            file_name="template.csv",
            mime="text/csv",
        )
        st.subheader(t("dashboard.data_preview", locale=locale))
        st.dataframe(df, width="stretch")

    with tab_analysis:
        st.subheader(t("analysis.results_header", locale=locale))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(t("analysis.table_93", locale=locale))
            st.dataframe(result.mass_change_pct, width="stretch")
        with col2:
            st.markdown(t("analysis.table_94", locale=locale))
            st.dataframe(result.protective_effectiveness_pct, width="stretch")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown(t("analysis.table_95", locale=locale))
            st.dataframe(result.scale_thickness_um, width="stretch")
        with col4:
            st.markdown(t("analysis.table_96", locale=locale))
            st.dataframe(result.parabolic_rate, width="stretch")

        fig_mass = plot_mass_change(
            result.mass_change_pct,
            coated_samples + [config.control_column],
            locale=locale,
        )
        st.plotly_chart(fig_mass, width="stretch")

        if coated_samples:
            fig_sk = plot_protective_effectiveness(
                result.protective_effectiveness_pct,
                coated_samples,
                locale=locale,
            )
            st.plotly_chart(fig_sk, width="stretch")

        st.subheader(t("analysis.export_header", locale=locale))
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            st.download_button(
                t("analysis.export_csv", locale=locale),
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
                    t("analysis.export_svg", locale=locale),
                    data=figure_to_svg_bytes(fig_mass),
                    file_name="kinetics_mass_change.svg",
                    mime="image/svg+xml",
                )
            except Exception as exc:
                st.caption(t("analysis.svg_unavailable", locale=locale, error=exc))
        with exp_col3:
            try:
                st.download_button(
                    t("analysis.export_pdf", locale=locale),
                    data=figure_to_pdf_bytes(fig_mass),
                    file_name="kinetics_mass_change.pdf",
                    mime="application/pdf",
                )
            except Exception as exc:
                st.caption(t("analysis.pdf_unavailable", locale=locale, error=exc))

        try:
            report_pdf = build_text_report_pdf(
                t("analysis.report_title", locale=locale),
                [
                    t(
                        "analysis.report_samples",
                        locale=locale,
                        samples=", ".join(config.sample_columns or []),
                    ),
                    t(
                        "analysis.report_control",
                        locale=locale,
                        control=config.control_column,
                    ),
                    t(
                        "analysis.report_alerts",
                        locale=locale,
                        count=len(alerts),
                    ),
                ],
                {
                    t("analysis.report_section_mass", locale=locale): result.mass_change_pct,
                    t("analysis.report_section_sk", locale=locale): result.protective_effectiveness_pct,
                },
            )
            st.download_button(
                t("analysis.export_report_pdf", locale=locale),
                data=report_pdf,
                file_name="corrosionlab_report.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.caption(t("analysis.report_unavailable", locale=locale, error=exc))

    with tab_spall:
        st.subheader(t("spallation.header", locale=locale))
        st.markdown(t("spallation.description", locale=locale))
        if alerts.empty:
            st.success(t("spallation.no_alerts", locale=locale))
        else:
            st.warning(
                t("spallation.alerts_found", locale=locale, count=len(alerts))
            )
            st.dataframe(alerts, width="stretch")

        fig_spall = plot_spallation(
            result.mass_change_pct,
            alerts,
            coated_samples + [config.control_column],
            locale=locale,
        )
        st.plotly_chart(fig_spall, width="stretch")

    with tab_fit:
        st.subheader(t("extrapolation.header", locale=locale))
        if not coated_samples:
            st.info(t("extrapolation.no_samples", locale=locale))
        else:
            fit_sample = st.selectbox(
                t("extrapolation.sample", locale=locale),
                options=coated_samples,
            )
            fit_model = st.selectbox(
                t("extrapolation.model", locale=locale),
                options=["parabolic", "linear", "paralinear"],
                format_func=lambda x: t(f"extrapolation.models.{x}", locale=locale),
            )
            max_time = float(df[TIME_COLUMN].max())
            extrap_hours = st.slider(
                t("extrapolation.horizon", locale=locale),
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
                st.metric(
                    t("extrapolation.r_squared", locale=locale),
                    f"{fit_result.r_squared:.4f}",
                )
                fig_fit = plot_fit_extrapolation(fit_result, fit_sample, locale=locale)
                st.plotly_chart(fig_fit, width="stretch")
                if len(fit_result.extrapolation):
                    st.markdown(
                        t(
                            "extrapolation.prediction",
                            locale=locale,
                            hours=extrap_hours,
                            value=float(fit_result.extrapolation[-1]),
                        )
                    )
            except LocalizedError as exc:
                st.error(format_error(exc, locale=locale))

    with tab_expert:
        st.subheader(t("expert.header", locale=locale))
        st.markdown(t("expert.intro", locale=locale))

        priority = st.radio(
            t("expert.priority_label", locale=locale),
            options=["max_protection", "min_spallation", "low_cost", "multi_layer", "balanced"],
            format_func=lambda x: t(f"expert.priority.{x}", locale=locale),
            horizontal=True,
        )
        layer_pref = st.selectbox(
            t("expert.layers_label", locale=locale),
            options=["flexible", "single", "five"],
            format_func=lambda x: t(f"expert.layers.{x}", locale=locale),
        )
        budget = st.selectbox(
            t("expert.budget_label", locale=locale),
            options=["low", "medium", "high"],
            format_func=lambda x: t(f"expert.budget.{x}", locale=locale),
        )
        avoid_spallation = st.checkbox(
            t("expert.avoid_spallation", locale=locale),
            value=True,
        )

        prefs = UserPreferences(
            priority=priority,
            layer_preference=layer_pref,
            budget=budget,
            avoid_spallation=avoid_spallation,
        )
        rec = recommend_coating(prefs, locale=locale)

        st.success(f"**{rec.title}**")
        st.markdown(rec.description)
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        meta_col1.metric(t("expert.sample_code", locale=locale), rec.sample_code)
        meta_col2.metric(t("expert.expected_sk", locale=locale), rec.expected_sk_pct)
        meta_col3.metric(t("expert.layer_count", locale=locale), rec.layers)

        st.markdown(
            t("expert.nanoparticle", locale=locale, nanoparticle=rec.nanoparticle)
        )
        with st.expander(t("expert.rules_expander", locale=locale)):
            for rule in rec.rules_applied:
                st.markdown(f"- {rule}")

        st.subheader(t("expert.knowledge_base", locale=locale))
        meta_rows = [
            {
                t("expert.knowledge.code", locale=locale): code,
                t("expert.knowledge.nanoparticle", locale=locale): meta.nanoparticle,
                t("expert.knowledge.layers", locale=locale): meta.layers,
                t("expert.knowledge.sk_120h", locale=locale): meta.sk_at_120h,
                t("expert.knowledge.spallation_risk", locale=locale): (
                    t("expert.knowledge.yes", locale=locale)
                    if meta.spallation_prone
                    else t("expert.knowledge.no", locale=locale)
                ),
            }
            for code, meta in SAMPLE_METADATA.items()
        ]
        st.dataframe(meta_rows, width="stretch")


if __name__ == "__main__":
    main()

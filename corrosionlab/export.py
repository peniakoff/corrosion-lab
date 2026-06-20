"""Export utilities for tables and figures."""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a dataframe to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def combine_results_csv(
    mass_change: pd.DataFrame,
    sk: pd.DataFrame,
    thickness: pd.DataFrame,
    kp: pd.DataFrame,
) -> bytes:
    """Combine all result tables into a single CSV with section headers."""
    sections = [
        ("mass_change_pct", mass_change),
        ("protective_effectiveness_pct", sk),
        ("scale_thickness_um", thickness),
        ("parabolic_rate", kp),
    ]
    parts: list[str] = []
    for name, frame in sections:
        parts.append(f"# {name}")
        parts.append(frame.to_csv(index=False))
    return "\n".join(parts).encode("utf-8")


def figure_to_svg_bytes(fig: go.Figure) -> bytes:
    """Export a Plotly figure to SVG."""
    return fig.to_image(format="svg", engine="kaleido")


def figure_to_pdf_bytes(fig: go.Figure) -> bytes:
    """Export a Plotly figure to PDF."""
    return fig.to_image(format="pdf", engine="kaleido")


def build_text_report_pdf(
    title: str,
    summary_lines: list[str],
    tables: dict[str, pd.DataFrame],
) -> bytes:
    """Build a simple PDF report with summary text and truncated tables."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    for line in summary_lines:
        pdf.multi_cell(0, 6, line)
    pdf.ln(4)

    for section_name, df in tables.items():
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, section_name, ln=True)
        pdf.set_font("Helvetica", "", 8)
        preview = df.head(12).to_string(index=False)
        pdf.multi_cell(0, 4, preview)
        pdf.ln(4)

    out = BytesIO()
    pdf.output(out)
    return out.getvalue()

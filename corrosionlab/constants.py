"""Physical constants and sample metadata from the Master's thesis."""

from dataclasses import dataclass

# Table 9.2 — constants used in equations 9.3 and 9.4
M_AL2O3 = 101.96  # g/mol
M_O = 16.00  # g/mol
RHO_AL2O3 = 3.97  # g/cm³

# Reference sample for surface area calculation (thesis section 9)
M_REF = 0.10950  # g
S_REF = 7.0  # cm²

DEFAULT_CONTROL_COLUMN = "TM_Control"
TIME_COLUMN = "time_h"

SECONDS_PER_HOUR = 3600


@dataclass(frozen=True)
class SampleMetadata:
    """Table 8.1 — coating composition and layer count."""

    code: str
    nanoparticle: str
    layers: int
    sk_at_120h: float | None = None
    spallation_prone: bool = False


SAMPLE_METADATA: dict[str, SampleMetadata] = {
    "TM1A": SampleMetadata("TM1A", "Al₂O₃ (Aluminiumoxid C)", 1, sk_at_120h=4.5),
    "TM1B": SampleMetadata("TM1B", "Al₂O₃ (Aluminiumoxid C)", 5, sk_at_120h=25.0),
    "TM2A": SampleMetadata("TM2A", "SiO₂ (Aerosil 380)", 1, sk_at_120h=55.0),
    "TM2B": SampleMetadata("TM2B", "SiO₂ (Aerosil 380)", 5, sk_at_120h=28.0),
    "TM3A": SampleMetadata("TM3A", "SiO₂ (Aerosil R974)", 1, sk_at_120h=36.0),
    "TM3B": SampleMetadata("TM3B", "SiO₂ (Aerosil R974)", 5, sk_at_120h=22.0),
    "TM4A": SampleMetadata("TM4A", "ZrO₂ (Y-stabilized)", 1, sk_at_120h=80.5),
    "TM4B": SampleMetadata("TM4B", "ZrO₂ (Y-stabilized)", 5, sk_at_120h=100.0),
    "TM5A": SampleMetadata("TM5A", "Y₂O₃", 1, sk_at_120h=15.9, spallation_prone=True),
    "TM5B": SampleMetadata("TM5B", "Y₂O₃", 5, sk_at_120h=27.3, spallation_prone=True),
    "TM6A": SampleMetadata("TM6A", "ZrO₂ (Y-stabilized)", 1, sk_at_120h=33.3),
    "TM6B": SampleMetadata("TM6B", "ZrO₂ (Y-stabilized)", 5, sk_at_120h=36.0),
    "TM7A": SampleMetadata("TM7A", "CeO₂/ZrO₂", 1, sk_at_120h=34.0),
    "TM7B": SampleMetadata("TM7B", "CeO₂/ZrO₂", 5, sk_at_120h=40.0),
}

# Reference values from thesis tables for regression tests
THESIS_REFERENCE = {
    "TM_Control": {"delta_m_pct_120h": 3.0},
    "TM1A": {"delta_m_pct_120h": 2.8, "sk_120h": 2.8},
    "TM4B": {"delta_m_pct_120h": 0.0, "sk_120h": 100.0},
    "TM5A": {"delta_m_pct_120h": 2.9, "sk_120h": 15.9},
}

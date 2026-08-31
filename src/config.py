from dataclasses import dataclass

RANDOM_STATE = 42

CONTINUOUS_FEATURES = ["duration", "amount", "age"]

# South German Credit represents these as integer-coded categories / ordered buckets.
CATEGORICAL_FEATURES = [
    "status",
    "credit_history",
    "purpose",
    "savings",
    "employment_duration",
    "installment_rate",
    "personal_status_sex",
    "other_debtors",
    "present_residence",
    "property",
    "other_installment_plans",
    "housing",
    "number_credits",
    "job",
    "people_liable",
    "telephone",
    "foreign_worker",
]

@dataclass(frozen=True)
class StressScenario:
    name: str
    weight: float
    pd_multiplier: float
    lgd_addon: float

# Illustrative scenario design for demonstrating the engine. These are not
# regulatory, accounting, or institution-specific calibration parameters.
SCENARIOS = (
    StressScenario("base", 0.60, 1.00, 0.00),
    StressScenario("downside", 0.30, 1.35, 0.05),
    StressScenario("severe", 0.10, 1.75, 0.15),
)

BASE_LGD = 0.45
EFFECTIVE_INTEREST_RATE = 0.05
STAGE2_ABSOLUTE_PD = 0.10
SICR_RATIO = 2.0

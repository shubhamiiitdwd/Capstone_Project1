"""
ML Models (optional prediction layer)
Trains simple scikit-learn models on simulation data and exposes prediction
helpers for:
  1. Breakdown Prediction  – probability a line breaks down in next 4 h
  2. Delay Prediction       – delivery delay risk score (0-1)
  3. Supplier Risk Scoring  – score each supplier 0-100
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=FutureWarning)

# Try importing sklearn; gracefully degrade if not installed
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# ---------------------------------------------------------------------------
# Line order and name mapping (consistent across delay/breakdown)
# ---------------------------------------------------------------------------
ALL_LINES = ["HighRange_1", "HighRange_2", "MediumRange_1", "MediumRange_2", "MediumRange_3"]
# Map data column values to canonical names (e.g. HighRange_Line1 -> HighRange_1)
LINE_NAME_MAP = {
    "HighRange_Line1": "HighRange_1", "HighRange_1": "HighRange_1",
    "HighRange_Line2": "HighRange_2", "HighRange_2": "HighRange_2",
    "MedRange_Line1": "MediumRange_1", "MediumRange_1": "MediumRange_1",
    "MedRange_Line2": "MediumRange_2", "MediumRange_2": "MediumRange_2",
    "MedRange_Line3": "MediumRange_3", "MediumRange_3": "MediumRange_3",
}


def _line_df_for_canonical(df: pd.DataFrame, canonical_line: str) -> pd.DataFrame:
    """Get rows for a canonical line name; handles HighRange_Line1 vs HighRange_1 etc."""
    possible_names = [k for k, v in LINE_NAME_MAP.items() if v == canonical_line]
    mask = df["Assembly_Line"].astype(str).isin(possible_names)
    return df[mask] if mask.any() else pd.DataFrame()


# ---------------------------------------------------------------------------
# Data classes for predictions
# ---------------------------------------------------------------------------
@dataclass
class BreakdownPrediction:
    line: str
    probability: float          # 0-1
    risk_level: str             # LOW / MEDIUM / HIGH
    contributing_factors: List[str] = field(default_factory=list)


@dataclass
class DelayPrediction:
    risk_score: float           # 0-1
    risk_level: str
    line: str = ""              # Assembly line (for per-line delay risk)
    factors: List[str] = field(default_factory=list)
    # Calculation breakdown for UI transparency
    calculation_breakdown: Optional[Dict[str, Any]] = None  # formula, inputs, contributions


@dataclass
class SupplierRisk:
    supplier_name: str
    score: float                # 0-100 (higher = safer)
    risk_level: str
    lead_time_days: int = 0
    reliability: float = 0.0


@dataclass
class MLPredictions:
    """Aggregated ML model output."""
    breakdown_predictions: List[BreakdownPrediction] = field(default_factory=list)
    delay_prediction: Optional[DelayPrediction] = None  # Kept for backward compat (worst line)
    delay_predictions: List[DelayPrediction] = field(default_factory=list)  # Per-line delay risk
    supplier_risks: List[SupplierRisk] = field(default_factory=list)
    models_trained: bool = False


# ---------------------------------------------------------------------------
# ML Model Manager
# ---------------------------------------------------------------------------
class MLModelManager:
    """Trains and manages the three prediction models."""

    def __init__(self):
        self.breakdown_model = None
        self.delay_model = None
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.trained = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, df: pd.DataFrame) -> bool:
        """Train models on the full simulation dataset (1000 records)."""
        if not HAS_SKLEARN:
            print("  [ML] scikit-learn not installed – ML models disabled")
            return False

        try:
            self._train_breakdown_model(df)
            self._train_delay_model(df)
            self.trained = True
            print("  [OK] ML models trained successfully")
            return True
        except Exception as e:
            print(f"  [ML] Training error: {e}")
            return False

    def _train_breakdown_model(self, df: pd.DataFrame):
        """Binary classifier: will a maintenance alert fire? (proxy for breakdown)"""
        features = ["Machine_Uptime_%", "Worker_Availability_%", "Defect_Rate_%",
                     "Energy_Consumption_kWh"]
        available = [f for f in features if f in df.columns]
        if not available or "Alert_Status" not in df.columns:
            return

        X = df[available].fillna(0).copy()
        # Target: 1 if maintenance alert, 0 otherwise
        y = (df["Alert_Status"] == "Maintenance_Alert").astype(int)

        if y.sum() < 5:
            return  # too few positives

        self.breakdown_model = RandomForestClassifier(
            n_estimators=100, max_depth=5, random_state=42, class_weight="balanced"
        )
        self.breakdown_model.fit(X, y)
        self._breakdown_features = available

    def _train_delay_model(self, df: pd.DataFrame):
        """Regressor: predict KPI impact (proxy for delay severity)."""
        if "Predicted_KPI_Impact_%" not in df.columns:
            return

        features = ["Inventory_Status_%", "Machine_Uptime_%",
                     "Worker_Availability_%", "Defect_Rate_%"]
        available = [f for f in features if f in df.columns]
        if not available:
            return

        X = df[available].fillna(0).copy()
        y = df["Predicted_KPI_Impact_%"].fillna(0)

        self.delay_model = GradientBoostingRegressor(
            n_estimators=80, max_depth=4, random_state=42
        )
        self.delay_model.fit(X, y)
        self._delay_features = available

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def predict(
        self, scenario_df: pd.DataFrame, context: Dict[str, Any]
    ) -> MLPredictions:
        """Run all predictions for a given scenario."""
        output = MLPredictions(models_trained=self.trained)

        if not self.trained:
            # Provide heuristic fallbacks
            output.breakdown_predictions = self._heuristic_breakdown(scenario_df)
            delay_list = self._heuristic_delay_per_line(scenario_df)
            output.delay_predictions = delay_list
            output.delay_prediction = max(delay_list, key=lambda d: d.risk_score) if delay_list else None
            output.supplier_risks = self._heuristic_supplier_risk(context)
            return output

        output.breakdown_predictions = self._predict_breakdown(scenario_df)
        delay_list = self._predict_delay_per_line(scenario_df)
        output.delay_predictions = delay_list
        output.delay_prediction = max(delay_list, key=lambda d: d.risk_score) if delay_list else None
        output.supplier_risks = self._heuristic_supplier_risk(context)  # always heuristic

        return output

    def _predict_breakdown(self, df: pd.DataFrame) -> List[BreakdownPrediction]:
        preds = []
        if self.breakdown_model is None:
            return self._heuristic_breakdown(df)

        for line in ALL_LINES:
            line_df = _line_df_for_canonical(df, line)
            use_df = line_df if len(line_df) > 0 else df
            X = pd.DataFrame(
                [use_df[self._breakdown_features].fillna(0).mean()],
                columns=self._breakdown_features,
            )
            prob = float(self.breakdown_model.predict_proba(X)[0, 1])
            risk = "HIGH" if prob > 0.6 else "MEDIUM" if prob > 0.3 else "LOW"

            factors = []
            uptime = float(use_df["Machine_Uptime_%"].mean()) if "Machine_Uptime_%" in use_df.columns else 85.0
            if uptime < 80:
                factors.append(f"Low uptime ({uptime:.1f}%)")
            defect = float(use_df["Defect_Rate_%"].mean()) if "Defect_Rate_%" in use_df.columns else 1.0
            if defect > 1.5:
                factors.append(f"High defect rate ({round(defect, 2)}%)")

            preds.append(BreakdownPrediction(
                line=line, probability=round(prob, 2),
                risk_level=risk, contributing_factors=factors,
            ))
        order_map = {ln: i for i, ln in enumerate(ALL_LINES)}
        return sorted(preds, key=lambda p: (order_map.get(p.line, 99), -p.probability))

    def _predict_delay_per_line(self, df: pd.DataFrame) -> List[DelayPrediction]:
        """Delay risk per assembly line (line-wise). Always returns all 5 lines in fixed order."""
        if self.delay_model is None:
            return self._heuristic_delay_per_line(df)

        preds = []
        for line in ALL_LINES:
            line_df = _line_df_for_canonical(df, line)
            use_df = line_df if len(line_df) > 0 else df
            X = pd.DataFrame(
                [use_df[self._delay_features].fillna(0).mean()],
                columns=self._delay_features,
            )
            kpi_impact = float(self.delay_model.predict(X)[0])
            risk_score = max(0.0, min(1.0, 1.0 - kpi_impact / 10.0))
            risk = "HIGH" if risk_score > 0.6 else "MEDIUM" if risk_score > 0.3 else "LOW"

            inv = float(use_df["Inventory_Status_%"].mean()) if "Inventory_Status_%" in use_df.columns else 0.0
            if np.isnan(inv) or (inv != inv):
                inv = float(df["Inventory_Status_%"].mean()) if "Inventory_Status_%" in df.columns else 0.0
            inv = 0.0 if np.isnan(inv) else inv
            semi = "Available"
            if "Semiconductor_Availability" in use_df.columns and len(use_df) > 0:
                semi = str(use_df["Semiconductor_Availability"].mode().iloc[0])
            elif "Semiconductor_Availability" in df.columns and len(df) > 0:
                semi = str(df["Semiconductor_Availability"].mode().iloc[0])
            factors = [f"Inventory at {inv:.2f}%", f"Semiconductor: {semi}"]

            preds.append(DelayPrediction(
                risk_score=round(risk_score, 2), risk_level=risk, line=line,
                factors=factors,
                calculation_breakdown={"method": "ML (Gradient Boosting Regressor)", "line": line},
            ))
        order_map = {ln: i for i, ln in enumerate(ALL_LINES)}
        return sorted(preds, key=lambda p: (order_map.get(p.line, 99), -p.risk_score))

    # ------------------------------------------------------------------
    # Heuristic fallbacks (when sklearn unavailable)
    # ------------------------------------------------------------------
    @staticmethod
    def _heuristic_breakdown(df: pd.DataFrame) -> List[BreakdownPrediction]:
        preds = []
        for line in ALL_LINES:
            line_df = _line_df_for_canonical(df, line)
            use_df = line_df if len(line_df) > 0 else df
            uptime = float(use_df["Machine_Uptime_%"].mean()) if "Machine_Uptime_%" in use_df.columns else 85.0
            prob = max(0.0, min(1.0, (100 - uptime) / 50))
            risk = "HIGH" if prob > 0.5 else "MEDIUM" if prob > 0.25 else "LOW"
            factors = []
            if uptime < 80:
                factors.append(f"Low uptime ({round(uptime, 2)}%)")
            preds.append(BreakdownPrediction(
                line=line, probability=round(prob, 2),
                risk_level=risk, contributing_factors=factors,
            ))
        order_map = {ln: i for i, ln in enumerate(ALL_LINES)}
        return sorted(preds, key=lambda p: (order_map.get(p.line, 99), -p.probability))

    @staticmethod
    def _heuristic_delay_per_line(df: pd.DataFrame) -> List[DelayPrediction]:
        """Delay risk per assembly line (line-wise heuristic). Always returns all 5 lines in fixed order."""
        preds = []
        for line in ALL_LINES:
            line_df = _line_df_for_canonical(df, line)
            use_df = line_df if len(line_df) > 0 else df
            inv = float(use_df["Inventory_Status_%"].mean()) if "Inventory_Status_%" in use_df.columns else 80.0
            inv = 80.0 if (inv != inv or np.isnan(inv)) else inv
            semi_mode = (str(use_df["Semiconductor_Availability"].mode().iloc[0]) if "Semiconductor_Availability" in use_df.columns and len(use_df) > 0
                        else str(df["Semiconductor_Availability"].mode().iloc[0]) if "Semiconductor_Availability" in df.columns and len(df) > 0 else "Available")
            risk_score = 0.2
            factors = [f"Inventory at {inv:.2f}%", f"Semiconductor: {semi_mode}"]
            if inv < 75:
                risk_score += 0.3
            if semi_mode == "Shortage":
                risk_score += 0.3
            elif semi_mode == "Delayed":
                risk_score += 0.15
            risk_score = min(1.0, risk_score)
            risk = "HIGH" if risk_score > 0.6 else "MEDIUM" if risk_score > 0.3 else "LOW"
            preds.append(DelayPrediction(
                risk_score=round(risk_score, 2), risk_level=risk, line=line,
                factors=factors,
                calculation_breakdown={"method": "Heuristic", "line": line},
            ))
        order_map = {ln: i for i, ln in enumerate(ALL_LINES)}
        return sorted(preds, key=lambda p: (order_map.get(p.line, 99), -p.risk_score))

    @staticmethod
    def _heuristic_supplier_risk(ctx: Dict[str, Any]) -> List[SupplierRisk]:
        suppliers = ctx.get("suppliers", [])
        risks = []
        for s in suppliers[:15]:
            reliability = float(s.get("reliability", 85))
            lead = int(s.get("lead_time_days", 5))
            # Score: higher is safer (stable delivery, low delay risk)
            score = reliability - (lead * 1.5)
            score = max(0, min(100, score))
            risk = "LOW" if score >= 80 else "MEDIUM" if score >= 60 else "HIGH"
            risks.append(SupplierRisk(
                supplier_name=s.get("name", s.get("id", "Unknown")),
                score=round(score, 2),
                risk_level=risk,
                lead_time_days=lead,
                reliability=reliability,
            ))
        return sorted(risks, key=lambda r: r.score, reverse=True)

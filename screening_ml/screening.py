"""
Screening/ML Module
------------------
Implements both rule-based and ML-driven screening for identifying multi-bagger candidates.
- Modular, extendable, and ready for both filter logic and ML classifiers.
- Handles feature engineering from financial data, sentiment, etc.
"""
from typing import Dict, List
import numpy as np
from utils.logger import setup_logger

logger = setup_logger(__name__)

class StockScreener:
    """
    Rule-based and ML-based screener for multi-bagger identification.
    """
    def __init__(self, ml_model=None):
        """
        Args:
            ml_model: Optional sklearn-compatible model for ML-based screening.
        """
        self.ml_model = ml_model

    @staticmethod
    def passes_filters(metrics: Dict) -> bool:
        """
        Hard-coded rules for identifying multi-bagger prospects.
        Args:
            metrics (Dict): Dict of company financials (expects keys like 'ROCE', 'ROE', 'CAGR', 'DE', etc.)
        Returns:
            bool: True if company passes all filters
        """
        try:
            roce = float(metrics.get('ROCE', 0))
            roe = float(metrics.get('ROE', 0))
            cagr = float(metrics.get('CAGR', 0))
            de = float(metrics.get('DE', 1))
            pe = float(metrics.get('PE', 100))
            fcf = float(metrics.get('FCF', 0))
            # Filters: strong returns, low leverage, attractive valuation
            if (
                roce >= 15 and
                roe >= 15 and
                cagr >= 15 and
                de < 0.5 and
                pe < 25 and
                fcf > 0
            ):
                return True
        except Exception as e:
            logger.error(f"Filter check failed: {e}")
        return False

    def filter_stocks(self, all_metrics: List[Dict]) -> List[Dict]:
        """
        Applies rule-based filter to a batch of companies.
        Args:
            all_metrics (List[Dict]): Each dict has metrics for one company.
        Returns:
            List[Dict]: Only those passing filters.
        """
        passed = [m for m in all_metrics if self.passes_filters(m)]
        logger.info(f"{len(passed)}/{len(all_metrics)} companies passed rule-based filters.")
        return passed

    def ml_predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predict multi-bagger probabilities using trained ML model.
        Args:
            features (np.ndarray): Feature array for batch prediction.
        Returns:
            np.ndarray: Array of probabilities.
        """
        if self.ml_model:
            try:
                preds = self.ml_model.predict_proba(features)[:, 1]  # 2-class model: probability multi-bagger
                logger.info(f"ML predicted probabilities shape: {preds.shape}")
                return preds
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
        else:
            logger.warning("No ML model set; returning zeros.")
        return np.zeros(features.shape[0])

# Example usage:
# screener = StockScreener(ml_model=your_loaded_model)
# passed = screener.filter_stocks([metrics1, metrics2, ...])
# probs = screener.ml_predict(feature_matrix)

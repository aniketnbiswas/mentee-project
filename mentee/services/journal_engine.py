import difflib
import numpy as np
from sqlalchemy import desc
from mentee.models import JournalEntry, UserIdentity, db

class PerformanceEngine:
    
    # Elite Scoring Weights
    WEIGHTS = {
        'focus': 0.35,
        'stability': 0.25,
        'execution': 0.25,
        'recovery': 0.15
    }

    @staticmethod
    def compute_score(metrics: dict) -> float:
        """
        Calculates the Weighted Mental Performance Score.
        Returns float 0.0 - 10.0.
        """
        try:
            score = (
                (float(metrics.get('focus', 0)) * PerformanceEngine.WEIGHTS['focus']) +
                (float(metrics.get('stability', 0)) * PerformanceEngine.WEIGHTS['stability']) +
                (float(metrics.get('execution', 0)) * PerformanceEngine.WEIGHTS['execution']) +
                (float(metrics.get('recovery', 0)) * PerformanceEngine.WEIGHTS['recovery'])
            )
            return round(score, 2)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def detect_autopilot(current_text: str, user_id: int) -> str:
        """
        Anti-Autopilot System.
        Compares current entry text against the last entry to detect low-effort copy-pasting.
        """
        if not current_text or len(current_text) < 8:
            return 'autopilot' # Too short

        last_entry = JournalEntry.query.filter_by(user_id=user_id)\
            .order_by(desc(JournalEntry.date)).first()
        
        if last_entry and last_entry.reflection_data:
            # Flatten previous dict values to string
            prev_text = " ".join([str(v) for v in last_entry.reflection_data.values() if v])
            
            # Sequence Matcher: Ratio > 0.65 implies high similarity (copy-paste)
            similarity = difflib.SequenceMatcher(None, current_text, prev_text).ratio()
            
            if similarity > 0.65:
                return 'autopilot'
        
        return 'high_entropy'

    @staticmethod
    def get_identity_schema(user_id: int):
        """
        Generates dynamic prompts based on the user's psychological archetype.
        """
        identity = UserIdentity.query.filter_by(user_id=user_id).first()
        
        # Base Protocol (Night Closure)
        base_schema = [
            {"id": "win", "label": "Tactical Victory", "placeholder": "One specific execution win..."},
            {"id": "fix", "label": "Mechanical Failure", "placeholder": "One error to correct tomorrow..."}
        ]

        if not identity or not identity.core_traits:
            return base_schema

        # Archetype Injection
        traits = identity.core_traits
        if "Stoic" in traits:
            base_schema.append({"id": "id_check", "label": "Emotional Override", "placeholder": "Where did you suppress impulse today?"})
        if "Aggressive" in traits:
            base_schema.append({"id": "id_check", "label": "Hesitation Audit", "placeholder": "Did you strike when the window opened?"})
        if "Analytical" in traits:
            base_schema.append({"id": "id_check", "label": "Data Divergence", "placeholder": "What outcome defied your prediction?"})

        return base_schema

    @staticmethod
    def analyze_trends(user_id: int):
        """
        Lightweight worker for /api/performance-insights.
        Calculates Volatility, Trend Vector, and Consistency Grade.
        """
        # Fetch last 14 entries (2 weeks)
        entries = JournalEntry.query.filter_by(user_id=user_id)\
            .order_by(desc(JournalEntry.date)).limit(14).all()
        
        if not entries or len(entries) < 3:
            return {"status": "insufficient_data"}

        # Extract non-null scores
        scores = [e.performance_score for e in entries if e.performance_score is not None]
        
        if not scores:
            return {"status": "insufficient_data"}

        # Math Stats
        mean = sum(scores) / len(scores)
        variance = sum([((x - mean) ** 2) for x in scores]) / len(scores)
        volatility = variance ** 0.5

        # Trend Vector (Linear approximation of start vs end)
        trend = "Stable"
        if scores[0] > scores[-1] * 1.1: trend = "Ascending"
        elif scores[0] < scores[-1] * 0.9: trend = "Decaying"

        # Consistency Grading
        grade = "Volatile"
        if volatility < 0.8: grade = "Elite"
        elif volatility < 1.5: grade = "Stable"

        return {
            "status": "success",
            "current_mean": round(mean, 1),
            "volatility_index": round(volatility, 2),
            "trend_vector": trend,
            "consistency_grade": grade,
            "sample_size": len(scores)
        }
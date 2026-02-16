"""
Context Rot Monitor - Lightweight Drift Detection Engine
Uses TF-IDF instead of sentence transformers for Windows compatibility
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConversationTurn:
    turn_number: int
    user_message: str
    assistant_response: str
    timestamp: datetime


@dataclass
class DriftMetrics:
    turn_number: int
    similarity_score: float
    is_drifting: bool
    last_good_turn: int
    drift_reason: Optional[str] = None


class DriftEngine:
    def __init__(self, similarity_threshold: float = 0.45, check_interval: int = 3):
        """
        Initialize the drift detection engine with TF-IDF
        
        Args:
            similarity_threshold: Below this cosine similarity, we consider the conversation drifting
            check_interval: Check for drift every N turns
        """
        self.threshold = similarity_threshold
        self.check_interval = check_interval
        
        # Use TF-IDF vectorizer (lightweight alternative to transformers)
        print("Loading TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Conversation state
        self.north_star: Optional[str] = None
        self.north_star_embedding: Optional[np.ndarray] = None
        self.conversation_history: List[ConversationTurn] = []
        self.drift_history: List[DriftMetrics] = []
        self.last_good_turn = 0
        self.all_texts = []  # Keep track of all texts for vectorizer
        
    def set_north_star(self, initial_prompt: str):
        """Set the original goal/intent from Turn 1"""
        self.north_star = initial_prompt
        self.all_texts = [initial_prompt]
        self.last_good_turn = 1
        print(f"✅ North Star set: {initial_prompt[:100]}...")
        
    def add_turn(self, user_message: str, assistant_response: str) -> Optional[DriftMetrics]:
        """
        Add a conversation turn and check for drift if needed
        
        Returns:
            DriftMetrics if drift check was performed, None otherwise
        """
        turn_number = len(self.conversation_history) + 1
        turn = ConversationTurn(
            turn_number=turn_number,
            user_message=user_message,
            assistant_response=assistant_response,
            timestamp=datetime.now()
        )
        self.conversation_history.append(turn)
        
        # Add to all texts
        self.all_texts.append(f"{user_message} {assistant_response}")
        
        # Check for drift at intervals
        if turn_number % self.check_interval == 0:
            return self.check_drift()
        
        return None
    
    def generate_state_summary(self) -> str:
        """
        Generate a summary of the last N turns
        """
        # Take last 3 turns for context
        recent_turns = self.conversation_history[-3:]
        
        summary_parts = []
        for turn in recent_turns:
            summary_parts.append(f"{turn.user_message} {turn.assistant_response}")
        
        return " ".join(summary_parts)
    
    def check_drift(self) -> DriftMetrics:
        """
        Check if the conversation has drifted from the North Star
        
        Returns:
            DriftMetrics containing similarity score and drift status
        """
        if not self.north_star:
            raise ValueError("North Star not set. Call set_north_star() first.")
        
        # Generate current state summary
        current_state = self.generate_state_summary()
        
        # Create vectors using TF-IDF
        texts = [self.north_star, current_state]
        try:
            vectors = self.vectorizer.fit_transform(texts)
            similarity_matrix = sklearn_cosine_similarity(vectors[0:1], vectors[1:2])
            similarity = float(similarity_matrix[0][0])
        except Exception as e:
            print(f"Warning: Vectorization failed, using fallback: {e}")
            # Simple fallback: word overlap ratio
            north_words = set(self.north_star.lower().split())
            current_words = set(current_state.lower().split())
            if len(north_words | current_words) > 0:
                similarity = len(north_words & current_words) / len(north_words | current_words)
            else:
                similarity = 0.0
        
        # Determine if drifting
        is_drifting = similarity < self.threshold
        
        # Update last good turn
        if not is_drifting:
            self.last_good_turn = len(self.conversation_history)
        
        metrics = DriftMetrics(
            turn_number=len(self.conversation_history),
            similarity_score=float(similarity),
            is_drifting=is_drifting,
            last_good_turn=self.last_good_turn
        )
        
        self.drift_history.append(metrics)
        
        print(f"🔍 Turn {metrics.turn_number}: Similarity = {similarity:.3f} {'🔴 DRIFTING' if is_drifting else '🟢 ON TRACK'}")
        
        return metrics
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the entire conversation state"""
        return {
            "total_turns": len(self.conversation_history),
            "north_star": self.north_star,
            "last_good_turn": self.last_good_turn,
            "current_drift_status": self.drift_history[-1].is_drifting if self.drift_history else False,
            "drift_checks": len(self.drift_history),
            "conversation_history": [
                {
                    "turn": t.turn_number,
                    "user": t.user_message,
                    "assistant": t.assistant_response
                }
                for t in self.conversation_history
            ]
        }


# Quick test
if __name__ == "__main__":
    engine = DriftEngine(similarity_threshold=0.45, check_interval=3)
    
    # Simulate a conversation that drifts
    engine.set_north_star("I need help processing a refund for order #12345")
    
    # Turn 2-3: On track
    engine.add_turn("The order was placed last week", "I can help with that refund. Let me look up order #12345.")
    engine.add_turn("What's the status?", "Order #12345 is eligible for refund. I'll process it now.")
    
    # Turn 4-6: Starting to drift
    metrics = engine.add_turn("Actually, I can't log in", "Let me help you with login issues. What's your email?")
    if metrics:
        print(f"Drift detected at turn {metrics.turn_number}: {metrics.similarity_score:.3f}")
    
    engine.add_turn("test@example.com", "I'll send you a password reset link.")
    engine.add_turn("I didn't get the email", "Let me check your spam folder settings.")
    
    # Turn 7: Should show significant drift
    metrics = engine.add_turn("How do I change my email preferences?", "Here's how to update your email settings...")
    if metrics:
        print(f"Drift detected at turn {metrics.turn_number}: {metrics.similarity_score:.3f}")

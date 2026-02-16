"""
Context Rot Monitor - LLM Supervisor
Uses Groq's Llama-3 to provide qualitative analysis of drift
"""
import os
from groq import Groq
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class SupervisorAnalysis:
    is_pursuing_goal: bool
    distraction: Optional[str]
    realignment_instruction: str
    confidence: str  # "high", "medium", "low"


class LLMSupervisor:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client"""
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"  # Fast and accurate
        
    def analyze_drift(
        self, 
        north_star: str, 
        current_conversation: str,
        similarity_score: float
    ) -> SupervisorAnalysis:
        """
        Use LLM-as-a-Judge to analyze why drift occurred
        
        Args:
            north_star: Original user goal
            current_conversation: Recent conversation context
            similarity_score: Numerical drift score
            
        Returns:
            SupervisorAnalysis with actionable insights
        """
        system_prompt = """You are a conversation quality supervisor. Your job is to detect when an AI agent has drifted from the user's original goal and provide clear guidance to get back on track.

Be concise and actionable. Focus on what matters."""

        user_prompt = f"""Original Goal: {north_star}

Current Conversation State:
{current_conversation}

Drift Score: {similarity_score:.3f} (below 0.7 indicates drift)

Analyze this conversation and provide:
1. Is the agent still pursuing the original goal? (Yes/No)
2. If No, what specific distraction occurred?
3. One-sentence instruction to realign the agent.

Format your response as JSON:
{{
    "pursuing_goal": true/false,
    "distraction": "brief description or null",
    "realignment": "one-sentence instruction",
    "confidence": "high/medium/low"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistency
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return SupervisorAnalysis(
                is_pursuing_goal=result.get("pursuing_goal", False),
                distraction=result.get("distraction"),
                realignment_instruction=result.get("realignment", "Return to the original goal."),
                confidence=result.get("confidence", "medium")
            )
            
        except Exception as e:
            print(f"⚠️ Supervisor analysis failed: {e}")
            # Fallback analysis
            return SupervisorAnalysis(
                is_pursuing_goal=similarity_score >= 0.45,
                distraction="Unable to analyze (API error)",
                realignment_instruction=f"Refocus on: {north_star}",
                confidence="low"
            )
    
    def generate_intervention_prompt(
        self, 
        north_star: str,
        analysis: SupervisorAnalysis
    ) -> str:
        """
        Generate a prompt that can be injected to realign the conversation
        
        Returns:
            A system message that reminds the agent of its goal
        """
        intervention = f"""⚠️ DRIFT DETECTED - REALIGNMENT REQUIRED

Original Goal: {north_star}

Issue Identified: {analysis.distraction or 'Conversation has drifted from original intent'}

Action Required: {analysis.realignment_instruction}

Please acknowledge the user's current question briefly, then redirect focus back to the original goal."""

        return intervention


# Quick test
if __name__ == "__main__":
    import sys
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ Set GROQ_API_KEY environment variable")
        print("Get your free key at: https://console.groq.com/keys")
        sys.exit(1)
    
    supervisor = LLMSupervisor()
    
    # Test scenario
    north_star = "I need help processing a refund for order #12345"
    drifted_conversation = """User: Actually, I can't log in
Assistant: Let me help you with login issues. What's your email?
User: test@example.com
Assistant: I'll send you a password reset link.
User: How do I change my email preferences?
Assistant: Here's how to update your email settings..."""
    
    print("🔍 Running supervisor analysis...")
    analysis = supervisor.analyze_drift(north_star, drifted_conversation, 0.45)
    
    print(f"\n{'='*60}")
    print(f"Pursuing Goal: {analysis.is_pursuing_goal}")
    print(f"Distraction: {analysis.distraction}")
    print(f"Realignment: {analysis.realignment_instruction}")
    print(f"Confidence: {analysis.confidence}")
    print(f"{'='*60}\n")
    
    intervention = supervisor.generate_intervention_prompt(north_star, analysis)
    print("📝 Intervention Prompt:")
    print(intervention)

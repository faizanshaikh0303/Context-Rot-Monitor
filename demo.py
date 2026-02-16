"""
Interactive Live Demo - Context Rot Monitor (Simplified)
Clean, working version with correct drift tracking
"""
import requests
import os
from groq import Groq
from colorama import init, Fore, Style

init(autoreset=True)

API_URL = "http://localhost:8000"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = []
north_star = None
drift_detected = False
drift_started_turn = None
intervention_applied = False


def generate_agent_response(user_message, apply_intervention=False):
    """Generate AI agent response"""
    
    if apply_intervention:
        system_prompt = f"""You are a customer support agent.

🚨 CRITICAL: The customer's original request was: "{north_star}"

You got sidetracked helping with other things. Now COMPLETE the original request.

Response format: "[Brief acknowledgment]. Your refund for order #12345 is approved for $[amount] - you'll receive it in 5-7 business days."

Be specific and final. 1-2 sentences maximum."""
    else:
        system_prompt = """You are a customer support agent.

IMPORTANT RULES:
- Keep responses SHORT (1-2 sentences)
- Answer whatever the customer just asked
- Stay focused on their current question
- Be helpful and friendly

If they ask about login issues, help with that.
If they ask about refunds, help with that.
Focus on what they're asking RIGHT NOW."""
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for turn in conversation_history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["assistant"]})
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.8,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"{Fore.RED}⚠️ AI Error: {str(e)[:100]}{Style.RESET_ALL}")
        return "Let me help you with that."


def check_drift(user_msg, assistant_msg):
    """Check for drift after adding turn"""
    response = requests.post(
        f"{API_URL}/add-turn",
        json={
            "user_message": user_msg,
            "assistant_response": assistant_msg
        }
    )
    
    if response.status_code == 200 and response.json():
        return response.json()
    return None


def run_demo():
    global north_star, conversation_history, drift_detected, drift_started_turn, intervention_applied
    
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print("🎭 INTERACTIVE DEMO - Context Rot Monitor")
    print(f"{'=' * 80}{Style.RESET_ALL}\n")
    
    print("Demo Instructions:")
    print("  1. Type as customer (introduce drift naturally)")
    print("  2. AI agent responds")
    print("  3. Watch drift detection")
    print("  4. Mention original topic to trigger intervention")
    print("  5. Type 'quit' to end\n")
    
    # Health check
    try:
        requests.get(f"{API_URL}/health")
        print(f"{Fore.GREEN}✅ Backend ready{Style.RESET_ALL}")
    except:
        print(f"{Fore.RED}❌ Backend not running{Style.RESET_ALL}")
        return
    
    if not os.getenv("GROQ_API_KEY"):
        print(f"{Fore.RED}❌ GROQ_API_KEY not set{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}✅ AI ready{Style.RESET_ALL}\n")
    
    requests.post(f"{API_URL}/reset")
    
    turn = 1
    
    while True:
        print(f"\n{Fore.CYAN}{'─' * 80}")
        print(f"Turn {turn}")
        print(f"{'─' * 80}{Style.RESET_ALL}")
        
        user_input = input(f"{Fore.GREEN}👤 You: {Style.RESET_ALL}").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        if not user_input:
            continue
        
        # Set north star
        if turn == 1:
            north_star = user_input
            requests.post(f"{API_URL}/initialize", json={"north_star": north_star})
            print(f"\n{Fore.YELLOW}📍 North Star: {north_star}{Style.RESET_ALL}")
        
        # Check if should intervene
        # Intervention triggers automatically after drift has been ongoing for 2-3 turns
        should_intervene = False
        if drift_detected and not intervention_applied and drift_started_turn is not None:
            turns_drifting = turn - drift_started_turn
            
            # Intervene after 2-3 turns of drifting
            if turns_drifting >= 2:
                should_intervene = True
                intervention_applied = True
                print(f"\n{Fore.MAGENTA}💡 INTERVENTION TRIGGERED{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}   System detected {turns_drifting} turns of drift")
                print(f"   Automatically instructing agent to refocus and complete original goal...{Style.RESET_ALL}")
        
        # Generate response
        print(f"\n{Fore.BLUE}🤖 Agent: {Style.RESET_ALL}", end="", flush=True)
        agent_msg = generate_agent_response(user_input, should_intervene)
        print(agent_msg)
        
        # Save to history
        conversation_history.append({"user": user_input, "assistant": agent_msg})
        
        # Check drift
        drift_data = check_drift(user_input, agent_msg)
        
        if drift_data and 'similarity_score' in drift_data:
            score = drift_data['similarity_score']
            is_drifting = drift_data['is_drifting']
            
            print(f"\n{Fore.CYAN}📊 Analysis:{Style.RESET_ALL}")
            print(f"   Similarity: {score:.3f}")
            
            if is_drifting:
                print(f"   Status: {Fore.RED}🔴 DRIFTING{Style.RESET_ALL}")
                if not drift_detected:
                    drift_detected = True
                    drift_started_turn = turn
                    print(f"   {Fore.YELLOW}⚠️  Drift first detected!{Style.RESET_ALL}")
                if drift_data.get('supervisor_analysis', {}).get('distraction'):
                    print(f"   Topic: {drift_data['supervisor_analysis']['distraction']}")
            else:
                print(f"   Status: {Fore.GREEN}🟢 ON TRACK{Style.RESET_ALL}")
                # Reset drift if we're back on track
                if drift_detected and not intervention_applied:
                    drift_detected = False
                    drift_started_turn = None
        
        # Natural ending
        if 'no' in user_input.lower() and any(w in agent_msg.lower() for w in ['great day', 'anything else', 'welcome']):
            print(f"\n{Fore.GREEN}✅ Conversation ended naturally{Style.RESET_ALL}")
            break
        
        turn += 1
    
    # Summary
    if conversation_history:
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print("📊 Summary")
        print(f"{'=' * 80}{Style.RESET_ALL}")
        print(f"Total turns: {turn}")
        print(f"Drift detected: {'Yes' if drift_detected else 'No'}")
        print(f"Intervention: {'Yes' if intervention_applied else 'No'}")


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("Set GROQ_API_KEY first!")
    else:
        run_demo()
# 🎯 Context Rot Monitor

An agentic system that detects and prevents "context rot" in multi-turn RAG conversations using semantic drift detection and LLM-powered supervision.

## 🌟 Features

- **Semantic Drift Detection**: Uses sentence embeddings to track how far conversations stray from original goals
- **LLM Supervisor**: Groq-powered analysis providing qualitative insights on why drift occurred and on which turn
- **Chrome DevTools Integration**: Professional developer overlay for real-time monitoring
- **Intervention System**: Automatic prompt generation to realign drifting conversations to stay true to the goal

## 🏗️ Architecture

```
┌─────────────────────┐
│  Chrome Extension   │
│  (DevTools Panel)   │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│  ┌───────────────┐  │
│  │ Drift Engine  │  │  ← Sentence Transformers
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │  Supervisor   │  │  ← Groq (Llama-3)
│  └───────────────┘  │
└─────────────────────┘
```

## 📋 Prerequisites

- Python 3.12+
- Chrome/Edge browser
- Groq API key (free at [console.groq.com](https://console.groq.com/keys))

## 🚀 Quick Start (15 minutes)

### 1. Get Your Groq API Key

1. Visit https://console.groq.com/keys
2. Sign up for free account
3. Create a new API key
4. Save it for the next step

### 2. Setup Backend

```bash
cd context-rot-monitor

# Install dependencies
pip install -r backend/requirements.txt --break-system-packages

# Configure API key
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start the server
python main.py
```

The API will start at `http://localhost:8000`

### 3. Load Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `extension/` folder from this project
5. The extension should now appear in your extensions list

### 4. Open DevTools Panel

1. Navigate to any webpage
2. Open Chrome DevTools (F12 or Cmd+Option+I)
3. Look for the "Context Rot" tab at the top
4. Click "Connect" to link to the backend

### 5. Run Demo

```bash
# In a new terminal, from project root:
python demo.py
```

This will simulate a conversation where you can act as a customer and deliberately drift from original issue and watch the agent bring it up again.

## 📊 How It Works

### Phase 1: Drift Detection

1. **North Star Extraction**: The first user prompt is saved as the conversation's goal
2. **Turn Snapshots**: Every N turns (default: 3), a state summary is generated
3. **Vector Comparison**: Cosine similarity between North Star and current state
4. **Drift Signal**: If similarity < 0.5, conversation is "rotting"

### Phase 2: LLM Supervisor

When drift is detected, Groq's Llama-3 analyzes:
- Is the agent still pursuing the original goal?
- What distraction caused the drift?
- One-sentence instruction to realign

### Phase 3: Intervention

The system generates a re-alignment prompt that can be:
- Copied to clipboard
- Injected directly into the conversation

## 📈 Use Cases

### Customer Support
Detect when support agents drift from solving the original issue into tangential troubleshooting.

### Coding Assistants
Monitor when programming help strays from the main implementation goal into debugging rabbit holes.

### RAG Applications
Track when document retrieval systems start pulling irrelevant context.

### Long Conversations
Prevent goal amnesia in 20+ turn conversations.

## ⚙️ Configuration

Edit `backend/.env`:

```env
GROQ_API_KEY=your_key_here
```

Adjust thresholds in `main.py`:

```python
engine = DriftEngine(
    similarity_threshold=0.7,  # Lower = stricter drift detection
    check_interval=3           # Check every N turns
)
```

## 🎯 Example Drift Scenario

```
Turn 1 (North Star): "I need help processing a refund for order #12345"
Similarity: 1.000 🟢

Turn 4: Discussion about login issues
Similarity: 0.12 🟢

Turn 7: Explaining email preference settings  
Similarity: 0.15 🔴 DRIFT DETECTED

Supervisor Analysis:
- Pursuing Goal: ❌ No
- Distraction: "Agent got sidetracked into account settings"
- Realignment: "Acknowledge the email question briefly, then return to 
  completing the refund for order #12345"
```

## 📚 Tech Stack

- **Backend**: FastAPI, Sentence-Transformers, Groq SDK
- **Frontend**: Vanilla JavaScript, Chrome Extension APIs
- **ML**: all-MiniLM-L6-v2 embeddings, Llama-3-70B (via Groq)

## 🔮 Future Enhancements

- [ ] Auto-detection of chat platforms (ChatGPT, Claude, etc.)
- [ ] Persistent conversation history
- [ ] Drift trend visualization
- [ ] Multi-conversation tracking
- [ ] WebSocket for real-time updates
- [ ] Export drift reports

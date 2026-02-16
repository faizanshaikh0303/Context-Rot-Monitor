# 🎯 Context Rot Monitor - Demo Day Checklist

## ⏰ Pre-Demo Setup (10 minutes before)

### ✅ Backend Setup
- [ ] Navigate to project: `cd context-rot-monitor/backend`
- [ ] Groq API key configured in `.env` file
- [ ] Start server: `python main.py`
- [ ] Verify health: Open `http://localhost:8000/health` in browser
- [ ] Should see: `{"status": "healthy", ...}`

### ✅ Chrome Extension
- [ ] Open Chrome
- [ ] Go to `chrome://extensions/`
- [ ] Developer mode enabled
- [ ] Extension loaded from `extension/` folder
- [ ] No errors in extension card

### ✅ DevTools Panel
- [ ] Open any webpage (or about:blank)
- [ ] Open DevTools (F12)
- [ ] "Context Rot" tab visible at top
- [ ] Click tab to open panel
- [ ] Click "Connect" button
- [ ] Connection status shows "Connected" 🟢

---

## 🎬 Demo Script (10 minutes)

### Part 1: Introduction (2 min)
"I built an agentic system that detects 'context rot' in multi-turn conversations. 
This is when an AI assistant drifts away from the user's original goal."

**Show the problem:**
- "Imagine asking for a refund, but ending up troubleshooting login issues"
- "This happens in customer support, coding assistants, and RAG systems"

### Part 2: Architecture Overview (2 min)
**Point to code/diagram:**

1. **Drift Engine** (`backend/drift_engine.py`):
   - Uses sentence embeddings to track semantic distance
   - Compares current conversation to "North Star" (original goal)
   - Triggers alert when similarity < 0.7

2. **LLM Supervisor** (`backend/supervisor.py`):
   - Groq-powered Llama-3 acts as "judge"
   - Analyzes WHY drift occurred
   - Generates intervention prompts

3. **Chrome DevTools** (`extension/`):
   - Professional developer overlay
   - Real-time metrics
   - One-click intervention injection

### Part 3: Live Demo (4 min)

**Step 1: Run the demo conversation**
```bash
python demo.py
```

**Step 2: Show DevTools panel in real-time**
- Point to drift meter going from green to red
- Show similarity score dropping: 1.00 → 0.83 → 0.61
- Highlight "Last Good Turn" metric

**Step 3: Show supervisor analysis**
When drift detected:
- Pursuing Goal: ❌ No
- Distraction: "Agent got sidetracked into account settings"
- Realignment: Clear, actionable instruction

**Step 4: Show intervention feature**
- Click "Copy Intervention Prompt"
- Show the generated re-alignment message
- Explain how this gets injected into conversation

### Part 4: Technical Deep Dive (2 min)

**Show the code:**

1. **Drift detection logic** (`drift_engine.py` line ~70):
```python
similarity = cosine_similarity(north_star_embedding, current_embedding)
is_drifting = similarity < 0.7
```

2. **Supervisor prompt** (`supervisor.py` line ~40):
```python
"Is the agent still pursuing the goal?
What was the distraction?
Provide a one-sentence instruction to realign."
```

3. **FastAPI endpoint** (`main.py` line ~90):
```python
@app.post("/add-turn")
# Auto-checks drift every N turns
# Triggers supervisor if drifting
```

---

## 💡 Key Talking Points

### What makes this impressive:

1. **Real-world problem**: Solves actual pain point in production RAG systems
2. **Agentic design**: Uses LLM-as-a-judge pattern (hot in 2024/2025)
3. **Professional UI**: Chrome DevTools integration (not just a CLI)
4. **Production-ready**: FastAPI backend, proper error handling, clean architecture

### Technical highlights:

- Semantic embeddings vs simple keyword matching
- Groq for fast, free LLM inference
- Chrome Extension Manifest V3
- RESTful API design

### Use cases:

- Enterprise customer support (prevent goal drift)
- Developer tools (keep coding sessions focused)
- Research assistants (maintain query relevance)
- Educational platforms (track learning objectives)

---

## 🐛 Troubleshooting During Demo

### Backend not connecting:
```bash
# Check if running:
curl http://localhost:8000/health

# Restart if needed:
cd backend && python main.py
```

### Demo script errors:
```bash
# Check API is accessible:
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

### DevTools not showing data:
1. Click "Refresh State" button
2. Check browser console for errors (F12 → Console)
3. Verify backend logs for API calls

### Extension not loading:
1. chrome://extensions → Remove and re-add
2. Check for manifest.json errors
3. Click "Reload" on extension card

---

## 📊 Metrics to Highlight

After demo.py completes:
- **Total Turns**: 9
- **Drift Checks**: 3 (every 3 turns)
- **Drift Detected**: Turn 7 (similarity: 0.612)
- **Response Time**: < 500ms per turn
- **LLM Latency**: ~1-2s for supervisor analysis

---

## 🎯 Closing Points

**What I learned:**
- Semantic similarity is powerful for context tracking
- LLM-as-a-judge is more nuanced than rule-based systems
- DevTools extensions provide great UX for developers

**Next steps:**
- Add WebSocket for real-time updates
- Support multiple conversation threads
- Export drift reports for analysis
- Auto-detect drift patterns

**Ask for:**
- Questions
- Feedback
- Internship opportunities 😊

---

## 📝 Post-Demo

After presenting:
- [ ] Share GitHub repo link
- [ ] Offer to do 1-on-1 walkthrough
- [ ] Ask for feedback on architecture
- [ ] Connect on LinkedIn

---

**Good luck! You've got this! 🚀**

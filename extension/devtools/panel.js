// Context Rot Monitor - DevTools Panel Logic

class ContextRotMonitor {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.connected = false;
        this.pollInterval = null;
        
        this.initializeUI();
        this.attachEventListeners();
        this.log('Monitor initialized. Connect to backend to start tracking.');
    }

    initializeUI() {
        // Load saved API URL
        chrome.storage.local.get(['apiUrl'], (result) => {
            if (result.apiUrl) {
                this.apiUrl = result.apiUrl;
                document.getElementById('apiUrl').value = this.apiUrl;
            }
        });
    }

    attachEventListeners() {
        // Connect button
        document.getElementById('connectBtn').addEventListener('click', () => {
            this.connect();
        });

        // Reset button
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetConversation();
        });

        // Manual check button
        document.getElementById('manualCheckBtn').addEventListener('click', () => {
            this.manualDriftCheck();
        });

        // Refresh state button
        document.getElementById('refreshStateBtn').addEventListener('click', () => {
            this.refreshState();
        });

        // Copy intervention button
        document.getElementById('copyInterventionBtn').addEventListener('click', () => {
            this.copyIntervention();
        });

        // Inject intervention button
        document.getElementById('injectInterventionBtn').addEventListener('click', () => {
            this.injectIntervention();
        });
    }

    async connect() {
        const urlInput = document.getElementById('apiUrl');
        this.apiUrl = urlInput.value;

        // Save URL
        chrome.storage.local.set({ apiUrl: this.apiUrl });

        try {
            const response = await fetch(`${this.apiUrl}/health`);
            const data = await response.json();

            if (data.status === 'healthy') {
                this.connected = true;
                this.updateConnectionStatus(true);
                this.log('✅ Connected to backend successfully', 'success');
                
                // Start polling for state updates
                this.startPolling();
                
                // Initial state fetch
                this.refreshState();
            } else {
                throw new Error('Backend unhealthy');
            }
        } catch (error) {
            this.connected = false;
            this.updateConnectionStatus(false);
            this.log(`❌ Connection failed: ${error.message}`, 'error');
        }
    }

    updateConnectionStatus(connected) {
        const dot = document.getElementById('connectionDot');
        const text = document.getElementById('connectionText');

        if (connected) {
            dot.classList.add('connected');
            dot.classList.remove('disconnected');
            text.textContent = 'Connected';
        } else {
            dot.classList.remove('connected');
            dot.classList.add('disconnected');
            text.textContent = 'Disconnected';
        }
    }

    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        // Poll every 2 seconds for state updates
        this.pollInterval = setInterval(() => {
            this.refreshState();
        }, 2000);
    }

    async refreshState() {
        if (!this.connected) return;

        try {
            const response = await fetch(`${this.apiUrl}/get-state`);
            const state = await response.json();

            this.updateUI(state);
        } catch (error) {
            console.error('Failed to refresh state:', error);
        }
    }

    updateUI(state) {
        // Update North Star
        if (state.north_star) {
            const northStarEl = document.getElementById('northStarDisplay');
            northStarEl.textContent = state.north_star;
            northStarEl.classList.remove('placeholder');
            document.getElementById('resetBtn').style.display = 'inline-block';
        }

        // Update status values
        document.getElementById('totalTurns').textContent = state.total_turns;
        document.getElementById('driftChecks').textContent = state.drift_checks;
        document.getElementById('lastGoodTurn').textContent = 
            state.last_good_turn > 0 ? state.last_good_turn : '--';
        
        const statusEl = document.getElementById('currentStatus');
        if (state.current_drift_status) {
            statusEl.textContent = '🔴 Drifting';
            statusEl.style.color = '#ef4444';
        } else if (state.total_turns > 0) {
            statusEl.textContent = '🟢 On Track';
            statusEl.style.color = '#4ade80';
        } else {
            statusEl.textContent = '--';
            statusEl.style.color = '#e0e0e0';
        }

        // Update recent turns
        this.updateRecentTurns(state.recent_turns);
    }

    updateRecentTurns(turns) {
        const container = document.getElementById('recentTurns');
        
        if (!turns || turns.length === 0) {
            container.innerHTML = '<div class="placeholder">No conversation turns yet...</div>';
            return;
        }

        container.innerHTML = turns.map(turn => `
            <div class="turn-item">
                <div class="turn-number">Turn ${turn.turn}</div>
                <div class="turn-message">
                    <span class="turn-label">User:</span> ${this.escapeHtml(turn.user)}
                </div>
                <div class="turn-message">
                    <span class="turn-label">Assistant:</span> ${this.escapeHtml(turn.assistant)}
                </div>
            </div>
        `).join('');
    }

    updateDriftMeter(similarityScore, isDrifting) {
        const valueEl = document.getElementById('similarityValue');
        const barEl = document.getElementById('driftBar');

        valueEl.textContent = similarityScore.toFixed(3);
        
        // Update bar width (0.0 to 1.0 -> 0% to 100%)
        const width = Math.max(0, Math.min(100, similarityScore * 100));
        barEl.style.width = `${width}%`;

        // Update color based on drift status
        if (isDrifting) {
            valueEl.style.color = '#ef4444';
        } else {
            valueEl.style.color = '#4ade80';
        }
    }

    showSupervisorAnalysis(analysis) {
        const section = document.getElementById('supervisorSection');
        section.style.display = 'block';

        document.getElementById('pursuingGoal').textContent = 
            analysis.pursuing_goal ? '✅ Yes' : '❌ No';
        document.getElementById('distraction').textContent = 
            analysis.distraction || 'N/A';
        document.getElementById('realignment').textContent = 
            analysis.realignment;
        document.getElementById('supervisorConfidence').textContent = 
            analysis.confidence;
    }

    showIntervention(prompt) {
        const section = document.getElementById('interventionSection');
        section.style.display = 'block';
        
        document.getElementById('interventionPrompt').textContent = prompt;
        this.currentIntervention = prompt;
    }

    async manualDriftCheck() {
        if (!this.connected) {
            this.log('⚠️ Not connected to backend', 'warning');
            return;
        }

        this.log('🔍 Running manual drift check...');

        try {
            const response = await fetch(`${this.apiUrl}/check-drift`);
            const result = await response.json();

            this.updateDriftMeter(result.similarity_score, result.is_drifting);

            if (result.is_drifting) {
                this.log(`🔴 Drift detected! Score: ${result.similarity_score.toFixed(3)}`, 'warning');
                
                if (result.supervisor_analysis) {
                    this.showSupervisorAnalysis(result.supervisor_analysis);
                }
                
                if (result.intervention_prompt) {
                    this.showIntervention(result.intervention_prompt);
                }
            } else {
                this.log(`🟢 Conversation on track. Score: ${result.similarity_score.toFixed(3)}`, 'success');
            }

            // Refresh full state
            this.refreshState();
        } catch (error) {
            this.log(`❌ Drift check failed: ${error.message}`, 'error');
        }
    }

    async resetConversation() {
        if (!confirm('Reset the conversation? This will clear all tracking data.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/reset`, { method: 'POST' });
            const result = await response.json();

            this.log('🔄 Conversation reset', 'success');
            
            // Reset UI
            document.getElementById('northStarDisplay').textContent = 
                'Not set - waiting for first conversation turn...';
            document.getElementById('northStarDisplay').classList.add('placeholder');
            document.getElementById('resetBtn').style.display = 'none';
            
            document.getElementById('supervisorSection').style.display = 'none';
            document.getElementById('interventionSection').style.display = 'none';
            
            this.refreshState();
        } catch (error) {
            this.log(`❌ Reset failed: ${error.message}`, 'error');
        }
    }

    copyIntervention() {
        if (!this.currentIntervention) return;

        navigator.clipboard.writeText(this.currentIntervention);
        this.log('📋 Intervention prompt copied to clipboard', 'success');
    }

    injectIntervention() {
        if (!this.currentIntervention) return;

        // Send message to content script to inject into active chat
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    type: 'INJECT_INTERVENTION',
                    prompt: this.currentIntervention
                });
                this.log('💉 Intervention injected into page', 'success');
            }
        });
    }

    log(message, type = 'info') {
        const logContainer = document.getElementById('activityLog');
        const timestamp = new Date().toLocaleTimeString();
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${timestamp}] ${message}`;
        
        logContainer.insertBefore(entry, logContainer.firstChild);
        
        // Keep only last 50 entries
        while (logContainer.children.length > 50) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize monitor when panel loads
const monitor = new ContextRotMonitor();

// Listen for messages from background/content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'DRIFT_DETECTED') {
        monitor.updateDriftMeter(message.data.similarity_score, message.data.is_drifting);
        
        if (message.data.supervisor_analysis) {
            monitor.showSupervisorAnalysis(message.data.supervisor_analysis);
        }
        
        if (message.data.intervention_prompt) {
            monitor.showIntervention(message.data.intervention_prompt);
        }
        
        monitor.log('🔔 Drift alert received from page', 'warning');
    }
});

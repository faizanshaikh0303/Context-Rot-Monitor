// Content Script - Monitors conversation turns on the page

console.log('Context Rot Monitor: Content script loaded');

// Listen for messages from DevTools panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'INJECT_INTERVENTION') {
        injectIntervention(message.prompt);
        sendResponse({ success: true });
    }
});

function injectIntervention(prompt) {
    // Try to find a text input or textarea on the page
    const inputs = [
        ...document.querySelectorAll('textarea'),
        ...document.querySelectorAll('input[type="text"]'),
        ...document.querySelectorAll('[contenteditable="true"]')
    ];

    if (inputs.length > 0) {
        // Find the most likely chat input (usually the largest textarea)
        const chatInput = inputs.reduce((largest, current) => {
            const largestArea = largest.offsetWidth * largest.offsetHeight;
            const currentArea = current.offsetWidth * current.offsetHeight;
            return currentArea > largestArea ? current : largest;
        });

        // Insert the intervention prompt
        if (chatInput.tagName === 'TEXTAREA' || chatInput.tagName === 'INPUT') {
            chatInput.value = prompt;
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
        } else if (chatInput.isContentEditable) {
            chatInput.textContent = prompt;
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
        }

        // Focus on the input
        chatInput.focus();

        // Visual feedback
        chatInput.style.border = '2px solid #ef4444';
        setTimeout(() => {
            chatInput.style.border = '';
        }, 1000);

        console.log('Context Rot Monitor: Intervention injected');
    } else {
        console.warn('Context Rot Monitor: No suitable input found on page');
        alert('No chat input found. Please copy the intervention manually.');
    }
}

// Optional: Auto-detect conversation turns on popular chat platforms
// This is a simple example - would need to be customized per platform

function observeChatMessages() {
    // Example: Monitor for new messages in a chat interface
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    // Check if this looks like a chat message
                    // This would need platform-specific selectors
                    const isMessage = node.matches('.message, [role="article"], .chat-message');
                    
                    if (isMessage) {
                        console.log('Context Rot Monitor: New message detected');
                        // Could potentially auto-send to backend here
                    }
                }
            });
        });
    });

    // Observe the document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Start observing after page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', observeChatMessages);
} else {
    observeChatMessages();
}

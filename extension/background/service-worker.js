// Background Service Worker - Handles extension lifecycle

console.log('Context Rot Monitor: Background service worker initialized');

// Listen for installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Context Rot Monitor installed');
        
        // Set default configuration
        chrome.storage.local.set({
            apiUrl: 'http://localhost:8000',
            checkInterval: 3,
            similarityThreshold: 0.7
        });
    }
});

// Handle messages from content scripts and DevTools
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Background received message:', message.type);
    
    switch (message.type) {
        case 'DRIFT_ALERT':
            // Forward drift alerts to all DevTools panels
            chrome.runtime.sendMessage({
                type: 'DRIFT_DETECTED',
                data: message.data
            });
            break;
            
        case 'LOG_EVENT':
            console.log('Event:', message.data);
            break;
    }
    
    return true; // Keep message channel open for async response
});

// Optional: Badge to show drift status
function updateBadge(isDrifting) {
    if (isDrifting) {
        chrome.action.setBadgeText({ text: '!' });
        chrome.action.setBadgeBackgroundColor({ color: '#ef4444' });
    } else {
        chrome.action.setBadgeText({ text: '' });
    }
}

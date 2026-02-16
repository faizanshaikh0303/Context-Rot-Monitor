// DevTools initialization - creates the "Context Rot" panel
chrome.devtools.panels.create(
    "Context Rot",
    "",  // No icon for now
    "devtools/panel.html",
    function(panel) {
        console.log("Context Rot Monitor panel created");
    }
);

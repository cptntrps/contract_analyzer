// Test script to verify tab switching functionality
function testTabSwitching() {
    console.log('Starting tab switching test...');
    
    // Test data for tabs
    const tabs = ['dashboard', 'upload', 'settings'];
    
    tabs.forEach(tabName => {
        console.log(`\n=== Testing ${tabName} tab ===`);
        
        // Check if tab content exists
        const tabContent = document.getElementById(tabName);
        if (!tabContent) {
            console.error(`❌ Tab content not found: ${tabName}`);
            return;
        }
        
        // Check if menu item exists
        const menuItem = document.querySelector(`[data-tab="${tabName}"]`);
        if (!menuItem) {
            console.error(`❌ Menu item not found: ${tabName}`);
            return;
        }
        
        console.log(`✅ Tab content found: ${tabName}`);
        console.log(`✅ Menu item found: ${tabName}`);
        
        // Test tab switching
        if (typeof showTab === 'function') {
            console.log(`Testing showTab('${tabName}')...`);
            const result = showTab(tabName);
            if (result !== false) {
                console.log(`✅ Tab switching successful: ${tabName}`);
            } else {
                console.log(`❌ Tab switching failed: ${tabName}`);
            }
        } else {
            console.error('❌ showTab function not found');
        }
        
        // Test menu item click
        console.log(`Testing menu item click for ${tabName}...`);
        try {
            menuItem.click();
            console.log(`✅ Menu item click successful: ${tabName}`);
        } catch (error) {
            console.error(`❌ Menu item click failed: ${tabName}`, error);
        }
    });
    
    console.log('\n=== Tab switching test completed ===');
}

// Run test when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for the dashboard to initialize
    setTimeout(testTabSwitching, 2000);
}); 
// Dashboard API 테스트 스크립트
async function testDashboard() {
    console.log('Testing Dashboard APIs...\n');
    
    const apiUrl = 'http://localhost:8000';
    const endpoints = [
        '/dashboard/stats',
        '/dashboard/publishing-activity',
        '/dashboard/platforms'
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`Testing ${endpoint}...`);
            const response = await fetch(`${apiUrl}${endpoint}`);
            const data = await response.json();
            console.log(`✅ Success: ${JSON.stringify(data)}\n`);
        } catch (error) {
            console.log(`❌ Error: ${error.message}\n`);
        }
    }
}

testDashboard();
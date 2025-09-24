# Minimal Frontend Deployment - Railway Compatible
# This deploys a working frontend while backend issues are resolved

echo "=== Minimal Frontend Deployment ==="

# 1. Create production-ready frontend that works with current Railway endpoints
cat > static/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Nurse Florence - Healthcare AI Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .optimization-card { 
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
            border-left: 4px solid #3b82f6;
            transition: all 0.3s ease;
        }
        .optimization-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); 
        }
        .enhanced-query { 
            background: #f0fdf4; 
            border-left: 4px solid #10b981; 
        }
        .ai-response { 
            background: #fef3c7; 
            border-left: 4px solid #f59e0b; 
        }
        .results-panel { 
            max-height: 600px; 
            overflow-y: auto; 
        }
        .spinner-border {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-gradient-to-r from-blue-800 to-blue-600 text-white shadow-lg">
        <div class="max-w-6xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-stethoscope text-2xl"></i>
                    <div>
                        <h1 class="text-xl font-bold">AI Nurse Florence</h1>
                        <p class="text-sm text-blue-100">Healthcare AI Assistant - Clinical Information System</p>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button onclick="loadSample()" class="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded text-sm">
                        Load Sample
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- System Status Banner -->
    <div id="statusBanner" class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <div class="max-w-6xl mx-auto flex items-center">
            <div class="flex-shrink-0">
                <i class="fas fa-spinner fa-spin text-yellow-400"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm text-yellow-700">
                    <span id="statusText">Checking system status...</span>
                </p>
            </div>
        </div>
    </div>

    <main class="max-w-6xl mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Panel: Input & Enhancement -->
            <div class="space-y-6">
                <!-- Clinical Question Input -->
                <div class="optimization-card rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4 flex items-center">
                        <i class="fas fa-question-circle text-blue-600 mr-2"></i>
                        Clinical Question
                    </h3>
                    <textarea 
                        id="clinicalInput" 
                        class="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                        rows="4"
                        placeholder="Enter a disease or medical condition to research..."
                        oninput="enhanceQueryRealtime()"
                    ></textarea>
                    <p class="text-xs text-gray-500 mt-2">
                        Search for comprehensive medical information from trusted sources
                    </p>
                </div>

                <!-- Enhancement Options -->
                <div class="optimization-card rounded-lg p-6">
                    <h3 class="text-lg font-semibold mb-4 flex items-center">
                        <i class="fas fa-cog text-green-600 mr-2"></i>
                        Query Enhancement
                        <span id="optimizationScore" class="ml-2 text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded">
                            Ready
                        </span>
                    </h3>
                    
                    <!-- Quick Options -->
                    <div class="grid grid-cols-2 gap-3 mb-4">
                        <button onclick="enhanceForNursing()" class="p-3 text-left border border-gray-300 rounded-lg hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <div class="font-medium text-sm text-blue-900">Nursing Focus</div>
                            <div class="text-xs text-blue-700">Assessment priorities</div>
                        </button>
                        <button onclick="enhanceForPatient()" class="p-3 text-left border border-gray-300 rounded-lg hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500">
                            <div class="font-medium text-sm text-green-900">Patient Education</div>
                            <div class="text-xs text-green-700">Teaching points</div>
                        </button>
                    </div>
                </div>

                <!-- Action Button -->
                <div class="flex space-x-3">
                    <button 
                        onclick="getAIResponse()" 
                        id="getResponseBtn"
                        class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        disabled
                    >
                        <i class="fas fa-search mr-2"></i>Get Medical Information
                    </button>
                </div>
            </div>

            <!-- Right Panel: Results -->
            <div class="space-y-6">
                <!-- Enhanced Query Preview -->
                <div class="bg-white rounded-lg shadow-sm border">
                    <div class="p-4 border-b border-gray-200">
                        <h3 class="font-semibold flex items-center">
                            <i class="fas fa-eye text-purple-600 mr-2"></i>
                            Search Query
                        </h3>
                    </div>
                    <div class="p-4">
                        <div id="enhancedQueryPreview" class="enhanced-query rounded-lg p-3 text-sm min-h-[120px]">
                            Enter a medical condition above to begin your search...
                        </div>
                    </div>
                </div>

                <!-- AI Response Panel -->
                <div class="bg-white rounded-lg shadow-sm border">
                    <div class="p-4 border-b border-gray-200">
                        <h3 class="font-semibold flex items-center">
                            <i class="fas fa-stethoscope text-red-600 mr-2"></i>
                            Medical Information
                        </h3>
                    </div>
                    <div class="p-4 results-panel">
                        <div id="aiResponseArea" class="ai-response rounded-lg p-4 min-h-[300px]">
                            <div class="text-center text-gray-500 py-12">
                                <i class="fas fa-stethoscope text-6xl mb-4 opacity-30"></i>
                                <h4 class="font-semibold mb-2">Ready for Medical Research</h4>
                                <p>Enter a disease or condition and click "Get Medical Information" to receive evidence-based information</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Educational Disclaimer -->
    <footer class="bg-gray-900 text-white py-6 mt-12">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <div class="bg-yellow-100 text-yellow-800 p-4 rounded-lg mb-4">
                <p class="font-semibold">Educational Use Only</p>
                <p class="text-sm">This system provides educational healthcare information from medical databases. Always verify with healthcare providers and follow institutional protocols.</p>
            </div>
            <p class="text-gray-400">© 2025 AI Nurse Florence - Healthcare AI Assistant</p>
        </div>
    </footer>

    <script>
        // Configuration - Uses current Railway endpoints
        const API_BASE = 'https://ai-nurse-florence-production.up.railway.app/api/v1';
        
        // Application State
        let systemStatus = 'unknown';
        let currentQuery = '';

        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            checkSystemStatus();
            enhanceQueryRealtime();
        });

        // System Status Check
        async function checkSystemStatus() {
            const statusBanner = document.getElementById('statusBanner');
            const statusText = document.getElementById('statusText');
            
            try {
                const response = await fetch(`${API_BASE}/health`);
                
                if (response.ok) {
                    const data = await response.json();
                    systemStatus = 'online';
                    statusBanner.className = 'bg-green-50 border-l-4 border-green-400 p-4';
                    statusText.innerHTML = '<i class="fas fa-check-circle text-green-600 mr-1"></i>System Online - Medical database access available';
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                systemStatus = 'offline';
                statusBanner.className = 'bg-red-50 border-l-4 border-red-400 p-4';
                statusText.innerHTML = '<i class="fas fa-times-circle text-red-600 mr-1"></i>System Offline - Check connection';
                console.error('Health check failed:', error);
            }
        }

        // Real-time Query Enhancement
        function enhanceQueryRealtime() {
            const clinicalInput = document.getElementById('clinicalInput').value.trim();
            
            if (!clinicalInput) {
                document.getElementById('enhancedQueryPreview').textContent = 'Enter a medical condition above to begin your search...';
                document.getElementById('getResponseBtn').disabled = true;
                document.getElementById('optimizationScore').textContent = 'Ready';
                return;
            }

            // Build Enhanced Query
            currentQuery = clinicalInput;
            document.getElementById('enhancedQueryPreview').textContent = `Searching medical databases for: "${clinicalInput}"`;
            
            // Update status
            document.getElementById('optimizationScore').textContent = 'Query Ready';
            document.getElementById('optimizationScore').className = 'ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded';
            
            // Enable button if system is online
            document.getElementById('getResponseBtn').disabled = systemStatus !== 'online';
        }

        // Enhancement shortcuts
        function enhanceForNursing() {
            const input = document.getElementById('clinicalInput');
            if (input.value.trim()) {
                input.value += ' - nursing assessment priorities';
                enhanceQueryRealtime();
            }
        }

        function enhanceForPatient() {
            const input = document.getElementById('clinicalInput');
            if (input.value.trim()) {
                input.value += ' - patient education';
                enhanceQueryRealtime();
            }
        }

        // Main API Call Function
        async function getAIResponse() {
            const btn = document.getElementById('getResponseBtn');
            const responseArea = document.getElementById('aiResponseArea');
            const clinicalInput = document.getElementById('clinicalInput').value.trim();
            
            if (!clinicalInput) {
                alert('Please enter a medical condition first.');
                return;
            }

            // Show Loading State
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Searching Medical Databases...';
            btn.disabled = true;
            
            responseArea.innerHTML = `
                <div class="flex items-center justify-center py-12">
                    <div class="text-center">
                        <div class="spinner-border mx-auto mb-4"></div>
                        <h4 class="font-semibold text-gray-700 mb-2">Searching Medical Literature</h4>
                        <p class="text-gray-600">Retrieving evidence-based information...</p>
                    </div>
                </div>
            `;

            try {
                // Call Disease API (using current Railway endpoint structure)
                const response = await fetch(`${API_BASE}/disease?q=${encodeURIComponent(clinicalInput)}`);
                
                if (!response.ok) {
                    throw new Error(`API Error: HTTP ${response.status} ${response.statusText}`);
                }

                const data = await response.json();
                
                // Format Professional Response
                let formattedResponse = `<div class="space-y-4">`;
                
                // Header
                formattedResponse += `
                    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
                        <h4 class="font-bold text-blue-900 mb-1 flex items-center">
                            <i class="fas fa-stethoscope mr-2"></i>
                            Medical Information: ${data.name || clinicalInput}
                        </h4>
                        <p class="text-blue-800 text-sm">${data.banner || 'Evidence-based medical information from trusted databases'}</p>
                    </div>
                `;
                
                // Clinical Summary
                if (data.summary) {
                    formattedResponse += `
                        <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
                            <h4 class="font-semibold text-green-900 mb-2 flex items-center">
                                <i class="fas fa-clipboard-list mr-2"></i>
                                Clinical Summary
                            </h4>
                            <div class="text-green-800 prose prose-sm max-w-none">
                                ${data.summary.replace(/\n/g, '<br>')}
                            </div>
                        </div>
                    `;
                }

                // Evidence Sources
                if (data.references && data.references.length > 0) {
                    formattedResponse += `
                        <div class="bg-gray-50 border-l-4 border-gray-500 p-4 rounded-r-lg">
                            <h4 class="font-semibold text-gray-900 mb-3 flex items-center">
                                <i class="fas fa-book-medical mr-2"></i>
                                Medical References
                            </h4>
                            <ul class="space-y-2">
                    `;
                    data.references.forEach((ref, index) => {
                        formattedResponse += `
                            <li class="text-sm flex items-start">
                                <span class="bg-gray-200 text-gray-700 rounded-full px-2 py-1 text-xs font-medium mr-2 mt-0.5">${index + 1}</span>
                                <div>
                                    <a href="${ref.url}" target="_blank" class="text-blue-600 hover:underline font-medium">${ref.title}</a>
                                    <span class="text-gray-600 block">${ref.source}</span>
                                </div>
                            </li>
                        `;
                    });
                    formattedResponse += `</ul></div>`;
                }

                // Professional Disclaimer
                formattedResponse += `
                    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                        <div class="flex items-start">
                            <i class="fas fa-exclamation-triangle text-yellow-600 mr-2 mt-0.5"></i>
                            <div>
                                <p class="text-yellow-800 text-sm font-medium mb-1">Educational Use Only</p>
                                <p class="text-yellow-700 text-xs">This information is for educational purposes. Always verify with healthcare providers and follow clinical guidelines for patient care decisions.</p>
                            </div>
                        </div>
                    </div>
                `;

                formattedResponse += `</div>`;
                responseArea.innerHTML = formattedResponse;

            } catch (error) {
                console.error('API Error:', error);
                responseArea.innerHTML = `
                    <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                        <div class="flex items-start">
                            <i class="fas fa-exclamation-circle text-red-600 mr-2 mt-0.5"></i>
                            <div>
                                <h4 class="font-semibold text-red-900 mb-2">Connection Error</h4>
                                <p class="text-red-800 mb-2">Unable to retrieve medical information: ${error.message}</p>
                                <p class="text-red-700 text-sm">Please check your connection and try again. The medical database may be temporarily unavailable.</p>
                                <button onclick="checkSystemStatus()" class="mt-3 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm">
                                    <i class="fas fa-redo mr-1"></i>Retry Connection
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            } finally {
                // Reset Button
                btn.innerHTML = '<i class="fas fa-search mr-2"></i>Get Medical Information';
                btn.disabled = systemStatus !== 'online';
            }
        }

        // Load Sample Data
        function loadSample() {
            document.getElementById('clinicalInput').value = 'diabetes mellitus';
            enhanceQueryRealtime();
            
            setTimeout(() => {
                alert('Sample medical condition loaded! Click "Get Medical Information" to see comprehensive medical data from trusted sources.');
            }, 500);
        }
    </script>
</body>
</html>
EOF

echo "Frontend created successfully!"

# 2. Backup any existing static files
mkdir -p backups/frontend-$(date +%Y%m%d_%H%M%S)
cp -r static/* backups/frontend-$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "No existing files to backup"

# 3. Test the frontend locally first
echo "Testing frontend locally..."
if command -v python3 &> /dev/null; then
    cd static && python3 -m http.server 8080 &
    SERVER_PID=$!
    sleep 2
    echo "Frontend test server running at http://localhost:8080"
    echo "Press any key to stop test server and deploy to Railway..."
    read -n 1
    kill $SERVER_PID 2>/dev/null
    cd ..
fi

# 4. Deploy to Railway
echo "Deploying to Railway..."
git add static/index.html
git commit -m "Deploy: Minimal working frontend compatible with current Railway backend"
git push origin main

echo ""
echo "=== Deployment Complete ==="
echo "Frontend URL: https://ai-nurse-florence-production.up.railway.app/static/index.html"
echo ""
echo "This frontend works with the current 6-route Railway backend:"
echo "- Uses /api/v1/disease endpoint (working)"
echo "- Uses /api/v1/health endpoint (working)" 
echo "- Graceful error handling for missing features"
echo ""
echo "Test URL after 2-3 minutes:"
echo "https://ai-nurse-florence-production.up.railway.app/static/index.html"
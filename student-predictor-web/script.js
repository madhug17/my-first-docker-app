async function makePrediction() {
    // 1. Reference elements based on your NEW index.html
    const btn = document.getElementById('predict-btn');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const predictionText = document.getElementById('prediction-text');
    const confidencePct = document.getElementById('confidence-pct');
    const progressBar = document.getElementById('progress-bar');

    // 2. Safety Check: If any element is missing, stop here
    if (!loader || !resultContainer || !predictionText || !progressBar) {
        console.error("Critical Error: script.js IDs do not match index.html.");
        return;
    }

    // 3. UI Loading State
    btn.disabled = true;
    btn.innerText = "Analyzing...";
    loader.classList.remove('hidden');      // Show scanning text
    resultContainer.classList.add('hidden'); // Hide previous results

    // 4. API Configuration (Update URL to your Space)
    const API_URL = "https://madhug17-student-performance-api.hf.space/predict-easy";

    // 5. Gather Data from inputs
    const payload = {
        "G1": parseInt(document.getElementById('g1').value) || 0,
        "G2": parseInt(document.getElementById('g2').value) || 0,
        "absences": parseInt(document.getElementById('absences').value) || 0,
        "higher": document.getElementById('higher').value,
        // Mandatory model fields
        "failures": 0, "studytime": 2, "Medu": 4, "Fedu": 4, "goout": 2, "health": 5, "sex": "M", "school": "GP"
    };

    try {
        // 6. Connect to AI Engine
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Status: ${response.status}`);

        const data = await response.json();

        // 7. Update UI with AI Results
        loader.classList.add('hidden');          // Hide scanning text
        resultContainer.classList.remove('hidden'); // Show result box

        // Set Results
        predictionText.innerText = data.prediction === "Pass" ? "✅ Predicted: PASS" : "❌ Predicted: FAIL";
        predictionText.style.color = data.prediction === "Pass" ? "#22c55e" : "#ef4444";

        // Update Confidence and Progress Bar
        confidencePct.innerText = data.confidence;
        progressBar.style.width = `${data.confidence}%`;
        progressBar.style.backgroundColor = data.prediction === "Pass" ? "#22c55e" : "#ef4444";

    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Failed to reach the AI. Make sure Hugging Face is 'Running'.");
        loader.classList.add('hidden');
    } finally {
        // 8. Reset Button
        btn.disabled = false;
        btn.innerText = "Analyze Performance";
    }
}
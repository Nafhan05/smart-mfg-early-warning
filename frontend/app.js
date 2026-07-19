const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : '';

document.getElementById('predictForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const sector = document.getElementById('sector').value;
    const horizon = parseInt(document.getElementById('horizon').value);
    
    const predictBtn = document.getElementById('predictBtn');
    const resultSection = document.getElementById('resultSection');
    const loadingSection = document.getElementById('loadingSection');
    
    predictBtn.disabled = true;
    predictBtn.textContent = 'Memproses...';
    resultSection.style.display = 'none';
    loadingSection.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sector: sector,
                horizon_months: horizon
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResult(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Gagal mendapatkan prediksi. Silakan coba lagi.');
    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Ramalkan';
        loadingSection.style.display = 'none';
    }
});

function displayResult(data) {
    const resultSection = document.getElementById('resultSection');
    const predictedIndex = document.getElementById('predictedIndex');
    const predictedChange = document.getElementById('predictedChange');
    const direction = document.getElementById('direction');
    const keyDrivers = document.getElementById('keyDrivers');
    const recommendation = document.getElementById('recommendation');
    
    predictedIndex.textContent = data.predicted_index.toFixed(2);
    
    const changePct = data.predicted_change_pct;
    predictedChange.textContent = `${changePct > 0 ? '+' : ''}${changePct.toFixed(2)}%`;
    predictedChange.className = `change ${changePct > 0 ? 'positive' : 'negative'}`;
    
    direction.textContent = data.direction.charAt(0).toUpperCase() + data.direction.slice(1);
    direction.className = `direction ${data.direction}`;
    
    keyDrivers.innerHTML = '';
    data.key_drivers.forEach(driver => {
        const li = document.createElement('li');
        li.textContent = driver;
        keyDrivers.appendChild(li);
    });
    
    recommendation.textContent = data.recommendation;
    
    resultSection.style.display = 'block';
}

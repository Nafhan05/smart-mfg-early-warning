const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL ?? (
    ['localhost', '127.0.0.1'].includes(window.location.hostname)
        ? 'http://localhost:8000'
        : ''
);

const form = document.getElementById('predictForm');
const predictBtn = document.getElementById('predictBtn');
const resultSection = document.getElementById('resultSection');
const emptyResult = document.getElementById('emptyResult');
const resultContent = document.getElementById('resultContent');
const errorMessage = document.getElementById('errorMessage');

document.querySelectorAll('input[name="horizon"]').forEach((input) => {
    input.addEventListener('change', () => {
        document.querySelectorAll('.horizon-option').forEach((option) => {
            option.classList.toggle('selected', option.querySelector('input').checked);
        });
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const sector = document.getElementById('sector').value;
    const horizon = Number(document.querySelector('input[name="horizon"]:checked').value);

    predictBtn.disabled = true;
    predictBtn.setAttribute('aria-busy', 'true');
    predictBtn.querySelector('span').textContent = 'Menganalisis...';
    errorMessage.hidden = true;
    resultSection.classList.add('is-loading');

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
            const errorBody = await response.json().catch(() => ({}));
            throw new Error(errorBody.detail || `Server mengembalikan status ${response.status}.`);
        }

        const data = await response.json();
        displayResult(data);
    } catch (error) {
        console.error('Error:', error);
        errorMessage.textContent = `Prediksi gagal: ${error.message}`;
        errorMessage.hidden = false;
    } finally {
        predictBtn.disabled = false;
        predictBtn.removeAttribute('aria-busy');
        predictBtn.querySelector('span').textContent = 'Jalankan prediksi';
        resultSection.classList.remove('is-loading');
    }
});

function displayResult(data) {
    const predictedIndex = document.getElementById('predictedIndex');
    const predictedChange = document.getElementById('predictedChange');
    const currentIndex = document.getElementById('currentIndex');
    const direction = document.getElementById('direction');
    const keyDrivers = document.getElementById('keyDrivers');
    const recommendation = document.getElementById('recommendation');

    const formatNumber = (value) => new Intl.NumberFormat('id-ID', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);

    const changePct = Number(data.predicted_change_pct);
    predictedIndex.textContent = formatNumber(data.predicted_index);
    currentIndex.textContent = formatNumber(data.current_index);
    predictedChange.textContent = `${changePct > 0 ? '+' : ''}${formatNumber(changePct)}%`;
    predictedChange.className = `change ${changePct > 0 ? 'positive' : changePct < 0 ? 'negative' : 'neutral'}`;

    const directionLabels = { naik: 'Naik', turun: 'Turun', stabil: 'Stabil' };
    direction.textContent = directionLabels[data.direction] || data.direction;
    direction.className = `direction ${data.direction}`;

    document.getElementById('resultPeriod').textContent = `${data.horizon_months} bulan ke depan`;
    keyDrivers.innerHTML = '';
    (data.key_drivers || []).forEach((driver) => {
        const li = document.createElement('li');
        li.textContent = driver;
        keyDrivers.appendChild(li);
    });

    recommendation.textContent = data.recommendation;
    emptyResult.hidden = true;
    resultContent.hidden = false;
}

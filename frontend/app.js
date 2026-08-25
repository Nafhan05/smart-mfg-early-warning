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

const EXAMPLES = [
    { period: '2024-03', horizon: 2, label: 'Maret 2024 · 2 bulan · proyeksi turun' },
    { period: '2024-05', horizon: 1, label: 'Mei 2024 · 1 bulan · proyeksi turun' },
    { period: '2024-04', horizon: 3, label: 'April 2024 · 3 bulan · proyeksi naik' },
    { period: '2024-09', horizon: 3, label: 'Sep 2024 · 3 bulan · proyeksi naik' },
];

const sampleSelect = document.getElementById('sampleSelect');
EXAMPLES.forEach((ex) => {
    const option = document.createElement('option');
    option.value = JSON.stringify({ period: ex.period, horizon: ex.horizon });
    option.textContent = ex.label;
    sampleSelect.appendChild(option);
});

const horizonGroup = document.querySelector('.horizon-group');
const sampleGroup = document.getElementById('sampleGroup');

document.querySelectorAll('input[name="mode"]').forEach((input) => {
    input.addEventListener('change', () => {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        document.querySelectorAll('.mode-option').forEach((option) => {
            option.classList.toggle('selected', option.querySelector('input').checked);
        });
        const isBacktest = mode === 'backtest';
        sampleGroup.hidden = !isBacktest;
        horizonGroup.hidden = isBacktest;
    });
});

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
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const body = { sector, mode };

    if (mode === 'backtest') {
        const selected = JSON.parse(sampleSelect.value);
        body.horizon_months = selected.horizon;
        body.sample_period = selected.period;
    } else {
        body.horizon_months = Number(document.querySelector('input[name="horizon"]:checked').value);
    }

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
            body: JSON.stringify(body)
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
    const backtestBlock = document.getElementById('backtestBlock');

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

    const isBacktest = data.mode === 'backtest';
    document.getElementById('resultPeriod').textContent = isBacktest
        ? `${data.sample_period} · ${data.horizon_months} bulan · backtest`
        : `${data.horizon_months} bulan ke depan`;

    if (isBacktest) {
        document.getElementById('actualIndex').textContent = formatNumber(data.actual_index);
        const actualPct = Number(data.actual_change_pct);
        document.getElementById('actualChange').textContent =
            `${actualPct > 0 ? '+' : ''}${formatNumber(actualPct)}%`;
        const deltaAbs = Number(data.delta_abs);
        const deltaEl = document.getElementById('deltaAbs');
        deltaEl.textContent = `${deltaAbs > 0 ? '+' : ''}${formatNumber(deltaAbs)}`;
        deltaEl.className = deltaAbs > 0 ? 'delta-positive' : 'delta-negative';
        backtestBlock.hidden = false;
    } else {
        backtestBlock.hidden = true;
    }

    keyDrivers.innerHTML = '';
    (data.key_drivers || []).forEach((driver) => {
        const li = document.createElement('li');
        li.textContent = driver;
        keyDrivers.appendChild(li);
    });

    recommendation.textContent = data.recommendation;
    emptyResult.hidden = true;
    emptyResult.classList.add('is-hidden');
    resultContent.hidden = false;
}

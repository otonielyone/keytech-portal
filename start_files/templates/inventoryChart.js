const API_URL = '/api';
let items = []; // Will only have GPS Units and Card Readers

async function loadFromDB() {
    try {
        const response = await fetch(`${API_URL}/inventory`);
        const dbItems = await response.json();
        items = dbItems; // [{id, name, used}, ...]
        renderLiveInputs();
    } catch (err) {
        console.error("Failed to load from DB:", err);
    }
}

async function saveToDB(itemId, newUsedValue) {
    try {
        await fetch(`${API_URL}/inventory/${itemId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ used: newUsedValue })
        });
    } catch (err) {
        console.error("Failed to save to DB:", err);
    }
}

// Render last two inputs
const liveContainer = document.getElementById("liveContainer");
function renderLiveInputs() {
    liveContainer.innerHTML = "";
    items.forEach(item => {
        const div = document.createElement("div");
        div.className = "live-item";
        div.innerHTML = `
            <span class="item-name">${item.name}</span>
            <div class="item-current">Current: <strong>${item.used}</strong></div>
            <input type="number" min="0" value="0" class="item-input" placeholder="Enter amount">
            <button class="apply-btn">Add</button>
            <button class="remove-btn">Remove</button>
        `;
        const currentDisplay = div.querySelector(".item-current strong");
        const input = div.querySelector(".item-input");

        div.querySelector(".apply-btn").addEventListener("click", async () => {
            const val = parseInt(input.value);
            if (!isNaN(val) && val > 0) {
                item.used += val;
                currentDisplay.textContent = item.used;
                input.value = 0;
                await saveToDB(item.id, item.used);
            }
        });

        div.querySelector(".remove-btn").addEventListener("click", async () => {
            const val = parseInt(input.value);
            if (!isNaN(val) && val > 0) {
                item.used -= val;
                if (item.used < 0) item.used = 0;
                currentDisplay.textContent = item.used;
                input.value = 0;
                await saveToDB(item.id, item.used);
            }
        });

        liveContainer.appendChild(div);
    });
}

window.addEventListener("DOMContentLoaded", loadFromDB);

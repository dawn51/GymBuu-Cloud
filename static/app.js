<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gym Tracker - Antrenman Notları</title>
    <style>
        :root { --main-green: #2ecc71; --dark-green: #27ae60; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #e8f5e9; margin: 0; padding: 20px; color: #2c3e50; }
        .container { max-width: 1000px; margin: auto; display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        
        /* Sol ve Sağ Paneller */
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .header { grid-column: 1 / span 2; display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }
        .logo-placeholder { width: 50px; height: 50px; background: var(--main-green); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }

        h2, h3 { color: var(--dark-green); margin-top: 0; }
        input, button, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        
        button { background-color: var(--main-green); color: white; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background-color: var(--dark-green); }

        /* Tablo ve Liste Tasarımı */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
        th { background-color: #f9f9f9; color: #666; }
        .delete-btn { color: #e74c3c; cursor: pointer; background: none; border: none; font-size: 14px; width: auto; padding: 5px; }

        /* Notlar Kısmı */
        .notes-container { max-height: 400px; overflow-y: auto; }
        .note-card { background: #fffde7; border-left: 4px solid #fbc02d; padding: 15px; margin-bottom: 10px; border-radius: 5px; position: relative; }
        .note-date { font-size: 11px; color: #999; display: block; margin-bottom: 5px; }

        @media (max-width: 768px) { .container { grid-template-columns: 1fr; } .header { grid-column: 1; } }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="logo-placeholder">GYM</div>
        <h1>Gym Tracker</h1>
    </div>

    <div class="main-content">
        <div class="card" style="margin-bottom: 20px;">
            <h3>Antrenman Ekle</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <input type="date" id="ent-date">
                <input type="text" id="ent-ex" placeholder="Egzersiz (örn: Bench)">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                <input type="number" id="ent-sets" placeholder="Set">
                <input type="number" id="ent-reps" placeholder="Tekrar">
                <input type="number" id="ent-weight" placeholder="Kilo">
            </div>
            <button onclick="addEntry()">Ekle</button>

            <table id="entry-table">
                <thead><tr><th>Tarih</th><th>Egzersiz</th><th>Set/Tekrar</th><th>Kg</th><th></th></tr></thead>
                <tbody></tbody>
            </table>
        </div>

        <div class="card">
            <h3>Haftalık Kilo Takibi</h3>
            <div style="display: flex; gap: 10px;">
                <input type="date" id="w-date">
                <input type="number" id="w-kg" placeholder="Kilo (kg)">
                <button onclick="addWeight()" style="width: 100px;">Ekle</button>
            </div>
            <table id="weight-table">
                <thead><tr><th>Tarih</th><th>Kilo</th><th></th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <div class="side-content">
        <div class="card">
            <h3>Notlarım</h3>
            <textarea id="note-content" placeholder="Antrenman nasıl geçti? Bugün odak noktan neydi?" style="height: 100px; resize: none;"></textarea>
            <button onclick="addNote()">Not Kaydet</button>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <div id="notes-list" class="notes-container">
                </div>
        </div>
    </div>
</div>

<script>
    // Sayfa yüklendiğinde verileri çek
    document.addEventListener('DOMContentLoaded', () => {
        loadEntries();
        loadWeights();
        loadNotes();
    });

    // API İstekleri
    async function loadEntries() {
        const res = await fetch('/api/entries');
        const data = await res.json();
        const tbody = document.querySelector("#entry-table tbody");
        tbody.innerHTML = data.map(e => `
            <tr>
                <td>${e.date}</td>
                <td><strong>${e.exercise}</strong></td>
                <td>${e.sets} x ${e.reps}</td>
                <td>${e.weight} kg</td>
                <td><button class="delete-btn" onclick="deleteItem('entries', ${e.id})">Sil</button></td>
            </tr>
        `).join('');
    }

    async function addEntry() {
        const payload = {
            date: document.getElementById('ent-date').value,
            exercise: document.getElementById('ent-ex').value,
            sets: document.getElementById('ent-sets').value,
            reps: document.getElementById('ent-reps').value,
            weight: document.getElementById('ent-weight').value
        };
        if(!payload.exercise) return alert("Egzersiz adı gir kanka!");
        await fetch('/api/entries', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
        loadEntries();
    }

    async function loadWeights() {
        const res = await fetch('/api/weights');
        const data = await res.json();
        const tbody = document.querySelector("#weight-table tbody");
        tbody.innerHTML = data.map(w => `
            <tr>
                <td>${w.date}</td>
                <td>${w.kg} kg</td>
                <td><button class="delete-btn" onclick="deleteItem('weights', ${w.id})">Sil</button></td>
            </tr>
        `).join('');
    }

    async function addWeight() {
        const payload = { date: document.getElementById('w-date').value, kg: document.getElementById('w-kg').value };
        await fetch('/api/weights', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
        loadWeights();
    }

    async function loadNotes() {
        const res = await fetch('/api/notes');
        const data = await res.json();
        const list = document.getElementById('notes-list');
        list.innerHTML = data.map(n => `
            <div class="note-card">
                <span class="note-date">${n.date}</span>
                <div>${n.content}</div>
                <button class="delete-btn" style="position:absolute; top:5px; right:5px;" onclick="deleteItem('notes', ${n.id})">×</button>
            </div>
        `).join('');
    }

    async function addNote() {
        const content = document.getElementById('note-content').value;
        if(!content) return;
        const date = new Date().toLocaleDateString('tr-TR');
        await fetch('/api/notes', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date, content})});
        document.getElementById('note-content').value = '';
        loadNotes();
    }

    async function deleteItem(type, id) {
        if(!confirm("Emin misin kanka?")) return;
        await fetch(`/api/${type}/${id}`, { method: 'DELETE' });
        if(type === 'entries') loadEntries();
        if(type === 'weights') loadWeights();
        if(type === 'notes') loadNotes();
    }
</script>

</body>
</html>
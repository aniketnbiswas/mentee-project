const Journal = {
    viewDate: new Date(),
    selDate: null,
    dataCache: {},

    init() {
        this.renderGrid();
        this.fetchData();
        this.bindEvents();
    },

    bindEvents() {
        document.getElementById('btnPrev').onclick = () => this.shiftMonth(-1);
        document.getElementById('btnNext').onclick = () => this.shiftMonth(1);
        document.getElementById('btnToday').onclick = () => {
            this.viewDate = new Date();
            this.renderGrid();
            this.fetchData();
        };

        // Mood Select
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.onclick = (e) => {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
            }
        });

        // Slider
        document.getElementById('inScore').oninput = (e) => {
            document.getElementById('scoreDisplay').innerText = e.target.value;
        };
    },

    shiftMonth(dir) {
        this.viewDate.setMonth(this.viewDate.getMonth() + dir);
        this.renderGrid();
        this.fetchData();
    },

    renderGrid() {
        const year = this.viewDate.getFullYear();
        const month = this.viewDate.getMonth();
        
        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        document.getElementById('monthTitle').innerText = `${monthNames[month]} ${year}`;

        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const todayStr = new Date().toISOString().split('T')[0];

        // Spacers
        for(let i=0; i<firstDay; i++) {
            const div = document.createElement('div');
            div.className = 'd-cell empty';
            grid.appendChild(div);
        }

        // Days
        for(let i=1; i<=daysInMonth; i++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
            
            const cell = document.createElement('div');
            cell.className = 'd-cell';
            cell.id = `cell-${dateStr}`;
            cell.innerHTML = `
                <span class="d-num">${i}</span>
                <div class="d-indicator"></div>
            `;

            if(dateStr === todayStr) cell.classList.add('today');

            // Click Binding
            cell.onclick = () => this.openPanel(dateStr);

            grid.appendChild(cell);
        }
    },

    async fetchData() {
        const year = this.viewDate.getFullYear();
        const month = String(this.viewDate.getMonth() + 1).padStart(2, '0');
        
        try {
            const res = await fetch(`/api/journal/calendar?month=${year}-${month}`);
            const data = await res.json();
            this.dataCache = data;
            this.updateVisuals();
        } catch(e) { console.error("API Error", e); }
    },

    updateVisuals() {
        let streak = 0;
        
        Object.keys(this.dataCache).forEach(date => {
            const cell = document.getElementById(`cell-${date}`);
            if(cell) {
                const entry = this.dataCache[date];
                cell.classList.add('filled');
                const indicator = cell.querySelector('.d-indicator');
                
                // Reset
                indicator.style.backgroundColor = ''; 
                indicator.style.boxShadow = '';

                if(entry.mood === 'fire') {
                    indicator.style.backgroundColor = 'var(--m-fire)';
                    indicator.style.boxShadow = '0 0 8px var(--m-fire)';
                } else if(entry.mood === 'happy') {
                    indicator.style.backgroundColor = 'var(--m-happy)';
                } else if(entry.mood === 'stressed') {
                    indicator.style.backgroundColor = 'var(--m-stressed)';
                } else if(entry.mood === 'calm') {
                    indicator.style.backgroundColor = 'var(--m-calm)';
                } else if(entry.mood === 'neutral') {
                    indicator.style.backgroundColor = 'var(--m-neutral)';
                } else {
                    indicator.style.backgroundColor = 'var(--j-accent)';
                }
                streak++;
            }
        });
        document.getElementById('streakCount').innerText = streak;
    },

    async openPanel(dateStr) {
        this.selDate = dateStr;
        const d = new Date(dateStr);
        
        // Header
        document.getElementById('panelDay').innerText = d.getDate();
        document.getElementById('panelMonth').innerText = d.toLocaleString('default', {month: 'long'}).toUpperCase();
        document.getElementById('panelYear').innerText = d.getFullYear();

        // Reset
        document.getElementById('inWin').value = "";
        document.getElementById('inReflect').value = "";
        document.getElementById('inScore').value = 5;
        document.getElementById('scoreDisplay').innerText = "5";
        document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
        document.getElementById('checkDump').checked = false;

        // Show
        document.getElementById('entryPanel').classList.add('open');

        // Fetch
        try {
            const res = await fetch(`/api/journal/${dateStr}`);
            const json = await res.json();

            if(json.exists) {
                const data = json.data;
                if(data.mood) document.querySelector(`.mood-btn[data-val="${data.mood}"]`)?.classList.add('selected');
                if(data.score) {
                    document.getElementById('inScore').value = data.score;
                    document.getElementById('scoreDisplay').innerText = data.score;
                }
                if(data.content) {
                    document.getElementById('inWin').value = data.content.micro_win || "";
                    document.getElementById('inReflect').value = data.content.reflection || "";
                    document.getElementById('checkDump').checked = data.content.brain_dump_mode || false;
                }
            }
        } catch(e) { console.error("Load Error:", e); }
    },

    close() {
        document.getElementById('entryPanel').classList.remove('open');
    },

    async save() {
        const moodEl = document.querySelector('.mood-btn.selected');
        
        const payload = {
            date: this.selDate,
            mood: moodEl ? moodEl.dataset.val : null,
            score: document.getElementById('inScore').value,
            micro_win: document.getElementById('inWin').value,
            reflection: document.getElementById('inReflect').value,
            brain_dump_mode: document.getElementById('checkDump').checked
        };

        const msg = document.getElementById('saveMsg');
        msg.innerText = "Saving...";
        msg.style.opacity = 1;

        try {
            await fetch('/api/journal', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            msg.innerText = "Saved!";
            this.fetchData(); // Refresh Grid
            setTimeout(() => msg.style.opacity = 0, 1500);
        } catch(e) {
            msg.innerText = "Error";
        }
    }
};

document.addEventListener('DOMContentLoaded', () => Journal.init());
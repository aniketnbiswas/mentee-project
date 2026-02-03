/* mentee/static/js/drill_engine.js */

class DrillEngine {
    static currentSession = null;

    static startSession(drillId) {
        document.getElementById('overlay-start').classList.remove('active');
        const canvas = document.getElementById('game-canvas');
        
        // Router for Game Logic
        switch(drillId) {
            case 'reaction': this.currentSession = new ReactionDrill(canvas); break;
            case 'memory':   this.currentSession = new MemoryDrill(canvas); break;
            case 'vision':   this.currentSession = new VisionDrill(canvas); break;
            case 'focus':    this.currentSession = new FocusDrill(canvas); break;
            case 'pattern':  this.currentSession = new PatternDrill(canvas); break;
            case 'decision': this.currentSession = new DecisionDrill(canvas); break;
            default: alert("Drill module not found"); return;
        }

        this.currentSession.start();
    }
}

// --- BASE DRILL CLASS (Shared Logic) ---
class BaseDrill {
    constructor(canvas) {
        this.canvas = canvas;
        this.score = 0;
        this.level = 1;
        this.timer = 60; // seconds
        this.isRunning = false;
        this.interval = null;
        this.accuracyHits = 0;
        this.accuracyTotal = 0;
    }

    start() {
        this.isRunning = true;
        this.score = 0;
        this.updateHUD();
        this.startTimer();
        this.setupGame();
    }

    startTimer() {
        this.updateTimerDisplay();
        this.interval = setInterval(() => {
            if(!this.isRunning) return;
            this.timer--;
            this.updateTimerDisplay();
            if(this.timer <= 0) this.endGame();
        }, 1000);
    }

    updateTimerDisplay() {
        const min = Math.floor(this.timer / 60);
        const sec = this.timer % 60;
        document.getElementById('hud-timer').innerText = `${min}:${sec.toString().padStart(2, '0')}`;
    }

    addScore(points) {
        this.score += points;
        this.updateHUD();
    }

    updateHUD() {
        document.getElementById('hud-score').innerText = this.score;
        document.getElementById('hud-level').innerText = this.level;
    }

    recordAction(correct) {
        this.accuracyTotal++;
        if(correct) this.accuracyHits++;
    }

    async endGame() {
        this.isRunning = false;
        clearInterval(this.interval);
        this.canvas.innerHTML = ''; // Clear game

        // Calculate Stats
        const acc = this.accuracyTotal === 0 ? 0 : Math.round((this.accuracyHits / this.accuracyTotal) * 100);
        
        // UI Update
        document.getElementById('res-score').innerText = this.score;
        document.getElementById('res-acc').innerText = acc + '%';
        document.getElementById('res-lvl').innerText = this.level;
        document.getElementById('overlay-results').classList.add('active');

        // Backend Save
        try {
            await fetch('/api/drills/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    drill_id: DRILL_ID,
                    score: this.score,
                    accuracy: acc,
                    level: this.level,
                    duration: 60 - this.timer
                })
            });
        } catch(e) { console.error("Save failed", e); }
    }
}

// ==========================================
// INDIVIDUAL DRILLS
// ==========================================

// 1. REACTION SPEED
class ReactionDrill extends BaseDrill {
    setupGame() {
        this.timer = 45; 
        this.canvas.innerHTML = `<div id="rxn-zone" class="reaction-target wait">Wait...</div>`;
        this.zone = document.getElementById('rxn-zone');
        this.zone.onclick = () => this.handleClick();
        this.state = 'wait'; // wait, ready, go
        this.scheduleNext();
    }

    scheduleNext() {
        if(!this.isRunning) return;
        this.state = 'wait';
        this.zone.className = 'reaction-target wait';
        this.zone.innerText = "Wait...";
        
        const delay = Math.random() * 2000 + 1500; // 1.5s - 3.5s
        this.timeout = setTimeout(() => {
            if(!this.isRunning) return;
            this.state = 'go';
            this.zone.className = 'reaction-target go';
            this.zone.innerText = "CLICK!";
            this.startTime = Date.now();
        }, delay);
    }

    handleClick() {
        if(this.state === 'wait') {
            this.score -= 50; // Penalty
            this.zone.innerText = "TOO EARLY!";
            this.recordAction(false);
            clearTimeout(this.timeout);
            setTimeout(() => this.scheduleNext(), 1000);
        } else if(this.state === 'go') {
            const time = Date.now() - this.startTime;
            const points = Math.max(0, 500 - time); // Faster = more points
            this.addScore(points);
            this.recordAction(true);
            this.zone.innerText = `${time}ms`;
            this.state = 'done';
            setTimeout(() => this.scheduleNext(), 1000);
        }
        this.updateHUD();
    }
}

// 2. TACTICAL MEMORY (Grid Pattern)
class MemoryDrill extends BaseDrill {
    setupGame() {
        this.timer = 90;
        this.gridSize = 3;
        this.patternLength = 3;
        this.renderGrid();
        this.startRound();
    }

    renderGrid() {
        this.canvas.innerHTML = `<div id="mem-grid" class="game-grid" style="grid-template-columns: repeat(${this.gridSize}, 1fr); width: 300px; height: 300px;"></div>`;
        const grid = document.getElementById('mem-grid');
        for(let i=0; i<this.gridSize*this.gridSize; i++) {
            const cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.dataset.idx = i;
            cell.onclick = () => this.handleInput(i, cell);
            grid.appendChild(cell);
        }
    }

    async startRound() {
        this.inputActive = false;
        this.pattern = [];
        const cells = document.querySelectorAll('.grid-cell');
        
        // Generate Pattern
        for(let i=0; i<this.patternLength; i++) {
            let idx;
            do { idx = Math.floor(Math.random() * (this.gridSize*this.gridSize)); }
            while(this.pattern.includes(idx));
            this.pattern.push(idx);
        }

        // Show Pattern
        await new Promise(r => setTimeout(r, 500));
        for(let idx of this.pattern) {
            cells[idx].classList.add('active');
        }
        await new Promise(r => setTimeout(r, 1000 + (this.level * 200))); // Show longer based on level
        cells.forEach(c => c.classList.remove('active'));
        
        this.inputActive = true;
        this.playerPattern = [];
    }

    handleInput(idx, cell) {
        if(!this.inputActive) return;
        
        if(this.pattern.includes(idx) && !this.playerPattern.includes(idx)) {
            cell.classList.add('correct');
            this.playerPattern.push(idx);
            if(this.playerPattern.length === this.pattern.length) {
                // Round Win
                this.addScore(100 * this.level);
                this.recordAction(true);
                this.level++;
                if(this.level % 2 === 0) this.gridSize = Math.min(5, this.gridSize+1); // Increase grid size every 2 levels
                this.patternLength = Math.min(8, this.patternLength + 1);
                this.renderGrid();
                setTimeout(() => this.startRound(), 1000);
            }
        } else {
            // Wrong
            cell.classList.add('wrong');
            this.recordAction(false);
            this.inputActive = false;
            setTimeout(() => {
                cell.classList.remove('wrong');
                this.startRound(); // Retry same level
            }, 800);
        }
    }
}

// 3. FIELD VISION (Target Hunter)
class VisionDrill extends BaseDrill {
    setupGame() {
        this.timer = 60;
        this.spawnTarget();
    }

    spawnTarget() {
        if(!this.isRunning) return;
        const size = Math.max(30, 80 - (this.level * 2)); // Smaller as levels go up
        const x = Math.random() * (this.canvas.clientWidth - size);
        const y = Math.random() * (this.canvas.clientHeight - size);

        const target = document.createElement('div');
        target.className = 'vision-target';
        target.style.width = size + 'px';
        target.style.height = size + 'px';
        target.style.left = x + 'px';
        target.style.top = y + 'px';
        
        target.onmousedown = () => {
            this.addScore(50);
            this.recordAction(true);
            target.remove();
            if(this.score % 250 === 0) this.level++;
            this.spawnTarget();
        };

        this.canvas.innerHTML = '';
        this.canvas.appendChild(target);
    }
}

// 4. FOCUS GRID (1 to N)
class FocusDrill extends BaseDrill {
    setupGame() {
        this.gridSize = 3;
        this.startRound();
    }

    startRound() {
        this.currentNum = 1;
        this.maxNum = this.gridSize * this.gridSize;
        
        this.canvas.innerHTML = `<div id="focus-grid" class="game-grid" style="grid-template-columns: repeat(${this.gridSize}, 1fr); width: 400px; height: 400px;"></div>`;
        const grid = document.getElementById('focus-grid');
        
        // Generate numbers
        const nums = Array.from({length: this.maxNum}, (_, i) => i + 1).sort(() => Math.random() - 0.5);
        
        nums.forEach(n => {
            const cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.innerText = n;
            cell.onclick = () => this.check(n, cell);
            grid.appendChild(cell);
        });
    }

    check(n, cell) {
        if(n === this.currentNum) {
            cell.style.opacity = 0;
            cell.style.pointerEvents = 'none';
            this.currentNum++;
            this.recordAction(true);
            if(this.currentNum > this.maxNum) {
                this.addScore(500 * this.level);
                this.level++;
                this.gridSize = Math.min(6, this.gridSize + 1);
                this.startRound();
            }
        } else {
            this.score -= 10;
            this.recordAction(false);
            cell.classList.add('wrong');
            setTimeout(() => cell.classList.remove('wrong'), 300);
        }
        this.updateHUD();
    }
}

// 5. PATTERN RECALL (Simon Says)
class PatternDrill extends BaseDrill {
    setupGame() {
        this.sequence = [];
        this.playerIdx = 0;
        this.colors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b'];
        
        this.canvas.innerHTML = `<div class="game-grid" style="grid-template-columns: 1fr 1fr; width: 300px; height: 300px; gap: 10px;">
            <div class="grid-cell" id="btn-0" style="background:${this.colors[0]}50; border:2px solid ${this.colors[0]}"></div>
            <div class="grid-cell" id="btn-1" style="background:${this.colors[1]}50; border:2px solid ${this.colors[1]}"></div>
            <div class="grid-cell" id="btn-2" style="background:${this.colors[2]}50; border:2px solid ${this.colors[2]}"></div>
            <div class="grid-cell" id="btn-3" style="background:${this.colors[3]}50; border:2px solid ${this.colors[3]}"></div>
        </div>`;

        // Bind clicks
        for(let i=0; i<4; i++) {
            document.getElementById(`btn-${i}`).onclick = () => this.handleInput(i);
        }
        
        this.nextRound();
    }

    async nextRound() {
        this.playerIdx = 0;
        this.inputActive = false;
        this.sequence.push(Math.floor(Math.random() * 4));
        
        await new Promise(r => setTimeout(r, 1000));

        // Play Sequence
        for(let idx of this.sequence) {
            const el = document.getElementById(`btn-${idx}`);
            el.style.background = this.colors[idx];
            el.style.boxShadow = `0 0 30px ${this.colors[idx]}`;
            await new Promise(r => setTimeout(r, 400));
            el.style.background = `${this.colors[idx]}50`;
            el.style.boxShadow = 'none';
            await new Promise(r => setTimeout(r, 200));
        }
        this.inputActive = true;
    }

    handleInput(idx) {
        if(!this.inputActive) return;
        
        const el = document.getElementById(`btn-${idx}`);
        // Flash visual
        el.style.background = this.colors[idx];
        setTimeout(() => el.style.background = `${this.colors[idx]}50`, 150);

        if(idx === this.sequence[this.playerIdx]) {
            this.playerIdx++;
            if(this.playerIdx >= this.sequence.length) {
                this.addScore(100 * this.sequence.length);
                this.recordAction(true);
                this.level++;
                this.nextRound();
            }
        } else {
            this.recordAction(false);
            this.endGame();
        }
    }
}

// 6. DECISION RUSH
class DecisionDrill extends BaseDrill {
    setupGame() {
        this.timer = 60;
        this.canvas.innerHTML = `
            <div class="decision-card">
                <div class="decision-prompt" id="d-prompt">EVEN?</div>
            </div>
            <div class="decision-controls" style="margin-top:2rem">
                <button class="btn-decision" onclick="DrillEngine.currentSession.check(true)">Yes</button>
                <button class="btn-decision" onclick="DrillEngine.currentSession.check(false)">No</button>
            </div>
        `;
        this.nextCard();
    }

    nextCard() {
        this.number = Math.floor(Math.random() * 100);
        this.isEvenPrompt = Math.random() > 0.5;
        
        document.getElementById('d-prompt').innerText = this.number;
        document.querySelector('.decision-card').style.borderColor = this.isEvenPrompt ? '#3b82f6' : '#ef4444';
        
        // Add text instruction
        if(!document.getElementById('d-inst')) {
            const inst = document.createElement('div');
            inst.id = 'd-inst';
            inst.style.marginTop = '10px';
            inst.style.color = '#94a3b8';
            document.querySelector('.decision-card').appendChild(inst);
        }
        document.getElementById('d-inst').innerText = this.isEvenPrompt ? "Is it EVEN?" : "Is it ODD?";
    }

    check(userSaidYes) {
        const isEven = this.number % 2 === 0;
        const correctAnswer = this.isEvenPrompt ? isEven : !isEven;

        if(userSaidYes === correctAnswer) {
            this.addScore(50);
            this.recordAction(true);
            this.level = Math.floor(this.score / 500) + 1;
        } else {
            this.score -= 20;
            this.recordAction(false);
            const card = document.querySelector('.decision-card');
            card.style.transform = 'translateX(10px)';
            setTimeout(() => card.style.transform = 'translateX(0)', 100);
        }
        this.nextCard();
    }
}
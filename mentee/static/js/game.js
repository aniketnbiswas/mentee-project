/* mentee/static/js/games.js */

const ImpulseGame = {
    state: 'idle', 
    box: document.getElementById('game-impulse'), 
    text: document.getElementById('impulse-status'), 
    overlay: document.querySelector('#game-impulse .game-overlay'), 
    timer: null,
    
    init() { 
        if(this.state !== 'idle') return; 
        this.reset(); 
        this.start(); 
    },
    
    reset() { 
        this.overlay.style.display = 'none'; 
        this.box.style.background = '#0F172A'; 
        this.text.innerText = 'WAIT'; 
        this.text.style.color = '#94A3B8'; 
        this.box.onclick = () => this.click(); 
    },
    
    start() { 
        this.state = 'waiting'; 
        const d = Math.random() * 2000 + 2000; 
        this.timer = setTimeout(() => { 
            if(this.state === 'waiting'){ 
                this.state = 'ready'; 
                this.box.style.background = '#10B981'; 
                this.text.innerText = 'CLICK'; 
                this.text.style.color = '#fff'; 
                this.startTime = Date.now(); 
            } 
        }, d); 
    },
    
    click() { 
        if(this.state === 'waiting'){ 
            clearTimeout(this.timer); 
            this.end(false); 
        } else if(this.state === 'ready'){ 
            this.end(true); 
        } 
    },
    
    end(success) { 
        this.state = 'idle'; 
        this.box.onclick = null; 
        if(success){ 
            const t = Date.now() - this.startTime; 
            this.text.innerText = t + 'ms'; 
            document.getElementById('impulse-last').innerText = t + 'ms'; 
        } else { 
            this.text.innerText = 'TOO EARLY'; 
            this.text.style.color = '#EF4444'; 
        } 
        setTimeout(() => {
            this.overlay.style.display = 'flex';
            this.overlay.innerText = success ? 'AGAIN' : 'RETRY';
        }, 1500); 
    }
};

const ResilienceGame = {
    grid: document.getElementById('resilience-grid'), 
    overlay: document.querySelector('#game-resilience .game-overlay'), 
    seq: [], 
    idx: 0,
    
    init() { 
        this.overlay.style.display = 'none'; 
        this.seq = []; 
        this.build(); 
        this.next(); 
    },
    
    build() { 
        this.grid.innerHTML = ''; 
        for(let i=0; i<4; i++){ 
            let d = document.createElement('div'); 
            d.className = 'pattern-block'; 
            d.onclick = () => this.check(i, d); 
            this.grid.appendChild(d); 
        } 
    },
    
    async next() { 
        this.idx = 0; 
        this.seq.push(Math.floor(Math.random() * 4)); 
        await new Promise(r => setTimeout(r, 500)); 
        const b = document.querySelectorAll('.pattern-block'); 
        for(let i of this.seq){ 
            b[i].classList.add('active'); 
            await new Promise(r => setTimeout(r, 400)); 
            b[i].classList.remove('active'); 
            await new Promise(r => setTimeout(r, 200)); 
        } 
    },
    
    check(i, el) { 
        el.classList.add('active'); 
        setTimeout(() => el.classList.remove('active'), 150); 
        if(i === this.seq[this.idx]){ 
            this.idx++; 
            if(this.idx >= this.seq.length){ 
                document.getElementById('resilience-streak').innerText = this.seq.length; 
                this.next(); 
            } 
        } else { 
            document.getElementById('resilience-streak').innerText = 0; 
            this.overlay.style.display = 'flex'; 
            this.overlay.innerText = 'RETRY'; 
        } 
    }
};

const FocusGame = {
    grid: document.getElementById('focus-grid'), 
    overlay: document.querySelector('#game-focus .game-overlay'), 
    curr: 1,
    
    init() { 
        this.overlay.style.display = 'none'; 
        this.curr = 1; 
        this.start = Date.now(); 
        this.render(); 
    },
    
    render() { 
        this.grid.innerHTML = ''; 
        let n = Array.from({length: 9}, (_, i) => i + 1).sort(() => Math.random() - 0.5); 
        n.forEach(x => { 
            let d = document.createElement('div'); 
            d.className = 'focus-cell'; 
            d.innerText = x; 
            if(x < this.curr) d.style.opacity = 0.2; 
            d.onclick = () => this.click(x); 
            this.grid.appendChild(d); 
        }); 
    },
    
    click(x) { 
        if(x === this.curr){ 
            this.curr++; 
            if(this.curr > 9){ 
                let t = ((Date.now() - this.start) / 1000).toFixed(2); 
                document.getElementById('focus-time').innerText = t + 's'; 
                this.overlay.style.display = 'flex'; 
                this.overlay.innerText = t + 's'; 
            } else { 
                this.render(); 
            } 
        } 
    }
};
/* MENTAL EDGE SYSTEM LOGIC */

const Library = {
    state: {
        category: 'all',
        sport: 'all',
        wizardData: {}
    },

    init() {
        this.cards = document.querySelectorAll('.article-card');
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('sport-dropdown');
            if (dropdown && !dropdown.contains(e.target)) {
                dropdown.querySelector('.dropdown-menu').classList.remove('show');
            }
        });

        console.log("System Loaded.");
    },

    // --- DROPDOWN LOGIC ---
    toggleDropdown() {
        const menu = document.querySelector('.dropdown-menu');
        menu.classList.toggle('show');
    },

    selectSport(sport, btn) {
        this.state.sport = sport;
        
        // Update Label
        const label = sport === 'all' ? 'All Sports' : sport;
        document.getElementById('dropdown-label').textContent = label;
        
        // Update Selected styling
        document.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
        btn.classList.add('selected');
        
        // Hide Menu
        document.querySelector('.dropdown-menu').classList.remove('show');
        
        this.applyFilters();
    },

    // --- FILTERING ---
    filter(category, btn) {
        this.state.category = category;
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        if(btn) btn.classList.add('active');
        this.applyFilters();
    },

    applyFilters() {
        this.cards.forEach(card => {
            const cardCat = card.dataset.category;
            const cardSport = card.dataset.sport;
            
            const catMatch = this.state.category === 'all' || cardCat === this.state.category;
            const sportMatch = this.state.sport === 'all' || cardSport === this.state.sport || cardSport === 'General';

            if (catMatch && sportMatch) {
                card.style.display = 'flex';
                card.style.animation = 'fadeIn 0.3s ease';
            } else {
                card.style.display = 'none';
            }
        });
    },

    // --- CURRICULUM WIZARD ---
    openWizard() {
        document.getElementById('curriculum-wizard').style.display = 'flex';
    },

    closeWizard() {
        document.getElementById('curriculum-wizard').style.display = 'none';
        this.resetWizard();
    },

    nextStep(selection) {
        this.state.wizardData.sport = selection;
        document.getElementById('step-1').classList.remove('active');
        document.getElementById('step-2').classList.add('active');
    },

    finishWizard(challenge) {
        this.state.wizardData.challenge = challenge;
        this.closeWizard();
        
        // Auto-filter based on selection
        const filterBtn = document.querySelector(`.filter-pill[data-filter="${challenge}"]`);
        if (filterBtn) {
            this.filter(challenge, filterBtn);
            // Scroll to grid
            document.querySelector('.library-toolbar').scrollIntoView({ behavior: 'smooth' });
        }
    },

    resetWizard() {
        document.getElementById('step-2').classList.remove('active');
        document.getElementById('step-1').classList.add('active');
        this.state.wizardData = {};
    }
};

document.addEventListener('DOMContentLoaded', () => Library.init());

// CSS Animation Keyframes injection
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
`;
document.head.appendChild(styleSheet);
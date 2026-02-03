/* Mentee Marketplace Logic */

const Mentors = {
    state: {
        category: 'all',
        search: '',
        view: 'grid'
    },

    init() {
        console.log("Mentors Marketplace Loaded");
        this.grid = document.getElementById('mentor-grid');
        this.cards = document.querySelectorAll('.mentor-card');
        this.noResults = document.getElementById('no-results');
    },

    setCategory(cat, btn) {
        this.state.category = cat.toLowerCase();
        
        // Update Active Pill
        document.querySelectorAll('.filter-pills .pill').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        
        this.applyFilters();
    },

    filter() {
        this.state.search = document.getElementById('mentor-search').value.toLowerCase();
        this.applyFilters();
    },

    applyFilters() {
        let visibleCount = 0;

        this.cards.forEach(card => {
            const name = card.dataset.name;
            const tags = card.dataset.tags;
            const searchMatch = name.includes(this.state.search) || tags.includes(this.state.search);
            
            const catMatch = this.state.category === 'all' || tags.includes(this.state.category);

            if (searchMatch && catMatch) {
                card.style.display = 'flex'; // 'flex' because cards are flex containers
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        // Show/Hide Empty State
        this.noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    },

    setView(view) {
        this.state.view = view;
        
        // Toggle Buttons
        document.querySelectorAll('.icon-btn').forEach(b => b.classList.remove('active'));
        event.currentTarget.classList.add('active');

        // Apply Class
        if (view === 'list') {
            this.grid.classList.add('view-list');
            this.grid.classList.remove('view-grid');
        } else {
            this.grid.classList.add('view-grid');
            this.grid.classList.remove('view-list');
        }
    },

    reset() {
        document.getElementById('mentor-search').value = '';
        this.state.search = '';
        this.state.category = 'all';
        document.querySelectorAll('.filter-pills .pill').forEach(p => p.classList.remove('active'));
        document.querySelector('.filter-pills .pill:first-child').classList.add('active');
        this.applyFilters();
    }
};

document.addEventListener('DOMContentLoaded', () => Mentors.init());
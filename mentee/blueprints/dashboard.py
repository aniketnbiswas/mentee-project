from flask import Blueprint, render_template, jsonify, request, abort, redirect, url_for
from flask_login import current_user, login_required
from mentee.models import JournalEntry, DrillSession, UserIdentity, db
from datetime import datetime
import json
from sqlalchemy import func

dashboard = Blueprint('dashboard', __name__)

# ==========================================
# 1. MENTAL EDGE LIBRARY DATA (PRESERVED)
# ==========================================
ARTICLES_DATA = [
    {
        "id": "1",
        "title": "The Vagus Nerve Masterclass",
        "subtitle": "A complete physiological override system for high-stakes anxiety.",
        "category": "Anti-Choking",
        "sport": "General",
        "type": "Deep Dive",
        "read_time": "25 min",
        "level": "Elite",
        "image": "img/1.png", 
        "badges": ["Neurobiology", "Protocol", "Polyvagal Theory"],
        "references": [
            "Huberman Lab: Tools for Managing Stress",
            "Porges, S. W. (2011). The Polyvagal Theory.",
            "Lehrer, P. M., & Gevirtz, R. (2014). Heart rate variability biofeedback."
        ],
        "content": {
            "intro": "In high-pressure environments, the distinction between 'nervous' and 'choking' is purely biological...",
            "sections": [
                {"heading": "Part I: The Neurobiology of 'The Choke'", "body": "To defeat choking, you must understand the mechanism..."},
                {"heading": "Part II: The Physiological Sigh (The Primary Lever)", "body": "Discovered by Stanford neurobiologists..."},
                {"heading": "Part III: Panoramic Vision (The Secondary Lever)", "body": "Your eyes are essentially external parts of your brain..."},
                {"heading": "Part IV: Mechanical Anchoring", "body": "Anxiety often manifests as a feeling of 'floating'..."},
                {"heading": "Advanced Troubleshooting", "body": "**Scenario: My hands are still shaking.**..."}
            ]
        }
    },
    {
        "id": "2",
        "title": "The Cortical Interference Protocol",
        "subtitle": "Why trying harder makes you play worse: The science of Reinvestment.",
        "category": "Focus",
        "sport": "Tennis",
        "type": "Deep Dive",
        "read_time": "30 min",
        "level": "Elite",
        "image": "img/2.png",
        "badges": ["Theory", "Gold Standard", "Motor Learning"],
        "references": ["Masters, R. S. W. (1992). Knowledge, knerves and know-how.", "Wulf, G. (2013). Attentional focus and motor learning."],
        "content": {
            "intro": "We have all seen it: The world-class shooter who airballs a free throw...",
            "sections": [
                {"heading": "The Theory of Reinvestment", "body": "Reinvestment Theory posits that under pressure..."},
                {"heading": "Solution 1: The External Focus Loop", "body": "The brain cannot think about two things at once..."},
                {"heading": "Solution 2: The Holier-Than-Thou Gaze (Quiet Eye)", "body": "In archery and shooting sports, we see 'Quiet Eye'..."},
                {"heading": "Advanced Training: Constraint-Based Chaos", "body": "You cannot learn to avoid interference by practicing in silence..."}
            ]
        }
    },
    {
        "id": "3",
        "title": "The 2-Hour Recovery Algorithm",
        "subtitle": "A structured timeline to process defeat and prevent performance slumps.",
        "category": "Recovery",
        "sport": "General",
        "type": "Deep Dive",
        "read_time": "20 min",
        "level": "Intermediate",
        "image": "img/3.png",
        "badges": ["System", "Mental Health", "CBT"],
        "references": ["Cognitive Behavioral Therapy for Sports Performance", "The Chimp Paradox - Dr. Steve Peters"],
        "content": {
            "intro": "In tournament play, you do not have the luxury of grieving a loss for a week...",
            "sections": [
                {"heading": "T+00:00 - The Decompression Phase", "body": "Goal: Physiological Reset..."},
                {"heading": "T+00:30 - The Venting Phase (Strictly Timed)", "body": "Goal: Emotional Externalization..."},
                {"heading": "T+01:00 - The Detective Phase", "body": "Goal: Cognitive Extraction..."},
                {"heading": "T+02:00 - The Bookend Ritual", "body": "Goal: Psychological Closure..."}
            ]
        }
    },
    {
        "id": "4",
        "title": "Djokovic vs. Federer: The Smile",
        "subtitle": "A forensic psychological analysis of the 2019 Wimbledon Final tie-break.",
        "category": "Strategy",
        "sport": "Tennis",
        "type": "Breakdown",
        "read_time": "22 min",
        "level": "Advanced",
        "image": "img/4.png",
        "badges": ["Case Study", "Elite", "Analysis"],
        "references": ["Inner Game of Tennis - Gallwey", "Match Analysis: Wimbledon 2019"],
        "content": {
            "context": "Wimbledon 2019. The Final. 5th Set. 12-12. Tie-break...",
            "moments": [
                {"time": "The Cognitive Reappraisal", "analysis": "When the crowd erupts in chants..."},
                {"time": "The Isolation Protocol", "analysis": "Watch Djokovic between points..."},
                {"time": "The Tempo Dictatorship", "analysis": "At 12-12, most players rush..."}
            ],
            "takeaway": "In your own performance, you cannot control the referee..."
        }
    },
    {
        "id": "5",
        "title": "The Finisher's Mindset",
        "subtitle": "Why teams choke with the lead and the psychology of closing.",
        "category": "Confidence",
        "sport": "Basketball",
        "type": "Playbook",
        "read_time": "15 min",
        "level": "Elite",
        "image": "img/5.png",
        "badges": ["Framework", "Leadership"],
        "references": ["Thinking, Fast and Slow - Kahneman", "Relentless - Tim Grover"],
        "content": {
            "rules": [
                {"rule": "Promotion vs. Prevention Orientation", "desc": "Psychologically, there are two modes..."},
                {"rule": "The Certainty Matrix", "desc": "In the first 3 quarters, you take 50/50 risks..."},
                {"rule": "The 10-Second Flush Ritual", "desc": "You will make a mistake in the clutch..."}
            ]
        }
    },
    {
        "id": "6",
        "title": "Grandmaster Time Management",
        "subtitle": "Decision making heuristics for extreme time pressure scenarios.",
        "category": "Strategy",
        "sport": "Chess",
        "type": "Playbook",
        "read_time": "18 min",
        "level": "Elite",
        "image": "img/6.png",
        "badges": ["Expert Reviewed", "Cognitive Science"],
        "references": ["Kotov: Think Like a Grandmaster", "Garry Kasparov on Decision Making"],
        "content": {
            "rules": [
                {"rule": "The 20% Rule of Allocation", "desc": "In complex positions, perfection is the enemy..."},
                {"rule": "The 'Hope Chess' Fallacy", "desc": "Under pressure, the brain seeks an easy way out..."},
                {"rule": "The Intuition Switch (System 1 vs System 2)", "desc": "Daniel Kahneman's 'Thinking Fast and Slow' applies here..."}
            ]
        }
    },
    {
        "id": "7",
        "title": "The Cinema of the Mind",
        "subtitle": "Advanced protocols for multisensory visualization and neural priming.",
        "category": "Focus",
        "sport": "General",
        "type": "Deep Dive",
        "read_time": "20 min",
        "level": "All Levels",
        "image": "img/7.png",
        "badges": ["Foundational", "Performance", "Neural Priming"],
        "references": ["Functional Equivalence Theory", "Dr. Judd Biasiotto - Psychology"],
        "content": {
            "intro": "Visualization is often dismissed as 'daydreaming'...",
            "sections": [
                {"heading": "Case Study: The Injured Gymnast", "body": "An Olympic gymnast broke her leg..."},
                {"heading": "The 3D Framework: Functional Equivalence", "body": "For visualization to work..."},
                {"heading": "Practical Task: The Bedtime Script", "body": "Write a script of your perfect performance..."}
            ]
        }
    },
    {
        "id": "8",
        "title": "Sleep Banking for Athletes",
        "subtitle": "Optimizing circadian rhythms and recovery during tournament weeks.",
        "category": "Recovery",
        "sport": "General",
        "type": "Deep Dive",
        "read_time": "20 min",
        "level": "Advanced",
        "image": "img/8.png",
        "badges": ["Science", "Physiology", "Sleep Architecture"],
        "references": ["Matthew Walker: Why We Sleep", "Stanford Sleep & Performance Research Center"],
        "content": {
            "intro": "Sleep is the most potent performance-enhancing drug that is legal...",
            "sections": [
                {"heading": "The Science of Sleep Extension", "body": "A landmark Stanford study..."},
                {"heading": "The Banking Strategy", "body": "You cannot 'catch up' on sleep effectively..."},
                {"heading": "The Caffeine-Melatonin Cycle", "body": "To master sleep, you must master light and chemicals..."}
            ]
        }
    },
    {
        "id": "9",
        "title": "Reframing Self-Talk",
        "subtitle": "Cognitive restructuring techniques for resilience.",
        "category": "Confidence",
        "sport": "General",
        "type": "Deep Dive",
        "read_time": "15 min",
        "level": "Beginner",
        "image": "img/9.png",
        "badges": ["Psychology", "Resilience", "CBT"],
        "references": ["Ethan Kross: Chatter", "Stoic Philosophy"],
        "content": {
            "intro": "Your inner voice is the most influential coach you will ever have...",
            "sections": [
                {"heading": "The Theory of Cognitive Distortions", "body": "Anxiety often stems from 'Cognitive Distortions'..."},
                {"heading": "The Third-Person Shift (Solomon's Paradox)", "body": "When you talk to yourself using 'I' ..."},
                {"heading": "Instructional vs. Motivational Self-Talk", "body": "In high-precision tasks..."}
            ]
        }
    }
]

COLLECTIONS_DATA = [
    {"id": "c1", "title": "🏆 Tournament Survival Kit", "desc": "Essential mental protocols for game day.", "bg": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"},
    {"id": "c2", "title": "❄️ Ice In The Veins", "desc": "Protocols to lower heart rate instantly.", "bg": "linear-gradient(135deg, #06b6d4 0%, #0f172a 100%)"},
    {"id": "c3", "title": "🔥 Burnout Prevention", "desc": "Sustainable performance strategies.", "bg": "linear-gradient(135deg, #f43f5e 0%, #0f172a 100%)"},
]

PATHS_DATA = [
    {"id": "p1", "title": "Anti-Choking System", "steps": "4 Modules", "icon": "🛡️", "color": "#ef4444"},
    {"id": "p2", "title": "Confidence Rebuild", "steps": "6 Modules", "icon": "🚀", "color": "#f59e0b"},
    {"id": "p3", "title": "Elite Focus Mastery", "steps": "5 Modules", "icon": "🎯", "color": "#3b82f6"},
]

MENTORS_DATA = [
    {"id": 1, "name": "Dr. Sarah Jenkins", "title": "Elite Performance Psychologist", "specialties": ["Pressure", "Focus"], "price": 45, "rating": 4.9, "reviews": 124, "experience": "10+ Years", "next_slot": "Tomorrow, 10:00 AM", "is_elite": True, "image": "https://randomuser.me/api/portraits/women/44.jpg", "bio": "Former Olympic consultant helping athletes crush performance anxiety."},
    {"id": 2, "name": "Marcus Thorne", "title": "Mental Conditioning Coach", "specialties": ["Recovery", "Confidence"], "price": 30, "rating": 4.7, "reviews": 89, "experience": "5 Years", "next_slot": "Today, 4:00 PM", "is_elite": False, "image": "https://randomuser.me/api/portraits/men/32.jpg", "bio": "Specializes in comeback mentality and injury recovery for contact sports."},
    {"id": 3, "name": "Elena Rodriguez", "title": "Flow State Specialist", "specialties": ["Focus", "Tournament Prep"], "price": 60, "rating": 5.0, "reviews": 210, "experience": "12 Years", "next_slot": "Wed, 2:00 PM", "is_elite": True, "image": "https://randomuser.me/api/portraits/women/68.jpg", "bio": "I teach athletes how to enter 'The Zone' on command."},
    {"id": 4, "name": "Coach David Kim", "title": "Tactical Mindset Trainer", "specialties": ["Strategy", "Pressure"], "price": 35, "rating": 4.6, "reviews": 45, "experience": "4 Years", "next_slot": "Tomorrow, 11:00 AM", "is_elite": False, "image": "https://randomuser.me/api/portraits/men/86.jpg", "bio": "Focusing on decision making speed and tactical awareness under fatigue."},
    {"id": 5, "name": "Jessica Vance", "title": "Youth Performance Mentor", "specialties": ["Confidence", "Rising Juniors"], "price": 25, "rating": 4.8, "reviews": 67, "experience": "3 Years", "next_slot": "Today, 5:30 PM", "is_elite": False, "image": "https://randomuser.me/api/portraits/women/12.jpg", "bio": "Helping young athletes build unshakeable foundations early."},
    {"id": 6, "name": "Alex Volkov", "title": "High-Stakes Competitor Coach", "specialties": ["Tournament Prep", "Aggression"], "price": 55, "rating": 4.9, "reviews": 150, "experience": "8 Years", "next_slot": "Fri, 9:00 AM", "is_elite": True, "image": "https://randomuser.me/api/portraits/men/46.jpg", "bio": "Turn your nerves into aggression. For combat and contact sports."}
]

DRILLS_CONFIG = {
    'reaction': {'title': 'Neural Impulse', 'desc': 'Train pure reaction speed and inhibition control.', 'icon': '⚡', 'color': '#ef4444'},
    'memory': {'title': 'Tactical Grid', 'desc': 'Reconstruct complex patterns from short-term memory.', 'icon': '🛡️', 'color': '#3b82f6'},
    'vision': {'title': 'Peripheral Hunter', 'desc': 'Expand your field of view and track multiple targets.', 'icon': '👁️', 'color': '#10b981'},
    'focus': {'title': 'Focus Ascend', 'desc': 'Locate sequential targets under grid noise.', 'icon': '🎯', 'color': '#f59e0b'},
    'pattern': {'title': 'Sequence Recall', 'desc': 'Memorize and repeat lengthening sequences.', 'icon': '🧬', 'color': '#8b5cf6'},
    'decision': {'title': 'Decision Rush', 'desc': 'Make rapid, accurate binary choices under pressure.', 'icon': '⚖️', 'color': '#06b6d4'}
}

# ==========================================
# VIEW ROUTES
# ==========================================

@dashboard.route('/')
def index():
    return render_template('dashboard/index.html')

@dashboard.route('/articles')
def articles():
    return render_template('dashboard/articles.html', 
                           articles=ARTICLES_DATA, 
                           collections=COLLECTIONS_DATA,
                           paths=PATHS_DATA,
                           total_count=142)

@dashboard.route('/articles/read/<article_id>')
def read_article(article_id):
    article = next((item for item in ARTICLES_DATA if item["id"] == article_id), None)
    if not article:
        abort(404)
    related = [a for a in ARTICLES_DATA if a['category'] == article['category'] and a['id'] != article['id']][:3]
    return render_template('dashboard/article_view.html', article=article, related=related)

@dashboard.route('/mentors')
def mentors():
    return render_template('dashboard/mentors.html', mentors=MENTORS_DATA)

@dashboard.route('/drills')
@login_required
def drills_hub():
    stats = {}
    for d_id in DRILLS_CONFIG.keys():
        best = db.session.query(func.max(DrillSession.score))\
            .filter_by(user_id=current_user.id, drill_id=d_id).scalar()
        stats[d_id] = best if best else 0
    return render_template('dashboard/drills_hub.html', drills=DRILLS_CONFIG, stats=stats)

@dashboard.route('/drills/play/<drill_id>')
@login_required
def play_drill(drill_id):
    if drill_id not in DRILLS_CONFIG:
        abort(404)
    config = DRILLS_CONFIG[drill_id]
    best = db.session.query(func.max(DrillSession.score))\
        .filter_by(user_id=current_user.id, drill_id=drill_id).scalar()
    return render_template('dashboard/play_drill.html', drill_id=drill_id, config=config, best_score=best if best else 0)

@dashboard.route('/training')
@login_required
def training():
    return redirect(url_for('dashboard.drills_hub'))

@dashboard.route('/ai-counselling')
def ai_counselling():
    return render_template('dashboard/ai_counselling.html')

# ==========================================
# JOURNAL API (NEW CALENDAR SYSTEM)
# ==========================================

@dashboard.route('/journal')
@login_required
def journal():
    """Renders the New Calendar Interface"""
    return render_template('dashboard/journal.html')

@dashboard.route('/api/journal/calendar', methods=['GET'])
@login_required
def get_calendar_data():
    """Fetches mood/score data for the calendar grid."""
    month_str = request.args.get('month') 
    if not month_str:
        month_str = datetime.utcnow().strftime('%Y-%m')

    entries = JournalEntry.query.filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.date.startswith(month_str)
    ).all()

    data = {}
    for e in entries:
        data[e.date] = { "mood": e.mood, "score": e.performance_score }
    
    return jsonify(data)

@dashboard.route('/api/journal/<date_str>', methods=['GET'])
@login_required
def get_entry(date_str):
    """Fetches details for the sliding panel"""
    entry = JournalEntry.query.filter_by(
        user_id=current_user.id, 
        date=date_str
    ).first()

    if entry:
        return jsonify({"exists": True, "data": entry.to_dict()})
    
    return jsonify({"exists": False})

@dashboard.route('/api/journal', methods=['POST'])
@login_required
def save_entry():
    """UPSERTs the journal entry via Sliding Panel"""
    try:
        data = request.get_json()
        date_str = data.get('date')
        
        if not date_str:
            return jsonify({"error": "Date required"}), 400

        entry = JournalEntry.query.filter_by(
            user_id=current_user.id, 
            date=date_str
        ).first()

        if not entry:
            entry = JournalEntry(user_id=current_user.id, date=date_str)
            db.session.add(entry)

        # Visuals
        entry.mood = data.get('mood')
        entry.performance_score = int(data.get('score')) if data.get('score') else None
        
        # Content
        entry.content = {
            "micro_win": data.get('micro_win', ''),
            "reflection": data.get('reflection', ''),
            "brain_dump_mode": bool(data.get('brain_dump_mode'))
        }
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({"status": "success", "data": entry.to_dict()})

    except Exception as e:
        db.session.rollback()
        print(f"JOURNAL SAVE ERROR: {e}") 
        return jsonify({"error": str(e)}), 500

@dashboard.route('/api/performance-insights')
@login_required
def get_insights():
    return jsonify({"status": "ok"})

# ==========================================
# DRILLS API
# ==========================================

@dashboard.route('/api/drills/save', methods=['POST'])
@login_required
def save_drill_session():
    data = request.get_json()
    session = DrillSession(
        user_id=current_user.id,
        drill_id=data.get('drill_id'),
        score=data.get('score'),
        accuracy=data.get('accuracy'),
        level_reached=data.get('level'),
        duration_seconds=data.get('duration'),
        meta_data=json.dumps(data.get('meta', {}))
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'status': 'success', 'id': session.id})
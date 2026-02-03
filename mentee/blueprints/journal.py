# routes/journal.py

from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from mentee import db
from mentee.models import Journal

journal_bp = Blueprint("journal", __name__)

@journal_bp.route("/dashboard/journal", methods=["GET", "POST"])
@login_required
def journal():
    selected_date_str = request.args.get("date")
    today = date.today()

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = today

    journal_entry = Journal.query.filter_by(
        user_id=current_user.id,
        entry_date=selected_date
    ).first()

    is_today = (selected_date == today)

    if request.method == "POST" and is_today:
        if not journal_entry:
            journal_entry = Journal(
                user_id=current_user.id,
                entry_date=today
            )
            db.session.add(journal_entry)

        journal_entry.performance_score = request.form.get("performance_score")
        journal_entry.went_well = request.form.get("went_well")
        journal_entry.mental_challenges = request.form.get("mental_challenges")
        journal_entry.focus_energy = request.form.get("focus_energy")
        journal_entry.lesson = request.form.get("lesson")
        journal_entry.intention = request.form.get("intention")

        db.session.commit()
        return redirect(url_for("journal.journal"))

    all_entries = Journal.query.filter_by(
        user_id=current_user.id
    ).all()

    entry_dates = [j.entry_date.isoformat() for j in all_entries]

    return render_template(
        "journal.html",
        journal=journal_entry,
        selected_date=selected_date,
        today=today,
        is_today=is_today,
        entry_dates=entry_dates
    )

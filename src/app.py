from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask import send_from_directory
from datetime import timedelta
import random

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "change-this-to-a-secure-random-key"  # replace in prod
app.permanent_session_lifetime = timedelta(days=7)

QUESTION_BANK = [
    {
        "id": 1,
        "category": "password",
        "prompt": "Which password is the strongest?",
        "options": ["12345", "mypassword", "Tr0ub4dor&3", "ilovecats"],
        "answer_index": 2,
        "hint": "Strong passwords combine upper/lower letters, numbers and symbols, and are not dictionary words."
    },
    {
        "id": 2,
        "category": "phishing",
        "prompt": "You receive an email: 'Your bank account is locked. Click here to unlock.' The sender is 'support@bank-secure.com'. What do you do?",
        "options": ["Click the link and log in", "Ignore and report as phishing", "Reply asking for more info", "Forward to a friend"],
        "answer_index": 1,
        "hint": "Phishing emails pressure you to click links or disclose credentials. Verify via official channels."
    },
    {
        "id": 3,
        "category": "social",
        "prompt": "A colleague asks for your login to a shared tool for convenience. How should you respond?",
        "options": ["Give them your password", "Create a guest account or request access properly", "Share a screenshot of your dashboard", "Tell them the password over chat"],
        "answer_index": 1,
        "hint": "Never share credentials. Use proper access management or ask IT."
    },
    {
        "id": 4,
        "category": "link",
        "prompt": "Which URL looks suspicious?",
        "options": ["https://paypal.com", "https://secure-paypal.com.login.verify.info", "https://github.com", "https://google.com"],
        "answer_index": 1,
        "hint": "Look for domain authority and weird subdomains or extra sections that impersonate a site."
    }
]

XP_PER_CORRECT = 10
LEVEL_XP = 50  # XP needed per level
STREAK_BONUS = 10  # bonus XP on 3-correct streak

def init_session():
    session.permanent = True
    if "xp" not in session:
        session["xp"] = 0
        session["level"] = 1
        session["streak"] = 0
        session["badges"] = []
        session["answered"] = {}  # question_id -> attempts/correct
    # keep session changes
    session.modified = True

@app.route("/")
def landing():
    init_session()
    return render_template("landingPage.html")

@app.route("/index")
def index():
    init_session()
    return render_template("index.html")

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/api/questions")
def questions():
    # simple: return all questions in random order
    init_session()
    q = QUESTION_BANK.copy()
    random.shuffle(q)
    # Hide answer key
    for item in q:
        item_copy = item.copy()
    return jsonify(q)

@app.route("/api/answer", methods=["POST"])
def answer():
    init_session()
    data = request.json
    qid = data.get("question_id")
    selected = data.get("selected_index")
    # find question
    q = next((x for x in QUESTION_BANK if x["id"] == qid), None)
    if not q:
        return jsonify({"error": "Invalid question id"}), 400

    correct = (selected == q["answer_index"])
    xp_gained = 0
    badge_unlocked = None

    # update answered attempts
    answered = session.get("answered", {})
    attempts = answered.get(str(qid), {"tries": 0, "correct": False})
    attempts["tries"] += 1
    if correct:
        attempts["correct"] = True
    answered[str(qid)] = attempts
    session["answered"] = answered

    if correct:
        session["streak"] = session.get("streak", 0) + 1
        xp_gained += XP_PER_CORRECT
        # streak bonus
        if session["streak"] > 0 and session["streak"] % 3 == 0:
            xp_gained += STREAK_BONUS
    else:
        session["streak"] = 0

    # update XP & level
    session["xp"] = session.get("xp", 0) + xp_gained
    prev_level = session.get("level", 1)
    new_level = prev_level + (session["xp"] // LEVEL_XP) - ((prev_level - 1) if prev_level>1 else 0)
    # simpler: recompute from xp:
    new_level = (session["xp"] // LEVEL_XP) + 1
    session["level"] = new_level

    # Check for a sample badge: Password Master if answered 3 password questions correctly (we keep it simple)
    if q["category"] == "password" and correct:
        # count correct password answers
        count = 0
        for k, v in session["answered"].items():
            qobj = next((x for x in QUESTION_BANK if str(x["id"]) == k), None)
            if qobj and qobj["category"] == "password" and v.get("correct"):
                count += 1
        if count >= 3 and "Password Master" not in session["badges"]:
            session["badges"].append("Password Master")
            badge_unlocked = "Password Master"

    session.modified = True

    response = {
        "correct": correct,
        "hint": q.get("hint"),
        "xp_gained": xp_gained,
        "xp_total": session["xp"],
        "level": session["level"],
        "streak": session["streak"],
        "badges": session["badges"],
        "badge_unlocked": badge_unlocked
    }
    return jsonify(response)

@app.route("/api/status")
def status():
    init_session()
    return jsonify({
        "xp": session.get("xp", 0),
        "level": session.get("level", 1),
        "streak": session.get("streak", 0),
        "badges": session.get("badges", [])
    })

if __name__ == "__main__":
    app.run(debug=True)
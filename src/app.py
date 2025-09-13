from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask import send_from_directory
from datetime import timedelta
import random

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "change-this-to-a-secure-random-key" 
app.permanent_session_lifetime = timedelta(days=7)

QUESTION_BANK = [
    {
    "id": 1,
    "category": "password",
    "prompt": "Which password is the strongest?",
    "options": ["12345", "mypassword", "Tr0ub4dor&3", "ilovecats"],
    "answer_index": 2,
    "hint": "Strong passwords mix upper/lowercase, numbers, symbols, and avoid dictionary words."
    },
    {
    "id": 2,
    "category": "password",
    "prompt": "What is the best practice for managing many complex passwords?",
    "options": [
        "Write them all down on a sticky note",
        "Reuse one strong password everywhere",
        "Use a password manager",
        "Save them in your email drafts"
    ],
    "answer_index": 2,
    "hint": "Password managers securely store and generate unique passwords."
    },
    {
    "id": 3,
    "category": "password",
    "prompt": "What is two-factor authentication (2FA)?",
    "options": [
        "Logging in with two different passwords",
        "Using a password plus another form of verification (like SMS code or app)",
        "Using a fingerprint only",
        "Asking a friend to confirm your login"
    ],
    "answer_index": 1,
    "hint": "2FA combines something you know (password) with something you have (code/device)."
    },
    {
    "id": 4,
    "category": "password",
    "prompt": "Which is the safest way to store backup recovery codes?",
    "options": [
        "Screenshot and upload to social media",
        "Save in plain text on desktop",
        "Write down and store securely offline",
        "Email them to yourself"
    ],
    "answer_index": 2,
    "hint": "Recovery codes should be kept offline in a secure place."
    },
    {
    "id": 5,
    "category": "phishing",
    "prompt": "You receive an email: 'Your bank account is locked. Click here to unlock.' The sender is 'support@bank-secure.com'. What do you do?",
    "options": [
        "Click the link and log in",
        "Ignore and report as phishing",
        "Reply asking for more info",
        "Forward to a friend"
    ],
    "answer_index": 1,
    "hint": "Phishing emails pressure you to click links or give credentials."
    },
    {
    "id": 6,
    "category": "phishing",
    "prompt": "Which is a common sign of a phishing email?",
    "options": [
        "Personalized greeting using your full name",
        "Poor spelling/grammar and urgent threats",
        "Email from your known manager",
        "A company newsletter you subscribed to"
    ],
    "answer_index": 1,
    "hint": "Look for red flags like bad grammar, urgency, and suspicious links."
    },
    {
    "id": 7,
    "category": "phishing",
    "prompt": "You hover over a link in an email, and the URL is 'http://login.paypa1.com/'. What should you do?",
    "options": [
        "Click it quickly before it expires",
        "Trust it since it has 'paypal' in the name",
        "Do not click and report as suspicious",
        "Forward to a coworker to test it"
    ],
    "answer_index": 2,
    "hint": "Look carefully: 'paypa1' uses a number '1' to mimic 'l'."
    },
    {
    "id": 8,
    "category": "phishing",
    "prompt": "Which action is safest if you suspect a phishing attempt?",
    "options": [
        "Delete the email without reporting",
        "Verify directly with the organization using official contact info",
        "Reply asking if it is legitimate",
        "Click and see if the page looks real"
    ],
    "answer_index": 1,
    "hint": "Always verify via official websites or phone numbers, never via the suspicious message."
    },
    {
    "id": 9,
    "category": "social",
    "prompt": "A colleague asks for your login to a shared tool for convenience. How should you respond?",
    "options": [
        "Give them your password",
        "Create a guest account or request proper access",
        "Share a screenshot of your dashboard",
        "Tell them the password over chat"
    ],
    "answer_index": 1,
    "hint": "Never share credentials. Use proper access management."
    },
    {
    "id": 10,
    "category": "social",
    "prompt": "An attacker pretends to be IT support and calls asking for your password. What is the correct action?",
    "options": [
        "Provide the password to help IT",
        "Hang up and report the incident",
        "Ask them to email you instead",
        "Tell them part of the password"
    ],
    "answer_index": 1,
    "hint": "Legitimate IT staff will never ask for your password."
    },
    {
    "id": 11,
    "category": "social",
    "prompt": "Why should you be careful about oversharing personal info on social media?",
    "options": [
        "Hackers may use details for security questions or scams",
        "Your friends might get jealous",
        "It reduces the number of likes you get",
        "It makes ads less personalized"
    ],
    "answer_index": 0,
    "hint": "Attackers can use birthdays, pets' names, etc., to guess passwords or answers."
    },
    {
    "id": 12,
    "category": "social",
    "prompt": "What is 'shoulder surfing' in cybersecurity?",
    "options": [
        "Spying over someone’s shoulder to steal sensitive info",
        "Looking at someone’s social media profile",
        "Surfing the web on public Wi-Fi",
        "A phishing website disguised as social media"
    ],
    "answer_index": 0,
    "hint": "Shoulder surfing means visually stealing information, like watching you type a password."
    }

]

LEVEL_CATEGORIES = [
    "password",
    "phishing",
    "social"
]
LEVEL_XP_THRESHOLD = 30  # XP needed to pass a level


XP_PER_CORRECT = 10
LEVEL_XP = 30  # XP needed per level
STREAK_BONUS = 10  # bonus XP on 3-correct streak

def init_session():
    session.permanent = True
    if "xp" not in session:
        session["xp"] = 0
        session["level"] = 1
        session["answered"] = {}  # question_id -> attempts/correct
        session["level_xp"] = 0  # XP earned in current level
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
    init_session()
    level = session.get("level", 1)
    # Clamp level to available categories
    category = LEVEL_CATEGORIES[min(level-1, len(LEVEL_CATEGORIES)-1)]
    q = [item for item in QUESTION_BANK if item["category"] == category]
    random.shuffle(q)
    return jsonify(q)

@app.route("/api/answer", methods=["POST"])
def answer():
    init_session()
    data = request.json
    qid = data.get("question_id")
    selected = data.get("selected_index")
    q = next((x for x in QUESTION_BANK if x["id"] == qid), None)
    if not q:
        return jsonify({"error": "Invalid question id"}), 400

    correct = (selected == q["answer_index"])
    xp_gained = XP_PER_CORRECT if correct else 0

    # update answered attempts
    answered = session.get("answered", {})
    attempts = answered.get(str(qid), {"tries": 0, "correct": False})
    attempts["tries"] += 1
    if correct:
        attempts["correct"] = True
    answered[str(qid)] = attempts
    session["answered"] = answered

    # Only count XP for questions in current level's category
    level = session.get("level", 1)
    category = LEVEL_CATEGORIES[min(level-1, len(LEVEL_CATEGORIES)-1)]
    if q["category"] == category:
        session["level_xp"] = session.get("level_xp", 0) + xp_gained
        session["xp"] = session.get("xp", 0) + xp_gained

    # Level progression logic
    level_completed = False
    game_completed = False
    if session.get("level_xp", 0) >= LEVEL_XP_THRESHOLD:
        session["level"] = min(session["level"] + 1, len(LEVEL_CATEGORIES))
        session["level_xp"] = 0
        level_completed = True

    if session.get("xp", 0) >= LEVEL_XP_THRESHOLD * len(LEVEL_CATEGORIES):
        game_completed = True

     # --- XP fallback logic on level fail ---
    if data.get("level_failed"):
        # Set XP to the threshold for the start of this level
        session["xp"] = LEVEL_XP_THRESHOLD * (level - 1)
        session["level_xp"] = 0

    session.modified = True

    response = {
        "correct": correct,
        "hint": q.get("hint"),
        "xp_gained": xp_gained,
        "xp_total": session.get("xp", 0),
        "level": session["level"],
        "level_xp": session.get("level_xp", 0),
        "level_completed": level_completed,
        "game_completed": game_completed,
        "category": category
    }
    return jsonify(response)

@app.route("/api/status")
def status():
    init_session()
    return jsonify({
        "xp": session.get("xp", 0),
        "level": session.get("level", 1),
        "level_xp": session.get("level_xp", 0)
    })
@app.route("/end")
def end():
    return render_template("end.html")

if __name__ == "__main__":
    app.run(debug=True)
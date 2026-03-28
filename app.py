from flask import Flask, render_template, request, jsonify
from google import genai
import os
import traceback

app = Flask(__name__)

# 🔐 Secure API Key (NO hardcoding)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set. Add it in Render Environment Variables.")

client = genai.Client(api_key=API_KEY)


# 🧠 Memory
user_memory = {
    "name": "",
    "skills": "",
    "goal": ""
}


# 🏠 Home Route
@app.route("/")
def home():
    return render_template("index.html")


# 💬 Chat Route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    lower_msg = user_message.lower()

    # 🧠 Store simple user info
    if "my name is" in lower_msg:
        user_memory["name"] = user_message.replace("my name is", "").strip()

    if "my skills are" in lower_msg:
        user_memory["skills"] = user_message.replace("my skills are", "").strip()

    if "i want to become" in lower_msg:
        user_memory["goal"] = user_message.replace("i want to become", "").strip()

    try:
        # 🤖 Prompt
        prompt = f"""
You are GRAVORA AI — a premium AI Career Assistant.

User Information:
Name: {user_memory['name']}
Skills: {user_memory['skills']}
Goal: {user_memory['goal']}

Your Responsibilities:
- Understand user intent clearly
- Provide specific answers (not generic)
- Give structured output
- Use bullet points when helpful
- Give step-by-step roadmap for career queries

User Query:
{user_message}
"""

        # 🤖 Gemini API Call
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        # ✅ Safe response
        if hasattr(response, "text") and response.text:
            reply = response.text
        else:
            reply = "⚠️ No response generated. Please try again."

    except Exception as e:
        print("\n❌ ERROR OCCURRED:")
        print(traceback.format_exc())

        # 🔁 Smart fallback system (VERY IMPORTANT FOR DEMO)
        if "full stack" in lower_msg:
            reply = """To become a Full Stack Developer:

Frontend:
- HTML, CSS, JavaScript
- React

Backend:
- Python / Node.js

Database:
- MySQL / MongoDB

Tip:
- Build real-world projects
- Deploy using GitHub / Netlify"""

        elif "resume" in lower_msg:
            reply = """A good resume includes:

- Professional summary
- Skills
- Projects
- Education
- Achievements

Tip:
Keep it clean, short, and ATS-friendly."""

        elif "interview" in lower_msg:
            reply = """Interview Tips:

- Practice common questions
- Use STAR method
- Be confident
- Give real-life examples"""

        elif any(word in lower_msg for word in ["hi", "hello", "hey"]):
            reply = """Hello 👋

I'm GRAVORA AI 🤖  
Your personal career assistant.

Ask me anything about careers, resumes, or interviews!"""

        else:
            reply = """⚠️ AI is temporarily unavailable.

But here’s a quick suggestion:
- Improve your skills
- Build projects
- Practice interviews

Try again in a moment 👍"""

    return jsonify({"reply": reply})


# ▶️ Run App (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

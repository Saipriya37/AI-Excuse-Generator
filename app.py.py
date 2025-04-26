import streamlit as st
import random
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
from playsound import playsound
import pyperclip  # ✅ NEW
import urllib.parse  # ✅ NEW
import datetime  # ✅ NEW
from reportlab.lib.pagesizes import letter  # ✅ NEW
from reportlab.pdfgen import canvas  # ✅ NEW
from io import BytesIO  # ✅ NEW
from PIL import Image  # ✅ NEW

# ---------- CSS Styling ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: linear-gradient(to bottom right, #f0f4f8, #dcefff);
        padding: 2rem;
        border-radius: 0px;
    }

    h1, h2, h3 {
        color: #1c1f4a;
        font-weight: 700;
    }

    .stSelectbox, .stTextInput, .stDownloadButton > button {
        border-radius: 10px !important;
    }

    .stButton > button {
        background-color: #ff3377;
        color: white;
        font-weight: bold;
        padding: 0.7rem 1.6rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: 0.3s ease-in-out;
    }

    .stButton > button:hover {
        background-color: #cc0055;
        transform: scale(1.05);
    }

    .stDownloadButton > button {
        background-color: #3366ff;
        color: white;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        border-radius: 10px;
    }

    .stDownloadButton > button:hover {
        background-color: #0044cc;
    }

    .excuse-box {
        background-color: #ffffff;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 6px solid #ff3377;
        border-radius: 10px;
        font-size: 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }

    .history-item {
        background-color: #f4f5f7;
        padding: 0.75rem;
        border-left: 5px solid #607d8b;
        border-radius: 8px;
        margin-top: 10px;
    }

    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------- Emoji Dictionary ----------
emoji_dict = {
    "Work": "💼",
    "School": "📚",
    "Health": "🩺",
    "Family": "👨‍👩‍👧‍👦",
    "Technology": "💻",
    "Transport": "🚗",
    "Weather": "🌧️",
    "Pets": "🐶",
    "Food": "🍕"
}

# ---------- Language Mapping ----------
language_codes = {
    'English': 'en',
    'Hindi': 'hi',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Spanish': 'es'
}

# ---------- Excuses ----------
excuses = {
    "Work": [
        "My computer blue-screened right before the deadline.",
        "There was a surprise fire drill and we had to evacuate."
    ],
    "School": [
        "My assignment was eaten by my dog. Classic, I know.",
        "I thought today was Sunday. Honest mistake."
    ],
    "Health": [
        "I had a sudden migraine and couldn't get out of bed.",
        "My voice is gone—I think I scared my own immune system."
    ],
    "Family": [
        "A cousin I never met showed up for an emergency reunion.",
        "I had to babysit unexpectedly. Chaos ensued."
    ],
    "Technology": [
        "My WiFi decided to take a personal day.",
        "I updated Windows… and it's still updating."
    ],
    "Transport": [
        "My cab got lost following Google Maps.",
        "There was a chicken parade on the main road. Unbelievable."
    ],
    "Weather": [
        "I got caught in a hailstorm with zero visibility.",
        "Lightning struck the transformer. Boom—no power."
    ],
    "Pets": [
        "My cat spilled coffee all over my notes.",
        "My dog chewed through the power cable again."
    ],
    "Food": [
        "Bad sushi. Never trusting discount night again.",
        "Microwaved soup exploded all over my clothes."
    ]
}

# ---------- Scenario Dictionary ----------
scenarios = {
    "Late to Class": [
        "The bus broke down and I had to walk half the way.",
        "There was an unexpected traffic jam due to a local protest.",
        "I misread the schedule and came for the wrong class."
    ],
    "Missed a Deadline": [
        "My system crashed the night before submission.",
        "I thought the deadline was tomorrow!",
        "I had a personal emergency and couldn’t focus."
    ],
    "Didn’t Attend a Meeting": [
        "I joined the wrong Zoom call and didn’t realize.",
        "I wasn’t feeling well and took a short nap—overslept.",
        "The calendar notification didn’t pop up."
    ],
    "Family Emergency": [
        "My uncle had a medical emergency and I had to help.",
        "There was a crisis at home, and I couldn’t leave.",
        "A sudden family issue required my attention urgently."
    ],
    "Health Issue": [
        "I had a bad migraine and couldn’t move out of bed.",
        "Food poisoning hit me hard last night.",
        "I had a fever and avoided going out."
    ]
}

# ---------- Apology Generator ----------
apology_templates = {
    "Formal": {
        "Work": [
            "I sincerely apologize for missing the deadline. It won't happen again.",
            "I'm sorry for the delay in attending the meeting. I understand the importance and take full responsibility.",
        ],
        "School": [
            "I apologize for not submitting the assignment on time. I'll ensure timely submissions in future.",
            "Sorry for being absent during class. I’ll catch up with the missed material as soon as possible."
        ],
        "Family": [
            "I truly apologize for not being available. Family matters are very important to me.",
            "I'm sorry for the misunderstanding earlier — I’ll make it right."
        ],
        "Health": [
            "Apologies for not informing earlier — I was unwell and couldn't respond promptly.",
            "Sorry for the lack of communication — I was recovering from a sudden illness."
        ]
    },
    "Emotional": {
        "Work": [
            "I feel terrible about missing the meeting. It wasn’t intentional, and I regret it deeply.",
            "It hurts to know I disappointed the team. Please forgive me — I’ll make it right."
        ],
        "School": [
            "I'm really sorry for not showing up today. I wish things had been different.",
            "Missing class makes me feel like I let everyone down. Please understand."
        ],
        "Family": [
            "I never meant to hurt you. Please accept my sincere apology.",
            "You mean the world to me, and I hate that I let you down."
        ],
        "Health": [
            "It’s hard to explain how bad I feel for not being there — I was physically down.",
            "My condition took over, and I hate that it caused disappointment. I'm truly sorry."
        ]
    }
}

def generate_apology(tone, context):
    return random.choice(apology_templates[tone][context])

# ---------- Enhanced Proof Templates ----------
proof_templates = {
    "Internet Issue": [
        "📡 Network log for {user_name}: Disconnected at {time}. Reconnected at {reconnect_time}.",
        "📶 ISP alert for {user_name}: Outage in {location} — Ticket #{ticket_id} confirmed at {time}."
    ],
    "Family Emergency": [
        "📅 Calendar event for {user_name}: 'Family Medical Emergency' — Blocked from {time} to {reconnect_time}.",
        "📝 Message: 'Had to rush to the hospital for an emergency. Will update you soon.' – {user_name}"
    ],
    "Medical Reason": [
        "🧾 Doctor's Note for {user_name}: 'Prescribed 2 days of rest due to high fever.' (Issued at {time})",
        "🩺 Health Status: 'Viral infection detected – advised indoor rest.' (Time: {time})"
    ],
    "System Crash": [
        "💻 Error Report: Device '{device}' crashed at {time}. Code: 0x{ticket_id}.",
        "🛠️ Auto Repair Log: Windows recovery failed at {time}. Kernel panic dump generated."
    ],
    "Transport Delay": [
        "🚦 Google Maps Log: Route to {destination} delayed by 47 minutes due to traffic at {time}.",
        "🚗 Cab app: Trip was cancelled by driver at {time} – user: {user_name}"
    ]
}

def generate_proof(proof_type, user_name, location="Hyderabad", destination="college", device="Dell XPS"):
    now = datetime.datetime.now()
    time = now.strftime("%I:%M %p")
    reconnect_time = (now + datetime.timedelta(hours=2)).strftime("%I:%M %p")
    ticket_id = random.randint(100000, 999999)
    
    template = random.choice(proof_templates[proof_type])
    return template.format(
        user_name=user_name,
        location=location,
        destination=destination,
        device=device,
        time=time,
        reconnect_time=reconnect_time,
        ticket_id=ticket_id
    )

# ---------- Excuse Ranking System ----------
def rank_excuse(excuse_text, category):
    strong_keywords = ["system", "medical", "emergency", "hospital", "doctor", "crash"]
    weak_keywords = ["mirror", "aliens", "cat", "chicken", "fridge", "abducted"]
    
    score = 0
    text_lower = excuse_text.lower()

    # Keyword-based scoring
    for word in strong_keywords:
        if word in text_lower:
            score += 2
    for word in weak_keywords:
        if word in text_lower:
            score -= 2

    # Category-based modifiers
    if category in ["Work", "Health", "Family"]:
        score += 1
    if category == "Funny":
        score -= 2

    # Normalize score
    if score >= 2:
        label = "🔥 Strong & Believable"
    elif -1 <= score < 2:
        label = "🤔 Moderately Believable"
    else:
        label = "⚠️ Risky / Funny"

    return label

# ---------- Emergency Templates ----------
emergency_calls = [
    "📞 Incoming Call: MOM — 'Come home immediately!'",
    "📞 Incoming Call: College — 'Your attendance issue has escalated!'",
    "📞 Incoming Call: Doctor — 'Test reports just came in. Call me ASAP.'"
]

emergency_texts = [
    "💬 SMS: Emergency at home. Need you urgently!",
    "💬 SMS: Hospital reports critical update. Please respond.",
    "💬 SMS: Don't ignore this. Call me right now — urgent!"
]

def get_fake_call():
    return random.choice(emergency_calls)

def get_fake_sms():
    return random.choice(emergency_texts)

# ---------- PDF Proof Generator ----------
def create_proof_pdf(proof_text, uploaded_image=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "🧾 AI-Generated Proof Document")

    # Add proof text
    c.setFont("Helvetica", 12)
    text_lines = proof_text.split("\n")
    y = height - 100
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 20

    # Add image if available
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        img_path = "/tmp/temp_proof_image.jpg"
        img.save(img_path)
        c.drawImage(img_path, 50, y - 250, width=300, height=200)

    c.save()
    buffer.seek(0)
    return buffer

# ---------- Load & Save ----------
def load_history_from_file():
    if os.path.exists("excuse_history.txt"):
        with open("excuse_history.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return []

def save_excuse_to_file(excuse_text):
    with open("excuses.txt", "a", encoding="utf-8") as f:
        f.write(excuse_text + "\n")

# ---------- Favorite Handling ----------
def load_favorites():
    if os.path.exists("favorites.txt"):
        with open("favorites.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()
    return []

def save_favorite(excuse_text):
    favorites = load_favorites()
    if excuse_text not in favorites:
        with open("favorites.txt", "a", encoding="utf-8") as f:
            f.write(excuse_text + "\n")

# ---------- Translate ----------
def translate_text(text, lang):
    if lang == "English":
        return text
    translated = GoogleTranslator(source='auto', target=language_codes[lang]).translate(text)
    return translated

# ---------- Speak Excuse ----------
def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("excuse.mp3")
        playsound("excuse.mp3")
        os.remove("excuse.mp3")
    except Exception as e:
        st.error(f"Voice playback error: {e}")

# ---------- Auto-Scheduler: Time-Based Context Mapping ----------
def get_time_based_category():
    now = datetime.datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday

    # Morning (6 AM - 10 AM)
    if 6 <= hour < 10:
        return "Transport"
    # Late Morning / Work Time
    elif 10 <= hour < 14:
        return "Work" if weekday < 5 else "Family"
    # Afternoon
    elif 14 <= hour < 17:
        return "Health" if weekday < 5 else "Pets"
    # Evening (5 PM - 9 PM)
    elif 17 <= hour < 21:
        return "Family"
    # Night
    else:
        return "Technology"

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history = load_history_from_file()

# ---------- Header ----------
st.title("🤖 AI Excuse Engine")
st.markdown("Let AI help you generate the **perfect excuse** for any situation!")

# ---------- Category ----------
category = st.selectbox("📂 Choose a category", list(emoji_dict.keys()))
st.markdown(f"### {emoji_dict[category]} {category} Excuses")

# ---------- Scenario Selection ----------
st.markdown("### 🎯 Optional: Choose a Specific Scenario")
selected_scenario = st.selectbox("Pick a situation (or leave blank for category-based excuse):",
                                 ["None"] + list(scenarios.keys()))

# ---------- Language ----------
language = st.selectbox("🗣️ Choose a language", list(language_codes.keys()))

# ---------- Generate ----------
if st.button("🎲 Generate Excuse"):
    if selected_scenario != "None":
        excuse = random.choice(scenarios[selected_scenario])
    else:
        excuse = random.choice(excuses[category])

    emoji_excuse = f"{emoji_dict[category]} {excuse}"
    
    # ✅ Avoid duplicate excuses
    if emoji_excuse not in st.session_state.history:
        st.session_state.history.append(emoji_excuse)
        save_excuse_to_file(emoji_excuse)

    translated = GoogleTranslator(source='auto', target=language_codes[language]).translate(excuse)
    st.success(translated)
    speak_text(translated, language_codes[language])
    
    # ✅ Save as Favorite
    if st.button("⭐ Save as Favorite"):
        save_favorite(translated)
        st.success("Excuse saved to Favorites!")

    # ✅ Copy to clipboard
    if st.button("📋 Copy to Clipboard"):
        pyperclip.copy(translated)
        st.success("Excuse copied to clipboard!")

    # ✅ Share via WhatsApp
    whatsapp_message = urllib.parse.quote(translated)
    whatsapp_url = f"https://wa.me/?text={whatsapp_message}"
    st.markdown(f"[📱 Share on WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

    # ✅ Send via Email
    mailto_url = f"mailto:?subject=My AI-Generated Excuse&body={urllib.parse.quote(translated)}"
    st.markdown(f"[✉️ Send via Email]({mailto_url})", unsafe_allow_html=True)

    # ✅ Audio Playback (replay manually)
    try:
        tts = gTTS(text=translated, lang=language_codes[language])
        tts.save("excuse.mp3")
        st.audio("excuse.mp3", format="audio/mp3")
    except:
        st.warning("Audio playback may not be supported on your device.")

    # ---------- Rank the excuse ----------
    ranking_label = rank_excuse(excuse, category)
    st.markdown(f"### 📊 Excuse Rating: {ranking_label}")

# ---------- Auto-Scheduler Excuse Suggester ----------
st.markdown("### ⏰ Smart Time-Based Excuse Suggestion")

if st.button("🤖 Suggest Excuse Based on Time"):
    suggested_category = get_time_based_category()
    excuse = random.choice(excuses[suggested_category])
    emoji_excuse = f"{emoji_dict[suggested_category]} {excuse}"
    st.success(f"Suggested Category: **{suggested_category}**")
    st.markdown(f"**Suggested Excuse:** {emoji_excuse}")

    # Option to speak the excuse
    selected_lang_code = language_codes[language]
    try:
        tts = gTTS(text=excuse, lang=selected_lang_code)
        tts.save("auto_suggested_excuse.mp3")
        st.audio("auto_suggested_excuse.mp3", format="audio/mp3")
    except:
        st.warning("Voice playback error.")

    # Copy to clipboard
    if st.button("📋 Copy Suggested Excuse"):
        pyperclip.copy(excuse)
        st.success("Copied to clipboard!")

# ---------- Apology Generator UI ----------
st.markdown("### 🫥 Need an Apology Instead?")

tone = st.selectbox("Choose the tone of apology", ["Formal", "Emotional"])
context = st.selectbox("Select the context", ["Work", "School", "Family", "Health"])

if st.button("🙏 Generate Apology"):
    apology = generate_apology(tone, context)
    st.info(apology)

    # ✅ Copy to Clipboard
    if st.button("📋 Copy Apology"):
        pyperclip.copy(apology)
        st.success("Apology copied to clipboard!")

    # ✅ Apology TTS
    selected_lang_code = language_codes[language]
    try:
        tts_apology = gTTS(text=apology, lang=selected_lang_code)
        tts_apology.save("apology.mp3")
        st.audio("apology.mp3", format="audio/mp3")
    except:
        st.warning("Audio playback not supported or language unavailable.")

# ---------- Proof Generator UI ----------
st.markdown("### 📄 Need to Back it Up? Generate a Mock Proof")

proof_type = st.selectbox("Select proof type", list(proof_templates.keys()))
user_name = st.text_input("Enter your name", "Ammu")
location = st.text_input("Location (optional)", "Hyderabad")
destination = st.text_input("Destination (if transport related)", "college")
device = st.text_input("Device (for system errors)", "Dell XPS")

if st.button("🧾 Generate Proof"):
    proof = generate_proof(proof_type, user_name, location, destination, device)
    st.code(proof, language="markdown")

    if st.button("📋 Copy Proof"):
        pyperclip.copy(proof)
        st.success("Proof copied to clipboard!")

    # ✅ Generate PDF
    if st.button("📄 Download Proof as PDF"):
        pdf_buffer = create_proof_pdf(proof)
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name="proof_document.pdf",
            mime="application/pdf"
        )

# ---------- Emergency Call & Text Simulator ----------
st.markdown("### 🚨 Trigger Emergency Call or Text")

if st.button("📞 Simulate Call"):
    call_msg = get_fake_call()
    st.warning(call_msg)
    st.audio("https://www.soundjay.com/button/sounds/beep-07.mp3")  # Simulated ringtone

if st.button("💬 Simulate Text"):
    sms_msg = get_fake_sms()
    st.info(sms_msg)

    # Optional copy
    if st.button("📋 Copy SMS"):
        pyperclip.copy(sms_msg)
        st.success("SMS message copied!")

# ---------- Export to PDF ----------
if 'proof' in locals():  # only show if proof was generated
    st.markdown("### 📥 Export Your Proof as PDF")

    if st.button("⬇️ Download PDF"):
        pdf_buffer = create_proof_pdf(proof, uploaded_image)
        st.download_button(
            label="Download AI-Proof.pdf",
            data=pdf_buffer,
            file_name="AI_Excuse_Proof.pdf",
            mime="application/pdf"
        )

# ---------- Upload Proof Image ----------
st.markdown("### 🖼️ Or Upload a Custom Proof Image")

uploaded_image = st.file_uploader("Upload a screenshot or proof image (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_image is not None:
    st.image(uploaded_image, caption="Your Uploaded Proof", use_column_width=True)
    st.success("Image uploaded successfully!")

# ---------- History ----------
if st.session_state.history:
    st.markdown("### 📜 Excuse History")
    for i, item in enumerate(reversed(st.session_state.history), 1):
        st.write(f"{i}. {item}")

    st.download_button(
        label="⬇️ Download History as TXT",
        data="\n".join(st.session_state.history),
        file_name="excuse_history.txt",
        mime="text/plain"
    )

# ---------- Favorites Display ----------
favorites = load_favorites()
if favorites:
    st.markdown("### ⭐ Your Favorite Excuses")
    for i, fav in enumerate(reversed(favorites), 1):
        st.write(f"{i}. {fav}")
import random
import os
import csv
from datetime import datetime

# Unified Excuse Categories
EXCUSES = {
    "College": [
        "My assignment file got corrupted.",
        "I had a surprise test I forgot to prepare for.",
        "My bus broke down on the way to college.",
        "My roommate used my notes to clean up a spill.",
        "The library's ghost scared me away from my assignment.",
        "I joined the wrong Zoom class and stayed polite the whole time."
    ],
    "Work": [
        "I was stuck in a client meeting.",
        "There was a system outage at my office.",
        "My project deadline got shifted suddenly.",
        "My cat scheduled a team meeting while I was asleep.",
        "The Wi-Fi said it needed a break today.",
        "My chair rolled out from under me when I tried to log in."
    ],
    "Exams": [
        "My brain refused to cooperate with formulas today.",
        "I revised the wrong subject but gained deep wisdom.",
        "I misunderstood the syllabus... again.",
        "I forgot to set an alarm and missed the exam.",
        "My pen ran out of ink mid-answer."
    ],
    "Personal": [
        "I wasn't feeling mentally well.",
        "There was a family emergency.",
        "I had to visit the doctor unexpectedly.",
        "I lost track of time while journaling.",
        "I needed a digital detox for mental health."
    ],
    "Funny": [
        "My cat knocked over my Wi-Fi router!",
        "I was abducted by aliens for 2 hours.",
        "I time-traveled accidentally and just got back.",
        "My fridge started singing and I had to record it.",
        "I had a debate with my mirror on confidence."
    ]
}

# Category emojis
CATEGORY_EMOJIS = {
    "College": "🎓",
    "Work": "💼",
    "Exams": "📝",
    "Personal": "🧘‍♀️",
    "Funny": "😂"
}

# Generate an excuse from a category
def generate_excuse(category):
    return random.choice(EXCUSES.get(category, ["Oops! No excuse available."]))

# Get the emoji for a given category
def get_emoji(category):
    return CATEGORY_EMOJIS.get(category, "💡")

# Get the current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Save excuse to CSV with optional custom input
def save_excuse_to_csv(category, excuse, timestamp, custom_input=None):
    filepath = os.path.join("data", "excuse_history.csv")
    file_exists = os.path.exists(filepath)

    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Category", "Excuse", "User_Input"])
        writer.writerow([timestamp, category, excuse, custom_input or ""])

# Load past excuses
def load_excuse_history():
    filepath = os.path.join("data", "excuse_history.csv")
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)  # returns list of dicts now

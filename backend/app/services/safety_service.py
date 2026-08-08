"""
safety_service.py

Reuses the exact educational content that lived in the original utils.py:
cyber laws, helplines, safety tips, simulated social posts, toxic-word
highlighting, and the detox/safe-rewrite helper. No content was invented
or replaced - only relocated behind a service layer.
"""
import random
import re
from typing import Dict, List

CYBER_HELPLINES: List[Dict] = [
    {
        "agency": "National Cyber Crime Helpline",
        "contact": "1930 (Toll-Free, 24x7)",
        "desc": "The primary national helpline operated by the Ministry of Home Affairs to report online financial frauds and general cybercrimes immediately.",
        "website": "https://cybercrime.gov.in"
    },
    {
        "agency": "Childline India",
        "contact": "1098 (Toll-Free, 24x7)",
        "desc": "A dedicated emergency phone service for children in distress. Perfect for students facing severe online harassment, extortion, or bullying.",
        "website": "https://www.childlineindia.org"
    },
    {
        "agency": "National Commission for Women (NCW)",
        "contact": "011-26944880 or 7827170170",
        "desc": "Helpline for women facing cyberstalking, harassment, morphing of photos, or online threats.",
        "website": "http://ncw.nic.in"
    }
]

CYBER_LAWS: List[Dict] = [
    {
        "act": "Section 66E, IT Act 2000",
        "name": "Punishment for Violation of Privacy",
        "desc": "Applies if someone intentionally captures, publishes, or transmits the image of a private area of any person without consent. Penalty: Up to 3 years imprisonment or fine up to Rs. 2 Lakhs.",
        "relevance": "Directly applies to cases where private images/videos of students are shared online without consent (Doxxing/Morphing)."
    },
    {
        "act": "Section 67, IT Act 2000",
        "name": "Publishing Obscene Material in Electronic Form",
        "desc": "Punishes publishing or transmitting sexually explicit, obscene, or highly inappropriate content online. Penalty: Up to 3 years jail (first conviction) and Rs. 5 Lakhs fine.",
        "relevance": "Applies to sharing offensive or vulgar text, photos, or memes intended to harass a classmate."
    },
    {
        "act": "Section 507, Indian Penal Code (IPC)",
        "name": "Criminal Intimidation by Anonymous Communication",
        "desc": "If someone threatens another person anonymously online or using a fake profile. Penalty: Up to 2 additional years in jail.",
        "relevance": "Covers cyberbullying threats sent from anonymous/fake Instagram or WhatsApp accounts."
    },
    {
        "act": "Section 354D, IPC",
        "name": "Stalking (including Cyberstalking)",
        "desc": "Applies when a person repeatedly monitors a person's internet usage or attempts to contact them online despite clear disinterest. Penalty: Up to 3 years imprisonment.",
        "relevance": "Covers cases where a student is repeatedly followed, spammed, or harassed across multiple social networks."
    },
    {
        "act": "Section 499/500, IPC",
        "name": "Defamation (Online)",
        "desc": "If someone posts false rumors, memes, or text statements online with the sole intention of damaging a student's reputation. Penalty: Up to 2 years in jail or fine.",
        "relevance": "Directly targets creating fake accounts or posts to spread humiliating rumors about someone."
    }
]

SAFETY_TIPS: List[Dict] = [
    {
        "title": "Don't Respond or Retaliate",
        "desc": "Bullies seek a reaction. Responding often escalates the situation and feeds their behavior. Keep calm and do not text back in anger."
    },
    {
        "title": "Save the Evidence",
        "desc": "Always take screenshots of the offensive comments, direct messages, chat threads, or fake profiles. This acts as concrete proof when reporting."
    },
    {
        "title": "Block and Report",
        "desc": "Use the built-in safety tools of apps (Instagram, Snapchat, YouTube, WhatsApp) to immediately block the bully and report their post/account."
    },
    {
        "title": "Talk to a Trusted Adult",
        "desc": "Never suffer in silence. Share what you are experiencing with your parents, your class teacher, school counselor, or an adult you trust."
    },
    {
        "title": "Maintain Privacy Hygiene",
        "desc": "Keep your social media accounts private. Never share passwords, personal phone numbers, or addresses in public forums or with casual online friends."
    }
]

SIMULATED_POSTS: List[Dict] = [
    {
        "platform": "Instagram", "username": "daily_learner_99",
        "content": "Had an amazing weekend planting trees in our colony! It felt so good to give back to nature. 🌳✨ #GoGreen #EcoClub",
        "time": "2 hours ago", "avatar": "🌱"
    },
    {
        "platform": "Twitter", "username": "anonymous_troll_04",
        "content": "You look like a complete monster in your class video, go get some plastic surgery ugly loser. 🤮",
        "time": "15 mins ago", "avatar": "💀"
    },
    {
        "platform": "Instagram", "username": "tech_kid_rohit",
        "content": "Just completed learning Python in class! Working on a new machine learning project using Scikit-Learn. Exciting times! 💻🔥",
        "time": "4 hours ago", "avatar": "💻"
    },
    {
        "platform": "Twitter", "username": "bully_destroyer_x",
        "content": "If you dare come to school tomorrow, I will find you after class and personally break your phone. You better watch your back! 👊",
        "time": "5 mins ago", "avatar": "🔥"
    },
    {
        "platform": "Instagram", "username": "new_girl_ananya",
        "content": "It is my first week at the new school. It is hard to adapt, but I made some very sweet friends today in the computer science lab. 😊",
        "time": "1 hour ago", "avatar": "✨"
    },
    {
        "platform": "Twitter", "username": "outsider_hater_11",
        "content": "Go back to where you came from, we don't want you here in our school. You are an absolute waste of space. 😡",
        "time": "30 mins ago", "avatar": "🚫"
    },
    {
        "platform": "Instagram", "username": "class_captain_amit",
        "content": "Reminder to all Class XII-A students: Please submit your AI Capstone project report by Friday morning. Good luck everyone! 📝",
        "time": "5 hours ago", "avatar": "🎓"
    }
]


def highlight_toxic_words(text: str, matched_words: List[str]) -> str:
    """Identical to the original utils.highlight_toxic_words()."""
    if not matched_words:
        return text
    highlighted_text = text
    words = sorted(matched_words, key=len, reverse=True)
    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        highlighted_text = pattern.sub(f"**:{word}:**", highlighted_text)
    return highlighted_text


def detoxify_text(text: str, matched_words: List[str]) -> str:
    """Identical to the original utils.detoxify_text()."""
    if not matched_words:
        return text
    detoxified_text = text
    words = sorted(matched_words, key=len, reverse=True)
    replacements = ["🌸[kindness]🌸", "✨[friendly]✨", "🕊️[peace]🕊️", "💖[love]💖"]
    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        detoxified_text = pattern.sub(random.choice(replacements), detoxified_text)
    return detoxified_text

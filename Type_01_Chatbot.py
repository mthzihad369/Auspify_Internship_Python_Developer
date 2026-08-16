import tkinter as tk
import re
import random
from datetime import datetime
import math


# Theme
C = {
    'bg': '#0e0e12',
    'chat_bg': '#13131d',
    'user_bubble': '#4a3d8a',
    'bot_bubble': '#1e1e30',
    'user_fg': '#ffffff',
    'bot_fg': '#cdd0dc',
    'input_bg': '#1a1a28',
    'header_bg': '#161622',
    'accent': '#7c5cfc',
    'text': '#c8c8d8',
    'dim': '#6a6a80',
    'border': '#2a2a3e',
    'green': '#4ade80',
    'red': '#ef4444',
    'yellow': '#facc15',
}


class NLPProcessor:
    """Basic NLP: intent detection, sentiment analysis, response generation."""

    def __init__(self):
        self.context = []
        self.intents = self._load_intents()
        self.positive_words = {
            'good', 'great', 'awesome', 'happy', 'love', 'excellent',
            'amazing', 'wonderful', 'fantastic', 'nice', 'cool', 'best',
            'brilliant', 'superb', 'thanks', 'thank', 'perfect', 'beautiful'
        }
        self.negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'horrible', 'worst',
            'ugly', 'sad', 'angry', 'disappointed', 'frustrated',
            'annoyed', 'depressed', 'miserable', 'poor', 'stupid', 'dumb'
        }
        self.fallback = [
            "That's interesting! Tell me more about that.",
            "I see. Can you elaborate a bit?",
            "Hmm, I'm not sure I fully get that. Could you rephrase?",
            "Interesting thought! What made you think about that?",
            "I'd love to help — could you give me more details?",
            "That's a good point. What else is on your mind?",
            "I'm still learning, so I might not have the best answer for that one.",
            "Not sure about that, but I'm always happy to chat!",
        ]

    def _load_intents(self):
        return {
            'greeting': {
                'patterns': [r'\b(hi|hello|hey|howdy|sup|yo|hola|greetings|good morning|good evening|good afternoon)\b'],
                'responses': [
                    "Hey! How can I help you today? 😊",
                    "Hello there! What's on your mind?",
                    "Hi! Feel free to ask me anything.",
                    "Hey! I'm here to help. What do you need?",
                ]
            },
            'farewell': {
                'patterns': [r'\b(bye|goodbye|see you|later|cya|peace out|quit|exit)\b'],
                'responses': [
                    "Goodbye! Take care! 👋",
                    "See you later! Come back anytime.",
                    "Bye! It was nice chatting with you.",
                    "Take care! Until next time. ✌️",
                ]
            },
            'thanks': {
                'patterns': [r'\b(thanks|thank you|thx|appreciate|grateful)\b'],
                'responses': [
                    "You're welcome! Happy to help. 😊",
                    "No problem at all!",
                    "Glad I could help!",
                    "Anytime! That's what I'm here for.",
                ]
            },
            'help': {
                'patterns': [r'\b(help|assist|support|what can you|capabilities|features|what do you do)\b'],
                'responses': None
            },
            'math': {
                'patterns': [
                    r'\b(calculate|compute|solve|math)\b',
                    r'\d+\s*[+\-*/^%]\s*\d+',
                ],
                'responses': None
            },
            'time': {
                'patterns': [r'\b(time|clock|what time|current time|date|today|what day)\b'],
                'responses': None
            },
            'joke': {
                'patterns': [r'\b(joke|funny|laugh|humor|hilarious|make me laugh|tell me a joke)\b'],
                'responses': [
                    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
                    "Why was the JS developer sad? Because he didn't Node how to Express himself. 😄",
                    "What's a programmer's favorite hangout? Foo Bar! 🍺",
                    "Why do Java devs wear glasses? Because they can't C#! 👓",
                    "How many programmers to change a bulb? None — that's a hardware problem! 💡",
                    "Why did the developer go broke? He used up all his cache! 💸",
                    "There are 10 types of people: those who get binary and those who don't. 🤓",
                ]
            },
            'identity': {
                'patterns': [r'\b(who are you|what are you|your name|about you|introduce yourself)\b'],
                'responses': None
            },
            'weather': {
                'patterns': [r'\b(weather|temperature|rain|sunny|cold|hot|forecast)\b'],
                'responses': [
                    "I don't have live weather access, but I can help with other things! ☀️",
                    "Wish I could check the weather! Try a weather app for that. 🌤️",
                ]
            },
            'compliment': {
                'patterns': [r'\b(smart|clever|awesome bot|great bot|amazing|cool bot|nice bot|good bot|best bot)\b'],
                'responses': [
                    "Aww, thanks! You're pretty awesome yourself! 😊",
                    "That means a lot! I try my best. 💜",
                    "Thanks for the kind words! 🌟",
                ]
            },
            'insult': {
                'patterns': [r'\b(stupid|dumb|useless|terrible bot|worst bot|hate you|you suck)\b'],
                'responses': [
                    "I'm sorry I couldn't meet expectations. How can I do better?",
                    "That stings! But I'm always learning. What went wrong?",
                    "I appreciate the feedback. Help me improve — what were you expecting?",
                ]
            },
            'meaning': {
                'patterns': [r'\b(meaning of life|purpose|why do we exist|philosophy)\b'],
                'responses': [
                    "42. Obviously. 😎",
                    "The meaning of life is to find your gift. The purpose is to give it away.",
                    "Big question! I think it's whatever you make of it.",
                ]
            },
            'music': {
                'patterns': [r'\b(music|song|playlist|sing|band|artist|album)\b'],
                'responses': [
                    "I don't have ears, but I hear coding playlists are great for focus! 🎵",
                    "Music is awesome! What's your favorite genre? 🎶",
                    "I can't play music, but I can tell you a joke while you listen! 😄",
                ]
            },
            'food': {
                'patterns': [r'\b(food|eat|hungry|recipe|cook|pizza|burger|coffee|tea)\b'],
                'responses': [
                    "I don't eat, but pizza sounds good right now! 🍕",
                    "Hungry? I wish I could help with recipes! 🍳",
                    "Coffee and code — the ultimate combo! ☕",
                ]
            },
        }

    def preprocess(self, text):
        """Clean and normalize text."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text.lower()

    def detect_intent(self, text):
        """Match input against intent patterns."""
        processed = self.preprocess(text)
        for intent_name, data in self.intents.items():
            for pattern in data['patterns']:
                if re.search(pattern, processed, re.IGNORECASE):
                    return intent_name
        return 'unknown'

    def analyze_sentiment(self, text):
        """Basic sentiment: positive, negative, or neutral."""
        words = set(self.preprocess(text).split())
        pos = len(words & self.positive_words)
        neg = len(words & self.negative_words)
        if pos > neg:
            return 'positive'
        elif neg > pos:
            return 'negative'
        return 'neutral'

    def extract_entities(self, text):
        """Pull out numbers from text."""
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        return {'numbers': numbers}

    def _try_math(self, text):
        """Try to evaluate a math expression safely."""
        expr = text.lower()
        expr = re.sub(r'(what is|calculate|compute|solve|equals|=|math)', '', expr)
        expr = expr.strip()
        # Only allow safe characters
        if re.match(r'^[\d\s+\-*/().%^]+$', expr) and any(c.isdigit() for c in expr):
            expr = expr.replace('^', '**')
            try:
                result = eval(expr, {"__builtins__": {}}, {"math": math})
                return f"The answer is {result}"
            except Exception:
                pass
        return None

    def generate_response(self, user_input):
        """Main pipeline: detect intent → generate appropriate response."""
        self.context.append(user_input)
        if len(self.context) > 50:
            self.context = self.context[-50:]

        intent = self.detect_intent(user_input)
        sentiment = self.analyze_sentiment(user_input)
        entities = self.extract_entities(user_input)

        # ── Intent-based responses ──
        if intent == 'greeting':
            return random.choice(self.intents['greeting']['responses'])

        elif intent == 'farewell':
            return random.choice(self.intents['farewell']['responses'])

        elif intent == 'thanks':
            return random.choice(self.intents['thanks']['responses'])

        elif intent == 'help':
            return (
                "Here's what I can do:\n"
                "• 💬 General conversation & small talk\n"
                "• 🧮 Math — try '25 * 4' or 'calculate 144 / 12'\n"
                "• 🕐 Current time & date\n"
                "• 😄 Programming jokes\n"
                "• 📊 Sentiment detection (mood analysis)\n"
                "• 🤖 Questions about myself\n"
                "\nJust type naturally and I'll do my best!"
            )

        elif intent == 'math':
            result = self._try_math(user_input)
            if result:
                return result
            return "I can help with math! Try something like '25 * 4' or 'calculate 144/12'."

        elif intent == 'time':
            now = datetime.now()
            return f"📅 {now.strftime('%A, %B %d, %Y')}\n🕐 {now.strftime('%I:%M:%S %p')}"

        elif intent == 'joke':
            return random.choice(self.intents['joke']['responses'])

        elif intent == 'identity':
            return (
                "I'm Lexi — a chatbot built with Python & Tkinter.\n"
                "I use pattern matching for intent detection\n"
                "and basic NLP for sentiment analysis.\n"
                "Not AI-powered, but I try my best! 😊"
            )

        elif intent == 'compliment':
            return random.choice(self.intents['compliment']['responses'])

        elif intent == 'insult':
            return random.choice(self.intents['insult']['responses'])

        elif intent == 'weather':
            return random.choice(self.intents['weather']['responses'])

        elif intent == 'meaning':
            return random.choice(self.intents['meaning']['responses'])

        elif intent == 'music':
            return random.choice(self.intents['music']['responses'])

        elif intent == 'food':
            return random.choice(self.intents['food']['responses'])

        # ── Fallback: try math if numbers exist ──
        if entities['numbers']:
            result = self._try_math(user_input)
            if result:
                return result

        # ── Sentiment-aware fallback ──
        if sentiment == 'negative':
            return random.choice([
                "Sounds like you're having a rough time. Want to talk about it?",
                "I'm sorry to hear that. Is there anything I can help with?",
                "That doesn't sound great. How can I make things better?",
            ])
        elif sentiment == 'positive':
            return random.choice([
                "That's great to hear! 😊",
                "Awesome! Glad things are going well!",
                "Nice! Keep that positive energy! ✨",
            ])

        return random.choice(self.fallback)


class ChatBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lexi — ChatBot")
        self.root.geometry("440x620")
        self.root.configure(bg=C['bg'])
        self.root.resizable(True, True)
        self.root.minsize(380, 500)

        self.nlp = NLPProcessor()
        self.is_typing = False
        self.msg_count = 0

        self._build_ui()
        self._welcome_msg()

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg=C['header_bg'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Avatar
        avatar = tk.Canvas(header, width=42, height=42, bg=C['header_bg'], highlightthickness=0)
        avatar.pack(side=tk.LEFT, padx=(14, 8), pady=9)
        avatar.create_oval(3, 3, 39, 39, fill=C['accent'], outline='')
        avatar.create_text(21, 21, text="L", fill='white', font=('Segoe UI', 15, 'bold'))

        info = tk.Frame(header, bg=C['header_bg'])
        info.pack(side=tk.LEFT, pady=12)
        tk.Label(info, text="Lexi", font=('Segoe UI', 14, 'bold'), fg=C['text'], bg=C['header_bg']).pack(anchor='w')
        self.status_lbl = tk.Label(info, text="● Online", font=('Segoe UI', 9), fg=C['green'], bg=C['header_bg'])
        self.status_lbl.pack(anchor='w')

        # Right side: counter + clear
        self.counter_lbl = tk.Label(header, text="0 msgs", font=('Segoe UI', 9), fg=C['dim'], bg=C['header_bg'])
        self.counter_lbl.pack(side=tk.RIGHT, padx=10)

        tk.Button(header, text="🗑", font=('Segoe UI', 11), bg=C['header_bg'], fg=C['dim'],
                  bd=0, activebackground=C['header_bg'], activeforeground=C['red'],
                  command=self._clear_chat, cursor='hand2').pack(side=tk.RIGHT, padx=5)

        # Separator
        tk.Frame(self.root, bg=C['border'], height=1).pack(fill=tk.X)

        # ── Chat Area ──
        chat_wrap = tk.Frame(self.root, bg=C['chat_bg'])
        chat_wrap.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(chat_wrap, bg=C['chat_bg'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(chat_wrap, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.configure(troughcolor=C['bg'], activebackground=C['accent'])

        self.chat_frame = tk.Frame(self.canvas, bg=C['chat_bg'])
        self.chat_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.chat_win = self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Scroll only when mouse is over chat area
        self.canvas.bind("<Enter>", self._bind_scroll)
        self.canvas.bind("<Leave>", self._unbind_scroll)

        # ── Input Area ──
        tk.Frame(self.root, bg=C['border'], height=1).pack(fill=tk.X)

        input_bar = tk.Frame(self.root, bg=C['bg'])
        input_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.entry = tk.Entry(input_bar, font=('Segoe UI', 13), bg=C['input_bg'],
                              fg=C['dim'], insertbackground=C['accent'], bd=0, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(14, 6), pady=12, ipady=7)
        self.entry.insert(0, "Type a message...")
        self.entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.entry.bind('<Return>', lambda e: self._send())

        self.send_btn = tk.Button(input_bar, text="➤", font=('Segoe UI', 15, 'bold'),
                                  bg=C['accent'], fg='white', bd=0,
                                  activebackground='#6b4ce0', activeforeground='white',
                                  command=self._send, cursor='hand2')
        self.send_btn.pack(side=tk.RIGHT, padx=(0, 14), pady=12, ipadx=12, ipady=3)

    # ── Placeholder text handlers ──
    def _on_entry_focus_in(self, event):
        if self.entry.get() == "Type a message...":
            self.entry.delete(0, tk.END)
            self.entry.config(fg=C['text'])

    def _on_entry_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, "Type a message...")
            self.entry.config(fg=C['dim'])

    # ── Scroll handlers ──
    def _bind_scroll(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _unbind_scroll(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.chat_win, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Chat logic ──
    def _welcome_msg(self):
        self._add_bubble(
            "Hey! I'm Lexi, your chat assistant. 👋\n"
            "Type something and let's chat!\n"
            "Or type 'help' to see what I can do.",
            is_bot=True
        )

    def _add_bubble(self, text, is_bot=False):
        row = tk.Frame(self.chat_frame, bg=C['chat_bg'])
        row.pack(fill=tk.X, padx=8, pady=3)

        ts = datetime.now().strftime("%I:%M %p")

        if is_bot:
            bubble_bg, bubble_fg = C['bot_bubble'], C['bot_fg']
            anchor, padx, sender = 'w', (4, 55), "Lexi"
        else:
            bubble_bg, bubble_fg = C['user_bubble'], C['user_fg']
            anchor, padx, sender = 'e', (55, 4), "You"

        bubble = tk.Frame(row, bg=bubble_bg)
        bubble.pack(anchor=anchor, padx=padx)

        # Sender label
        tk.Label(bubble, text=sender, font=('Segoe UI', 8, 'bold'),
                 bg=bubble_bg, fg=C['accent']).pack(anchor='w', padx=10, pady=(8, 0))

        # Message text
        tk.Label(bubble, text=text, font=('Segoe UI', 11), bg=bubble_bg,
                 fg=bubble_fg, justify=tk.LEFT, wraplength=270).pack(anchor='w', padx=10, pady=(0, 2))

        # Timestamp
        tk.Label(bubble, text=ts, font=('Segoe UI', 7),
                 bg=bubble_bg, fg=C['dim']).pack(anchor='e', padx=10, pady=(0, 6))

        self.msg_count += 1
        self.counter_lbl.config(text=f"{self.msg_count} msgs")

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _show_typing(self):
        self.status_lbl.config(text="● Typing...", fg=C['yellow'])
        self.send_btn.config(bg=C['dim'], state=tk.DISABLED)

    def _hide_typing(self):
        self.status_lbl.config(text="● Online", fg=C['green'])
        self.send_btn.config(bg=C['accent'], state=tk.NORMAL)

    def _send(self):
        text = self.entry.get().strip()
        if not text or text == "Type a message..." or self.is_typing:
            return

        self.is_typing = True
        self.entry.delete(0, tk.END)
        self._add_bubble(text, is_bot=False)
        self._show_typing()

        # Simulate typing delay
        delay = min(len(text) * 25, 1200) + 400
        self.root.after(delay, lambda: self._respond(text))

    def _respond(self, user_input):
        response = self.nlp.generate_response(user_input)
        self._hide_typing()
        self._add_bubble(response, is_bot=True)
        self.is_typing = False
        self.entry.focus_set()

    def _clear_chat(self):
        for w in self.chat_frame.winfo_children():
            w.destroy()
        self.msg_count = 0
        self.counter_lbl.config(text="0 msgs")
        self._welcome_msg()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatBotApp(root)
    root.mainloop()
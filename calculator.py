"""
NEXUS Scientific Calculator
Task 3 (Medium) - Calculator with GUI
Built with Python + Tkinter

Features:
- Basic arithmetic: + - * / % ( )
- Scientific functions: sin, cos, tan, asin, acos, atan, log10, ln, sqrt,
  x^2, x^y, 1/x, n!, exp, pi, e, abs, +/-
- Degree / Radian mode toggle
- Memory functions: MC, MR, M+, M-
- Live expression preview + calculation history panel
- Full error handling (division by zero, invalid input, domain errors)
- Keyboard support (type numbers/operators, Enter = "=", Backspace, Esc = clear)
"""

import tkinter as tk
from tkinter import font as tkfont
import math

# ----------------------------------------------------------------------
# Theme (premium dark palette)
# ----------------------------------------------------------------------
COLOR_BG = "#0b0f1a"
COLOR_PANEL = "#121826"
COLOR_DISPLAY_BG = "#161d2e"
COLOR_BORDER = "#232c42"
COLOR_TEXT = "#e7ebf5"
COLOR_TEXT_DIM = "#8891a7"
COLOR_ACCENT = "#6c5ce7"
COLOR_ACCENT_2 = "#00d4b8"
COLOR_DANGER = "#ff5c7a"
COLOR_WARN = "#ffb347"

COLOR_BTN_NUM = "#1b2436"
COLOR_BTN_NUM_HOVER = "#242f47"
COLOR_BTN_OP = "#242b45"
COLOR_BTN_OP_HOVER = "#323b5c"
COLOR_BTN_FN = "#151c2c"
COLOR_BTN_FN_HOVER = "#1e2942"
COLOR_BTN_EQ = COLOR_ACCENT
COLOR_BTN_EQ_HOVER = "#8a7cf0"

# Safe namespaces exposed to eval() -- only math + a few helpers, no builtins.
# Two full namespaces (radians / degrees) avoid any string-surgery on the
# expression -- we just pick which set of trig functions to evaluate with.
_COMMON_NAMES = {
    "sqrt": math.sqrt,
    "log10": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e,
    "abs": abs,
    "fact": math.factorial,
}

SAFE_NAMES_RAD = {
    **_COMMON_NAMES,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
}

SAFE_NAMES_DEG = {
    **_COMMON_NAMES,
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
}


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS // Scientific Calculator")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

        self.degree_mode = True          # True = degrees, False = radians
        self.memory = 0.0
        self.expression = ""             # raw expression as typed (uses python-like tokens)
        self.display_text = tk.StringVar(value="0")
        self.history_items = []          # list of (expr, result) strings

        self._load_fonts()
        self._build_ui()
        self._bind_keys()

    # ------------------------------------------------------------------
    # Fonts
    # ------------------------------------------------------------------
    def _load_fonts(self):
        self.font_display = tkfont.Font(family="Consolas", size=30, weight="bold")
        self.font_expr = tkfont.Font(family="Consolas", size=12)
        self.font_btn = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.font_btn_small = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_brand = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.font_history = tkfont.Font(family="Consolas", size=10)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=COLOR_BG, padx=18, pady=18)
        outer.pack(fill="both", expand=True)

        # ---- Brand header ----
        header = tk.Frame(outer, bg=COLOR_BG)
        header.pack(fill="x", pady=(0, 12))
        tk.Label(
            header, text="NEXUS", font=self.font_brand, fg=COLOR_ACCENT_2, bg=COLOR_BG
        ).pack(side="left")
        tk.Label(
            header, text=" Scientific Calculator", font=self.font_brand, fg=COLOR_TEXT, bg=COLOR_BG
        ).pack(side="left")

        # ---- Main body: calculator (left) + history (right) ----
        body = tk.Frame(outer, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        calc_panel = tk.Frame(body, bg=COLOR_PANEL, padx=14, pady=14)
        calc_panel.pack(side="left", fill="both")

        self._build_display(calc_panel)
        self._build_mode_bar(calc_panel)
        self._build_keypad(calc_panel)

        self._build_history_panel(body)

    def _build_display(self, parent):
        display_frame = tk.Frame(parent, bg=COLOR_DISPLAY_BG, padx=14, pady=10)
        display_frame.pack(fill="x", pady=(0, 10))

        self.expr_label = tk.Label(
            display_frame,
            text="",
            font=self.font_expr,
            fg=COLOR_TEXT_DIM,
            bg=COLOR_DISPLAY_BG,
            anchor="e",
            justify="right",
        )
        self.expr_label.pack(fill="x")

        self.result_label = tk.Label(
            display_frame,
            textvariable=self.display_text,
            font=self.font_display,
            fg=COLOR_TEXT,
            bg=COLOR_DISPLAY_BG,
            anchor="e",
            justify="right",
        )
        self.result_label.pack(fill="x")

    def _build_mode_bar(self, parent):
        bar = tk.Frame(parent, bg=COLOR_PANEL)
        bar.pack(fill="x", pady=(0, 10))

        self.mode_btn = tk.Label(
            bar,
            text="DEG",
            font=self.font_btn_small,
            fg="#0b0f1a",
            bg=COLOR_ACCENT_2,
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.mode_btn.pack(side="left")
        self.mode_btn.bind("<Button-1>", lambda e: self.toggle_mode())

        self.mem_label = tk.Label(
            bar, text="M: 0", font=self.font_btn_small, fg=COLOR_TEXT_DIM, bg=COLOR_PANEL
        )
        self.mem_label.pack(side="right")

    def _build_keypad(self, parent):
        grid = tk.Frame(parent, bg=COLOR_PANEL)
        grid.pack()

        # (label, callback_kind, payload, style)
        # style: "fn" | "op" | "num" | "eq" | "mem"
        rows = [
            [("MC", "mem", "MC"), ("MR", "mem", "MR"), ("M+", "mem", "M+"), ("M-", "mem", "M-"), ("C", "clear_all", None), ("CE", "clear_entry", None)],
            [("sin", "func", "sin"), ("cos", "func", "cos"), ("tan", "func", "tan"), ("(", "insert", "("), (")", "insert", ")"), ("⌫", "backspace", None)],
            [("asin", "func", "asin"), ("acos", "func", "acos"), ("atan", "func", "atan"), ("x²", "square", None), ("xʸ", "insert", "**"), ("÷", "insert", "/")],
            [("log", "func", "log10"), ("ln", "func", "ln"), ("√", "func", "sqrt"), ("1/x", "reciprocal", None), ("n!", "factorial", None), ("×", "insert", "*")],
            [("π", "insert_const", "pi"), ("e", "insert_const", "e"), ("7", "digit", "7"), ("8", "digit", "8"), ("9", "digit", "9"), ("−", "insert", "-")],
            [("exp", "func", "exp"), ("|x|", "func", "abs"), ("4", "digit", "4"), ("5", "digit", "5"), ("6", "digit", "6"), ("+", "insert", "+")],
            [("%", "insert", "%"), ("±", "negate", None), ("1", "digit", "1"), ("2", "digit", "2"), ("3", "digit", "3"), ("=", "equals", None)],
            [("0", "digit_wide", "0"), (".", "digit", "."), ("=", "equals", None)],
        ]

        # We render rows[0..6] normally (6 cols) and handle the last special row separately
        for r in range(7):
            for c, (label, kind, payload) in enumerate(rows[r]):
                style = self._style_for(kind, label)
                btn = self._make_button(grid, label, style, kind, payload)
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        # Last row: 0 (span 2), ., = (span 2, tall accent)
        last = rows[7]
        btn0 = self._make_button(grid, last[0][0], self._style_for(last[0][1], last[0][0]), last[0][1], last[0][2])
        btn0.grid(row=7, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")

        btn_dot = self._make_button(grid, last[1][0], self._style_for(last[1][1], last[1][0]), last[1][1], last[1][2])
        btn_dot.grid(row=7, column=2, padx=4, pady=4, sticky="nsew")

        btn_eq = self._make_button(grid, last[2][0], self._style_for(last[2][1], last[2][0]), last[2][1], last[2][2])
        btn_eq.grid(row=7, column=3, columnspan=3, padx=4, pady=4, sticky="nsew")

        for c in range(6):
            grid.grid_columnconfigure(c, weight=1, uniform="col")
        for r in range(8):
            grid.grid_rowconfigure(r, weight=1)

    def _style_for(self, kind, label):
        if kind == "equals":
            return "eq"
        if kind in ("mem", "clear_all", "clear_entry", "backspace"):
            return "mem" if kind == "mem" else "op"
        if kind == "digit" or kind == "digit_wide":
            return "num"
        if label in ("+", "−", "×", "÷", "%"):
            return "op"
        return "fn"

    def _make_button(self, parent, label, style, kind, payload):
        colors = {
            "num": (COLOR_BTN_NUM, COLOR_BTN_NUM_HOVER, COLOR_TEXT),
            "op": (COLOR_BTN_OP, COLOR_BTN_OP_HOVER, COLOR_ACCENT_2),
            "fn": (COLOR_BTN_FN, COLOR_BTN_FN_HOVER, COLOR_TEXT_DIM),
            "eq": (COLOR_BTN_EQ, COLOR_BTN_EQ_HOVER, "#ffffff"),
            "mem": (COLOR_BTN_FN, COLOR_BTN_FN_HOVER, COLOR_WARN),
        }
        bg, hover, fg = colors[style]
        font = self.font_btn if style in ("num", "eq") else self.font_btn_small

        btn = tk.Label(
            parent,
            text=label,
            font=font,
            fg=fg,
            bg=bg,
            width=6,
            height=2,
            cursor="hand2",
        )
        btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        btn.bind("<Button-1>", lambda e, k=kind, p=payload: self.handle_action(k, p))
        return btn

    def _build_history_panel(self, parent):
        panel = tk.Frame(parent, bg=COLOR_PANEL, padx=12, pady=12, width=220)
        panel.pack(side="left", fill="y", padx=(10, 0))
        panel.pack_propagate(False)

        tk.Label(
            panel, text="HISTORY", font=self.font_btn_small, fg=COLOR_TEXT_DIM, bg=COLOR_PANEL
        ).pack(anchor="w", pady=(0, 8))

        self.history_frame = tk.Frame(panel, bg=COLOR_PANEL)
        self.history_frame.pack(fill="both", expand=True)

        clear_hist_btn = tk.Label(
            panel, text="Clear History", font=self.font_btn_small, fg=COLOR_DANGER, bg=COLOR_PANEL, cursor="hand2"
        )
        clear_hist_btn.pack(anchor="w", pady=(8, 0))
        clear_hist_btn.bind("<Button-1>", lambda e: self.clear_history())

    # ------------------------------------------------------------------
    # Keyboard bindings
    # ------------------------------------------------------------------
    def _bind_keys(self):
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Return>", lambda e: self.equals())
        self.root.bind("<KP_Enter>", lambda e: self.equals())
        self.root.bind("<BackSpace>", lambda e: self.backspace())
        self.root.bind("<Escape>", lambda e: self.clear_all())

    def _on_key(self, event):
        ch = event.char
        if ch and ch in "0123456789.+-*/()%":
            self.insert(ch)

    # ------------------------------------------------------------------
    # Core actions dispatcher
    # ------------------------------------------------------------------
    def handle_action(self, kind, payload):
        actions = {
            "digit": lambda: self.insert(payload),
            "digit_wide": lambda: self.insert(payload),
            "insert": lambda: self.insert(payload),
            "insert_const": lambda: self.insert_constant(payload),
            "func": lambda: self.insert_function(payload),
            "square": self.square,
            "reciprocal": self.reciprocal,
            "factorial": self.apply_factorial,
            "negate": self.negate,
            "clear_all": self.clear_all,
            "clear_entry": self.clear_entry,
            "backspace": self.backspace,
            "equals": self.equals,
            "mem": lambda: self.memory_action(payload),
        }
        actions[kind]()

    # ------------------------------------------------------------------
    # Expression building
    # ------------------------------------------------------------------
    def insert(self, token):
        self.expression += token
        self._refresh_expr_display()

    def insert_constant(self, name):
        self.expression += name
        self._refresh_expr_display()

    def insert_function(self, fname):
        self.expression += f"{fname}("
        self._refresh_expr_display()

    def negate(self):
        if self.expression:
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression
        self._refresh_expr_display()

    def square(self):
        self.expression += "**2"
        self._refresh_expr_display()

    def reciprocal(self):
        self.expression = f"1/({self.expression})" if self.expression else "1/(0)"
        self._refresh_expr_display()

    def apply_factorial(self):
        self.expression = f"fact({self.expression})" if self.expression else "fact(0)"
        self._refresh_expr_display()

    def backspace(self):
        self.expression = self.expression[:-1]
        self._refresh_expr_display()

    def clear_entry(self):
        self.expression = ""
        self._refresh_expr_display()

    def clear_all(self):
        self.expression = ""
        self.expr_label.config(text="")
        self.display_text.set("0")

    def clear_history(self):
        self.history_items = []
        for widget in self.history_frame.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    # Mode / memory
    # ------------------------------------------------------------------
    def toggle_mode(self):
        self.degree_mode = not self.degree_mode
        self.mode_btn.config(text="DEG" if self.degree_mode else "RAD")

    def memory_action(self, action):
        try:
            current = float(self.display_text.get())
        except ValueError:
            current = 0.0

        if action == "MC":
            self.memory = 0.0
        elif action == "MR":
            self.expression += self._format_number(self.memory)
            self._refresh_expr_display()
        elif action == "M+":
            self.memory += current
        elif action == "M-":
            self.memory -= current

        self.mem_label.config(text=f"M: {self._format_number(self.memory)}")

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def equals(self):
        raw = self.expression.strip()
        if not raw:
            return

        namespace = SAFE_NAMES_DEG if self.degree_mode else SAFE_NAMES_RAD

        try:
            result = eval(raw, {"__builtins__": {}}, namespace)
            if isinstance(result, complex):
                raise ValueError("Result is not a real number")
            formatted = self._format_number(result)
            self.display_text.set(formatted)
            self.expr_label.config(text=raw + " =")
            self._add_history(raw, formatted)
            self.expression = formatted
        except ZeroDivisionError:
            self._show_error("Cannot divide by zero")
        except ValueError as e:
            self._show_error("Invalid input")
        except (SyntaxError, TypeError, NameError, OverflowError):
            self._show_error("Invalid expression")
        except Exception:
            self._show_error("Error")

    def _format_number(self, value):
        if isinstance(value, float):
            if value == int(value) and abs(value) < 1e15:
                return str(int(value))
            return f"{value:.10g}"
        return str(value)

    def _show_error(self, message):
        self.display_text.set(message)
        self.expr_label.config(text=self.expression)
        self.expression = ""

    def _refresh_expr_display(self):
        self.expr_label.config(text=self.expression)
        self.display_text.set(self.expression if self.expression else "0")

    # ------------------------------------------------------------------
    # History panel
    # ------------------------------------------------------------------
    def _add_history(self, expr, result):
        self.history_items.append((expr, result))
        if len(self.history_items) > 8:
            self.history_items.pop(0)
            for widget in self.history_frame.winfo_children():
                widget.destroy()
            for e, r in self.history_items:
                self._render_history_row(e, r)
        else:
            self._render_history_row(expr, result)

    def _render_history_row(self, expr, result):
        row = tk.Frame(self.history_frame, bg=COLOR_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(
            row, text=expr, font=self.font_history, fg=COLOR_TEXT_DIM, bg=COLOR_PANEL, anchor="w", wraplength=190, justify="left"
        ).pack(fill="x")
        tk.Label(
            row, text=f"= {result}", font=self.font_history, fg=COLOR_ACCENT_2, bg=COLOR_PANEL, anchor="w"
        ).pack(fill="x")


def main():
    root = tk.Tk()
    ScientificCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import messagebox
import winsound # Для Windows. Залиште для крос-платформності, або замініть на бібліотеку simpleaudio для Mac/Linux.
import time

# --- Таблиці кодування (Міжнародний стандарт) ---

# Кирилиця використовує стандартизовані коди, засновані на схожості звучання/вигляду латинських літер.
CYRILLIC_MORSE_DICT = {
    'А': '.-', 'Б': '-...', 'В': '.--', 'Г': '--.', 'Д': '-..', 'Е': '.', 
    'Є': '..-..', 'Ж': '...-', 'З': '--..', 'И': '..', 'І': '..', 'Ї': '..-..',
    'Й': '.---', 'К': '-.-', 'Л': '.-..', 'М': '--', 'Н': '-.', 'О': '---', 
    'П': '.--.', 'Р': '.-.', 'С': '...', 'Т': '-', 'У': '..-', 'Ф': '..-.', 
    'Х': '....', 'Ц': '-.-.', 'Ч': '---.', 'Ш': '----', 'Щ': '--.-', 'Ь': '-..-', 
    'Ю': '..--', 'Я': '.-.-',
    # Додаємо цифри та розділові знаки
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': ' / ', '.': '.-.-.-', ',': '--..--', '?': '..-..', '!': '-.-.--'
}

LATIN_MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    # Додаємо цифри та розділові знаки
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': ' / ', '.': '.-.-.-', ',': '--..--', '?': '..-..', '!': '-.-.--'
}

# --- Налаштування мов та їх словників ---
LANGUAGES = {
    "English 🇬🇧": {"dict": LATIN_MORSE_DICT, "reverse_dict": {v: k for k, v in LATIN_MORSE_DICT.items()}, "is_morse": False},
    "Українська 🇺🇦": {"dict": CYRILLIC_MORSE_DICT, "reverse_dict": {v: k for k, v in CYRILLIC_MORSE_DICT.items()}, "is_morse": False},
    "Русский 🇷🇺": {"dict": CYRILLIC_MORSE_DICT, "reverse_dict": {v: k for k, v in CYRILLIC_MORSE_DICT.items()}, "is_morse": False},
    "Морзе 📶": {"dict": {}, "reverse_dict": {}, "is_morse": True}
}

class TranslatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Google-like Морзе-Перекладач")

        # Налаштування за замовчуванням
        self.source_lang = tk.StringVar(value="English 🇬🇧")
        self.target_lang = tk.StringVar(value="Морзе 📶")
        self.dot_duration_ms = 100  # Швидкість/тривалість звуку

        # --- Головний макет ---
        main_frame = tk.Frame(master)
        main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # --- 1. Панель керування (Control Panel) ---
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))

        # 1.1. Вибір мови-джерела (ліворуч)
        lang_options = [lang for lang in LANGUAGES]
        self.source_menu = tk.OptionMenu(control_frame, self.source_lang, *lang_options)
        self.source_menu.config(width=15)
        self.source_menu.pack(side=tk.LEFT, padx=5)

        # 1.2. Кнопка перемикання (центр)
        self.swap_btn = tk.Button(control_frame, text="⇆", command=self.swap_languages)
        self.swap_btn.pack(side=tk.LEFT, padx=5)

        # 1.3. Вибір мови-цілі (праворуч)
        self.target_menu = tk.OptionMenu(control_frame, self.target_lang, *lang_options)
        self.target_menu.config(width=15)
        self.target_menu.pack(side=tk.LEFT, padx=5)

        # 1.4. Кнопка "Перекласти"
        self.translate_btn = tk.Button(
            control_frame, text="Перекласти", command=self.translate_text, 
            bg="#4285F4", fg="white", font=("Arial", 10, "bold")
        )
        self.translate_btn.pack(side=tk.RIGHT)

        # --- 2. Дві колонки для тексту (Текстові поля) ---
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 2.1. Ліве поле (Source)
        self.source_text = tk.Text(text_frame, height=10, width=30, font=("Arial", 12), wrap=tk.WORD)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 2.2. Праве поле (Target)
        self.target_text = tk.Text(text_frame, height=10, width=30, font=("Arial", 12), wrap=tk.WORD)
        self.target_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # --- 3. Панель дій (внизу) ---
        action_frame = tk.Frame(master)
        action_frame.pack(fill=tk.X, pady=(5, 10), padx=10)

        # 3.1. Кнопка "Відтворити"
        self.play_sound_btn = tk.Button(
            action_frame, text="🔊 Відтворити Морзе", command=self.play_morse_sound
        )
        self.play_sound_btn.pack(side=tk.LEFT)

        # 3.2. Кнопка "Параметри швидкості"
        self.settings_btn = tk.Button(
            action_frame, text="⚙️ Швидкість звуку", command=self.open_settings_window
        )
        self.settings_btn.pack(side=tk.RIGHT)

    # --- Методи керування інтерфейсом ---

    def swap_languages(self):
        """Міняє місцями мову-джерело та мову-ціль."""
        current_source = self.source_lang.get()
        current_target = self.target_lang.get()
        
        self.source_lang.set(current_target)
        self.target_lang.set(current_source)

        # Також міняємо місцями текст для зручності
        source_content = self.source_text.get("1.0", tk.END).strip()
        target_content = self.target_text.get("1.0", tk.END).strip()
        
        self.source_text.delete("1.0", tk.END)
        self.target_text.delete("1.0", tk.END)
        
        self.source_text.insert("1.0", target_content)
        self.target_text.insert("1.0", source_content)


    def translate_text(self):
        """Основна логіка перекладу в залежності від вибраних мов."""
        src_lang_key = self.source_lang.get()
        tgt_lang_key = self.target_lang.get()
        
        # Перевірка на переклад "сам в себе"
        if src_lang_key == tgt_lang_key:
            messagebox.showwarning("Помилка", "Не можна перекладати на ту ж саму мову.")
            return

        source_text = self.source_text.get("1.0", tk.END).strip().upper()
        
        if not source_text:
            self.target_text.delete("1.0", tk.END)
            return
            
        src_info = LANGUAGES[src_lang_key]
        tgt_info = LANGUAGES[tgt_lang_key]
        
        result_text = ""

        # Випадок 1: Звичайний текст -> Морзе
        if not src_info["is_morse"] and tgt_info["is_morse"]:
            morse_dict = src_info["dict"]
            morse_code = []
            for char in source_text:
                morse_code.append(morse_dict.get(char, ' ? ')) # Використовуємо ' ? ' для невідомих символів
            result_text = " ".join(morse_code)

        # Випадок 2: Морзе -> Звичайний текст
        elif src_info["is_morse"] and not tgt_info["is_morse"]:
            reverse_dict = tgt_info["reverse_dict"]
            morse_chars = source_text.split(' ')
            text = []
            for morse_char in morse_chars:
                if not morse_char: continue
                # Спеціальна обробка роздільника слів
                if morse_char == '/':
                    text.append(' ')
                else:
                    text.append(reverse_dict.get(morse_char, '#')) # '#' для невідомого коду
            result_text = "".join(text)

        # Випадок 3: Інші комбінації (Морзе -> Морзе або Текст -> Текст)
        else:
            messagebox.showwarning("Некоректний переклад", "Оберіть 'Морзе 📶' як мову-ціль або мову-джерело.")
            return

        # Відображення результату
        self.target_text.delete("1.0", tk.END)
        self.target_text.insert("1.0", result_text)

    # --- Функції відтворення звуку ---
    
    def play_morse_sound(self):
        """Відтворює код Морзе як звукові сигнали."""
        # Беремо текст з того поля, де зараз стоїть 'Морзе 📶'
        if self.source_lang.get() == "Морзе 📶":
            morse = self.source_text.get("1.0", tk.END).strip()
        elif self.target_lang.get() == "Морзе 📶":
            morse = self.target_text.get("1.0", tk.END).strip()
        else:
            messagebox.showwarning("Помилка", "Жодне поле не містить коду Морзе.")
            return

        if not morse or all(c in (' ', '/', '\n') for c in morse):
            messagebox.showinfo("Помилка", "Немає коду Морзе для відтворення.")
            return
            
        # Встановлення тривалостей (на основі повзунка)
        dot_duration = self.dot_duration_ms 
        dash_duration = dot_duration * 3 
        pause_within_char = dot_duration 
        pause_between_char = dot_duration * 3 
        pause_between_word = dot_duration * 7 

        frequency = 600 

        for morse_char in morse.split(' '):
            if not morse_char:
                continue
            
            if morse_char == '/':
                time.sleep(pause_between_word / 1000.0) 
                continue
            
            for signal in morse_char:
                if signal == '.':
                    winsound.Beep(frequency, dot_duration)
                    time.sleep(pause_within_char / 1000.0)
                elif signal == '-':
                    winsound.Beep(frequency, dash_duration)
                    time.sleep(pause_within_char / 1000.0)
            
            time.sleep(pause_between_char / 1000.0)

    # --- Вікно параметрів (Швидкість звуку) ---

    def open_settings_window(self):
        """Відкриває вікно для налаштувань швидкості/гучності."""
        
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Параметри швидкості звуку")
        settings_window.geometry("300x150")

        tk.Label(settings_window, text="Швидкість відтворення (мс):").pack(pady=5)
        tk.Label(settings_window, text="(Чим менше мс, тим швидше)").pack()

        self.speed_var = tk.IntVar(value=self.dot_duration_ms)
        
        speed_slider = tk.Scale(
            settings_window, 
            from_=50, to=500, 
            orient=tk.HORIZONTAL, 
            variable=self.speed_var,
            label="Тривалість крапки (мс)"
        )
        speed_slider.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Button(settings_window, text="Зберегти", command=lambda: self.save_settings(settings_window)).pack(pady=10)

    def save_settings(self, window):
        """Зберігає налаштування швидкості."""
        self.dot_duration_ms = self.speed_var.get()
        window.destroy()

# --- Запуск програми ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
import customtkinter as ctk 
from tkinter import messagebox
import winsound 
import time

# Встановлюємо зовнішній вигляд та тему за замовчуванням
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

# --- Таблиці кодування (ЗАЛИШАЮТЬСЯ БЕЗ ЗМІН) ---
CYRILLIC_MORSE_DICT = {
    'А': '.-', 'Б': '-...', 'В': '.--', 'Г': '--.', 'Д': '-..', 'Е': '.', 
    'Є': '..-..', 'Ж': '...-', 'З': '--..', 'И': '..', 'І': '..', 'Ї': '..-..',
    'Й': '.---', 'К': '-.-', 'Л': '.-..', 'М': '--', 'Н': '-.', 'О': '---', 
    'П': '.--.', 'Р': '.-.', 'С': '...', 'Т': '-', 'У': '..-', 'Ф': '..-.', 
    'Х': '....', 'Ц': '-.-.', 'Ч': '---.', 'Ш': '----', 'Щ': '--.-', 'Ь': '-..-', 
    'Ю': '..--', 'Я': '.-.-',
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
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': ' / ', '.': '.-.-.-', ',': '--..--', '?': '..-..', '!': '-.-.--'
}

LANGUAGES = {
    "English 🇬🇧": {"dict": LATIN_MORSE_DICT, "reverse_dict": {v: k for k, v in LATIN_MORSE_DICT.items()}, "is_morse": False},
    "Українська 🇺🇦": {"dict": CYRILLIC_MORSE_DICT, "reverse_dict": {v: k for k, v in CYRILLIC_MORSE_DICT.items()}, "is_morse": False},
    "Русский 🇷🇺": {"dict": CYRILLIC_MORSE_DICT, "reverse_dict": {v: k for k, v in CYRILLIC_MORSE_DICT.items()}, "is_morse": False},
    "Морзе 📶": {"dict": {}, "reverse_dict": {}, "is_morse": True}
}

class TranslatorApp(ctk.CTk): 
    def __init__(self):
        super().__init__() 
        self.title("Стильний Морзе-Перекладач")
        self.geometry("800x500")

        # Налаштування за замовчуванням
        self.source_lang = ctk.StringVar(value="English 🇬🇧")
        self.target_lang = ctk.StringVar(value="Морзе 📶")
        self.dot_duration_ms = 100  
        self.current_theme = ctk.StringVar(value=ctk.get_appearance_mode()) # Зберігаємо поточну тему
        
        # Визначення кольору для віджетів (темніший/світліший, ніж фон)
        WIDGET_COLOR = ("#E5E5E5", "#444444") 

        # --- Налаштування макету (Grid) ---
        self.grid_columnconfigure((0, 1), weight=1) 
        self.grid_rowconfigure(1, weight=1) 

        # --- 1. Панель керування (Рядок 0) ---
        lang_options = [lang for lang in LANGUAGES]
        
        # 1.1. Вибір мови-джерела (ліворуч)
        self.source_menu = ctk.CTkOptionMenu(
            self, variable=self.source_lang, values=lang_options, width=150
        )
        self.source_menu.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # 1.2. Кнопка перемикання (центр)
        self.swap_btn = ctk.CTkButton(
            self, text="⇆", command=self.swap_languages, width=40, 
            fg_color="transparent", hover_color=("#dbdbdb", "#2b2b2b"), text_color=("black", "white")
        )
        self.swap_btn.grid(row=0, column=0, columnspan=2) 
        
        # 1.3. Вибір мови-цілі (праворуч)
        self.target_menu = ctk.CTkOptionMenu(
            self, variable=self.target_lang, values=lang_options, width=150
        )
        self.target_menu.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 5))
        
        # --- 2. Дві колонки для тексту (Рядок 1) ---

        # 2.1. Ліве поле (Source)
        self.source_text = ctk.CTkTextbox(
            self, 
            height=200, 
            corner_radius=10, 
            fg_color=WIDGET_COLOR, 
            font=ctk.CTkFont(family="Arial", size=14), 
            wrap="word"
        )
        self.source_text.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        # Прив'язка події для автоматичного очищення
        self.source_text.bind("<KeyRelease>", self.check_for_auto_clear)
        
        # 2.2. Праве поле (Target)
        self.target_text = ctk.CTkTextbox(
            self, 
            height=200, 
            corner_radius=10, 
            fg_color=WIDGET_COLOR, 
            font=ctk.CTkFont(family="Arial", size=14), 
            wrap="word"
        )
        self.target_text.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        
        # --- 3. Панель дій (Рядок 2 та 3) ---

        # 3.1. Кнопка "Перекласти" (Акцентний колір)
        self.translate_btn = ctk.CTkButton(
            self, 
            text="Перекласти", 
            command=self.translate_text, 
            fg_color="#0066CC", 
            hover_color="#005CB8", 
            corner_radius=15, 
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            width=150
        )
        self.translate_btn.grid(row=2, column=0, columnspan=2, pady=(10, 5))
        
        # 3.2. Кнопка "Очистити" (Ліворуч, під полем)
        self.clear_btn = ctk.CTkButton(
            self, 
            text="🗑️ Очистити поле", 
            command=self.clear_source_field, 
            fg_color=("#E5E5E5", "#444444"),
            text_color=("black", "white"), 
            corner_radius=10,
            width=150
        )
        self.clear_btn.grid(row=3, column=0, sticky="w", padx=10, pady=(5, 10))

        # 3.3. Кнопка "Відтворити" (Центр)
        self.play_sound_btn = ctk.CTkButton(
            self, text="🔊 Відтворити Морзе", command=self.play_morse_sound, 
            fg_color="#0066CC", hover_color="#005CB8", 
            text_color="white", width=150
        )
        self.play_sound_btn.grid(row=3, column=0, columnspan=2, pady=(5, 10))

        # 3.4. Кнопка "Параметри" (Праворуч)
        self.settings_btn = ctk.CTkButton(
            self, 
            text="⚙️ Налаштування", 
            command=self.open_settings_window,
            fg_color=("#E5E5E5", "#444444"),
            text_color=("black", "white"), 
            corner_radius=10,
            width=150
        )
        self.settings_btn.grid(row=3, column=1, sticky="e", padx=10, pady=(5, 10))

    # --- Нові функції ---

    def clear_source_field(self):
        """Очищує ліве поле та автоматично праве."""
        self.source_text.delete("0.0", "end")
        self.target_text.delete("0.0", "end") # Автоматичне очищення правого поля

    def check_for_auto_clear(self, event):
        """Перевіряє ліве поле при натисканні клавіші та очищує праве, якщо ліве порожнє."""
        # Отримуємо вміст, видаляючи зайві пробіли та переноси рядків
        content = self.source_text.get("0.0", "end").strip()
        if not content:
            # Якщо поле стало порожнім, очищуємо праве поле
            self.target_text.delete("0.0", "end")
            
    # --- Оновлені функції ---

    def swap_languages(self):
        # ... (логіка обміну без змін) ...
        current_source = self.source_lang.get()
        current_target = self.target_lang.get()
        
        self.source_lang.set(current_target)
        self.target_lang.set(current_source)

        source_content = self.source_text.get("0.0", "end").strip()
        target_content = self.target_text.get("0.0", "end").strip()
        
        self.source_text.delete("0.0", "end")
        self.target_text.delete("0.0", "end")
        
        self.source_text.insert("0.0", target_content)
        self.target_text.insert("0.0", source_content)

    def translate_text(self):
        # ... (логіка перекладу без змін) ...
        src_lang_key = self.source_lang.get()
        tgt_lang_key = self.target_lang.get()
        
        if src_lang_key == tgt_lang_key:
            messagebox.showwarning("Помилка", "Не можна перекладати на ту ж саму мову.")
            return

        source_text = self.source_text.get("0.0", "end").strip().upper() 
        
        if not source_text:
            self.target_text.delete("0.0", "end") # Додаткова перевірка перед перекладом
            return
            
        src_info = LANGUAGES[src_lang_key]
        tgt_info = LANGUAGES[tgt_lang_key]
        result_text = ""

        # Випадок 1: Звичайний текст -> Морзе
        if not src_info["is_morse"] and tgt_info["is_morse"]:
            morse_dict = src_info["dict"]
            morse_code = []
            for char in source_text:
                morse_code.append(morse_dict.get(char, ' ? ')) 
            result_text = " ".join(morse_code)

        # Випадок 2: Морзе -> Звичайний текст
        elif src_info["is_morse"] and not tgt_info["is_morse"]:
            reverse_dict = tgt_info["reverse_dict"]
            morse_chars = source_text.split(' ')
            text = []
            for morse_char in morse_chars:
                if not morse_char: continue
                if morse_char == '/':
                    text.append(' ')
                else:
                    text.append(reverse_dict.get(morse_char, '#'))
            result_text = "".join(text)

        else:
            messagebox.showwarning("Некоректний переклад", "Оберіть 'Морзе 📶' як мову-ціль або мову-джерело.")
            return

        self.target_text.delete("0.0", "end")
        self.target_text.insert("0.0", result_text)

    # ... (play_morse_sound без змін) ...

    def play_morse_sound(self):
        # ... (логіка відтворення звуку) ...
        if self.source_lang.get() == "Морзе 📶":
            morse = self.source_text.get("0.0", "end").strip()
        elif self.target_lang.get() == "Морзе 📶":
            morse = self.target_text.get("0.0", "end").strip()
        else:
            messagebox.showwarning("Помилка", "Жодне поле не містить коду Морзе.")
            return

        if not morse or all(c in (' ', '/', '\n') for c in morse):
            messagebox.showinfo("Помилка", "Немає коду Морзе для відтворення.")
            return
            
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

    # --- Вікно параметрів (Оновлено для вибору теми) ---

    def open_settings_window(self):
        
        settings_window = ctk.CTkToplevel(self) 
        settings_window.title("Налаштування")
        settings_window.geometry("300x300")
        settings_window.resizable(False, False)

        # --- Налаштування ШВИДКОСТІ ---
        ctk.CTkLabel(settings_window, text="Швидкість відтворення (мс):").pack(pady=(10, 0))
        ctk.CTkLabel(settings_window, text="(Чим менше мс, тим швидше)").pack()

        self.speed_var = ctk.IntVar(value=self.dot_duration_ms)
        speed_slider = ctk.CTkSlider(
            settings_window, from_=50, to=500, variable=self.speed_var, command=self.update_slider_label
        )
        speed_slider.pack(pady=10, padx=20, fill="x")

        self.slider_label = ctk.CTkLabel(settings_window, text=f"Поточна тривалість: {self.dot_duration_ms} мс")
        self.slider_label.pack()
        
        # --- Налаштування ТЕМИ ---
        ctk.CTkLabel(settings_window, text="--- Вибір теми оформлення ---").pack(pady=(20, 5))
        
        theme_options = ["System", "Dark", "Light"]
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode()) # Поточна тема

        ctk.CTkOptionMenu(
            settings_window,
            variable=self.theme_var,
            values=theme_options
        ).pack(pady=5)
        
        # --- Кнопка Зберегти ---
        ctk.CTkButton(settings_window, text="Зберегти", command=lambda: self.save_settings(settings_window)).pack(pady=10)

    def update_slider_label(self, value):
        self.slider_label.configure(text=f"Поточна тривалість: {int(value)} мс")

    def save_settings(self, window):
        """Зберігає швидкість та застосовує нову тему."""
        self.dot_duration_ms = self.speed_var.get()
        
        # Застосування нової теми
        new_theme = self.theme_var.get()
        ctk.set_appearance_mode(new_theme)
        self.current_theme.set(new_theme)
        
        window.destroy()


# --- Запуск програми ---
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
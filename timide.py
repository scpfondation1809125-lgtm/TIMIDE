import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import subprocess
import os
import re

class TimIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("🍑 TimIDE — среда разработки TimLang (с подсветкой!)")
        self.root.geometry("900x700")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.interpreter_path = os.path.join(base_dir, "twu.exe")
        if not os.path.exists(self.interpreter_path):
            self.interpreter_path = "twu.exe"

        # Поле для кода (с подсветкой)
        self.editor = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 12))
        self.editor.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Настраиваем теги для подсветки
        self.editor.tag_config("keyword", foreground="darkblue", font=("Courier New", 12, "bold"))
        self.editor.tag_config("builtin", foreground="purple", font=("Courier New", 12, "bold"))
        self.editor.tag_config("string", foreground="green")
        self.editor.tag_config("number", foreground="orange")
        self.editor.tag_config("comment", foreground="gray")

        # Привязываем подсветку к событиям (печать и вставка)
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
        self.editor.bind("<<Paste>>", self.highlight_syntax)

        # Горячие клавиши
        self.editor.bind("<Control-c>", self.copy_text)
        self.editor.bind("<Control-v>", self.paste_text)
        self.editor.bind("<Control-a>", self.select_all)

        # Контекстное меню
        self.editor_menu = tk.Menu(self.editor, tearoff=0)
        self.editor_menu.add_command(label="Вырезать", command=self.cut_text)
        self.editor_menu.add_command(label="Копировать", command=self.copy_text)
        self.editor_menu.add_command(label="Вставить", command=self.paste_text)
        self.editor_menu.add_separator()
        self.editor_menu.add_command(label="Выделить всё", command=self.select_all)
        self.editor.bind("<Button-3>", self.show_editor_menu)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn_frame, text="▶ Запустить", command=self.run_code, bg="lightgreen", width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="💾 Сохранить", command=self.save_file, bg="lightblue", width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="📂 Открыть", command=self.load_file, bg="lightyellow", width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="🗑 Очистить вывод", command=self.clear_output, bg="lightcoral", width=14).pack(side=tk.LEFT, padx=2)

        # Вывод
        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12, font=("Courier New", 10), bg="black", fg="white")
        self.output.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.output.tag_config("error", foreground="red")

        self.output_menu = tk.Menu(self.output, tearoff=0)
        self.output_menu.add_command(label="Копировать", command=self.copy_output)
        self.output_menu.add_command(label="Очистить", command=self.clear_output)
        self.output.bind("<Button-3>", self.show_output_menu)

        self.status = tk.Label(root, text="✅ Готов к работе!", anchor="w", fg="green")
        self.status.pack(fill=tk.X, padx=5, pady=2)

        # Первая подсветка
        self.highlight_syntax()

    # ========= ПОДСВЕТКА СИНТАКСИСА =========
    def highlight_syntax(self, event=None):
        # Удаляем старые теги
        for tag in ["keyword", "builtin", "string", "number", "comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        text = self.editor.get("1.0", tk.END)

        # Комментарии (серый)
        for match in re.finditer(r'//.*', text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("comment", start, end)

        # Строки (зелёный)
        for match in re.finditer(r'"[^"]*"', text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("string", start, end)

        # Числа (оранжевый)
        for match in re.finditer(r'\b\d+(\.\d+)?\b', text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("number", start, end)

        # Ключевые слова (синий)
        keywords = ["fn", "if", "else", "loop", "return", "in", "set", "mut"]
        for kw in keywords:
            for match in re.finditer(r'\b' + re.escape(kw) + r'\b', text):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.editor.tag_add("keyword", start, end)

        # Встроенные команды (фиолетовый)
        builtins = ["say"]
        for blt in builtins:
            for match in re.finditer(r'\b' + re.escape(blt) + r'\b', text):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.editor.tag_add("builtin", start, end)

    # ========= ФУНКЦИИ РЕДАКТОРА =========
    def copy_text(self, event=None):
        try:
            self.editor.clipboard_clear()
            text = self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.editor.clipboard_append(text)
            self.status.config(text="📋 Скопировано!", fg="blue")
        except:
            pass

    def paste_text(self, event=None):
        try:
            text = self.root.clipboard_get()
            self.editor.insert(tk.INSERT, text)
            self.highlight_syntax()
            self.status.config(text="📋 Вставлено!", fg="blue")
        except:
            pass

    def cut_text(self):
        try:
            self.copy_text()
            self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.status.config(text="✂️ Вырезано!", fg="blue")
        except:
            pass

    def select_all(self, event=None):
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)
        return "break"

    def show_editor_menu(self, event):
        self.editor_menu.post(event.x_root, event.y_root)

    # ========= ФУНКЦИИ ВЫВОДА =========
    def copy_output(self):
        try:
            self.output.clipboard_clear()
            text = self.output.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.output.clipboard_append(text)
            self.status.config(text="📋 Скопировано из вывода!", fg="blue")
        except:
            pass

    def show_output_menu(self, event):
        self.output_menu.post(event.x_root, event.y_root)

    # ========= ОСНОВНЫЕ ФУНКЦИИ =========
    def run_code(self):
        code = self.editor.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Пустой код", "Напиши что-нибудь на TimLang!")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.join(base_dir, "temp.tim")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(code)

        self.output.delete("1.0", tk.END)
        try:
            result = subprocess.run(
                [self.interpreter_path, temp_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                cwd=base_dir
            )
            self.output.insert(tk.END, result.stdout)
            if result.stderr:
                self.output.insert(tk.END, "\n\n[ОШИБКА]\n")
                self.output.insert(tk.END, result.stderr)
                self.status.config(text="❌ Ошибка выполнения!", fg="red")
            else:
                self.status.config(text="✅ Выполнено успешно!", fg="green")
        except FileNotFoundError:
            self.output.insert(tk.END, f"❌ Ошибка: не найден интерпретатор '{self.interpreter_path}'\n")
            self.output.insert(tk.END, "Убедись, что twu.exe лежит в папке с TimIDE")
        except Exception as e:
            self.output.insert(tk.END, f"❌ Ошибка системы: {e}")

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".tim", filetypes=[("TimLang files", "*.tim *.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", tk.END))
            self.status.config(text=f"💾 Файл сохранён: {os.path.basename(path)}", fg="blue")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("TimLang files", "*.tim *.txt")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert("1.0", f.read())
                self.highlight_syntax()
                self.status.config(text=f"📂 Загружен: {os.path.basename(path)}", fg="blue")
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать файл:\n{e}")

    def clear_output(self):
        self.output.delete("1.0", tk.END)
        self.status.config(text="🗑 Вывод очищен", fg="gray")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimIDE(root)
    root.mainloop()
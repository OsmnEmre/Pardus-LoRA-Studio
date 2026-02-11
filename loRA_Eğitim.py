import tkinter as tk
from tkinter import filedialog, messagebox
import os
import platform

# --- TOOLTIP (İPUCU) SINIFI ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 30
        y += self.widget.winfo_rooty() + 30
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#2d3436", foreground="white", relief='flat',
                         padx=10, pady=5, font=("Segoe UI", "9"))
        label.pack()

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw: tw.destroy()

class LoraLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("LoRA Studio v1.7.1")
        self.root.geometry("650x850")
        
        self.dark_mode = True
        self.is_turkish = True

        self.themes = {
            "dark": {"bg": "#121212", "card": "#1e1e1e", "fg": "#e0e0e0", "accent": "#00b894", "btn_idle": "#2d3436", "input_bg": "#252525"},
            "light": {"bg": "#f5f6fa", "card": "#ffffff", "fg": "#2f3640", "accent": "#00b894", "btn_idle": "#dcdde1", "input_bg": "#f1f2f6"}
        }

        # --- EKSİK ANAHTARLAR (tip_steps, tip_lr) BURAYA EKLENDİ ---
        self.lang_pack = {
            "tr": {
                "title": "LoRA Geliştirme Aracı", "model": "Model Dosyası", "data": "Veri Seti",
                "output": "Kayıt Yolu", "params": "Eğitim Ayarları", "steps": "Adım Sayısı",
                "lr": "Öğrenme Hızı", "start": "EĞİTİMİ BAŞLAT", "reset": "Varsayılanlara Dön",
                "theme": "Mod Değiştir", "lang": "TR / EN", "select": "Seç",
                "cmd_ready": "Komut Hazır!", "error": "Hata", "error_path": "Lütfen yolları seçin.",
                "tip_steps": "Eğitimin kaç adım süreceğini belirler.", "tip_lr": "Öğrenme hızı (Örn: 0.0001)"
            },
            "en": {
                "title": "LoRA Development Tool", "model": "Base Model", "data": "Dataset Path",
                "output": "Output Path", "params": "Training Settings", "steps": "Total Steps",
                "lr": "Learning Rate", "start": "START TRAINING", "reset": "Reset Defaults",
                "theme": "Toggle Theme", "lang": "EN / TR", "select": "Browse",
                "cmd_ready": "Command Ready!", "error": "Error", "error_path": "Select paths.",
                "tip_steps": "Number of training iterations.", "tip_lr": "Learning speed (Ex: 0.0001)"
            }
        }

        self.widgets = {"labels": [], "entries": [], "cards": [], "btns": [], "tips": []}
        self.setup_ui()
        self.refresh_ui()

    def setup_ui(self):
        self.top_bar = tk.Frame(self.root); self.top_bar.pack(fill="x", padx=20, pady=10)
        self.widgets["cards"].append(self.top_bar)
        
        self.lang_btn = tk.Button(self.top_bar, command=self.toggle_language, relief="flat", padx=10)
        self.lang_btn.pack(side="right", padx=5); self.widgets["btns"].append(self.lang_btn)
        
        self.theme_btn = tk.Button(self.top_bar, command=self.toggle_theme, relief="flat", padx=10)
        self.theme_btn.pack(side="right"); self.widgets["btns"].append(self.theme_btn)

        self.title_lbl = tk.Label(self.root, font=("Segoe UI", 22, "bold"))
        self.title_lbl.pack(pady=20); self.widgets["labels"].append((self.title_lbl, "title", True))

        self.card_paths = tk.Frame(self.root, padx=20, pady=20)
        self.card_paths.pack(fill="x", padx=30, pady=10); self.widgets["cards"].append(self.card_paths)

        self.model_path = tk.StringVar(value=r"C:\Users\Emre\Desktop\model.safetensors") 
        self.create_row(self.card_paths, "model", self.model_path, True)
        self.data_path = tk.StringVar(); self.create_row(self.card_paths, "data", self.data_path, True)
        self.out_path = tk.StringVar(); self.create_row(self.card_paths, "output", self.out_path, True)

        self.card_params = tk.Frame(self.root, padx=20, pady=20)
        self.card_params.pack(fill="x", padx=30, pady=10); self.widgets["cards"].append(self.card_params)
        
        self.steps = tk.StringVar(value="1500")
        self.create_row(self.card_params, "steps", self.steps, False, "tip_steps")
        self.lr = tk.StringVar(value="0.0001")
        self.create_row(self.card_params, "lr", self.lr, False, "tip_lr")

        self.reset_btn = tk.Button(self.root, command=self.reset, relief="flat")
        self.reset_btn.pack(pady=10); self.widgets["btns"].append(self.reset_btn)

        self.start_btn = tk.Button(self.root, font=("Segoe UI", 14, "bold"), height=2, width=30, relief="flat", command=self.start_training)
        self.start_btn.pack(pady=20); self.widgets["btns"].append(self.start_btn)

    def create_row(self, parent, lang_key, var, is_path, tip_key=None):
        row = tk.Frame(parent); row.pack(fill="x", pady=8)
        self.widgets["cards"].append(row)
        cursor_type = "question_arrow" if tip_key else ""
        lbl = tk.Label(row, font=("Segoe UI", 10), cursor=cursor_type); lbl.pack(anchor="w")
        self.widgets["labels"].append((lbl, lang_key, False))
        if tip_key: self.widgets["tips"].append((lbl, tip_key))
        
        entry = tk.Entry(row, textvariable=var, relief="flat", font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=8, pady=5); self.widgets["entries"].append(entry)
        
        if is_path:
            btn = tk.Button(row, text="...", relief="flat", width=4, command=lambda v=var: self.select(v))
            btn.pack(side="right", padx=(10, 0), ipady=4); self.widgets["btns"].append(btn)

    def select(self, var):
        path = filedialog.askopenfilename() if "model" in str(var) else filedialog.askdirectory()
        if path: var.set(os.path.normpath(path))

    def reset(self): self.steps.set("1500"); self.lr.set("0.0001")

    def refresh_ui(self):
        t = self.themes["dark"] if self.dark_mode else self.themes["light"]
        l = self.lang_pack["tr"] if self.is_turkish else self.lang_pack["en"]
        self.root.configure(bg=t["bg"])
        
        for c in self.widgets["cards"]: c.configure(bg=t["card"])
        for lbl, key, is_title in self.widgets["labels"]:
            lbl.configure(text=l[key], bg=t["bg"] if is_title else t["card"], fg=t["accent"] if is_title else t["fg"])
        
        for e in self.widgets["entries"]: e.configure(bg=t["input_bg"], fg=t["fg"], insertbackground=t["fg"])
        
        for b in self.widgets["btns"]:
            btn_text = str(b.cget("text")).upper()
            is_start = "EĞİTİM" in btn_text or "TRAINING" in btn_text
            b.configure(bg=t["accent"] if is_start else t["btn_idle"], fg="white" if is_start else t["fg"])
            
        self.start_btn.configure(text=l["start"]); self.reset_btn.configure(text=l["reset"])
        self.lang_btn.configure(text=l["lang"]); self.theme_btn.configure(text=l["theme"])
        
        # Tooltip'leri burada güncelliyoruz
        for w, k in self.widgets["tips"]: ToolTip(w, l[k])

    def toggle_theme(self): self.dark_mode = not self.dark_mode; self.refresh_ui()
    def toggle_language(self): self.is_turkish = not self.is_turkish; self.refresh_ui()

    def start_training(self):
        l = self.lang_pack["tr"] if self.is_turkish else self.lang_pack["en"]
        if not self.model_path.get() or not self.data_path.get():
            messagebox.showerror(l["error"], l["error_path"]); return
        
        final_cmd = f'accelerate launch train_network.py --pretrained_model_name_or_path="{self.model_path.get()}" --train_data_dir="{self.data_path.get()}" --max_train_steps={self.steps.get()} --learning_rate={self.lr.get()}'
        print(f"\n--- OLUŞTURULAN KOMUT ---\n{final_cmd}\n")
        messagebox.showinfo(l["cmd_ready"], "Komut terminale (VScode alt paneli) yazdırıldı!")

if __name__ == "__main__":
    root = tk.Tk(); app = LoraLauncher(root); root.mainloop()
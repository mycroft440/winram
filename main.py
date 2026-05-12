import tkinter as tk
import customtkinter as ctk
import psutil
import threading
import time
from optimizer import optimize_system, is_admin

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WinRAMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WinRAM Ultimate v2.0")
        self.geometry("700x550")
        self.resizable(False, False)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(padx=20, pady=20, sticky="nsew")
        
        # Header
        self.label_title = ctk.CTkLabel(self.main_frame, text="🚀 WinRAM Ultimate", font=ctk.CTkFont(size=28, weight="bold"))
        self.label_title.pack(pady=(20, 5))
        
        admin_text = "Status: Administrador Ativo ✅" if is_admin() else "Aviso: Execute como Admin para Otimização Total ⚠️"
        admin_color = "#4CAF50" if is_admin() else "#FFD740"
        self.label_admin = ctk.CTkLabel(self.main_frame, text=admin_text, text_color=admin_color, font=ctk.CTkFont(size=12))
        self.label_admin.pack(pady=(0, 10))

        # RAM Dashboard
        self.ram_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a", corner_radius=10)
        self.ram_frame.pack(padx=30, pady=10, fill="x")
        
        self.ram_label = ctk.CTkLabel(self.ram_frame, text="MEMÓRIA RAM", font=ctk.CTkFont(size=12, weight="bold"))
        self.ram_label.pack(pady=(10, 0))
        
        self.ram_usage_text = ctk.CTkLabel(self.ram_frame, text="0%", font=ctk.CTkFont(size=42, weight="bold"))
        self.ram_usage_text.pack()
        
        self.ram_bar = ctk.CTkProgressBar(self.ram_frame, width=500, height=12)
        self.ram_bar.pack(pady=(0, 15), padx=20)
        self.ram_bar.set(0)

        # Optimization Modes
        self.modes_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.modes_frame.pack(pady=20, fill="x", padx=30)
        
        # Mode 1: Quick
        self.btn_quick = ctk.CTkButton(self.modes_frame, text="RÁPIDO\n(RAM + Temp)", height=80, width=180,
                                       fg_color="#333333", hover_color="#444444",
                                       command=lambda: self.start_opt("quick"))
        self.btn_quick.grid(row=0, column=0, padx=5)
        
        # Mode 2: Advanced
        self.btn_adv = ctk.CTkButton(self.modes_frame, text="AVANÇADO\n(+ Disco + DNS)", height=80, width=180,
                                     fg_color="#1f538d", hover_color="#2a6dbd",
                                     command=lambda: self.start_opt("advanced"))
        self.btn_adv.grid(row=0, column=1, padx=5)
        
        # Mode 3: Ultimate
        self.btn_ult = ctk.CTkButton(self.modes_frame, text="ULTIMATE TURBO\n(TUDO + Registry)", height=80, width=180,
                                     fg_color="#d32f2f", hover_color="#f44336",
                                     command=lambda: self.start_opt("ultimate"))
        self.btn_ult.grid(row=0, column=2, padx=5)

        # Log Console
        self.console_frame = ctk.CTkFrame(self.main_frame, fg_color="black", corner_radius=5)
        self.console_frame.pack(padx=30, pady=(0, 20), fill="both", expand=True)
        
        self.console_label = ctk.CTkLabel(self.console_frame, text="> Console de Otimização pronto.", 
                                          font=ctk.CTkFont(family="Consolas", size=11), 
                                          text_color="#00FF00", justify="left", anchor="nw")
        self.console_label.pack(padx=10, pady=10, fill="both", expand=True)

        self.update_stats()

    def update_stats(self):
        ram = psutil.virtual_memory()
        percent = ram.percent
        self.ram_usage_text.configure(text=f"{percent}%")
        self.ram_bar.set(percent / 100)
        
        if percent > 85: self.ram_bar.configure(progress_color="#d32f2f")
        elif percent > 65: self.ram_bar.configure(progress_color="#fbc02d")
        else: self.ram_bar.configure(progress_color="#1976d2")
        
        self.after(1500, self.update_stats)

    def start_opt(self, mode):
        self.set_buttons_state("disabled")
        self.console_label.configure(text=f"> Iniciando modo {mode.upper()}...\n> Por favor, aguarde.")
        threading.Thread(target=self.run_task, args=(mode,), daemon=True).start()

    def set_buttons_state(self, state):
        self.btn_quick.configure(state=state)
        self.btn_adv.configure(state=state)
        self.btn_ult.configure(state=state)

    def run_task(self, mode):
        try:
            time.sleep(1)
            res = optimize_system(mode=mode)
            formatted_res = "\n".join([f"> {line}" for line in res.split("\n")])
            self.console_label.configure(text=f"> OTIMIZAÇÃO CONCLUÍDA ✨\n{formatted_res}")
        except Exception as e:
            self.console_label.configure(text=f"> ERRO CRÍTICO: {e}", text_color="red")
        finally:
            self.set_buttons_state("normal")

if __name__ == "__main__":
    app = WinRAMApp()
    app.mainloop()

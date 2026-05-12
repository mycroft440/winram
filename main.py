import tkinter as tk
import customtkinter as ctk
import psutil
import threading
import time
from optimizer import optimize_system, is_admin

# Configuração visual premium
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WinRAMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WinRAM Pro - Optimizer")
        self.geometry("600x450")
        self.resizable(False, False)

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Container Central
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Título
        self.label_title = ctk.CTkLabel(self.main_frame, text="WinRAM Optimizer", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(pady=(20, 10))

        # Status de Admin
        admin_text = "Modo Administrador: ATIVO" if is_admin() else "Modo Administrador: INATIVO (Recomendado)"
        admin_color = "#4CAF50" if is_admin() else "#FF5252"
        self.label_admin = ctk.CTkLabel(self.main_frame, text=admin_text, text_color=admin_color, font=ctk.CTkFont(size=12))
        self.label_admin.grid(pady=(0, 20))

        # Indicador de RAM
        self.ram_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.ram_frame.grid(pady=10)
        
        self.ram_usage_label = ctk.CTkLabel(self.ram_frame, text="0%", font=ctk.CTkFont(size=48, weight="bold"))
        self.ram_usage_label.grid(row=0, column=0)
        
        self.ram_info_label = ctk.CTkLabel(self.ram_frame, text="Uso de Memória RAM", font=ctk.CTkFont(size=14))
        self.ram_info_label.grid(row=1, column=0)

        # Barra de Progresso (RAM)
        self.ram_progress = ctk.CTkProgressBar(self.main_frame, width=400)
        self.ram_progress.grid(pady=20)
        self.ram_progress.set(0)

        # Checkbox Otimizacao Completa
        self.full_opt_var = ctk.BooleanVar(value=False)
        self.check_full = ctk.CTkCheckBox(self.main_frame, text="Otimizacao Completa (TRIM/Defrag)", 
                                          variable=self.full_opt_var, font=ctk.CTkFont(size=12))
        self.check_full.grid(pady=(0, 10))

        # Botão Otimizar
        self.btn_optimize = ctk.CTkButton(self.main_frame, text="OTIMIZAR AGORA", 
                                          height=50, width=250, corner_radius=10,
                                          font=ctk.CTkFont(size=16, weight="bold"),
                                          command=self.start_optimization)
        self.btn_optimize.grid(pady=20)

        # Terminal de Logs
        self.log_text = ctk.CTkLabel(self.main_frame, text="Aguardando ação...", font=ctk.CTkFont(size=11), text_color="#AAAAAA")
        self.log_text.grid(pady=(0, 20))

        # Iniciar thread de atualização de RAM
        self.update_ram_usage()

    def update_ram_usage(self):
        ram = psutil.virtual_memory()
        percent = ram.percent
        self.ram_usage_label.configure(text=f"{percent}%")
        self.ram_progress.set(percent / 100)
        
        # Mudar cor baseado no uso
        if percent > 80: self.ram_progress.configure(progress_color="#FF5252")
        elif percent > 60: self.ram_progress.configure(progress_color="#FFD740")
        else: self.ram_progress.configure(progress_color="#448AFF")
        
        self.after(2000, self.update_ram_usage)

    def start_optimization(self):
        self.btn_optimize.configure(state="disabled", text="OTIMIZANDO...")
        self.log_text.configure(text="Iniciando procedimentos de limpeza profunda...")
        
        # Rodar em thread para não travar a GUI
        threading.Thread(target=self.run_optimization_task, daemon=True).start()

    def run_optimization_task(self):
        try:
            time.sleep(1) # Efeito dramático
            full_mode = self.full_opt_var.get()
            result = optimize_system(full=full_mode)
            self.log_text.configure(text=result)
        except Exception as e:
            self.log_text.configure(text=f"Erro durante a otimização: {e}")
        finally:
            self.btn_optimize.configure(state="normal", text="OTIMIZAR AGORA")

if __name__ == "__main__":
    app = WinRAMApp()
    app.mainloop()

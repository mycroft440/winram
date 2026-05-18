import os
import sys
import math
import time
import shutil
import ctypes
import winreg
import platform
import threading
import subprocess
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
import psutil

# ═══════════════════════════════════════════════════════════
#  FUNÇÕES DE OTIMIZAÇÃO (antigo optimizer.py)
# ═══════════════════════════════════════════════════════════

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def kill_memory_hogs():
    targets = [
        "widgets.exe", "msedge.exe", "msteams.exe", "skype.exe", 
        "ctfmon.exe", "onedrive.exe", "phoneexperiencehost.exe", 
        "searchhost.exe", "startmenuexperiencehost.exe"
    ]
    killed = 0
    freed_ram = 0
    errors = []
    
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in targets:
                    freed_ram += proc.info['memory_info'].rss / (1024 * 1024)
                    proc.kill()
                    killed += 1
            except Exception as e:
                errors.append(f"Erro ao encerrar {proc.info.get('name', 'PID '+str(proc.info.get('pid')))}: {e}")
                
        msg = f"Expurgo: {killed} parasitas encerrados (~{freed_ram:.0f}MB liberados)."
        if errors:
            msg += "\n    Avisos: " + " | ".join(errors[:3])
        return msg
    except Exception as e:
        return f"Erro fatal no expurgo de processos: {e}"

def restart_explorer():
    try:
        r = subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], capture_output=True, text=True)
        subprocess.Popen(['explorer.exe'])
        if r.returncode != 0 and "not found" not in r.stderr.lower():
            return f"Aviso ao matar explorer: {r.stderr.strip()}"
        return "Windows Shell reiniciado (Vazamento de RAM contido)."
    except Exception as e:
        return f"Falha ao reiniciar o Windows Shell: {e}"

def optimize_virtual_memory():
    if not is_admin(): return "Aviso: Otimizar Memória Virtual exige Admin."
    try:
        script = "Set-WmiInstance -Class Win32_ComputerSystem -EnableAllPrivileges -Arguments @{AutomaticManagedPagefile=$true}"
        r = subprocess.run(['powershell', '-Command', script], capture_output=True, text=True)
        if r.returncode != 0:
            return f"Erro no WMI Pagefile: {r.stderr.strip()}"
        return "Memória Virtual (Pagefile) transferida e otimizada."
    except Exception as e:
        return f"Erro crítico ao configurar Memória Virtual: {e}"

def disable_useless_services():
    services = ["SysMain", "DiagTrack", "WerSvc"]
    logs = []
    for svc in services:
        try:
            r1 = subprocess.run(['sc', 'config', svc, 'start=', 'disabled'], capture_output=True, text=True)
            r2 = subprocess.run(['net', 'stop', svc], capture_output=True, text=True)
            if r1.returncode != 0 and "Access is denied" in r1.stderr:
                logs.append(f"[sc {svc}] Acesso Negado (Sem Admin)")
            elif r1.returncode != 0 and "OpenService FAILED 1060" not in r1.stdout:
                logs.append(f"[sc {svc}] {r1.stderr.strip() or r1.stdout.strip()}")
                
            if r2.returncode != 0 and "not started" not in r2.stderr.lower() and "não foi iniciado" not in r2.stderr.lower():
                logs.append(f"[net stop {svc}] {r2.stderr.strip() or r2.stdout.strip()}")
        except Exception as e: 
            logs.append(f"[Falha API {svc}]: {e}")
            
    if logs:
        unique_logs = list(set([log.replace("\n", " ").strip() for log in logs if log.strip()]))
        return "Serviços ajustados com avisos:\n    " + "\n    ".join(unique_logs)
    return "Serviços de telemetria e SysMain desativados perfeitamente."

def disable_vbs_and_visuals():
    logs = []
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity") as key:
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
    except Exception as e: logs.append(f"VBS falhou: {e}")
    
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects") as key:
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
    except Exception as e: logs.append(f"Visuais falhou: {e}")
    
    if logs: return "Otimização Visual/VBS concluída com erros: " + " | ".join(logs)
    return "VBS (Virtualization) e Efeitos Visuais otimizados."

def optimize_gpu_scheduling():
    logs = []
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers") as key:
            winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2)
    except Exception as e: logs.append(f"HAGS: {e}")
        
    try:
        games_key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, games_key_path) as key:
            winreg.SetValueEx(key, "GPU Priority", 0, winreg.REG_DWORD, 8)
            winreg.SetValueEx(key, "Priority", 0, winreg.REG_DWORD, 6)
            winreg.SetValueEx(key, "Scheduling Category", 0, winreg.REG_SZ, "High")
            winreg.SetValueEx(key, "SFIO Priority", 0, winreg.REG_SZ, "High")
    except Exception as e: logs.append(f"MMCSS: {e}")
        
    if logs: return "Agendamento GPU aplicado com erros menores: " + " | ".join(logs)
    return "Agendamento de GPU (HAGS) e MMCSS elevados ao máximo."

def optimize_network_latency():
    logs = []
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile") as key:
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xffffffff)
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
    except Exception as e: logs.append(f"Throttling Registry: {e}")
        
    try:
        r1 = subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'], capture_output=True, text=True)
        r2 = subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'ecncapability=disabled'], capture_output=True, text=True)
        if r1.returncode != 0: logs.append(f"TCP AutoTuning: {r1.stderr.strip() or r1.stdout.strip()}")
        if r2.returncode != 0: logs.append(f"TCP ECN: {r2.stderr.strip() or r2.stdout.strip()}")
    except Exception as e: logs.append(f"Netsh API: {e}")
        
    if logs: return "Rede otimizada com avisos: " + " | ".join(logs)
    return "Throttling de rede removido e TCP/IP otimizado (Menor Ping)."

def disable_bloat_and_compression():
    logs = []
    try:
        r = subprocess.run(['powershell', '-Command', 'Disable-MMAgent -mc'], capture_output=True, text=True)
        if r.returncode != 0: logs.append(f"MMAgent: {r.stderr.strip()}")
    except Exception as e: logs.append(f"MMAgent API: {e}")
        
    try:
        r = subprocess.run(['powercfg', '/h', 'off'], capture_output=True, text=True)
        if r.returncode != 0: logs.append(f"Hibernação: {r.stderr.strip() or r.stdout.strip()}")
    except Exception as e: logs.append(f"PowerCfg API: {e}")
        
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\WindowsCopilot") as key:
            winreg.SetValueEx(key, "TurnOffWindowsCopilot", 0, winreg.REG_DWORD, 1)
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Edge") as key:
            winreg.SetValueEx(key, "BackgroundModeEnabled", 0, winreg.REG_DWORD, 0)
    except Exception as e: logs.append(f"Registry Bloat: {e}")
            
    if logs: return "Bloatwares bloqueados com avisos: " + " | ".join(logs)
    return "Compressão de RAM, Fast Startup e IAs em segundo plano bloqueados."

def clear_standby_and_shaders():
    results = []
    try:
        ctypes.windll.kernel32.SetSystemFileCacheSize(ctypes.c_size_t(-1), ctypes.c_size_t(-1), 0)
        results.append("Standby List limpo.")
    except Exception as e: results.append(f"Aviso Standby List: {e}")
    
    try:
        shader_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'D3DSCache')
        if os.path.exists(shader_path):
            shutil.rmtree(shader_path, ignore_errors=True)
            results.append("Cache Shaders expurgado.")
    except Exception as e: results.append(f"Aviso Shaders: {e}")
    return " | ".join(results)

def clean_ram():
    try: import psutil
    except: return "Erro: psutil não instalado."
    
    count = 0
    psapi = ctypes.WinDLL('psapi.dll')
    kernel32 = ctypes.WinDLL('kernel32.dll')
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100
    
    for _ in range(2):
        for proc in psutil.process_iter(['pid']):
            try:
                handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, proc.info['pid'])
                if handle:
                    res = psapi.EmptyWorkingSet(handle)
                    if res:
                        count += 1
                    kernel32.CloseHandle(handle)
            except: continue
            
    return f"Working Set esvaziado brutalmente em {count//2} processos."

def clean_temp_folders():
    paths = [
        os.environ.get('TEMP'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'Temp'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'Prefetch'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'SoftwareDistribution', 'Download')
    ]
    deleted = 0
    errors = 0
    for path in paths:
        if not path or not os.path.exists(path): continue
        for item in os.listdir(path):
            try:
                ip = os.path.join(path, item)
                if os.path.isfile(ip): os.remove(ip)
                else: shutil.rmtree(ip)
                deleted += 1
            except: 
                errors += 1
                continue
    msg = f"Limpeza: {deleted} arquivos removidos."
    if errors > 0:
        msg += f" (Falha em {errors} arquivos em uso)."
    return msg

def flush_dns():
    try:
        r = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
        if r.returncode != 0:
            return f"Aviso DNS: {r.stderr.strip() or r.stdout.strip()}"
        return 'Cache DNS limpo.'
    except Exception as e: return f'Erro DNS API: {e}'

def optimize_drive():
    try:
        r = subprocess.run(['defrag', 'C:', '/O'], capture_output=True, text=True)
        if r.returncode != 0:
            return f"Aviso Disco: {r.stderr.strip() or r.stdout.strip()}"
        return 'Disco otimizado (TRIM/Defrag).'
    except Exception as e: return f'Erro no disco API: {e}'

def clear_event_logs():
    if not is_admin(): return "Aviso: Limpar logs exige Admin."
    try:
        r = subprocess.run(['wevtutil', 'el'], capture_output=True, text=True)
        if r.returncode != 0:
            return f"Falha ao listar logs: {r.stderr.strip()}"
            
        logs = r.stdout.splitlines()
        errors = 0
        for log in logs:
            r2 = subprocess.run(['wevtutil', 'cl', log.strip()], capture_output=True, text=True)
            if r2.returncode != 0: errors += 1
            
        msg = "Logs de eventos limpos."
        if errors > 0: msg += f" (Falhou ao limpar {errors} logs restritos)."
        return msg
    except Exception as e: return f"Erro fatal ao limpar logs: {e}"

def apply_performance_tweaks():
    if not is_admin(): return "Aviso: Tweaks de registro exigem Admin."
    logs = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 1)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MenuShowDelay", 0, winreg.REG_SZ, "50")
            winreg.SetValueEx(key, "AutoEndTasks", 0, winreg.REG_SZ, "1")
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection") as key:
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
    except Exception as e: logs.append(f"Reg Tweaks: {e}")
        
    try:
        r = subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], capture_output=True, text=True)
        if r.returncode != 0: logs.append(f"Powercfg: {r.stderr.strip() or r.stdout.strip()}")
    except Exception as e: logs.append(f"Powercfg API: {e}")
        
    if logs: return "Ajustes de registro aplicados com avisos: " + " | ".join(logs)
    return "Ajustes de registro e energia aplicados."

def reset_network():
    if not is_admin(): return "Aviso: Reset de rede exige Admin."
    logs = []
    try:
        r1 = subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, text=True)
        r2 = subprocess.run(['netsh', 'int', 'ip', 'reset'], capture_output=True, text=True)
        if r1.returncode != 0: logs.append(f"Winsock: {r1.stderr.strip() or r1.stdout.strip()}")
        if r2.returncode != 0: logs.append(f"IP: {r2.stderr.strip() or r2.stdout.strip()}")
    except Exception as e: logs.append(f"Net API: {e}")
    
    if logs: return "Protocolos de rede resetados com avisos: " + " | ".join(logs)
    return "Protocolos de rede resetados sem erros."

def optimize_system(mode="quick"):
    res = []
    if mode == "quick":
        res = [clean_ram(), clean_temp_folders(), flush_dns()]
    elif mode == "advanced":
        res = [clean_ram(), clean_temp_folders(), flush_dns(), optimize_drive()]
    elif mode == "ultimate":
        res = [
            clean_ram(), 
            clean_temp_folders(), 
            flush_dns(), 
            optimize_drive(), 
            clear_event_logs(), 
            apply_performance_tweaks(),
            reset_network()
        ]
    elif mode == "ram_boost":
        res = [
            kill_memory_hogs(),
            clean_ram(),
            restart_explorer(),
            optimize_virtual_memory()
        ]
    elif mode == "god_mode" or mode == "all_in_one":
        res = [
            clean_ram(),
            clear_standby_and_shaders(),
            clean_temp_folders(),
            flush_dns(),
            optimize_network_latency(),
            optimize_drive(),
            clear_event_logs(),
            apply_performance_tweaks(),
            disable_useless_services(),
            disable_vbs_and_visuals(),
            optimize_gpu_scheduling(),
            disable_bloat_and_compression()
        ]
    return '\n'.join(res)

# ═══════════════════════════════════════════════════════════
#  PALETA DE CORES PREMIUM E GUI (antigo main.py)
# ═══════════════════════════════════════════════════════════

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Theme:
    BG_DARK      = "#0a0a0f"
    BG_CARD      = "#12121a"
    BG_CARD_ALT  = "#1a1a2e"
    BORDER       = "#2a2a3e"
    
    ACCENT_BLUE  = "#4f8cff"
    ACCENT_CYAN  = "#00d4ff"
    ACCENT_GREEN = "#00e676"
    ACCENT_RED   = "#ff3d71"
    ACCENT_PURPLE= "#b14dff"
    ACCENT_GOLD  = "#ffd740"
    ACCENT_ORANGE= "#ff6d00"
    
    TEXT_PRIMARY  = "#eaeaff"
    TEXT_SECONDARY= "#8888aa"
    TEXT_MUTED    = "#555577"
    
    QUICK_FG     = "#1e3a5f"
    QUICK_HV     = "#2a5080"
    ADV_FG       = "#1f538d"
    ADV_HV       = "#2a6dbd"
    ULT_FG       = "#8b1a1a"
    ULT_HV       = "#c62828"
    RAM_FG       = "#00873e"
    RAM_HV       = "#00c853"
    GOD_FG       = "#4a148c"
    GOD_HV       = "#7b1fa2"
    ALL_IN_FG    = "#005bb5"
    ALL_IN_HV    = "#0074e4"

class WinRAMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WinRAM Ultimate v2.0")
        self.geometry("1000x750")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_DARK)
        
        # ─── Tipografia ──────────────────────────────────
        self.font_title   = ctk.CTkFont(family="Segoe UI", size=32, weight="bold")
        self.font_subtitle= ctk.CTkFont(family="Segoe UI", size=13)
        self.font_big_num = ctk.CTkFont(family="Consolas", size=56, weight="bold")
        self.font_label   = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.font_btn     = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_btn_sub = ctk.CTkFont(family="Segoe UI", size=10)
        self.font_console = ctk.CTkFont(family="Consolas", size=11)
        self.font_stat    = ctk.CTkFont(family="Consolas", size=14, weight="bold")
        self.font_stat_lbl= ctk.CTkFont(family="Segoe UI", size=10)
        
        # ─── Container Principal ─────────────────────────
        self.main_frame = ctk.CTkFrame(self, fg_color=Theme.BG_DARK, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ═══════════════════════════════════════════════════
        #  HEADER (Titulo + Admin Badge)
        # ═══════════════════════════════════════════════════
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color=Theme.BG_DARK, corner_radius=0, height=80)
        self.header_frame.pack(fill="x", padx=30, pady=(20, 0))
        self.header_frame.pack_propagate(False)
        
        header_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_left.pack(side="left", fill="y")
        
        self.label_title = ctk.CTkLabel(header_left, text="⚡ WinRAM Ultimate", 
                                         font=self.font_title, text_color=Theme.TEXT_PRIMARY)
        self.label_title.pack(anchor="w")
        
        self.label_version = ctk.CTkLabel(header_left, text="v2.0  •  Motor de Otimização do Windows", 
                                           font=self.font_subtitle, text_color=Theme.TEXT_SECONDARY)
        self.label_version.pack(anchor="w")
        
        # Admin Badge
        header_right = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_right.pack(side="right", fill="y", pady=15)
        
        if is_admin():
            badge_color = Theme.ACCENT_GREEN
            badge_text = "🛡️  ADMINISTRADOR"
        else:
            badge_color = Theme.ACCENT_GOLD
            badge_text = "⚠️  MODO LIMITADO"
        
        self.admin_badge = ctk.CTkLabel(header_right, text=badge_text, 
                                         text_color=badge_color,
                                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                         fg_color=Theme.BG_CARD, corner_radius=8,
                                         padx=14, pady=6)
        self.admin_badge.pack(anchor="e")
        
        # ─── Linha divisória ─────────────────────────────
        divider = ctk.CTkFrame(self.main_frame, fg_color=Theme.BORDER, height=1)
        divider.pack(fill="x", padx=30, pady=(15, 0))
        
        # ═══════════════════════════════════════════════════
        #  ÁREA CENTRAL (Stats + Botões lado a lado)
        # ═══════════════════════════════════════════════════
        self.center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_frame.pack(fill="both", expand=True, padx=30, pady=(15, 0))
        self.center_frame.grid_columnconfigure(0, weight=2)
        self.center_frame.grid_columnconfigure(1, weight=3)
        self.center_frame.grid_rowconfigure(0, weight=1)
        
        # ─── PAINEL ESQUERDO: Monitor de RAM ─────────────
        self.stats_panel = ctk.CTkFrame(self.center_frame, fg_color=Theme.BG_CARD, 
                                         corner_radius=16, border_width=1, border_color=Theme.BORDER)
        self.stats_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Titulo do painel
        stats_header = ctk.CTkFrame(self.stats_panel, fg_color="transparent")
        stats_header.pack(fill="x", padx=20, pady=(18, 5))
        
        ctk.CTkLabel(stats_header, text="MONITOR DE MEMÓRIA", 
                     font=self.font_label, text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        
        # Numero gigante da RAM
        self.ram_usage_text = ctk.CTkLabel(self.stats_panel, text="0%", 
                                            font=self.font_big_num, text_color=Theme.ACCENT_CYAN)
        self.ram_usage_text.pack(pady=(10, 0))
        
        # Barra de progresso
        self.ram_bar = ctk.CTkProgressBar(self.stats_panel, width=220, height=10, 
                                           corner_radius=5, progress_color=Theme.ACCENT_CYAN,
                                           fg_color=Theme.BG_CARD_ALT)
        self.ram_bar.pack(pady=(5, 15), padx=30)
        self.ram_bar.set(0)
        
        # Info detalhada
        self.ram_detail = ctk.CTkLabel(self.stats_panel, text="Carregando...", 
                                        font=self.font_stat_lbl, text_color=Theme.TEXT_MUTED)
        self.ram_detail.pack(pady=(0, 10))
        
        # ─── Separador interno ───────────────────────────
        sep = ctk.CTkFrame(self.stats_panel, fg_color=Theme.BORDER, height=1)
        sep.pack(fill="x", padx=20, pady=5)
        
        # Mini Stats (CPU e Disco)
        mini_stats = ctk.CTkFrame(self.stats_panel, fg_color="transparent")
        mini_stats.pack(fill="x", padx=20, pady=(5, 5))
        mini_stats.grid_columnconfigure((0, 1), weight=1)
        
        # CPU
        cpu_frame = ctk.CTkFrame(mini_stats, fg_color=Theme.BG_CARD_ALT, corner_radius=10)
        cpu_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=2)
        ctk.CTkLabel(cpu_frame, text="CPU", font=self.font_stat_lbl, text_color=Theme.TEXT_MUTED).pack(pady=(8,0))
        self.cpu_label = ctk.CTkLabel(cpu_frame, text="0%", font=self.font_stat, text_color=Theme.ACCENT_BLUE)
        self.cpu_label.pack(pady=(0,8))
        
        # Disco
        disk_frame = ctk.CTkFrame(mini_stats, fg_color=Theme.BG_CARD_ALT, corner_radius=10)
        disk_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        ctk.CTkLabel(disk_frame, text="DISCO C:", font=self.font_stat_lbl, text_color=Theme.TEXT_MUTED).pack(pady=(8,0))
        self.disk_label = ctk.CTkLabel(disk_frame, text="0%", font=self.font_stat, text_color=Theme.ACCENT_ORANGE)
        self.disk_label.pack(pady=(0,8))
        
        # ─── Separador ───────────────────────────────────
        sep2 = ctk.CTkFrame(self.stats_panel, fg_color=Theme.BORDER, height=1)
        sep2.pack(fill="x", padx=20, pady=5)
        
        # Botão de Pânico
        self.btn_ram_boost = ctk.CTkButton(
            self.stats_panel, text="⚡  MAXIMIZAR RAM  ⚡", height=42,
            fg_color=Theme.RAM_FG, hover_color=Theme.RAM_HV, text_color="#ffffff",
            font=self.font_btn, corner_radius=10,
            command=lambda: self.start_opt("ram_boost"))
        self.btn_ram_boost.pack(padx=20, pady=(10, 18), fill="x")
        
        # ─── PAINEL DIREITO: Modos de Otimização ────────
        self.modes_panel = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.modes_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self.modes_panel.grid_rowconfigure((0, 1, 2), weight=1)
        self.modes_panel.grid_columnconfigure((0, 1), weight=1)
        
        # Botao Gigante (ALL IN ONE)
        self.btn_all_in = ctk.CTkButton(
            self.modes_panel, text="🚀 1-CLICK OTIMIZAÇÃO TOTAL\n(Executa Todas as Funções)", height=60,
            fg_color=Theme.ALL_IN_FG, hover_color=Theme.ALL_IN_HV, text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), corner_radius=14,
            command=lambda: self.start_opt("all_in_one"))
        self.btn_all_in.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=(5, 10))

        # ─── Card Builder ────────────────────────────────
        def make_mode_card(parent, row, col, icon, title, desc, fg, hv, mode):
            card = ctk.CTkFrame(parent, fg_color=Theme.BG_CARD, corner_radius=14,
                                border_width=1, border_color=Theme.BORDER)
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            card.grid_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(expand=True, fill="both", padx=16, pady=10)
            
            ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=24)).pack(anchor="w")
            ctk.CTkLabel(inner, text=title, font=self.font_btn, 
                        text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(2, 0))
            ctk.CTkLabel(inner, text=desc, font=self.font_btn_sub, 
                        text_color=Theme.TEXT_SECONDARY, wraplength=180, justify="left").pack(anchor="w")
            
            btn = ctk.CTkButton(inner, text="EXECUTAR", height=28, corner_radius=8,
                               fg_color=fg, hover_color=hv, font=self.font_btn_sub,
                               command=lambda: self.start_opt(mode))
            btn.pack(fill="x", pady=(8, 0))
            return btn
        
        self.btn_quick = make_mode_card(
            self.modes_panel, 1, 0,
            "🧹", "RÁPIDO", "Limpa RAM, Temp e DNS em segundos.",
            Theme.QUICK_FG, Theme.QUICK_HV, "quick")
        
        self.btn_adv = make_mode_card(
            self.modes_panel, 1, 1,
            "🔧", "AVANÇADO", "Inclui otimização de disco e defrag.",
            Theme.ADV_FG, Theme.ADV_HV, "advanced")
        
        self.btn_ult = make_mode_card(
            self.modes_panel, 2, 0,
            "🔥", "ULTIMATE", "Registro, energia, rede e logs.",
            Theme.ULT_FG, Theme.ULT_HV, "ultimate")
        
        self.btn_god = make_mode_card(
            self.modes_panel, 2, 1,
            "👑", "GOD MODE", "VBS, GPU, TCP, MMCSS, IAs e mais.",
            Theme.GOD_FG, Theme.GOD_HV, "god_mode")
        
        # ═══════════════════════════════════════════════════
        #  CONSOLE (Parte inferior)
        # ═══════════════════════════════════════════════════
        self.console_outer = ctk.CTkFrame(self.main_frame, fg_color=Theme.BG_CARD, 
                                           corner_radius=14, border_width=1, border_color=Theme.BORDER,
                                           height=180)
        self.console_outer.pack(fill="x", padx=30, pady=(15, 20))
        self.console_outer.pack_propagate(False)
        
        # Console Header
        console_header = ctk.CTkFrame(self.console_outer, fg_color="transparent")
        console_header.pack(fill="x", padx=16, pady=(10, 0))
        
        ctk.CTkLabel(console_header, text="CONSOLE DE OTIMIZAÇÃO E LOGS DE ERRO", 
                     font=self.font_label, text_color=Theme.TEXT_SECONDARY).pack(side="left")
        
        self.status_dot = ctk.CTkLabel(console_header, text="●  PRONTO", 
                                        font=self.font_stat_lbl, text_color=Theme.ACCENT_GREEN)
        self.status_dot.pack(side="right")
        
        # Console Text
        self.console_text = ctk.CTkTextbox(self.console_outer, font=self.font_console,
                                            fg_color=Theme.BG_DARK, text_color=Theme.ACCENT_GREEN,
                                            corner_radius=8, border_width=0, height=120,
                                            activate_scrollbars=True, wrap="word")
        self.console_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        self.console_text.insert("end", "  > Sistema pronto. Selecione um modo de otimização.\n")
        self.console_text.configure(state="disabled")
        
        # ─── Iniciar Loop de Monitoramento ───────────────
        self.update_stats()

    # ═══════════════════════════════════════════════════════
    #  MONITORAMENTO EM TEMPO REAL
    # ═══════════════════════════════════════════════════════
    def update_stats(self):
        # RAM
        ram = psutil.virtual_memory()
        percent = ram.percent
        used_gb = ram.used / (1024**3)
        total_gb = ram.total / (1024**3)
        
        self.ram_usage_text.configure(text=f"{percent:.0f}%")
        self.ram_bar.set(percent / 100)
        self.ram_detail.configure(text=f"{used_gb:.1f} GB / {total_gb:.1f} GB usados")
        
        if percent > 85:
            self.ram_bar.configure(progress_color=Theme.ACCENT_RED)
            self.ram_usage_text.configure(text_color=Theme.ACCENT_RED)
        elif percent > 65:
            self.ram_bar.configure(progress_color=Theme.ACCENT_GOLD)
            self.ram_usage_text.configure(text_color=Theme.ACCENT_GOLD)
        else:
            self.ram_bar.configure(progress_color=Theme.ACCENT_CYAN)
            self.ram_usage_text.configure(text_color=Theme.ACCENT_CYAN)
        
        # CPU
        cpu = psutil.cpu_percent(interval=0)
        self.cpu_label.configure(text=f"{cpu:.0f}%")
        
        # Disco
        try:
            disk = psutil.disk_usage('C:\\')
            self.disk_label.configure(text=f"{disk.percent}%")
        except: pass
        
        self.after(1500, self.update_stats)

    # ═══════════════════════════════════════════════════════
    #  EXECUÇÃO DE OTIMIZAÇÃO
    # ═══════════════════════════════════════════════════════
    def start_opt(self, mode):
        self.set_buttons_state("disabled")
        self.status_dot.configure(text="●  EXECUTANDO...", text_color=Theme.ACCENT_GOLD)
        
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        mode_names = {
            "quick": "RÁPIDO", "advanced": "AVANÇADO", "ultimate": "ULTIMATE",
            "ram_boost": "RAM BOOST", "god_mode": "GOD MODE", "all_in_one": "1-CLICK OTIMIZAÇÃO TOTAL"
        }
        self.console_text.insert("end", f"  > Iniciando modo {mode_names.get(mode, mode.upper())}...\n")
        self.console_text.insert("end", f"  > Aguarde enquanto o sistema é otimizado e os serviços analisam logs...\n\n")
        self.console_text.configure(state="disabled")
        
        threading.Thread(target=self.run_task, args=(mode,), daemon=True).start()

    def set_buttons_state(self, state):
        self.btn_quick.configure(state=state)
        self.btn_adv.configure(state=state)
        self.btn_ult.configure(state=state)
        self.btn_ram_boost.configure(state=state)
        self.btn_god.configure(state=state)
        self.btn_all_in.configure(state=state)

    def run_task(self, mode):
        try:
            time.sleep(0.5)
            res = optimize_system(mode=mode)
            lines = res.split("\n")
            
            self.console_text.configure(state="normal")
            self.console_text.delete("1.0", "end")
            self.console_text.insert("end", "  ╔══════════════════════════════════════════╗\n")
            self.console_text.insert("end", "  ║   ✨  OTIMIZAÇÃO CONCLUÍDA COM SUCESSO   ║\n")
            self.console_text.insert("end", "  ╚══════════════════════════════════════════╝\n\n")
            for line in lines:
                if "Erro" in line or "Aviso" in line or "Acesso Negado" in line or "Falhou" in line or "falhou" in line:
                    self.console_text.insert("end", f"  [!] {line}\n", "error_tag")
                else:
                    self.console_text.insert("end", f"  ✓  {line}\n")
                    
            self.console_text.tag_config("error_tag", foreground=Theme.ACCENT_ORANGE)
            self.console_text.configure(state="disabled")
            self.console_text.see("end")
            
            self.status_dot.configure(text="●  CONCLUÍDO", text_color=Theme.ACCENT_GREEN)
        except Exception as e:
            self.console_text.configure(state="normal")
            self.console_text.delete("1.0", "end")
            self.console_text.insert("end", f"  ✗  ERRO CRÍTICO NA APLICAÇÃO: {e}\n", "error_critical")
            self.console_text.tag_config("error_critical", foreground=Theme.ACCENT_RED)
            self.console_text.configure(state="disabled")
            self.status_dot.configure(text="●  ERRO", text_color=Theme.ACCENT_RED)
        finally:
            self.set_buttons_state("normal")


if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    app = WinRAMApp()
    app.mainloop()

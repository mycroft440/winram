import os
import shutil
import ctypes
import platform
import subprocess
import winreg
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def clean_ram():
    try:
        import psutil
    except ImportError:
        return "Erro: psutil nao instalado."
    count = 0
    psapi = ctypes.WinDLL('psapi.dll')
    kernel32 = ctypes.WinDLL('kernel32.dll')
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100
    for proc in psutil.process_iter(['pid']):
        try:
            handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, proc.info['pid'])
            if handle:
                psapi.EmptyWorkingSet(handle)
                kernel32.CloseHandle(handle)
                count += 1
        except: continue
    return f"RAM otimizada em {count} processos."

def clean_temp_folders():
    paths = [
        os.environ.get('TEMP'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'Temp'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'Prefetch'),
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'SoftwareDistribution', 'Download')
    ]
    deleted = 0
    for path in paths:
        if not path or not os.path.exists(path): continue
        for item in os.listdir(path):
            try:
                ip = os.path.join(path, item)
                if os.path.isfile(ip): os.remove(ip)
                else: shutil.rmtree(ip)
                deleted += 1
            except: continue
    return f"Limpeza: {deleted} arquivos removidos."

def flush_dns():
    try:
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, check=True)
        return 'Cache DNS limpo.'
    except: return 'Erro DNS.'

def optimize_drive():
    try:
        subprocess.run(['defrag', 'C:', '/O'], capture_output=True, text=True, check=True)
        return 'Disco otimizado (TRIM/Defrag).'
    except: return 'Erro no disco.'

def clear_event_logs():
    if not is_admin(): return "Aviso: Limpar logs exige Admin."
    try:
        # Get all logs
        logs = subprocess.run(['wevtutil', 'el'], capture_output=True, text=True).stdout.splitlines()
        for log in logs:
            subprocess.run(['wevtutil', 'cl', log.strip()], capture_output=True)
        return "Logs de eventos limpos."
    except: return "Erro ao limpar logs."

def apply_performance_tweaks():
    if not is_admin(): return "Aviso: Tweaks de registro exigem Admin."
    results = []
    try:
        # 1. System Responsiveness
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 1)
        
        # 2. Menu Delay
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MenuShowDelay", 0, winreg.REG_SZ, "50")
            winreg.SetValueEx(key, "AutoEndTasks", 0, winreg.REG_SZ, "1")
            
        # 3. Disable Telemetry
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection") as key:
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            
        # 4. Power Plan (High Performance)
        # 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c is High Performance GUID
        subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], capture_output=True)
        
        return "Ajustes de registro e energia aplicados."
    except Exception as e:
        return f"Erro nos tweaks: {e}"

def reset_network():
    if not is_admin(): return "Aviso: Reset de rede exige Admin."
    try:
        subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True)
        subprocess.run(['netsh', 'int', 'ip', 'reset'], capture_output=True)
        return "Protocolos de rede resetados."
    except: return "Erro no reset de rede."

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
    return '\n'.join(res)
import os
import shutil
import ctypes
import platform
import subprocess
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
    return f"Memoria otimizada em {count} processos."

def clean_temp_folders():
    paths = [
        os.environ.get('TEMP'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'Temp'), 
        os.path.join(os.environ.get('SystemRoot', 'C:\\'), 'Windows', 'Prefetch')
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
    return f"Limpeza concluida: {deleted} itens removidos."

def flush_dns():
    try:
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, check=True)
        return 'Cache DNS limpo com sucesso.'
    except: return 'Falha ao limpar DNS.'

def optimize_drive():
    try:
        subprocess.run(['defrag', 'C:', '/O'], capture_output=True, text=True, check=True)
        return 'Otimizacao de disco (TRIM/Defrag) concluida.'
    except: return 'Falha ao otimizar disco.'

def optimize_system(full=False):
    res = [clean_ram(), clean_temp_folders(), flush_dns()]
    if full: res.append(optimize_drive())
    return '\n'.join(res)
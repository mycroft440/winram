import psutil
import ctypes
import time
import sys
import os

# Mutex para evitar múltiplas instâncias
mutex_name = "WinRAM_Daemon_AutoClean_Mutex"
kernel32 = ctypes.windll.kernel32
mutex = kernel32.CreateMutexW(None, False, mutex_name)
last_error = kernel32.GetLastError()
if last_error == 183: # ERROR_ALREADY_EXISTS
    sys.exit(0)

# Lista de jogos monitorados (em minúsculas)
GAMES_LIST = ["cs2.exe", "valorant.exe", "gta5.exe", "cyberpunk2077.exe", "dota2.exe", "leagueoflegends.exe", "r5apex.exe", "overwatch.exe", "bf2042.exe"]
GAME_MODE_ACTIVE = False
ACTIVE_GAME_PID = None

def clean_ram():
    psapi = ctypes.WinDLL('psapi.dll')
    k32 = ctypes.WinDLL('kernel32.dll')
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100

    for _ in range(2):
        for proc in psutil.process_iter(['pid']):
            try:
                handle = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, proc.info['pid'])
                if handle:
                    psapi.EmptyWorkingSet(handle)
                    k32.CloseHandle(handle)
            except:
                continue

def check_games_running():
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in GAMES_LIST:
                return proc
        except:
            continue
    return None

def apply_game_boost(proc):
    try:
        if sys.platform == 'win32':
            proc.nice(psutil.HIGH_PRIORITY_CLASS)
    except:
        pass

def main():
    global GAME_MODE_ACTIVE, ACTIVE_GAME_PID
    while True:
        try:
            game_proc = check_games_running()
            if game_proc and not GAME_MODE_ACTIVE:
                apply_game_boost(game_proc)
                GAME_MODE_ACTIVE = True
                ACTIVE_GAME_PID = game_proc.pid
                clean_ram()
            elif not game_proc and GAME_MODE_ACTIVE:
                GAME_MODE_ACTIVE = False
                ACTIVE_GAME_PID = None

            usage = psutil.virtual_memory().percent
            if usage >= 65:
                clean_ram()
                time.sleep(60)
            else:
                time.sleep(10)
        except Exception:
            time.sleep(10)

if __name__ == "__main__":
    main()
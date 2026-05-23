from pathlib import Path
import concurrent.futures
import ctypes
import customtkinter as ctk
import math
import os
import platform
import psutil
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import winreg


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
        r = subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], capture_output=True, text=True, creationflags=0x08000000)
        subprocess.Popen(['explorer.exe'])
        if r.returncode != 0 and "not found" not in r.stderr.lower():
            return f"Aviso ao matar explorer: {r.stderr.strip()}"
        return "Windows Shell reiniciado (Vazamento de RAM contido)."
    except Exception as e:
        return f"Falha ao reiniciar o Windows Shell: {e}"

def optimize_virtual_memory():
    if not is_admin(): return "Aviso: Otimizar Memória Virtual exige Admin."
    try:
        # Usa CIM Instance em vez de WMI para evitar erro "Provider is not capable"
        script = "Get-CimInstance -ClassName Win32_ComputerSystem | Set-CimInstance -Property @{AutomaticManagedPagefile=$True}"
        r = subprocess.run(['powershell', '-Command', script], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0:
            # Fallback para o metodo WMI tradicional
            script_fb = "$sys = Get-WmiObject Win32_ComputerSystem -EnableAllPrivileges; $sys.AutomaticManagedPagefile = $true; $sys.Put()"
            r_fb = subprocess.run(['powershell', '-Command', script_fb], capture_output=True, text=True, creationflags=0x08000000)
            if r_fb.returncode != 0:
                return f"Erro ao configurar Pagefile: {r_fb.stderr.strip()}"
        return "Memória Virtual (Pagefile) transferida e otimizada."
    except Exception as e:
        return f"Erro crítico ao configurar Memória Virtual: {e}"

def disable_useless_services():
    services = ["SysMain", "DiagTrack", "WerSvc", "Spooler", "DoSvc", "XboxGipSvc"]
    logs = []
    for svc in services:
        try:
            r1 = subprocess.run(['sc', 'config', svc, 'start=', 'disabled'], capture_output=True, text=True, creationflags=0x08000000)
            r2 = subprocess.run(['net', 'stop', svc], capture_output=True, text=True, creationflags=0x08000000)
            if r1.returncode != 0 and "Access is denied" in r1.stderr:
                logs.append(f"[sc {svc}] Acesso Negado (Sem Admin)")
            elif r1.returncode != 0 and "OpenService FAILED 1060" not in r1.stdout:
                logs.append(f"[sc {svc}] {r1.stderr.strip() or r1.stdout.strip()}")
            
            if r2.returncode != 0 and "not started" not in r2.stderr.lower() and "não foi iniciado" not in r2.stderr.lower():
                logs.append(f"[net stop {svc}] {r2.stderr.strip() or r2.stdout.strip()}")
        except Exception as e:
            logs.append(f"[Falha API {svc}]: {e}")

    try:
        tasks = [r'\Microsoft\Windows\Customer Experience Improvement Program\Consolidator',
             r'\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip']
        for t in tasks:
            subprocess.run(['schtasks', '/Change', '/TN', t, '/Disable'], capture_output=True, creationflags=0x08000000)
    except Exception as e: logs.append(f"Schtasks: {e}")

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

    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management") as key:
            winreg.SetValueEx(key, "FeatureSettingsOverride", 0, winreg.REG_DWORD, 3)
            winreg.SetValueEx(key, "DisablePagingExecutive", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "FeatureSettingsOverrideMask", 0, winreg.REG_DWORD, 3)
    except Exception as e: logs.append(f"Spectre Mitigations: {e}")

    if logs: return "Otimização Visual/VBS/Spectre concluída com erros: " + " | ".join(logs)
    return "VBS, Efeitos Visuais e Mitigações Spectre desativados (Max CPU)."
    
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects") as key:
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
    except Exception as e: logs.append(f"Visuais falhou: {e}")
    
    if logs: return "Otimização Visual/VBS concluída com erros: " + " | ".join(logs)
    return "VBS (Virtualization) e Efeitos Visuais otimizados."

def optimize_amd_gpu():
    if not is_admin(): return "Aviso: Otimizar AMD GPU exige Admin."
    try:
        ps_script = r'''
        $paths = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0*" -ErrorAction SilentlyContinue
        $disabled = 0
        foreach ($p in $paths) {
            $val = Get-ItemProperty -Path $p.PSPath -Name "EnableUlps" -ErrorAction SilentlyContinue
            if ($null -ne $val) {
                Set-ItemProperty -Path $p.PSPath -Name "EnableUlps" -Value 0 -Type DWord -ErrorAction SilentlyContinue
                Set-ItemProperty -Path $p.PSPath -Name "PP_SclkDeepSleepDisable" -Value 1 -Type DWord -ErrorAction SilentlyContinue
                $disabled++
            }
        }
        Write-Output $disabled
        '''
        r = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True, creationflags=0x08000000)
        count = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
        if count > 0:
            return f"AMD ULPS desativado em {count} placa(s). FPS e Stuttering otimizados!"
        return "Nenhuma placa AMD com ULPS encontrada. Tudo certo."
    except Exception as e:
        return f"Erro ao tentar otimizar AMD GPU: {e}"

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
    except Exception as e: logs.append(f"Games Priority: {e}")

    if logs: return "Otimizacao GPU concluida com erros: " + " | ".join(logs)
    return "GPU Scheduling otimizado."

def optimize_network_latency():
    logs = []
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile") as key:
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xffffffff)
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
    except Exception as e: logs.append(f"Throttling Registry: {e}")

    try:
        r1 = subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'], capture_output=True, text=True, creationflags=0x08000000)
        r2 = subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'ecncapability=disabled'], capture_output=True, text=True, creationflags=0x08000000)
        
        # BBR/CUBIC Congestion Provider
        r3 = subprocess.run(['netsh', 'int', 'tcp', 'set', 'supplemental', 'template=internet', 'congestionprovider=cubic'], capture_output=True, text=True, creationflags=0x08000000)
        
        if r1.returncode != 0: logs.append(f"TCP AutoTuning: {r1.stderr.strip() or r1.stdout.strip()}")
        if r2.returncode != 0: logs.append(f"TCP ECN: {r2.stderr.strip() or r2.stdout.strip()}")
        if r3.returncode != 0: logs.append(f"TCP CUBIC: {r3.stderr.strip() or r3.stdout.strip()}")
    except Exception as e: logs.append(f"Netsh API: {e}")

    try:
        qos_ps = "New-NetQosPolicy -Name 'GamingQoS' -AppPathNameMatchCondition '*.exe' -DSCPAction 46 -NetworkProfile All -PriorityValue8021Action 7 -ErrorAction SilentlyContinue"
        subprocess.run(['powershell', '-Command', qos_ps], capture_output=True, creationflags=0x08000000)
    except Exception as e: logs.append(f"QoS falhou: {e}")

    if logs: return "Rede otimizada com avisos: " + " | ".join(logs)
    return "Throttling de rede removido e TCP/IP/CUBIC/QoS otimizados (Ping)."
def disable_bloat_and_compression():
    logs = []
    try:
        r = subprocess.run(['powershell', '-Command', 'Disable-MMAgent -mc'], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0 and "não pode ser iniciado" not in r.stderr and "cannot be started" not in r.stderr and "nÆo pode ser iniciado" not in r.stderr:
            logs.append(f"MMAgent: {r.stderr.strip()}")
    except Exception as e: logs.append(f"MMAgent API: {e}")
    
    try:
        bloat_apps = [
            "Microsoft.BingNews",
            "Microsoft.MicrosoftSolitaireCollection",
            "Microsoft.Todos",
            "Microsoft.SkypeApp",
            "Microsoft.ZuneVideo"
        ]
        for app in bloat_apps:
            cmd = f'Get-AppxPackage *{app}* | Remove-AppxPackage'
            subprocess.run(['powershell', '-Command', cmd], creationflags=0x08000000)
    except Exception as e: logs.append(f"Bloatware API: {e}")
        
    try:
        r = subprocess.run(['powercfg', '/h', 'off'], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0: logs.append(f"Hibernação: {r.stderr.strip() or r.stdout.strip()}")
    except Exception as e: logs.append(f"PowerCfg API: {e}")
        
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\WindowsCopilot") as key:
            winreg.SetValueEx(key, "TurnOffWindowsCopilot", 0, winreg.REG_DWORD, 1)
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Edge") as key:
            winreg.SetValueEx(key, "BackgroundModeEnabled", 0, winreg.REG_DWORD, 0)
    except Exception as e: logs.append(f"Registry Bloat: {e}")
            
    if logs: return "Bloatwares bloqueados com avisos: " + " | ".join(logs)
    return "Compressão de RAM, Fast Startup, Bloatwares e IAs bloqueados."

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
    errors = []
    
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
        r = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0:
            return f"Aviso DNS: {r.stderr.strip() or r.stdout.strip()}"
        return 'Cache DNS limpo.'
    except Exception as e: return f'Erro DNS API: {e}'

def optimize_drive():
    try:
        r = subprocess.run(['defrag', 'C:', '/O'], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0:
            return f"Aviso Disco: {r.stderr.strip() or r.stdout.strip()}"
        return 'Disco otimizado (TRIM/Defrag).'
    except Exception as e: return f'Erro no disco API: {e}'

def clear_event_logs():
    if not is_admin(): return "Aviso: Limpar logs exige Admin."
    try:
        r = subprocess.run(['wevtutil', 'el'], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0:
            return f"Falha ao listar logs: {r.stderr.strip()}"

        logs = [log.strip() for log in r.stdout.splitlines() if log.strip()]
        
        def _clear_log(log_name):
            r2 = subprocess.run(['wevtutil', 'cl', log_name], capture_output=True, text=True, creationflags=0x08000000)
            return r2.returncode != 0

        errors = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(_clear_log, logs)
            errors = sum(results)

        msg = "Logs de eventos limpos."
        if errors > 0: msg += f" (Falhou ao limpar {errors} logs restritos)."
        return msg
    except Exception as e: return f"Erro fatal ao limpar logs: {e}"
def apply_performance_tweaks():
    if not is_admin(): return "Aviso: Tweaks de registro exigem Admin."
    logs = []
    def _safe_reg(func):
        try: func()
        except: pass

    def t1():
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 0, winreg.KEY_SET_VALUE) as key: winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 1)
    _safe_reg(t1)

    def t2():
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MenuShowDelay", 0, winreg.REG_SZ, "50")
            winreg.SetValueEx(key, "AutoEndTasks", 0, winreg.REG_SZ, "1")
    _safe_reg(t2)

    def t3():
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection") as key: winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
    _safe_reg(t3)

    # Disable MPO (Multi-Plane Overlay) to fix stuttering/black screens on AMD/NVIDIA
    def t_mpo():
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm") as key: winreg.SetValueEx(key, "OverlayTestMode", 0, winreg.REG_DWORD, 5)
    _safe_reg(t_mpo)

    # Disable GameDVR overhead
    def t_gamedvr():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore") as key: winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR") as key: winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_DWORD, 0)
    _safe_reg(t_gamedvr)

    def t4():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key: winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0)
    _safe_reg(t4)

    def t5():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM") as key: winreg.SetValueEx(key, "EnableAeroPeek", 0, winreg.REG_DWORD, 0)
    _safe_reg(t5)

    def t6():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects") as key: winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 3)
    _safe_reg(t6)

    def t7():
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
            winreg.SetValueEx(key, "TaskbarDa", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "TaskbarMn", 0, winreg.REG_DWORD, 0)
    _safe_reg(t7)

    try:
        r = subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], capture_output=True, text=True, creationflags=0x08000000)
        # Core Unparking
        subprocess.run(['powercfg', '-setacvalueindex', 'scheme_current', 'sub_processor', '0cc5b647-c1df-4637-891a-dec35c318583', '100'], capture_output=True, text=True, creationflags=0x08000000)
        # System Cooling Policy (1 = Active)
        subprocess.run(['powercfg', '-setacvalueindex', 'scheme_current', 'sub_processor', '94d3a615-a899-4ac5-ae2b-e4d8f634367f', '1'], creationflags=0x08000000)
        # Wireless Adapter Settings (0 = Max Performance)
        subprocess.run(['powercfg', '-setacvalueindex', 'scheme_current', '19cbb8fa-5279-450e-9fac-8a3d5fedd0c1', '12bbebe6-58d6-4636-95bb-3217ef867c1a', '0'], creationflags=0x08000000)
        # USB Selective Suspend (0 = Disabled)
        subprocess.run(['powercfg', '-setacvalueindex', 'scheme_current', '2a737441-1930-4402-8d77-b2bebba308a3', '48e6b7a6-50f5-4782-a5d4-53bb8f07e226', '0'], creationflags=0x08000000)
        # PCI Express Link State Power Management (0 = Off)
        subprocess.run(['powercfg', '-setacvalueindex', 'scheme_current', '501a4d13-42af-4429-9fd1-a8218c268e20', 'ee12f906-d277-404b-b6da-e5fa1a576df5', '0'], creationflags=0x08000000)
        subprocess.run(['powercfg', '-setactive', 'scheme_current'], capture_output=True, text=True, creationflags=0x08000000)
        if r.returncode != 0: logs.append(f"Powercfg: {r.stderr.strip() or r.stdout.strip()}")
    except Exception as e: logs.append(f"Powercfg API: {e}")

    if logs: return "Ajustes de registro aplicados com avisos: " + " | ".join(logs)
    return "Ajustes de registro, energia e Core Unparking aplicados."
    if logs: return "Ajustes de registro aplicados com avisos: " + " | ".join(logs)
    return "Ajustes de registro e energia aplicados."

def reset_network():
    if not is_admin(): return "Aviso: Reset de rede exige Admin."
    logs = []
    try:
        r1 = subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, text=True, creationflags=0x08000000)
        r2 = subprocess.run(['netsh', 'int', 'ip', 'reset'], capture_output=True, text=True, creationflags=0x08000000)
        if r1.returncode != 0: logs.append(f"Winsock: {r1.stderr.strip() or r1.stdout.strip()}")
        if r2.returncode != 0: logs.append(f"IP: {r2.stderr.strip() or r2.stdout.strip()}")
    except Exception as e: logs.append(f"Net API: {e}")
    
    if logs: return "Protocolos de rede resetados com avisos: " + " | ".join(logs)
    return "Protocolos de rede resetados sem erros."

def enable_storage_sense_and_boot():
    if not is_admin(): return "Aviso: Funcionalidades de disco/boot exigem Admin."
    logs = []
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy") as key:
            winreg.SetValueEx(key, "01", 0, winreg.REG_DWORD, 1) # Enable Storage Sense
        subprocess.run(['bcdedit', '/timeout', '3'], capture_output=True, text=True, creationflags=0x08000000)
    except Exception as e:
        logs.append(str(e))
    
    if logs: return "Storage Sense/Boot aplicados com erros: " + str(logs)
    return "Storage Sense ativado e Boot Timeout reduzido para 3s."

def repair_system():
    if not is_admin(): return "Aviso: Reparo de Sistema exige Admin."
    try:
        # Assincrono em nova janela
        script = "echo Iniciando Reparo do Sistema (DISM e SFC). Por favor, aguarde, isso pode demorar varios minutos... && sfc /scannow && DISM /Online /Cleanup-Image /RestoreHealth && echo Concluido! && pause"
        subprocess.Popen(['cmd', '/c', script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        return "Processo de Reparo de Imagem (SFC/DISM) iniciado em segunda plano."
    except Exception as e:
        return f"Falha ao iniciar reparo: {e}"

def optimize_system(mode="quick"):
    tasks = []
    if mode == "quick":
        tasks = [clean_ram, clean_temp_folders, flush_dns]
    elif mode == "advanced":
        tasks = [clean_ram, clean_temp_folders, flush_dns, optimize_drive]
    elif mode == "ultimate":
        tasks = [clean_ram, clean_temp_folders, flush_dns, optimize_drive,
                  clear_event_logs, apply_performance_tweaks, reset_network, enable_storage_sense_and_boot]
    elif mode == "ram_boost":
        tasks = [kill_memory_hogs, clean_ram, restart_explorer, optimize_virtual_memory]
    elif mode == "opt_limpeza":
        tasks = [clean_ram, clean_temp_folders, clear_standby_and_shaders, clear_event_logs, kill_memory_hogs]
    elif mode == "opt_rede":
        tasks = [flush_dns, optimize_network_latency, reset_network]
    elif mode == "opt_gpu_cpu":
        tasks = [optimize_amd_gpu, optimize_gpu_scheduling, apply_performance_tweaks]
    elif mode == "opt_computador":
        tasks = [disable_useless_services, disable_vbs_and_visuals, disable_bloat_and_compression, enable_storage_sense_and_boot, optimize_drive, restart_explorer, repair_system]
    elif mode == "god_mode" or mode == "all_in_one":
        tasks = [clean_ram, clear_standby_and_shaders, clean_temp_folders, flush_dns,
                  optimize_network_latency, optimize_drive, clear_event_logs,
                  apply_performance_tweaks, disable_useless_services, disable_vbs_and_visuals,
                  optimize_gpu_scheduling, optimize_amd_gpu, disable_bloat_and_compression, enable_storage_sense_and_boot, repair_system]


    states = check_states()
    def _run_task_with_check(t):
        if states.get(t.__name__) == True:
            return f"[PULADO] A configuração '{t.__name__}' já estava otimizada."
        return t()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_run_task_with_check, t): t for t in tasks}
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result()
                if res: yield res
            except Exception as e:
                yield f"Erro na tarefa: {e}"



ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --------------------------------------------------------------------------------
#  PALETA DE CORES PREMIUM
# --------------------------------------------------------------------------------
def check_states():
    """Retorna um dicionario com o estado de otimizacao das funcoes trackeaveis"""
    states = {}
    
    # 1. apply_performance_tweaks (MPO)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm") as key:
            val, _ = winreg.QueryValueEx(key, "OverlayTestMode")
            states["apply_performance_tweaks"] = (val == 5)
    except: states["apply_performance_tweaks"] = False

    # 2. optimize_gpu_scheduling
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers") as key:
            val, _ = winreg.QueryValueEx(key, "HwSchMode")
            states["optimize_gpu_scheduling"] = (val == 2)
    except: states["optimize_gpu_scheduling"] = False

    # 3. disable_vbs_and_visuals
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management") as key:
            val, _ = winreg.QueryValueEx(key, "FeatureSettingsOverride")
            states["disable_vbs_and_visuals"] = (val == 3)
    except: states["disable_vbs_and_visuals"] = False

    # 4. enable_storage_sense_and_boot
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy") as key:
            val, _ = winreg.QueryValueEx(key, "01")
            states["enable_storage_sense_and_boot"] = (val == 1)
    except: states["enable_storage_sense_and_boot"] = False

    # 5. disable_useless_services (SysMain)
    try:
        r = subprocess.run(['sc', 'query', 'SysMain'], capture_output=True, text=True, creationflags=0x08000000)
        states["disable_useless_services"] = ("1060" in r.stdout or "STOPPED" in r.stdout)
    except: states["disable_useless_services"] = False

    # 6. optimize_amd_gpu
    try:
        ps_script = r'''
        $paths = Get-ChildItem -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0*" -ErrorAction SilentlyContinue
        $is_opt = $false
        foreach ($p in $paths) {
            $ulps = Get-ItemProperty -Path $p.PSPath -Name "EnableUlps" -ErrorAction SilentlyContinue
            if ($null -ne $ulps -and $ulps.EnableUlps -eq 0) { $is_opt = $true; break }
        }
        Write-Output $is_opt
        '''
        r = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True, creationflags=0x08000000)
        states["optimize_amd_gpu"] = ("True" in r.stdout)
    except: states["optimize_amd_gpu"] = False

    # 7. disable_bloat_and_compression
    try:
        ps_script = "(Get-MMAgent).MemoryCompression"
        r = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True, creationflags=0x08000000)
        states["disable_bloat_and_compression"] = ("False" in r.stdout)
    except: states["disable_bloat_and_compression"] = False

    # 8. optimize_network_latency
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile") as key:
            val, _ = winreg.QueryValueEx(key, "NetworkThrottlingIndex")
            states["optimize_network_latency"] = (val == 0xffffffff)
    except: states["optimize_network_latency"] = False

    # 9. optimize_virtual_memory
    try:
        ps_script = "(Get-CimInstance -ClassName Win32_ComputerSystem).AutomaticManagedPagefile"
        r = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True, creationflags=0x08000000)
        states["optimize_virtual_memory"] = ("True" in r.stdout)
    except: states["optimize_virtual_memory"] = False

    return states

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
        window_width = 900
        window_height = 640
        self.geometry(f"{window_width}x{window_height}")
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"+{center_x}+{center_y}")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_DARK)
        
        # ------ Tipografia ---
        self.font_title   = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        self.font_subtitle= ctk.CTkFont(family="Segoe UI", size=13)
        self.font_big_num = ctk.CTkFont(family="Consolas", size=56, weight="bold")
        self.font_label   = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.font_btn     = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_btn_sub = ctk.CTkFont(family="Segoe UI", size=10)
        self.font_console = ctk.CTkFont(family="Consolas", size=11)
        self.font_stat    = ctk.CTkFont(family="Consolas", size=14, weight="bold")
        self.font_stat_lbl= ctk.CTkFont(family="Segoe UI", size=10)
        
        # ------ Container Principal ---
        self.main_frame = ctk.CTkFrame(self, fg_color=Theme.BG_DARK, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # --------------------------------------------------------------------------------
        #  HEADER (Titulo + Admin Badge)
        # --------------------------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color=Theme.BG_DARK, corner_radius=0, height=80)
        self.header_frame.pack(fill="x", padx=30, pady=(5, 0))
        self.header_frame.pack_propagate(False)
        
        header_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_left.pack(side="left", fill="y")
        
        self.label_title = ctk.CTkLabel(header_left, text="🚀 WinRAM Ultimate", 
                                         font=self.font_title, text_color=Theme.TEXT_PRIMARY)
        self.label_title.pack(anchor="w")
        
        self.label_version = ctk.CTkLabel(header_left, text="v2.0  ⚡  Motor de Otimização do Windows", 
                                           font=self.font_subtitle, text_color=Theme.TEXT_SECONDARY)
        self.label_version.pack(anchor="w")
        

        
        # ------ Linha divisória ---
        divider = ctk.CTkFrame(self.main_frame, fg_color=Theme.BORDER, height=1)
        divider.pack(fill="x", padx=30, pady=(15, 0))
        
        # --------------------------------------------------------------------------------
        #  ÁÁREA CENTRAL (Stats + Botões lado a lado)
        # --------------------------------------------------------------------------------
        self.center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_frame.pack(fill="both", expand=True, padx=30, pady=(5, 0))
        self.center_frame.grid_columnconfigure(0, weight=2)
        self.center_frame.grid_columnconfigure(1, weight=3)
        self.center_frame.grid_rowconfigure(0, weight=1)
        
        # ------ PAINEL ESQUERDO: Monitor de RAM 
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
        
        # ------ Separador interno ---
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
        
        # ------ Separador ---
        sep2 = ctk.CTkFrame(self.stats_panel, fg_color=Theme.BORDER, height=1)
        sep2.pack(fill="x", padx=20, pady=5)
        
        # Botão de Pânico
        self.btn_ram_boost = ctk.CTkButton(
            self.stats_panel, text="⚡  MAXIMIZAR RAM  ⚡", height=42,
            fg_color=Theme.RAM_FG, hover_color=Theme.RAM_HV, text_color="#ffffff",
            font=self.font_btn, corner_radius=10,
            command=lambda: self.start_opt("ram_boost"))
        self.btn_ram_boost.pack(padx=20, pady=(10, 18), fill="x")
        
        # ------ PAINEL DIREITO: Sistema de Abas com Funcoes Individuais ---
        self.modes_panel = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.modes_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        # Botao Gigante (MODO LORD) no topo
        self.btn_all_in = ctk.CTkButton(
            self.modes_panel, text="👑  MODO LORD  (Executar Tudo)", height=48,
            fg_color=Theme.GOD_FG, hover_color=Theme.GOD_HV, text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), corner_radius=12,
            command=lambda: self.start_opt("god_mode"))
        self.btn_all_in.pack(fill="x", padx=5, pady=(5, 8))

        # Tabview com categorias
        self.tabview = ctk.CTkTabview(self.modes_panel, fg_color=Theme.BG_CARD,
                                       segmented_button_fg_color=Theme.BG_CARD_ALT,
                                       segmented_button_selected_color=Theme.ACCENT_BLUE,
                                       segmented_button_unselected_color=Theme.BG_CARD_ALT,
                                       corner_radius=14, border_width=1, border_color=Theme.BORDER)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        tab_limpeza   = self.tabview.add("🧹 Limpeza")
        tab_rede      = self.tabview.add("🌐 Rede")
        tab_gpu_cpu   = self.tabview.add("🎮 GPU/CPU")
        tab_computador= self.tabview.add("⚙️ Computador")

        self.all_action_btns = []
        self.action_btns_dict = {}

        def make_action_btn(parent, icon, label, func_name, fg=Theme.ADV_FG, hv=Theme.ADV_HV):
            btn = ctk.CTkButton(parent, text=f"{icon}  {label}", height=34, corner_radius=8,
                               fg_color=fg, hover_color=hv, anchor="w", font=self.font_btn_sub,
                               text_color="#ffffff",
                               command=lambda fn=func_name: self.start_single(fn))
            btn.pack(fill="x", padx=10, pady=3)
            self.all_action_btns.append(btn)
            self.action_btns_dict[func_name] = btn
            return btn

        def make_master_btn(parent, icon, label, mode, fg=Theme.ALL_IN_FG, hv=Theme.ALL_IN_HV):
            btn = ctk.CTkButton(parent, text=f"{icon}  {label}", height=40, corner_radius=8,
                               fg_color=fg, hover_color=hv, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                               text_color="#ffffff", command=lambda m=mode: self.start_opt(m))
            btn.pack(fill="x", padx=10, pady=(5, 15))
            self.all_action_btns.append(btn)
            return btn

        # -- Aba Limpeza --
        make_master_btn(tab_limpeza, "🧹", "Executar Limpeza Completa", "opt_limpeza")
        make_action_btn(tab_limpeza, "🗑", "Limpar RAM (Working Set)", "clean_ram")
        make_action_btn(tab_limpeza, "🗑", "Limpar Temp e Shaders", "clean_temp_folders")
        make_action_btn(tab_limpeza, "💥", "Limpar Standby + Shaders", "clear_standby_and_shaders")
        make_action_btn(tab_limpeza, "📋", "Limpar Logs de Eventos", "clear_event_logs")
        make_action_btn(tab_limpeza, "☠", "Matar Processos Pesados", "kill_memory_hogs", fg="#8b1a1a", hv="#c62828")

        # -- Aba Rede --
        make_master_btn(tab_rede, "🌐", "Otimizar Rede Completa", "opt_rede", fg=Theme.RAM_FG, hv=Theme.RAM_HV)
        make_action_btn(tab_rede, "❌", "Otimizar Latência de Rede", "optimize_network_latency", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_rede, "🌐", "Flush DNS e IP", "flush_dns", fg=Theme.ADV_FG, hv=Theme.ADV_HV)
        make_action_btn(tab_rede, "🔧", "Reset Completo de Rede", "reset_network", fg=Theme.ADV_FG, hv=Theme.ADV_HV)

        # -- Aba GPU e CPU --
        make_master_btn(tab_gpu_cpu, "🎮", "Otimizar GPU e CPU", "opt_gpu_cpu", fg="#b71c1c", hv="#d32f2f")
        make_action_btn(tab_gpu_cpu, "❌", "Otimizar AMD GPU (ULPS)", "optimize_amd_gpu", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_gpu_cpu, "❌", "GPU Scheduling (Hardware)", "optimize_gpu_scheduling", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_gpu_cpu, "❌", "Tweaks de Registro e Energia", "apply_performance_tweaks", fg="#1a1a1a", hv="#2d2d2d")

        # -- Aba Computador --
        make_master_btn(tab_computador, "⚙️", "Otimizar Computador", "opt_computador", fg=Theme.ADV_FG, hv=Theme.ADV_HV)
        make_action_btn(tab_computador, "❌", "Desativar Serviços Inúteis", "disable_useless_services", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_computador, "❌", "Desativar VBS e Visuais", "disable_vbs_and_visuals", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_computador, "❌", "Desativar Bloat e Compressão", "disable_bloat_and_compression", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_computador, "❌", "Storage Sense + Boot 3s", "enable_storage_sense_and_boot", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_computador, "❌", "Otimizar Memória Virtual", "optimize_virtual_memory", fg="#1a1a1a", hv="#2d2d2d")
        make_action_btn(tab_computador, "💿", "Otimizar Drive (TRIM/Defrag)", "optimize_drive", fg=Theme.ADV_FG, hv=Theme.ADV_HV)
        make_action_btn(tab_computador, "🔄", "Reiniciar Windows Explorer", "restart_explorer", fg=Theme.ADV_FG, hv=Theme.ADV_HV)
        make_action_btn(tab_computador, "💉", "Reparar Sistema (SFC/DISM)", "repair_system", fg="#8b1a1a", hv="#c62828")

        self.mode_btns = []

        # Daemon switch
        self.daemon_var = ctk.StringVar(value=self.check_daemon_status())
        self.switch_daemon = ctk.CTkSwitch(
            self.modes_panel, text="Auto RAM Cleaner (Background)", command=self.toggle_daemon,
            variable=self.daemon_var, onvalue="on", offvalue="off",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            progress_color=Theme.ACCENT_GREEN)
        self.switch_daemon.pack(pady=(8, 0))

        
        # --------------------------------------------------------------------------------
        #  CONSOLE (Parte inferior)
        # --------------------------------------------------------------------------------
        self.console_outer = ctk.CTkFrame(self.main_frame, fg_color=Theme.BG_CARD, 
                                           corner_radius=14, border_width=1, border_color=Theme.BORDER,
                                           height=130)
        self.console_outer.pack(fill="x", padx=30, pady=(5, 10))
        self.console_outer.pack_propagate(False)
        
        # Console Header
        console_header = ctk.CTkFrame(self.console_outer, fg_color="transparent")
        console_header.pack(fill="x", padx=16, pady=(10, 0))
        
        ctk.CTkLabel(console_header, text="CONSOLE DE OTIMIZAÇÃO E LOGS DE ERRO", 
                     font=self.font_label, text_color=Theme.TEXT_SECONDARY).pack(side="left")
        
        self.status_dot = ctk.CTkLabel(console_header, text="✅  PRONTO", 
                                        font=self.font_stat_lbl, text_color=Theme.ACCENT_GREEN)
        self.status_dot.pack(side="right")
        
        # Console Text
        self.console_text = ctk.CTkTextbox(self.console_outer, font=self.font_console,
                                            fg_color=Theme.BG_DARK, text_color=Theme.ACCENT_GREEN,
                                            corner_radius=8, border_width=0, height=90,
                                            activate_scrollbars=True, wrap="word")
        self.console_text.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        self.console_text.insert("end", "  > Sistema pronto. Selecione um modo de otimização.\n")
        self.console_text.configure(state="disabled")
        
        # ------ Iniciar Loop de Monitoramento ---
        self.update_stats()
        self.refresh_button_states()

    # --------------------------------------------------------------------------------
    #  MONITORAMENTO EM TEMPO REAL
    # --------------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------------
    #  EXECUÇÃO DE OTIMIZAÇÃO
    # --------------------------------------------------------------------------------
    def start_opt(self, mode):
        self.set_buttons_state("disabled")
        self.status_dot.configure(text="⏳  EXECUTANDO...", text_color=Theme.ACCENT_GOLD)
        
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

    def refresh_button_states(self):
        def _bg_check():
            states = check_states()
            for func_name, is_opt in states.items():
                if is_opt and func_name in self.action_btns_dict:
                    btn = self.action_btns_dict[func_name]
                    # Update button to show it's optimized
                    old_text = btn.cget("text")
                    if "✅" not in old_text and "✔️" not in old_text:
                        btn.configure(text=old_text.replace(old_text.split()[0], "✅"))
        threading.Thread(target=_bg_check, daemon=True).start()

    def set_buttons_state(self, state):
        self.btn_ram_boost.configure(state=state)
        self.btn_all_in.configure(state=state)
        for btn in self.all_action_btns:
            btn.configure(state=state)
        for btn in self.mode_btns:
            btn.configure(state=state)

    def start_single(self, func_name):
        func_map = {
            "clean_ram": clean_ram, "clean_temp_folders": clean_temp_folders,
            "clear_standby_and_shaders": clear_standby_and_shaders,
            "clear_event_logs": clear_event_logs, "enable_storage_sense_and_boot": enable_storage_sense_and_boot,
            "kill_memory_hogs": kill_memory_hogs, "apply_performance_tweaks": apply_performance_tweaks,
            "disable_useless_services": disable_useless_services, "disable_vbs_and_visuals": disable_vbs_and_visuals,
            "disable_bloat_and_compression": disable_bloat_and_compression,
            "restart_explorer": restart_explorer, "optimize_virtual_memory": optimize_virtual_memory,
            "flush_dns": flush_dns, "optimize_network_latency": optimize_network_latency,
            "reset_network": reset_network, "optimize_gpu_scheduling": optimize_gpu_scheduling,
            "optimize_amd_gpu": optimize_amd_gpu,
            "optimize_drive": optimize_drive, "repair_system": repair_system,
        }
        func = func_map.get(func_name)
        if not func: return
        self.set_buttons_state("disabled")
        self.status_dot.configure(text="\u23f3  EXECUTANDO...", text_color=Theme.ACCENT_GOLD)
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.insert("end", f"  > Executando: {func_name}...\n\n")
        self.console_text.configure(state="disabled")

        def _run():
            try:
                states = check_states()
                if states.get(func_name) == True:
                    self.console_text.configure(state="normal")
                    self.console_text.insert("end", f"  \u2714\ufe0f  [PULADO] A funcao '{func_name}' ja estava otimizada.\n\n")
                    self.console_text.configure(state="disabled")
                    self.status_dot.configure(text="\U0001f7e2  CONCLUIDO", text_color=Theme.ACCENT_GREEN)
                else:
                    result = func()
                    self.console_text.configure(state="normal")
                    if "Erro" in str(result) or "Aviso" in str(result):
                        self.console_text.insert("end", f"  [!] {result}\n", "error_tag")
                        self.console_text.tag_config("error_tag", foreground=Theme.ACCENT_ORANGE)
                    else:
                        self.console_text.insert("end", f"  \u2714\ufe0f  {result}\n")
                    self.console_text.insert("end", "\n  \u2714\ufe0f  Concluido!\n")
                    self.console_text.configure(state="disabled")
                    self.status_dot.configure(text="\U0001f7e2  CONCLUIDO", text_color=Theme.ACCENT_GREEN)
            except Exception as e:
                self.console_text.configure(state="normal")
                self.console_text.insert("end", f"  \u274c  ERRO: {e}\n")
                self.console_text.configure(state="disabled")
                self.status_dot.configure(text="\U0001f534  ERRO", text_color=Theme.ACCENT_RED)
            finally:
                self.set_buttons_state("normal")
                self.refresh_button_states()
        threading.Thread(target=_run, daemon=True).start()

    def run_task(self, mode):
        try:
            time.sleep(0.5)
            self.console_text.configure(state="normal")
            self.console_text.delete("1.0", "end")
            self.console_text.insert("end", "  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\n")
            self.console_text.insert("end", "  ⚡   🔥  OTIMIZAÇÃO EM ANDAMENTO   🔥\n")
            self.console_text.insert("end", "  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\n\n")
            self.console_text.configure(state="disabled")

            for res in optimize_system(mode=mode):
                lines = res.split("\n")
                self.console_text.configure(state="normal")
                for line in lines:
                    if "Erro" in line or "Aviso" in line or "Acesso Negado" in line or "Falhou" in line or "falhou" in line:
                        self.console_text.insert("end", f"  [!] {line}\n", "error_tag")
                    else:
                        self.console_text.insert("end", f"  ✔️  {line}\n")
                self.console_text.tag_config("error_tag", foreground=Theme.ACCENT_ORANGE)
                self.console_text.configure(state="disabled")
                self.console_text.see("end")

            self.console_text.configure(state="normal")
            self.console_text.insert("end", "\n  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\n")
            self.console_text.insert("end", "  ✔️   🔥  OTIMIZAÇÃO CONCLUÍDA COM SUCESSO   🔥\n")
            self.console_text.insert("end", "  ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\n\n")
            self.console_text.configure(state="disabled")
            self.console_text.see("end")

            self.status_dot.configure(text="🟢  CONCLUÍDO", text_color=Theme.ACCENT_GREEN)
        except Exception as e:
            self.console_text.configure(state="normal")
            self.console_text.delete("1.0", "end")
            self.console_text.insert("end", f"  ❌  ERRO CRÍTICO NA APLICAÇÃO: {e}\n", "error_critical")
            self.console_text.tag_config("error_critical", foreground=Theme.ACCENT_RED)
            self.console_text.configure(state="disabled")
            self.status_dot.configure(text="🔴  ERRO", text_color=Theme.ACCENT_RED)
        finally:
            self.set_buttons_state("normal")

    def toggle_daemon(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "WinRAM_AutoCleaner"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if self.daemon_var.get() == "on":
                script_path = os.path.abspath(__file__)
                pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(pythonw_path):
                    pythonw_path = "pythonw.exe"
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{pythonw_path}" "{script_path}" "--daemon"')
                subprocess.Popen([pythonw_path, script_path, "--daemon"], creationflags=0x08000000)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                    subprocess.run('wmic process where "commandline like \'%winram.pyw%--daemon%\'" call terminate', capture_output=True, creationflags=0x08000000)
                except:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print("Daemon error:", e)

    def check_daemon_status(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "WinRAM_AutoCleaner"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return "on"
        except:
            return "off"



def daemon_main():
    import psutil, ctypes, time, sys
    mutex_name = "WinRAM_Daemon_AutoClean_Mutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == 183:
        sys.exit(0)

    GAMES_LIST = ["cs2.exe", "valorant.exe", "gta5.exe", "cyberpunk2077.exe", "dota2.exe", "leagueoflegends.exe", "r5apex.exe", "overwatch.exe", "bf2042.exe", "pubg.exe", "eldenring.exe", "cod.exe", "forzahorizon5.exe"]
    game_mode_active = False

    def clean_ram():
        psapi = ctypes.WinDLL('psapi.dll')
        k32 = ctypes.WinDLL('kernel32.dll')
        try:
            k32.SetSystemFileCacheSize(ctypes.c_size_t(-1), ctypes.c_size_t(-1), 0)
        except: pass
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_SET_QUOTA = 0x0100
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

    while True:
        try:
            game_proc = check_games_running()
            if game_proc and not game_mode_active:
                try:
                    if sys.platform == 'win32':
                        game_proc.nice(psutil.HIGH_PRIORITY_CLASS)
                except:
                    pass
                game_mode_active = True
                clean_ram()
            elif not game_proc and game_mode_active:
                game_mode_active = False

            if psutil.virtual_memory().percent >= 65:
                clean_ram()
                time.sleep(60)
            else:
                time.sleep(10)
        except:
            time.sleep(10)

if __name__ == "__main__":
    if "--daemon" in sys.argv:
        daemon_main()
        sys.exit(0)
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    app = WinRAMApp()
    app.mainloop()
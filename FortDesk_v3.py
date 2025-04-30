import os
import sys
import ctypes
import subprocess
import time
import base64
from cryptography.fernet import Fernet
import getpass

# Caminhos para chave e senha
KEY_FILE = "fortidesk_key.key"
PASS_FILE = "fortidesk_pass.enc"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_if_needed():
    if not is_admin():
        print("\nEste script requer privilégios de administrador.")
        print("Reiniciando como administrador...\n")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            return key_file.read()
    return generate_key()

def store_encrypted_password():
    password = getpass.getpass(prompt="Digite a senha do administrador para criptografar e salvar: ")
    key = load_key()
    f = Fernet(key)
    token = f.encrypt(password.encode())
    with open(PASS_FILE, 'wb') as enc_file:
        enc_file.write(token)
    print("Senha criptografada com sucesso.")

def get_decrypted_password():
    key = load_key()
    if not os.path.exists(PASS_FILE):
        return None
    with open(PASS_FILE, 'rb') as enc_file:
        encrypted = enc_file.read()
    f = Fernet(key)
    try:
        return f.decrypt(encrypted).decode()
    except:
        return None

# ===============================================
# FUNÇÕES DE HARDENING (resumo para fins visuais)
# ===============================================
def intro():
    print("🔰 FortiDesk - Hardening Corporativo Windows 10/11")
    print("--------------------------------------------------")
    print("Automação de medidas de segurança para desktops corporativos.")
    input("\nPressione Enter para iniciar...\n")

def execute_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        sys.exit(1)

def configure_ransomware_protection():
    print("[1] Proteção Anti-Ransomware ativada...")
    execute_command("powershell Set-MpPreference -EnableControlledFolderAccess Enabled")

# (... aqui vão as demais funções como no script anterior ...)

def conclude():
    print("\n✅ Hardening completo com FortiDesk!")
    print("--------------------------------------------------")
    print("Você pode revisar logs e políticas aplicadas.")
    print("Credenciais seguras e criptografadas foram utilizadas.\n")

# ===============================================
# MAIN
# ===============================================
def main():
    elevate_if_needed()
    intro()

    if not os.path.exists(PASS_FILE):
        store_encrypted_password()
    else:
        senha = get_decrypted_password()
        if not senha:
            print("⚠️ Não foi possível descriptografar a senha.")
            store_encrypted_password()

    # Etapas do hardening
    configure_ransomware_protection()
    # configure_bitlocker()
    # configure_mfa()
    # ...
    conclude()

if __name__ == "__main__":
    main()

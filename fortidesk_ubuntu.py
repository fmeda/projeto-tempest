# fortidesk_ubuntu.py
# FortiDesk para Linux Ubuntu 20.04+ – Hardening automatizado com interface CLI

import os
import subprocess
import getpass
import sys
from cryptography.fernet import Fernet

KEY_FILE = "fortidesk_key.key"
ENC_PASS_FILE = "fortidesk_pass.enc"

# -------------------------------------------------------------
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def encrypt_password(password, key):
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    with open(ENC_PASS_FILE, 'wb') as enc_file:
        enc_file.write(encrypted)

def decrypt_password(key):
    with open(ENC_PASS_FILE, 'rb') as enc_file:
        encrypted = enc_file.read()
    f = Fernet(key)
    return f.decrypt(encrypted).decode()

# -------------------------------------------------------------
def check_root():
    if os.geteuid() != 0:
        print("[!] Este script requer privilégios de root. Execute com 'sudo'.")
        sys.exit(1)

# -------------------------------------------------------------
def run_cmd(description, cmd):
    print(f"[+] {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("    [OK] Concluído.")
    except subprocess.CalledProcessError:
        print("    [ERRO] Falha na execução do comando.")

# -------------------------------------------------------------
def apply_hardening():
    print("\n==== Iniciando o FortiDesk Linux – Hardening de Ubuntu ====")

    run_cmd("Atualizando pacotes do sistema", "apt update && apt upgrade -y")
    run_cmd("Ativando UFW (Firewall Uncomplicated)", "ufw enable")
    run_cmd("Configurando UFW para negar conexões por padrão", "ufw default deny incoming && ufw default allow outgoing")
    run_cmd("Instalando e ativando Fail2Ban", "apt install -y fail2ban && systemctl enable --now fail2ban")
    run_cmd("Removendo serviços desnecessários", "apt purge -y telnet rsh-server xinetd")
    run_cmd("Desabilitando root por SSH", "sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && systemctl restart sshd")
    run_cmd("Aplicando política de senha forte", "apt install -y libpam-pwquality && echo 'password requisite pam_pwquality.so retry=3 minlen=12' >> /etc/pam.d/common-password")
    run_cmd("Habilitando atualizações automáticas", "apt install -y unattended-upgrades && dpkg-reconfigure -plow unattended-upgrades")
    run_cmd("Removendo arquivos temporários e histórico", "rm -rf /tmp/* ~/.bash_history")

    print("\n✅ Hardening concluído com sucesso!\n")

# -------------------------------------------------------------
def main():
    check_root()

    print("""
============================================================
🔰 FortiDesk – Linux Ubuntu 20.04+ CLI Hardening Tool
------------------------------------------------------------
Automação de medidas de segurança para estações Linux Ubuntu.
============================================================
""")

    key = load_key()

    if not os.path.exists(ENC_PASS_FILE):
        password = getpass.getpass("Digite a senha root para criptografar: ")
        encrypt_password(password, key)
        print("[✔] Senha criptografada com sucesso.")
    else:
        try:
            _ = decrypt_password(key)
            print("[✔] Credenciais criptografadas carregadas com sucesso.")
        except Exception:
            print("[!] Erro ao descriptografar senha. Delete os arquivos e reconfigure.")
            sys.exit(1)

    apply_hardening()

if __name__ == "__main__":
    main()

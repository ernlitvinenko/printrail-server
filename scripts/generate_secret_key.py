import subprocess

def generate_secret_key():
    output = subprocess.run(['openssl', 'rand', '-hex', '32'], capture_output=True, text=True)
    return output.stdout.strip()

if __name__ == "__main__":
    print(generate_secret_key())
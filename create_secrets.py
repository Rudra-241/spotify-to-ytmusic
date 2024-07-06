from os import fsync

def create():
    CLIENT_ID = input("Enter your client id: ")
    CLIENT_SECRET = input("Enter your client secret: ")
    with open('secrets.py','w') as file:
        file.write(f"CLIENT_ID = \"{CLIENT_ID}\"\n")
        file.write(f"CLIENT_SECRET = \"{CLIENT_SECRET}\"\n")
        fsync(file.fileno())
        print("secrets created")

def main(bad_secrets=False):
    try:
        with open('secrets.py','r') as file:
            content = file.read()
        if "CLIENT_ID" in content and "CLIENT_SECRET" in content and not bad_secrets:
            print("Secrets already exist")
        else:
            print("CLIENT_ID or CLIENT_SECRET does not exists in secrets, creating new secrets...")
            create()
    except FileNotFoundError:
        print("No secrets found, creating secrets...")
        create()

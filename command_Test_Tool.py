def send_command(command, payload):
        if len(command) != 4:
            raise ValueError("Command must be 4 characters long.")
        padded_payload = pad_payload(payload)
        message = f"#{command}{padded_payload}"
        checksum = calculate_checksum(command + padded_payload)
        message_with_checksum = f"{message}{checksum}#"
        return message_with_checksum

def calculate_checksum(command):
    checksum = 0
    for char in command:
        checksum ^= ord(char)
    return f"{checksum:03}"
    
def pad_payload(payload):
    if len(payload) > 32:
        raise ValueError("Payload must be 32 characters or less.")
    return payload + '@' * (32 - len(payload))


command = "RBUT"
payload = ""

print(send_command(command,payload))

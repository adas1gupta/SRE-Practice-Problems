import ctypes
import argparse
import os
import sys
import re

PTRACE_TRACEME = 0
PTRACE_SYSCALL = 24
PTRACE_GETREGS = 12

# numbers to system calls mapping
SYSCALL_NAMES = {}
with open("/usr/include/x86_64-linux-gnu/asm/unistd_64.h") as f:
    for line in f:
        match = re.match(r'#define __NR_(\w+)\s+(\d+)', line)
        if match:
            name, number = match.groups()
            syscall_names[int(number)] = name

class UserRegsStruct(ctypes.Structure):
    _fields_ = [
        ("r15", ctypes.c_ulonglong),
        ("r14", ctypes.c_ulonglong),
        ("r13", ctypes.c_ulonglong),
        ("r12", ctypes.c_ulonglong),
        ("rbp", ctypes.c_ulonglong),
        ("rbx", ctypes.c_ulonglong),
        ("r11", ctypes.c_ulonglong),
        ("r10", ctypes.c_ulonglong),
        ("r9", ctypes.c_ulonglong),
        ("r8", ctypes.c_ulonglong),
        ("rax", ctypes.c_ulonglong),
        ("rcx", ctypes.c_ulonglong),
        ("rdx", ctypes.c_ulonglong),
        ("rsi", ctypes.c_ulonglong),
        ("rdi", ctypes.c_ulonglong),
        ("orig_rax", ctypes.c_ulonglong),
        ("rip", ctypes.c_ulonglong),
        ("cs", ctypes.c_ulonglong),
        ("eflags", ctypes.c_ulonglong),
        ("rsp", ctypes.c_ulonglong),
        ("ss", ctypes.c_ulonglong),
    ]

if __name__ == "__main__":
    libc = ctypes.CDLL("libc.so.6")

    libc.ptrace.argtypes = [
        ctypes.c_long,    # request (PTRACE_TRACEME, PTRACE_SYSCALL, etc.)
        ctypes.c_int,     # pid
        ctypes.c_void_p,  # addr (usually NULL for what we're doing)
        ctypes.c_void_p,  # data (NULL, or pointer to regs struct)
    ]

    libc.ptrace.restype = ctypes.c_long

    parser = argparse.ArgumentParser(description="Monitor system call usage for any given binary")
    parser.add_argument("--binary", required=True, help="Run a program and monitor its system call usage")
    parser.add_argument("--args", nargs='*', default=[], required=False, help="Run target program with its arguments")
    parsed = parser.parse_args()
    binary = parsed.binary 
    binary_args = parsed.args or []

    

    pid = os.fork()

    if pid == 0:
        libc.ptrace(PTRACE_TRACEME, 0, None, None)
        os.execvp(binary, [binary] + binary_args)
    else:
        _, status = os.waitpid(pid, 0)
        if not os.WIFSTOPPED(status):
            print("child didn't stop cleanly")
            sys.exit(1)
        
        libc.ptrace(PTRACE_SYSCALL, pid, None, None)

        entry = True
        sys_num = None
                
        while True: 
            _, status = os.waitpid(pid, 0)
            if os.WIFSIGNALED(status):
                print("child killed")
                sys.exit(0)
            if os.WIFEXITED(status):
                print("child exited")
                sys.exit(0)
                
            registers = UserRegsStruct()
            libc.ptrace(PTRACE_GETREGS, pid, None, ctypes.byref(registers))

            if entry:
                sys_num = registers.orig_rax
            else:
                return_val = registers.rax 
                print(f"system call: {syscall_names[sys_num]}, arguments: {registers.rdi, registers.rsi, registers.rdx}, return value: {return_val}")

            entry = not entry
            libc.ptrace(PTRACE_SYSCALL, pid, None, None)
import ctypes

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

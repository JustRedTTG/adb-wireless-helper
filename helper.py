import sys

WAIT_RANGE = 10


def get_waiting(i):
    clean_value = i % (WAIT_RANGE * 2)
    if clean_value >= WAIT_RANGE:
        clean_value = 2 * WAIT_RANGE - clean_value - 1
    return f"[{''.join(('*' if (current_index := clean_value % WAIT_RANGE) == _ else ('-' if current_index - 1 == _ or current_index + 1 == _ else ' ') for _ in range(WAIT_RANGE)))}]"


def exit_program():
    input("\nPress Enter to exit...")
    sys.exit(0)

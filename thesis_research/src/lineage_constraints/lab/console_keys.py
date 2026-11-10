"""Send explicit console input to an isolated research VM's local monitor.

Used for recovery of the new overlays before WinRM is reachable. It does not
change the original disks and does not log input text. Do not use it to store
passwords in repository scripts or shell history.
"""

import argparse
import subprocess
import time


KEYS = {" ": "spc", "-": "minus", "_": "shift-minus", ".": "dot", "/": "slash",
        "\\": "backslash", ":": "shift-semicolon", ";": "semicolon", "=": "equal",
        "+": "shift-equal", "'": "apostrophe", '"': "shift-apostrophe", "$": "shift-4",
        "|": "shift-backslash", "(": "shift-9", ")": "shift-0", "{": "shift-bracket_left",
        "}": "shift-bracket_right", ",": "comma", "[": "bracket_left", "]": "bracket_right"}


def send_key(node, key):
    subprocess.run(["docker", "exec", "-i", f"goad-lineage-{node}", "nc", "-w", "1", "127.0.0.1", "4444"],
                   input=f"sendkey {key} 50\n".encode(), stdout=subprocess.DEVNULL, check=True, timeout=5)
    time.sleep(0.12)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("node", choices=["dc03", "srv03", "win2019"])
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--text")
    choice.add_argument("--key")
    parser.add_argument("--enter", action="store_true")
    args = parser.parse_args()
    if args.key:
        send_key(args.node, args.key)
    else:
        for character in args.text:
            if character in KEYS:
                key = KEYS[character]
            elif character.isascii() and character.isalnum():
                key = "shift-" + character.lower() if character.isupper() else character
            else:
                raise ValueError(f"Unsupported console character {character!r}")
            send_key(args.node, key)
    if args.enter:
        send_key(args.node, "ret")

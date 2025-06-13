import os
import subprocess
import sys
import time

def run(cmd, capture_output=False):
    if capture_output:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    else:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
os.system("clear")
def main():
    if os.geteuid() != 0:
        print("[✘] This script must be run as root. Use sudo.")
        sys.exit(1)
    while True:
        os.system("clear")
        print("#" * 40)
        print(" MacBook dGPU Disabler/Enabler ")
        print(" Only for models between 2010 and 2013 ")
        print(" Using it on other models ")
        print(" could permanently damage it.")
        print("#" * 40 + "\n")
        print("Choose mode:")
        print("1 - Create image to DISABLE dGPU")
        print("2 - Create image to ENABLE dGPU")
        print("q - Quit")
        choice = input("Enter an option: ").strip().lower()
        if choice == "q":
            print("\nExiting...")
            sys.exit(0)
        elif choice == "1":
            entry_name = "Disable dGPU"
            outb_cmds = """    outb 0x728 1
    outb 0x710 2
    outb 0x740 2
    outb 0x750 0"""
            break
        elif choice == "2":
            entry_name = "Enable dGPU"
            outb_cmds = """    outb 0x728 1
    outb 0x710 2
    outb 0x740 2
    outb 0x750 1"""
            break
        else:
            print(f"\n[✘] {choice} is a invalid option. Press Enter to try again.")
            input()
    script_dir = os.path.abspath(os.path.dirname(__file__))
    workdir = os.path.join(script_dir, "dGPU-disabler-enabler")
    img_path = os.path.join(workdir, "image_dgpu.img")
    mountdir = "/mnt/img"
    print(f"\n[+] Creating working directory: {workdir}")
    os.makedirs(workdir, exist_ok=True)
    os.chdir(workdir)
    print("[+] Creating image...")
    run(f"dd if=/dev/zero of={img_path} bs=1M count=8")
    print("[+] Creating FAT32 partition...")
    run(f"parted {img_path} mklabel msdos")
    run(f"parted {img_path} mkpart primary fat32 1MiB 100%")
    print("[+] Setting up loopback device...")
    loopdev = run(f"losetup -f --show -P {img_path}", capture_output=True)
    print(f"[+] Image attached to: {loopdev}")
    print("[+] Formatting partition as FAT32...")
    run(f"mkfs.vfat {loopdev}p1")
    print(f"[+] Mounting partition to {mountdir}...")
    os.makedirs(mountdir, exist_ok=True)
    run(f"mount {loopdev}p1 {mountdir}")
    print("[+] Creating GRUB directory structure...")
    run(f"mkdir -p {mountdir}/boot/grub")
    print(f"[+] Writing grub.cfg for: {entry_name}")
    grub_cfg = f"""set timeout=0
set default=0

menuentry "{entry_name}" {{
{outb_cmds}
    sleep 3
    reboot
}}
"""
    grub_path = os.path.join(mountdir, "boot", "grub", "grub.cfg")
    with open("temp_grub.cfg", "w") as f:
        f.write(grub_cfg)
    run(f"cp temp_grub.cfg {grub_path}")
    os.remove("temp_grub.cfg")
    print("[+] Installing GRUB to the image...")
    run(f"grub-install --target=i386-pc --boot-directory={mountdir}/boot "
        f"--modules='normal part_msdos ext2 fat' --force {loopdev}")
    print("[+] Unmounting image...")
    run(f"umount {mountdir}")
    run(f"losetup -d {loopdev}")
    print(f"[✔] Image successfully created at: {img_path}\n")
    copy = input("Do you want to copy this image to a USB drive now? (yes/no): ").strip().lower()
    if copy != "yes":
        print("Skipped copying.")
        sys.exit(0)
    print("\n[?] Available USB devices:")
    lsblk_output = subprocess.check_output("lsblk -ndo NAME,SIZE,TYPE | grep -E '^sd[a-z] ' | grep disk", shell=True, text=True)
    devices = lsblk_output.strip().splitlines()
    if not devices:
        print("[✘] No USB devices found.")
        sys.exit(1)
    for i, line in enumerate(devices):
        name, size, *_ = line.strip().split()
        print(f"{i+1}) /dev/{name} - {size}")
    while True:
        choice = input("Enter the number of the device to write the image to (or 'q' to quit): ").strip().lower()
        print("\n")
        if choice == 'q':
            print("Aborted.")
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(devices):
            dev_name = devices[int(choice)-1].split()[0]
            target_dev = f"/dev/{dev_name}"
            for i in range(2):
                confirm = input(f"[!!] WARNING: This will ERASE ALL DATA on {target_dev}. Type 'yes' to continue ({i+1}/2): ").strip().lower()
                if confirm != "yes":
                    print("\nAborted.")
                    sys.exit(0)
            print(f"[+] Writing image to {target_dev}...")
            run(f"dd if={img_path} of={target_dev} bs=1M status=progress conv=fsync")
            print("[✔] Image copied successfully.")
            break
        else:
            print("Invalid option. Try again.\n")
if __name__ == "__main__":
    main()

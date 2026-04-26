import subprocess
import logging

def ban_ip(ip_address):
    """Executes the Linux shell command to block an IP."""
    try:
        # -A INPUT: Append to the input chain
        # -s: source IP
        # -j DROP: Discard the packets
        command = ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"]
        subprocess.run(command, check=True)
        print(f"Successfully banned {ip_address}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to ban {ip_address}: {e}")
        return False

def unban_ip(ip_address):
    """Optional: Use this to lift the ban after the backoff time."""
    command = ["sudo", "iptables", "-D", "INPUT", "-s", ip_address, "-j", "DROP"]
    subprocess.run(command)
import socket

def find_open_ports():
    print("Checking ports 8000-8010...")
    for port in range(8000, 8011):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                print(f"Port {port} is OPEN")
            else:
                pass

if __name__ == "__main__":
    find_open_ports()

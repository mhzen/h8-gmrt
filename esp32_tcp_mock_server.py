# mock_esp32_server.py
import socket, struct, json, time

def recv_exact(conn, n):
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf

# Take packet from comvistest.py and send back a mock response
def create_mock_response(packet):
    # Unpack the incoming packet
    header = struct.unpack('!BBH', packet[:4])
    command = header[1]
    payload = packet[4:]

    # Create a mock response based on the command
    if command == 0x01:  # Example command for getting status
        response_data = {
            "status": "OK",
            "temperature": 25.5,
            "humidity": 60
        }
    elif command == 0x02:  # Coordinates packet (x, y) as two int32
        if len(payload) >= 8:
            x, y = struct.unpack('!ii', payload[:8])
            response_data = {
                "ack": True,
                "received_x": x,
                "received_y": y
            }
        else:
            response_data = {"error": "invalid coords payload"}
    else:
        response_data = {"error": "Unknown command"}

    response_json = json.dumps(response_data).encode('utf-8')
    response_length = len(response_json)
    response_header = struct.pack('!BBH', 0xFF, command, response_length)
    return response_header + response_json

if __name__ == "__main__":
    SERVER_IP = "0.0.0.0"
    SERVER_PORT = 5005
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((SERVER_IP, SERVER_PORT))
    srv.listen(1)
    print(f"Mock ESP32 TCP server listening on {SERVER_IP}:{SERVER_PORT}")
    try:
        while True:
            conn, addr = srv.accept()
            print("Connection from", addr)
            try:
                while True:
                    hdr = recv_exact(conn, 4)
                    if not hdr:
                        break
                    start, cmd, payload_len = struct.unpack('!BBH', hdr)
                    payload = recv_exact(conn, payload_len) if payload_len > 0 else b''
                    if payload is None:
                        break
                    packet = hdr + (payload or b'')
                    if cmd == 0x02 and len(payload) >= 8:
                        x, y = struct.unpack('!ii', payload[:8])
                        print(f"Received coords from {addr}: x={x}, y={y}")
                    else:
                        print(f"Received command {cmd} from {addr} (payload len {len(payload)})")
                    resp = create_mock_response(packet)
                    conn.sendall(resp)
            except ConnectionResetError:
                print("Client disconnected abruptly:", addr)
            finally:
                conn.close()
                print("Connection closed", addr)
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        srv.close()
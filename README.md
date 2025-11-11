# GMRT H8

## Testing (tanpa ESP32)

### HTTP
- Jalankan [esp32_http_mock_server.py](./esp32_http_mock_server.py), penerima request post dari python
- Jalankan [comvis.py](./comvis.py), pastikan `connection=wifi`
- Balik ke [esp32_http_mock_server.py](./esp32_http_mock_server.py), akan ada output yang merupakan kordinat dari [comvis.py](./comvis.py)

### USB (Serial)
Buat Linux:
- Jalankan `socat -d -d pty,raw,echo=0 pty,raw,echo=0` di terminal (install package socat jika belum ada)
- Catat dua path yang muncul (e.g. `/dev/pts/4` dan `/dev/pts/5`)
- Jalankan `cat {salah satu path}` di terminal, pilih saja salah satu path seperti: `cat /dev/pts/4`
- Jalankan [comvis.py](./comvis.py), pastikan `connection=usb` dan `serialAddress={path berbeda dengan yang di cat}` (seperti `serialAddress=/dev/pts/5`)
- Balik ke terminal dimana `cat` dijalankan, akan ada output yang merupakan kordinat dari [comvis.py](./comvis.py)

Buat windows/macos:

idk lol
import websocket
from time import sleep

if __name__ == "__main__":
    ws = websocket.WebSocket()
    print("Connect")
    ws.connect("ws://192.168.0.27:8080")
    print("Connected")
    ws.send("#00FF00")
    ws.send("F0000FF 5")
    sleep(2.5)
    ws.send("FFF0000 5")
    print("Sent")
    ws.close()

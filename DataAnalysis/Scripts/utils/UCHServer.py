from utils.tools import *
import psutil
import json
import socket
import time
import subprocess
import json

class UCHServer:
    MessageTypeSeparator = "\x1E"
    MessageSeparator = "\x1F"

    def __init__(self):
        
        if not "UltimateChickenHorse.exe" in (p.name() for p in psutil.process_iter()):
            self.startUCH()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect(("127.0.0.1", 4711))
        self.server.setblocking(False)
        self.keepAlive = False

    def __del__(self):
        if not self.keepAlive:
            self.sendShutdownMessage()
            self.server.close()

    def startUCH(self):
        path = f"\"{repoRoot}/UltimateChickenHorse/UltimateChickenHorse.exe\""
        print(f"Starting UCH: {path}")
        self.uch = subprocess.Popen(
            path, shell=False
        )
        time.sleep(2)

    def sendMessage(self, messageType, messageData):
        return self.server.send(
            f"{messageType}{self.MessageTypeSeparator}{messageData}{self.MessageSeparator}".encode()
        )

    def sendPingMessage(self):
        self.sendMessage("ping", "{}")

    def sendKeepAliveMessage(self):
        self.keepAlive = True
        return self.sendMessage("keepAlive", "{}")

    def sendShutdownMessage(self):
        return self.sendMessage("quit", "{}")

    def readMessages(self):
        try:
            data = self.server.recv(1024 * 1024 * 100)
            return self.__parseResults(data.decode())
        except BlockingIOError:
            return []

    def __parseResults(self, message):
        # Split the message string using the end-of-message delimiter \x1F
        message_parts = message.split("\x1F")

        # Parse each message part into a tuple
        messages = []
        for part in message_parts:
            if not part:
                continue
            message_sub_parts = part.split("\x1E")
            if len(message_sub_parts) == 0:
                continue
            messages.append((message_sub_parts[0], json.loads(message_sub_parts[1])))

        return messages

import json
import os
import signal
import socket
import threading
import time

from globals import HOST, MAX_MSG_LEN, MAX_RETRIES, PATH, PORT, SETTINGS
from message import Message
from playsound import playsound


class Client:

    def __init__(self) -> None:
        self.id: int = None
        self.socket = None
        self.thread: threading.Thread = None
        self.input_thread: threading.Thread = None
        if SETTINGS["allow_commands"]:
            self.thread = threading.Thread(target=self.listen)
            self.input_thread = threading.Thread(target=self.usr_input)
        
        
    def set_settings(self):
        """This method writes the current settings configuration into settings.json in a readable format.
        """

        with open(PATH[:-6] + "settings.json", "w") as stngs:
            settings: list[str] = json.dumps(SETTINGS).split(", ")
            stngs.write("{\n")
            stngs.write("    " + settings[0][1:] + ",\n")
            prent = False
            for setting in settings[1:-1]:

                if "{" in setting:
                    i = setting.index("{")
                    stngs.write("    %s\n" % setting[:i + 1])
                    stngs.write("        %s,\n" % setting[i + 1:])
                    prent = True
                    continue
                
                if "}" in setting:
                    stngs.write("        %s\n    },\n" % setting[:-1])
                    prent = False
                    continue
                
                if prent:
                    stngs.write("        %s,\n" % setting)
                    continue
                
                stngs.write("    %s,\n" % setting)
            stngs.write("    " + settings[len(settings) - 1][:-1] + "\n")
            stngs.write("}")

    def usr_input(self):
        while True:
            inp = Message(input(), self.id)
            self.process_request(msg=inp)
    
    def process_request(self, msg: Message):
    
        res = None
        data = msg.get_content().split(maxsplit=1)
        match data[0]:
            case "say":
                print("server:", data[1])
                
            case"client":
                res = "Hello from client %i" % self.id

            case "sound":
                playsound(PATH + "game-over.mp3")

            case "get":
                res = ""
                args = data[1].split()
                for y in range(-2, 3):
                    for x in range(-2, 3):
                        new_x = int(args[0]) + x
                        new_y = int(args[1]) + y
                        if 0 <= new_x < SETTINGS["width"] and 0 <= new_y < SETTINGS["height"]:
                            res += " %i" % self.grid.contents[new_y][new_x].data()
                        else:
                            res += " -4"

            case "reveal":
                args = data[1].split()
                mine_loc = self.reveal(int(args[0]), int(args[1]))
                if mine_loc:
                    res = "mine encountered at %s" % str(mine_loc)

            case "flag":
                args = data[1].split()
                self.flag(int(args[0]), int(args[1]))

            case "setting":
                args = data[1].split(maxsplit=1)
                setting = args[0]
                if setting in SETTINGS.keys():
                    val = args[1]
                    set_type = type(SETTINGS[setting])
                    if set_type == dict: # TODO Write this code better
                        val = eval(val)
                    else:
                        val = set_type(val)
                    SETTINGS[setting] = val
                    self.set_settings()
                else:
                    print("%s is not a valid setting! Valid settings: %s" % (args[0], SETTINGS.keys()))
                    
                    
            case "reset":
                self.reset()
            
            case "shutdown":
                print("server: shutdown requested")
                os.kill(os.getpid(), signal.SIGTERM)

            case _:
                res = data[0] + ": Command not found"
                print(res)

        msg = Message(data[0], self.id, self.socket)
        msg.send()
        if res != None:
            msg = Message(res, self.id, self.socket)
            msg.send()

    def connect(self):
        if SETTINGS["connect"]:
            i = 0
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    print("trying to connect to the server...")
                    self.socket.connect((HOST, PORT))
                    msg = Message.decipher(self.socket.recv(MAX_MSG_LEN))
                    data = msg.get_content()
                    self.id = int(msg.id)
                    print(data, "Id: %i" % self.id)
                    return True
                except ConnectionRefusedError:
                    i += 1
                    print("Try %i Failed" % i)
                    if i >= MAX_RETRIES:
                        print("Couldn't connect to the server")
                        return False
                    time.sleep(i)
        return False

    def listen(self):
        
        if self.connect():
            with self.socket:
                while self.running:
                    msg = Message.decipher(self.socket.recv(MAX_MSG_LEN))
                    if msg == None:
                        print("Server died... :(")
                        self.socket = None
                        self.id = None
                        if not self.connect():
                            break
                        else:
                            continue

                    self.process_request(msg)


    def run(self):
        if SETTINGS["allow_commands"]:
            if self.thread is not None and not self.thread.is_alive():
                self.thread.start()
                    
            if self.input_thread is not None and not self.input_thread.is_alive():
                self.input_thread.start()
        
        super().run()
        if self.socket is not None:
            self.socket.close()
        os.kill(os.getpid(), signal.SIGTERM)
        
    

        
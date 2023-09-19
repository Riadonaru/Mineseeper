import socket


class Message():

    def __init__(self, content: str, msgid: int, dest: socket.socket = None) -> None:
        self._content = content
        self.id = msgid
        self._dest = dest

    @classmethod
    def decipher(cls, bytes: bytes):
        if not bytes:
            return None
        rawmsg = str(bytes, 'ascii')
        rawmsg = rawmsg.split(maxsplit=1)
        return cls(rawmsg[1], rawmsg[0])

    def get_content(self):
        return self._content

    def to_bytes(self):
        if not self._content.isascii():
            raise Exception("The sent message is contaminated with non ascii characters!")
        return bytes(str(self.id) + " " + self._content, 'ascii')

    def print_content(self):
        print("server:", self._content)

    def send(self):
        if self._dest == None:
            print("client:", self._content)
            return
        try:
            self._dest.sendall(self.to_bytes())
        except Exception as e:
            raise Exception(e)

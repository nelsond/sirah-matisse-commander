import socket
import threading
import time


class MockServer:
    """
    Simple TCP mock server running in a separate thread for testing network
    connections to remote.

    Arguments:
        port (int, optional): Listening port, 30000 by default.
    """
    def __init__(self, port: int = 30000):
        self._port = port

        self._request = None
        self._response = None

        self._ready = None

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(1)

        self._thread = None
        self._loop = False

    def start(self):
        """Start server."""
        attempts = 1
        while self._loop is False and attempts < 10:
            try:
                self._socket.bind(('127.0.0.1', self._port))
                self._loop = True
            except OSError:
                time.sleep(0.1 * attempts)

            attempts += 1

        if self._loop is False:
            raise RuntimeError('Could not bind to network address.')

        self._ready = threading.Event()

        self._thread = threading.Thread(target=self.listen)
        self._thread.daemon = True
        self._thread.start()

        return self._ready

    def stop(self):
        """Stop server."""
        self._loop = False

        if self._thread is not None:
            self._thread.join()

    def setup(self, request: bytes, response: bytes):
        """
        Set expected request and response data.

        Arguments:
            request (bytes):
                Expected request data.

            reponse (bytes):
                Response data once expected request data is received.
        """
        self._request = request
        self._response = response

    def listen(self):
        """Listen for new connections."""
        while self._loop is True:
            self._socket.listen()
            self._ready.set()

            try:
                conn, _ = self._socket.accept()
                request = conn.recv(1024)

                if request == self._request:
                    conn.send(self._response)

                conn.close()

            except socket.timeout:
                pass

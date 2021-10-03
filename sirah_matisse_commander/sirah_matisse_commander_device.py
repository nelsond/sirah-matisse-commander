import socket
import struct
import re
import time

from typing import Union
from .matisse_control_status import MatisseControlStatus


class SirahMatisseCommanderDevice:
    """
    Simple client for the Matisse Commander TCP server.

    Arguments:
        host (str, optional):
            Host of the TCP server, 'localhost' by default.

        port (int, optional):
            Port of the TCP server, 30000 by default.

        timeout (int or float, optional):
            Timeout of the connection.
    """
    def __init__(self, host: str = 'localhost', port: int = 30000,
                 timeout: Union[int, float] = 1):
        self._address = (host, port)
        self._timeout = timeout

        self._socket = None

    def connect(self) -> None:
        """Establish TCP connection to Matisse Commander."""
        if self.is_connected:
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._timeout)
        self._socket.connect(self._address)

    def disconnect(self, delay: Union[int, float] = 0.3) -> None:
        """
        Close TCP connection to Matisse Commander.

        Arguments:
            delay (int or float, optional):
                Delay before closing network connection in seconds, 0.3 by
                default.

        Note:
        The default delay of 300ms is required Matisse Commander.
        """
        if not self.is_connected:
            return

        self.send('Close_Network_Connection')
        time.sleep(delay)

        self._socket.close()
        self._socket = None

    def send(self, data: str) -> int:
        """
        Send data to Matisse Commander.

        Arguments:
            data (str): Transmission data.

        Returns:
            int: Number of bytes sent.
        """
        data = data.encode('ascii')
        data_length = struct.pack('>L', len(data))

        return self._socket.send(data_length + data)

    def recv(self) -> str:
        """
        Receive response from Matisse Commander.

        Returns:
            str: Raw response data.
        """
        resp_length = self._socket.recv(4)
        if len(resp_length) != 4:
            raise RuntimeError(
                'Device did not send data length. Connection closed?')

        data_length = struct.unpack('>L', resp_length)[0]
        return self._socket.recv(data_length).decode('ascii')

    def query(self, var: str) -> Union[int, float, str, bool,
                                       MatisseControlStatus]:
        """
        Query variable from Matisse Commander.

        Arguments:
            var (str): Variable name.

        Returns:
            int, float, str, bool, or MatisseControlStatus: Response data.
        """
        self.send('{}?'.format(re.sub(r'\?$', '', var)))
        response = self.recv()
        _, value = self._parse_response(response)

        return value

    def set(self, var: str, value: Union[str, int, float]) -> bool:
        """
        Sets variable from Matisse Commander.

        Arguments:
            var (str): Variable name.
            value (str, int, or float): Set value.

        Returns:
            bool: True if setting variable was successful, False otherwise.
        """
        if isinstance(value, float):
            value = f'{value:.5f}'

        elif isinstance(value, int):
            value = f'{value:d}'

        self.send(' '.join((var, value)))
        response = self.recv()

        return response == 'OK'

    @property
    def is_connected(self) -> bool:
        """Connection to Matisse Commander established (bool)."""
        return self._socket is not None

    @property
    def server_alive(self) -> bool:
        """Connection alive (bool)."""
        if self.is_connected is False:
            return False

        self.send('Connection Valid?')

        try:
            return self.recv() == 'Server alive'
        except RuntimeError:
            return False

    @property
    def idn(self) -> str:
        """Identification (str)."""
        return self.query('*IDN')

    @property
    def diode_power_dc(self) -> float:
        """DC value of the integral power diode (float)."""
        return self.query('DPOW:DC')

    @property
    def piezo_ref_cell(self) -> float:
        """Piezo value of the reference cell (float)."""
        return self.query('REFCELL:NOW')

    @piezo_ref_cell.setter
    def piezo_ref_cell(self, value: float) -> None:
        self._validate_piezo_value(value)
        if self.set('REFCELL:NOW', value) is False:
            raise RuntimeError(
                'Setting slow piezo did not complete successfully.')

    @property
    def piezo_slow(self):
        """Slow piezo value (float)."""
        return self.query('SPZT:NOW')

    @piezo_slow.setter
    def piezo_slow(self, value: float) -> None:
        self._validate_piezo_value(value)
        if self.set('SPZT:NOW', value) is False:
            raise RuntimeError(
                'Setting slow piezo did not complete successfully.')

    @property
    def piezo_slow_status(self) -> MatisseControlStatus:
        """Status of the slow piezo (MatisseControlStatus)."""
        return self.query('SPZT:CNTRSTA')

    @property
    def piezo_fast_status(self) -> MatisseControlStatus:
        """Status of the fast piezo (MatisseControlStatus)."""
        return self.query('FPZT:CNTRSTA')

    @property
    def etalon_piezo_status(self) -> MatisseControlStatus:
        """Status of the piezo etalon (MatisseControlStatus)."""
        return self.query('PZETL:CNTRSTA')

    @property
    def etalon_thin_status(self) -> MatisseControlStatus:
        """Status of the thin etalon (MatisseControlStatus)."""
        return self.query('TE:CNTRSTA')

    @property
    def piezo_fast_lock(self) -> bool:
        """Fast piezo locked (bool)."""
        return self.query('FPZT:LOCK')

    @staticmethod
    def _validate_piezo_value(value: float) -> bool:
        if value < 0 or value > 0.7:
            raise ValueError('Invalid value {} (should be >= 0 and <= 0.7).')

    @staticmethod
    def _parse_response(content: str) -> Union[str, float, int,
                                               MatisseControlStatus, bool]:
        match = re.match(r'^\s*:([^\s]+):\s*(.+)\s*$', content)
        if match is None:
            raise ValueError('Invalid response data {}.'.format(content))

        cmd, value = match.groups()

        string_match = re.match(r'^\s*"([^"]+)"\s*$', value)
        if string_match is not None:
            return cmd, string_match.groups()[0]

        float_match = re.match(
            r'^\s*([+\-]?[0-9]*\.[0-9]*(?:[eE][+\-]?[0-9]+)?)\s*$', value)
        if float_match is not None:
            return cmd, float(float_match.groups()[0])

        int_match = re.match(r'^\s*([0-9]+)\s*$', value)
        if int_match is not None:
            return cmd, int(int_match.groups()[0])

        state_match = re.match(r'^\s*(RUN|STOP)\s*$', value)
        if state_match is not None:
            state = state_match.groups()[0].strip()
            if state == 'RUN':
                state = MatisseControlStatus.RUN
            else:
                state = MatisseControlStatus.STOP

            return cmd, state

        bool_match = re.match(r'^\s*(TRUE|FALSE)\s*$', value)
        if bool_match is not None:
            value = bool_match.groups()[0].strip()
            return cmd, value == 'TRUE'

        raise ValueError('Unknown response data format {}.'.format(content))

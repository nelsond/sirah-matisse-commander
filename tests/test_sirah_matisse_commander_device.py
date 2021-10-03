import pytest

from support import MockServer, data_length
from sirah_matisse_commander import (SirahMatisseCommanderDevice,
                                     MatisseControlStatus)


@pytest.fixture
def device_server():
    server = MockServer(30000)
    ready_event = server.start()
    ready_event.wait(1)

    yield server

    server.stop()


@pytest.fixture
def default_device():
    return SirahMatisseCommanderDevice('localhost', 30000, timeout=0.1)


def test_connects_to_device(default_device, device_server):
    device_server.setup(b'Close_Network_Connection', b'OK')
    default_device.connect()

    assert default_device.is_connected is True

    default_device.disconnect()


def test_server_alive_without_connection(default_device):
    assert default_device.server_alive is False


def test_server_alive_with_active_connection(default_device, device_server):
    device_server.setup(
        b'\x00\x00\x00\x11Connection Valid?',
        b'\x00\x00\x00\x0cServer alive'
    )

    default_device.connect()

    assert default_device.server_alive is True

    default_device.disconnect()


def test_server_alive_with_closed_connection(default_device, device_server):
    device_server.setup(
        b'\x00\x00\x00\x11Connection Valid?',
        b'\x00\x00\x00\x0cServer alive'
    )

    default_device.connect()
    default_device.server_alive

    device_server.stop()

    assert default_device.server_alive is False


def test_idn(default_device, device_server):
    idn = 'Matisse TS, S/N:XX-XX-XX, DSP Rev. XX.XX, Firmware: X.X, Date: XXX'\
          ' XX XXXX'
    device_server.setup(
        b'\x00\x00\x00\x05' + b'*IDN?',
        f'\x00\x00\x00\x52:IDN: "{idn}"'.encode('ascii'))

    default_device.connect()

    assert default_device.idn == idn

    default_device.disconnect()


def test_diode_power_dc(default_device, device_server):
    diode_power_dc = 3.125e-1
    device_server.setup(
        b'\x00\x00\x00\x08' + b'DPOW:DC?',
        f'\x00\x00\x00\x15:DPOW:DC: {diode_power_dc:.5e}'.encode('ascii'))

    default_device.connect()

    assert default_device.diode_power_dc == diode_power_dc

    default_device.disconnect()


def test_piezo_ref_cell(default_device, device_server):
    piezo_ref_cell = 0.3
    device_server.setup(
        b'\x00\x00\x00\x0c' + b'REFCELL:NOW?',
        f'\x00\x00\x00\x19:REFCELL:NOW: {piezo_ref_cell:.5e}'.encode('ascii'))

    default_device.connect()

    assert default_device.piezo_ref_cell == piezo_ref_cell

    default_device.disconnect()


def test_changing_piezo_ref_cell(default_device, device_server):
    for p in (0.0, 0.12345678, 0.3, 0.5, 0.7):
        cmd = f'REFCELL:NOW {p:.5f}'.encode('ascii')
        print(data_length(cmd) + cmd)
        device_server.setup(
            data_length(cmd) + cmd,
            b'\x00\x00\x00\x02OK'
        )

        default_device.connect()

        default_device.piezo_ref_cell = p

        default_device.disconnect()


def test_changing_piezo_ref_cell_with_invalid_value(default_device):
    with pytest.raises(ValueError, match='Invalid value'):
        print('raise')
        default_device.piezo_ref_cell = 0 - 0.1

    with pytest.raises(ValueError, match='Invalid value'):
        default_device.piezo_ref_cell = 0.7 + 0.1


def test_piezo_slow(default_device, device_server):
    piezo_slow = 0.1
    device_server.setup(
        b'\x00\x00\x00\x09' + b'SPZT:NOW?',
        f'\x00\x00\x00\x16:SPZT:NOW: {piezo_slow:.5e}'.encode('ascii'))

    default_device.connect()

    assert default_device.piezo_slow == piezo_slow

    default_device.disconnect()


def test_changing_piezo_slow(default_device, device_server):
    for p in (0.0, 0.12345678, 0.3, 0.5, 0.7):
        cmd = f'SPZT:NOW {p:.5f}'.encode('ascii')
        print(data_length(cmd) + cmd)
        device_server.setup(
            data_length(cmd) + cmd,
            b'\x00\x00\x00\x02OK'
        )

        default_device.connect()

        default_device.piezo_slow = p

        default_device.disconnect()


def test_changing_piezo_slow_with_invalid_value(default_device, device_server):
    with pytest.raises(ValueError, match='Invalid value'):
        print('raise')
        default_device.piezo_slow = 0 - 0.1

    with pytest.raises(ValueError, match='Invalid value'):
        default_device.piezo_slow = 0.7 + 0.1


def test_piezo_slow_status(default_device, device_server):
    it = ('RUN', 'STOP'), (MatisseControlStatus.RUN, MatisseControlStatus.STOP)
    for status, piezo_slow_status in zip(*it):
        cmd = f':SPZT:CNTRSTA: {status}'
        device_server.setup(
            b'\x00\x00\x00\x0d' + b'SPZT:CNTRSTA?',
            data_length(cmd) + cmd.encode('ascii'))

        default_device.connect()

        assert default_device.piezo_slow_status == piezo_slow_status

        default_device.disconnect()


def test_piezo_fast_status(default_device, device_server):
    it = ('RUN', 'STOP'), (MatisseControlStatus.RUN, MatisseControlStatus.STOP)
    for status, piezo_fast_status in zip(*it):
        cmd = f':FPZT:CNTRSTA: {status}'
        device_server.setup(
            b'\x00\x00\x00\x0d' + b'FPZT:CNTRSTA?',
            data_length(cmd) + cmd.encode('ascii'))

        default_device.connect()

        assert default_device.piezo_fast_status == piezo_fast_status

        default_device.disconnect()


def test_etalon_piezo_status(default_device, device_server):
    it = ('RUN', 'STOP'), (MatisseControlStatus.RUN, MatisseControlStatus.STOP)
    for status, etalon_piezo_status in zip(*it):
        cmd = f':PZETL:CNTRSTA: {status}'
        device_server.setup(
            b'\x00\x00\x00\x0e' + b'PZETL:CNTRSTA?',
            data_length(cmd) + cmd.encode('ascii'))

        default_device.connect()

        assert default_device.etalon_piezo_status == etalon_piezo_status

        default_device.disconnect()


def test_etalon_thin_status(default_device, device_server):
    it = ('RUN', 'STOP'), (MatisseControlStatus.RUN, MatisseControlStatus.STOP)
    for status, etalon_thin_status in zip(*it):
        cmd = f':TE:CNTRSTA: {status}'
        device_server.setup(
            b'\x00\x00\x00\x0b' + b'TE:CNTRSTA?',
            data_length(cmd) + cmd.encode('ascii'))

        default_device.connect()

        assert default_device.etalon_thin_status == etalon_thin_status

        default_device.disconnect()


def test_piezo_fast_lock(default_device, device_server):
    it = ('TRUE', 'FALSE'), (True, False)
    for status, piezo_fast_lock in zip(*it):
        cmd = f':FPZT:LOCK: {status}'
        device_server.setup(
            b'\x00\x00\x00\x0a' + b'FPZT:LOCK?',
            data_length(cmd) + cmd.encode('ascii'))

        default_device.connect()

        assert default_device.piezo_fast_lock == piezo_fast_lock

        default_device.disconnect()

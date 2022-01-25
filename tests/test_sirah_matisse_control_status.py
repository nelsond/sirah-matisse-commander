from sirah_matisse_commander import MatisseControlStatus


def test_matisse_controller_status():
    assert MatisseControlStatus.RUN != MatisseControlStatus.STOP

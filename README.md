# Sirah Matisse Commander

**NOTE: This module only works with the Matisse Commander TCP server.**

Minimal wrapper for the Sirah Matisse Commander. At the moment, the module only allows to read and write the most relevant values from a Sirah Matisse laser. In addition, arbitrary raw commands (see Matisse Commander manual for details) can be sent to the laser.

## Requirements

This module requires Python >= 3.6 and does not have any other dependencies.

## Install

Install with pip

```shell
$ pip install git+https://gitlab.physik.uni-muenchen.de/sqm/devices/sirah_matisse_commander.git
```

## Example usage

```python
from sirah_matisse_commander import SirahMatisseCommanderDevice

device = SirahMatisseCommanderDevice('localhost', 30000)

device.server_alive # => True
device.diode_power_dc # => 0.1

device.piezo_ref_cell = 0.3

device.disconnect()
```

## Development

Install requirements for development environment

```shell
$ pip install -r requirements/dev.txt
```

Run tests

```shell
$ pytest tests/
```

Generate coverage report

```shell
$ pytest --cov=sirah_matisse_commander --cov-report html tests/
```

---

Sirah and Matisse are registered trademarks of Sirah Lasertechnik GmbH.
# Sirah Matisse Commander

**NOTE: This module only works with the Matisse Commander TCP server, which can be enabled in the menu `Matisse > Communication Options`.**

This repository contains a simple Python client for the Sirah Matisse Commander TCP server. At the moment, the module only allows to read and write the most relevant values from a Sirah Matisse laser. In addition, arbitrary raw commands (see Matisse Commander manual for details) can be sent to the laser.

> Please do note that this client is not officially supported by Sirah Lasertechnik GmbH. Visit [www.sirah.com](https://www.sirah.com) for general support with your laser system.

## Requirements

This module requires Python >= 3.6 and does not have any other dependencies.

## Install

Install with pip

```shell
$ pip install git+https://github.com/nelsond/sirah-matisse-commander
```

## Example usage

```python
from sirah_matisse_commander import SirahMatisseCommanderDevice

device = SirahMatisseCommanderDevice('localhost', 30000)
device.connect()

device.server_alive # => True
device.diode_power_dc # => 0.1

device.piezo_ref_cell = 0.3
device.piezo_ref_cell # => 0.3

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

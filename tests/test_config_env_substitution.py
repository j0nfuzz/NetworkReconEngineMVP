from unittest import mock

import pytest

from app.config import load_default_credentials, load_devices


def _write_config(tmp_path, content):
    config_path = tmp_path / "devices.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def test_substitution_for_default_credentials(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: ${NRE_USER}
  password: ${NRE_PASS}
  enable_password: ${NRE_ENABLE}
devices:
  - name: switch01
    hostname: 10.0.0.1
""",
    )
    with mock.patch.dict(
        "os.environ",
        {"NRE_USER": "admin", "NRE_PASS": "<PASSWORD-01>", "NRE_ENABLE": "<PASSWORD-07>"},
    ):
        devices = load_devices(config)
        assert devices[0]["username"] == "admin"
        assert devices[0]["password"] == "<PASSWORD-01>"
        assert devices[0]["enable_password"] == "<PASSWORD-07>"


def test_substitution_for_device_override(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: ${NRE_USER}
  password: ${NRE_PASS}
devices:
  - name: switch01
    hostname: 10.0.0.1
    password: ${NRE_DEVICE_PASS}
""",
    )
    with mock.patch.dict(
        "os.environ",
        {"NRE_USER": "admin", "NRE_PASS": "<PASSWORD-01>", "NRE_DEVICE_PASS": "<PASSWORD-09>"},
    ):
        devices = load_devices(config)
        assert devices[0]["username"] == "admin"
        assert devices[0]["password"] == "<PASSWORD-09>"


def test_missing_environment_variable_raises(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: ${NRE_MISSING_USER}
devices:
  - name: switch01
    hostname: 10.0.0.1
""",
    )
    with pytest.raises(ValueError, match="Missing environment variable"):
        load_devices(config)


def test_mixed_literal_and_substituted_values(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: admin
  password: ${NRE_PASS}
devices:
  - name: switch01
    hostname: 10.0.0.1
""",
    )
    with mock.patch.dict("os.environ", {"NRE_PASS": "<PASSWORD-01>"}):
        devices = load_devices(config)
        assert devices[0]["username"] == "admin"
        assert devices[0]["password"] == "<PASSWORD-01>"


def test_literal_values_remain_untouched(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: admin
  password: <PASSWORD-10>
  enable_password: <PASSWORD-11>
devices:
  - name: switch01
    hostname: 10.0.0.1
""",
    )
    devices = load_devices(config)
    assert devices[0]["username"] == "admin"
    assert devices[0]["password"] == "<PASSWORD-10>"
    assert devices[0]["enable_password"] == "<PASSWORD-11>"


def test_inheritance_order_with_substitution(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: ${NRE_USER}
  password: ${NRE_PASS}
devices:
  - name: switch01
    hostname: 10.0.0.1
    username: deviceuser
""",
    )
    with mock.patch.dict("os.environ", {"NRE_USER": "admin", "NRE_PASS": "<PASSWORD-01>"}):
        devices = load_devices(config)
        assert devices[0]["username"] == "deviceuser"
        assert devices[0]["password"] == "<PASSWORD-01>"


def test_load_default_credentials_resolves_environment_variables(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: ${NRE_USER}
  password: ${NRE_PASS}
devices:
  - name: switch01
    hostname: 10.0.0.1
""",
    )
    with mock.patch.dict("os.environ", {"NRE_USER": "admin", "NRE_PASS": "<PASSWORD-01>"}):
        defaults = load_default_credentials(config)
        assert defaults["username"] == "admin"
        assert defaults["password"] == "<PASSWORD-01>"

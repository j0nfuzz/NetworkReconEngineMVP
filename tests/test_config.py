from app.config import load_devices


def _write_config(tmp_path, content):
    config_path = tmp_path / "devices.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def test_device_fully_inherits_default_credentials(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: admin
  password: <PASSWORD-01>
  enable_password: <PASSWORD-07>
devices:
  - host: 10.0.0.1
""",
    )
    devices = load_devices(config)
    assert devices[0]["username"] == "admin"
    assert devices[0]["password"] == "<PASSWORD-01>"
    assert devices[0]["enable_password"] == "<PASSWORD-07>"


def test_device_partial_override(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: admin
  password: <PASSWORD-01>
devices:
  - host: 10.0.0.1
    password: <PASSWORD-09>
""",
    )
    devices = load_devices(config)
    assert devices[0]["username"] == "admin"
    assert devices[0]["password"] == "<PASSWORD-09>"


def test_device_full_override(tmp_path):
    config = _write_config(
        tmp_path,
        """
default:
  username: admin
  password: <PASSWORD-01>
devices:
  - host: 10.0.0.1
    username: deviceuser
    password: <PASSWORD-09>
""",
    )
    devices = load_devices(config)
    assert devices[0]["username"] == "deviceuser"
    assert devices[0]["password"] == "<PASSWORD-09>"


def test_legacy_config_without_default(tmp_path):
    config = _write_config(
        tmp_path,
        """
devices:
  - host: 10.0.0.1
    username: deviceuser
    password: <PASSWORD-09>
""",
    )
    devices = load_devices(config)
    assert devices[0]["username"] == "deviceuser"
    assert devices[0]["password"] == "<PASSWORD-09>"

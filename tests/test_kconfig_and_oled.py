import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text()


KCONFIG = read('boards/shields/baseform/Kconfig.defconfig')
DTSI = read('boards/shields/baseform/baseform.dtsi')


def contains(pattern: str, text: str) -> bool:
    """Whitespace-tolerant search for *pattern* inside *text*."""
    return re.search(pattern, text, re.S) is not None


def test_central_config_enables_oled():
    central_conf = read('boards/shields/baseform/baseform_trio_base_central.conf')
    assert re.search(r'CONFIG_ZMK_DISPLAY\s*=\s*y', central_conf)


def test_dtsi_defines_oled_node():
    assert contains(r'oled:\s*ssd1306@3c', DTSI)


def test_kconfig_sets_oled_defaults():
    assert contains(r'config\s+I2C\s+default\s+y', KCONFIG)
    assert contains(r'config\s+SSD1306\s+default\s+y', KCONFIG)


def test_kconfig_has_keyboard_metadata():
    assert contains(r'config\s+ZMK_KEYBOARD_NAME\s+default\s+"baseform"', KCONFIG)


def test_kconfig_has_keymap_default():
    assert contains(
        r'config\s+ZMK_KEYMAP\s+string\s+default\s+"config/\$\(KEYMAP_LAYOUT\)/baseform.keymap"',
        KCONFIG,
    )


def test_kconfig_sets_split_role_central_under_central_shields():
    pattern = (
        r'if\s+SHIELD_BASEFORM_TRIO_BASE_CENTRAL\s*\|\|\s*SHIELD_BASEFORM_DUO_LEFT_CENTRAL.*?'
        r'config\s+ZMK_SPLIT_ROLE_CENTRAL\s+bool\s+default\s+y.*?'
        r'endif'
    )
    assert contains(pattern, KCONFIG)


def test_kconfig_sets_split_default_y_for_halves():
    split_pattern = (
        r'if\s+SHIELD_BASEFORM_TRIO_BASE_CENTRAL.*'
        r'SHIELD_BASEFORM_TRIO_LEFT_PERIPHERAL.*'
        r'SHIELD_BASEFORM_DUO_LEFT_CENTRAL.*'
        r'SHIELD_BASEFORM_ANY_RIGHT_PERIPHERAL.*?'
        r'config\s+ZMK_SPLIT\s+default\s+y'
    )
    assert contains(split_pattern, KCONFIG)

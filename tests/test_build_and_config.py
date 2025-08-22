import re
import pathlib

import yaml

# Paths
ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text()


def test_build_variants_and_studio_snippets():
    data = yaml.safe_load(read('build.yaml'))
    builds = data['include']

    layouts = ['qwerty', 'colemak', 'dvorak']
    # ensure duo and trio central builds exist for each layout
    for layout in layouts:
        assert any(
            b.get('shield') == 'baseform_duo_left_central' and layout in b.get('cmake-args', '')
            for b in builds
        ), f"missing duo build for {layout}"
        assert any(
            'baseform_trio_base_central' in b.get('shield', '') and layout in b.get('cmake-args', '')
            for b in builds
        ), f"missing trio build for {layout}"
        assert any(
            b.get('shield') == 'baseform_trio_left_peripheral' and layout in b.get('artifact-name', '')
            for b in builds
        ), f"missing trio peripheral build for {layout}"

    # central shields must include studio snippet; others must not
    for b in builds:
        shield = b.get('shield', '')
        snippet = b.get('snippet')
        is_central = 'baseform_duo_left_central' in shield or 'baseform_trio_base_central' in shield
        if is_central:
            assert snippet == 'studio-rpc-usb-uart'
        else:
            assert snippet is None


def test_studio_support_and_physical_layouts():
    # CONFIG_ZMK_STUDIO enabled in all layout configs
    for layout in ['qwerty', 'colemak', 'dvorak']:
        conf_text = read(f'config/{layout}/baseform.conf')
        assert re.search(r'CONFIG_ZMK_STUDIO\s*=\s*y', conf_text)

    # baseform.zmk.yml exposes studio
    zmk_yml = yaml.safe_load(read('boards/shields/baseform/baseform.zmk.yml'))
    assert 'studio' in zmk_yml.get('features', [])

    dtsi = read('boards/shields/baseform/baseform.dtsi')
    # chosen nodes for studio rpc and physical layout
    assert re.search(r'zmk,studio-rpc-uart\s*=\s*&uart1', dtsi)
    assert re.search(r'zmk,physical-layout\s*=\s*&baseform_6x4_lo', dtsi)

    # position maps for 6x4, 6x3, and 5x3 layouts
    for layout in ['6x4', '6x3', '5x3']:
        assert re.search(rf'baseform_{layout}_pm', dtsi), f"missing position map for {layout}"


def test_oled_and_other_kconfig_settings():
    # OLED enabled in central config
    central_conf = read('boards/shields/baseform/baseform_trio_base_central.conf')
    assert re.search(r'CONFIG_ZMK_DISPLAY\s*=\s*y', central_conf)

    dtsi = read('boards/shields/baseform/baseform.dtsi')
    assert 'oled: ssd1306@3c' in dtsi

    kconfig = read('boards/shields/baseform/Kconfig.defconfig')
    # OLED related defaults
    assert re.search(r'config\s+I2C\s*\n\s*default\s+y', kconfig)
    assert re.search(r'config\s+SSD1306\s*\n\s*default\s+y', kconfig)

    # critical kconfig settings
    assert re.search(r'config\s+ZMK_KEYBOARD_NAME\s*\n\s*default\s+"baseform"', kconfig)
    assert re.search(r'config\s+ZMK_KEYMAP\s*\n\s*string\s*\n\s*default\s+"config/\$\(KEYMAP_LAYOUT\)/baseform.keymap"', kconfig)
    assert re.search(r'config\s+ZMK_SPLIT_ROLE_CENTRAL\s*\n\s*bool\s*\n\s*default\s+y', kconfig)

    # ZMK_SPLIT default y for participating halves
    split_pattern = (
        r'if\s+SHIELD_BASEFORM_TRIO_BASE_CENTRAL.*'
        r'SHIELD_BASEFORM_TRIO_LEFT_PERIPHERAL.*'
        r'SHIELD_BASEFORM_DUO_LEFT_CENTRAL.*'
        r'SHIELD_BASEFORM_ANY_RIGHT_PERIPHERAL.*?'
        r'config\s+ZMK_SPLIT\s*\n\s*default\s+y'
    )
    assert re.search(split_pattern, kconfig, re.S)

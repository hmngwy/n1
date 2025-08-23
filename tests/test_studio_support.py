import pathlib
import re
import yaml
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text()


# Studio enabled in layout configs
LAYOUTS = ['qwerty', 'colemak', 'dvorak']


@pytest.mark.parametrize('layout', LAYOUTS)
def test_layout_config_enables_studio(layout):
    conf_text = read(f'config/{layout}/baseform.conf')
    assert re.search(r'CONFIG_ZMK_STUDIO\s*=\s*y', conf_text)


def test_zmk_yml_exposes_studio_feature():
    zmk_yml = yaml.safe_load(read('boards/shields/baseform/baseform.zmk.yml'))
    assert 'studio' in zmk_yml.get('features', [])

def test_dtsi_has_studio_rpc():
    dtsi = read('boards/shields/baseform/baseform.dtsi')
    assert re.search(r'zmk,studio-rpc-uart\s*=\s*&uart1', dtsi)


@pytest.mark.parametrize('layout', ['6x4', '6x3', '5x3'])
def test_physical_layout_nodes_exist(layout):
    dtsi = read('boards/shields/baseform/baseform.dtsi')
    pattern = rf'baseform_{layout}_lo:\s*baseform_{layout}_lo'
    assert re.search(pattern, dtsi)


@pytest.mark.parametrize('layout', ['6x4', '6x3', '5x3'])
def test_position_maps_exist(layout):
    dtsi = read('boards/shields/baseform/baseform.dtsi')
    assert re.search(rf'baseform_{layout}_pm', dtsi)

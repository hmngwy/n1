import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text()


def _builds():
    data = yaml.safe_load(read('build.yaml'))
    return data['include']


layouts = ['qwerty', 'colemak', 'dvorak']


def _has_build(predicate):
    return any(predicate(b) for b in _builds())


# Duo and trio build variants
import pytest

@pytest.mark.parametrize('layout', layouts)
def test_duo_central_build_exists(layout):
    assert _has_build(
        lambda b: b.get('shield') == 'baseform_duo_left_central' and layout in b.get('cmake-args', '')
    ), f"missing duo build for {layout}"


@pytest.mark.parametrize('layout', layouts)
def test_trio_central_build_exists(layout):
    assert _has_build(
        lambda b: 'baseform_trio_base_central' in b.get('shield', '') and layout in b.get('cmake-args', '')
    ), f"missing trio build for {layout}"


@pytest.mark.parametrize('layout', layouts)
def test_trio_peripheral_build_exists(layout):
    assert _has_build(
        lambda b: b.get('shield') == 'baseform_trio_left_peripheral' and layout in b.get('artifact-name', '')
    ), f"missing trio peripheral build for {layout}"


def test_any_right_peripheral_build_exists():
    assert _has_build(lambda b: b.get('shield') == 'baseform_any_right_peripheral'), "missing right peripheral build"


def test_only_central_builds_use_studio_snippet():
    for b in _builds():
        shield = b.get('shield', '')
        snippet = b.get('snippet')
        is_central = 'baseform_duo_left_central' in shield or 'baseform_trio_base_central' in shield
        if is_central:
            assert snippet == 'studio-rpc-usb-uart'
        else:
            assert snippet is None

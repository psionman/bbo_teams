from pathlib import Path

from sudoku.config import read_config


def test_config_no_directory(mocker):
    mocker.patch(
        'sudoku.config.CONFIG_PATH',
        Path(
            Path(__file__).parent,
            'test_data',
            'not a directory',
            'config.toml')
        )

    config = read_config()
    assert config.my_int == 1


def test_config_save(mocker):
    mocker.patch(
        'sudoku.config.CONFIG_PATH',
        Path(Path(__file__).parent, 'test_data', 'config', 'config.toml')
        )

    config = read_config()
    if config.path.is_file():
        config.path.unlink()

    config = read_config()
    config.update('my_int', 6)
    config.save()

    config = read_config()

    assert config.my_int == 6

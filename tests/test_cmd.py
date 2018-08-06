from spaken import cmd
from moto import mock_s3


def test_cli(isolated_cli_runner, s3_storage, monkeypatch):
    def mock(args):
        return
    monkeypatch.setattr(cmd, 'pip_command', mock)

    kwargs = [
        '--bucket-uri', 's3://%s/my-project/' % s3_storage['bucket'],
        '--dest', 'wheelhouse/',
        '--requirement', 'requirements.txt',
        '--binary-packages', 'some-package'
    ]

    with open('requirements.txt', 'w') as fh:
        fh.write('spaken')

    result = isolated_cli_runner.invoke(cmd.main, kwargs)
    assert result.exit_code == 0
    assert 'All done' in result.output


def test_cli_invalid(isolated_cli_runner, s3_storage, monkeypatch):
    def mock(args):
        return
    monkeypatch.setattr(cmd, 'pip_command', mock)

    kwargs = [
        '--bucket-uri', 's3://non-existing/my-project/',
        '--dest', 'wheelhouse/',
        '--requirement', 'requirements.txt'
    ]

    with open('requirements.txt', 'w') as fh:
        fh.write('spaken')

    result = isolated_cli_runner.invoke(cmd.main, kwargs)
    assert result.exit_code == 0
    assert 'Error connecting to the storage backend' in result.output
    assert 'All done' in result.output

import json
import subprocess
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import unquote

import pytest
import requests
from click.testing import CliRunner

import main
from generator.attack_registry import AttackRegistry
from generator.pcap_generator import PcapGenerator
from generator.traffic_engine import TrafficEngine
from generator.utils.http_client import TrafficClient
from generator.utils.obfuscator import Obfuscator


@pytest.mark.parametrize('student_id', ['', '.', '..', '../escape', '/tmp/escape', 'a/b', 'a\\b', 'a\x00b'])
def test_invalid_ids_never_reach_filesystem(student_id):
    with pytest.raises(ValueError, match='Student IDs'):
        TrafficEngine(student_id)


@pytest.mark.parametrize('options', [
    {'num_requests': 0}, {'num_requests': -1}, {'attack_count': -1},
    {'num_requests': 2, 'attack_count': 3}, {'attack_ratio': -0.1},
    {'attack_ratio': 1.1}, {'attack_ratio': float('nan')},
    {'obfuscation_level': 0}, {'obfuscation_level': 4},
])
def test_engine_rejects_invalid_options(options):
    with pytest.raises(ValueError):
        TrafficEngine('alice', **options)


@pytest.mark.parametrize('flag,value', [('--requests', '0'), ('--jobs', '0'),
    ('--attack-count', '-1'), ('--attack-ratio', 'nan'), ('--attack-ratio', '1.1'),
    ('--obfuscation', '4')])
def test_cli_validates_ranges(flag, value):
    with patch('generator.pcap_generator.PcapGenerator.generate_batch') as batch:
        result = CliRunner().invoke(main.cli, ['generate', 'alice', 'lo', flag, value])
    assert result.exit_code != 0
    batch.assert_not_called()


def test_batch_rejects_duplicate_ids_before_start(tmp_path):
    engine = TrafficEngine('alice')
    generator = PcapGenerator('lo', str(tmp_path))
    with patch.object(generator, '_generate_single') as run:
        with pytest.raises(ValueError, match='Duplicate'):
            generator.generate_batch([engine, engine], jobs=2)
    run.assert_not_called()


@pytest.mark.parametrize('existing', ['directory', 'symlink'])
def test_existing_output_is_preserved(tmp_path, existing):
    outside = tmp_path / 'original'
    outside.mkdir()
    (outside / 'traffic.pcap').write_bytes(b'keep')
    student = tmp_path / 'alice'
    if existing == 'symlink':
        student.symlink_to(outside, target_is_directory=True)
    else:
        student.mkdir()
        (student / 'traffic.pcap').write_bytes(b'keep')
    with pytest.raises(ValueError, match='Output already exists'):
        PcapGenerator('lo', str(tmp_path)).generate_batch([TrafficEngine('alice')])
    assert (student / 'traffic.pcap').read_bytes() == b'keep'


@patch('generator.pcap_generator.BackgroundServer')
def test_failed_capture_leaves_no_answer_key(server, tmp_path):
    @contextmanager
    def failed_capture(*args, **kwargs):
        yield
        raise RuntimeError('capture failed')
    with patch('generator.pcap_generator.packet_capture', failed_capture):
        engine = MagicMock(spec=TrafficEngine)
        engine.student_id = 'alice'
        engine.run.return_value = {'attacks': []}
        with pytest.raises(RuntimeError, match='capture failed'):
            PcapGenerator('lo', str(tmp_path)).generate_batch([engine])
    assert not (tmp_path / 'alice').exists()
    server.return_value.stop.assert_called_once()


@pytest.mark.parametrize('level', [2, 3])
@pytest.mark.parametrize('payload', ['cat /etc/passwd', 'alert(document.cookie)', '../../../../etc/passwd'])
def test_obfuscation_preserves_payload_semantics(level, payload):
    encoded = Obfuscator.obfuscate(payload, level)
    for _ in range(level - 1):
        encoded = unquote(encoded)
    assert encoded == payload


@patch('generator.utils.http_client.time.sleep')
def test_http_failures_are_reported_and_client_is_closed(sleep):
    session = MagicMock()
    session.request.side_effect = requests.ConnectionError('offline')
    engine = TrafficEngine('alice', client=TrafficClient(session), num_requests=1, attack_count=0)
    with pytest.raises(RuntimeError, match='HTTP request failed'):
        engine.run()
    session.close.assert_called_once()
    sleep.assert_called_once()


@patch('generator.utils.http_client.requests.Session')
def test_generated_http_does_not_use_environment_proxy(session):
    assert TrafficClient().session is session.return_value
    assert session.return_value.trust_env is False


def test_ground_truth_has_request_location_and_obfuscation():
    engine = TrafficEngine('alice', client=MagicMock(spec=TrafficClient), num_requests=5,
                           attack_count=2, obfuscation_level=2)
    data = engine.run()
    assert len(data['attacks']) == 2
    assert len({a['request_index'] for a in data['attacks']}) == 2
    assert all(1 <= a['request_index'] <= 5 and a['timestamp'] > 0 for a in data['attacks'])
    assert data['settings']['obfuscation_level'] == 2


def test_registry_default_cannot_be_shadowed_by_working_directory(tmp_path, monkeypatch):
    folder = tmp_path / 'generator'
    folder.mkdir()
    (folder / 'attacks.json').write_text('{"fake": "untrusted.module.Attack"}')
    monkeypatch.chdir(tmp_path)
    assert 'sqli' in AttackRegistry().get_all_attack_names()
    assert 'fake' not in AttackRegistry().get_all_attack_names()


@pytest.mark.parametrize('contents', ['[]', '{"bad": 42}'])
def test_registry_rejects_invalid_schema(tmp_path, contents):
    registry_file = tmp_path / 'attacks.json'
    registry_file.write_text(contents)
    assert AttackRegistry(registry_file).get_all_attack_names() == []


def test_missing_attack_does_not_silently_generate_normal_traffic():
    with pytest.raises(ValueError, match='Cannot load attack'):
        TrafficEngine('alice', enabled_attacks=['missing'])
    engine = TrafficEngine('alice', enabled_attacks=[], num_requests=1, attack_count=1)
    with pytest.raises(ValueError, match='No attack strategies'):
        engine.run()


@pytest.mark.parametrize('failure', [None, 'rewrite', 'replay'])
def test_replay_maps_dynamic_port_and_cleans_temp_files(tmp_path, failure):
    pcap = tmp_path / 'traffic.pcap'
    pcap.write_bytes(b'original')
    sentinel = tmp_path / 'traffic.pcap.tmp'
    sentinel.write_bytes(b'unrelated')
    (tmp_path / 'answer_key.json').write_text(json.dumps({'server_port': 45678}))
    rewritten = []
    def run(command, **kwargs):
        if command[0] == 'tcprewrite':
            assert '--portmap=45678:80' in command
            output = Path(next(x.split('=', 1)[1] for x in command if x.startswith('--outfile=')))
            output.write_bytes(b'partial' if failure == 'rewrite' else b'rewritten')
            rewritten.append(output)
        if command[0] == ('tcprewrite' if failure == 'rewrite' else 'tcpreplay') and failure:
            raise subprocess.CalledProcessError(1, command)
    with patch('main.interface_exists', return_value=True), patch('main.shutil.which', return_value='/bin/tool'), patch('main.subprocess.run', side_effect=run):
        result = CliRunner().invoke(main.cli, ['replay', 'lo', str(pcap), '--target-port', '80'])
    assert result.exit_code == (1 if failure else 0), result.output
    assert rewritten and not rewritten[0].exists()
    assert sentinel.read_bytes() == b'unrelated'
    assert pcap.read_bytes() == b'original'


@pytest.mark.parametrize('options', [['--target-ip', 'invalid'], ['--target-port', '0'], ['--target-port', '65536']])
def test_replay_rejects_invalid_targets(tmp_path, options):
    pcap = tmp_path / 'traffic.pcap'
    pcap.write_bytes(b'original')
    with patch('main.interface_exists', return_value=True), patch('main.shutil.which', return_value='/bin/tool'), patch('main.subprocess.run') as run:
        result = CliRunner().invoke(main.cli, ['replay', 'lo', str(pcap)] + options)
    assert result.exit_code != 0
    run.assert_not_called()


def test_clean_refuses_unrelated_files(tmp_path):
    source = tmp_path / 'main.py'
    source.write_text('keep')
    result = CliRunner().invoke(main.cli, ['clean', '--output-dir', str(tmp_path)])
    assert result.exit_code == 1
    assert source.read_text() == 'keep'


def test_clean_deletes_generated_outputs_only(tmp_path):
    output = tmp_path / 'output'
    student = output / 'alice'
    student.mkdir(parents=True)
    (student / 'traffic.pcap').write_bytes(b'capture')
    (student / 'answer_key.json').write_text('{}')
    result = CliRunner().invoke(main.cli, ['clean', '--output-dir', str(output)])
    assert result.exit_code == 0
    assert not output.exists()


@patch('generator.shell.PcapLabShell.clear_screen')
@patch('generator.shell.interface_exists', return_value=True)
@patch('builtins.input', return_value='')
@patch('questionary.select')
def test_shell_recovers_from_missing_student_file(select, prompt, interface, clear, tmp_path, capsys):
    from generator.shell import PcapLabShell
    shell = PcapLabShell()
    shell.config['student_file'] = str(tmp_path / 'missing.txt')
    select.return_value.ask.side_effect = ['Run Generation', 'Quit']
    shell.run_menu()
    assert 'Error during generation' in capsys.readouterr().out


def test_same_seed_repeats_requests_and_payloads():
    first = MagicMock(spec=TrafficClient)
    second = MagicMock(spec=TrafficClient)
    data = []
    for client in (first, second):
        result = TrafficEngine('alice', client=client, num_requests=10, attack_count=4,
                               obfuscation_level=3).run()
        for attack in result['attacks']:
            attack.pop('timestamp')
        data.append(result)
    assert data[0] == data[1]
    assert first.execute.call_args_list == second.execute.call_args_list


def test_replay_explicit_port_overrides_legacy_answer_key(tmp_path):
    pcap = tmp_path / 'traffic.pcap'
    pcap.write_bytes(b'original')
    (tmp_path / 'answer_key.json').write_text('{}')
    with patch('main.interface_exists', return_value=True), patch('main.shutil.which', return_value='/bin/tool'), patch('main.subprocess.run') as run:
        result = CliRunner().invoke(main.cli, ['replay', 'lo', str(pcap), '--target-port', '80', '--source-port', '45678'])
    assert result.exit_code == 0, result.output
    assert '--portmap=45678:80' in run.call_args_list[0].args[0]


@pytest.mark.parametrize('contents', ['{}', '[]', '{"server_port": true}', '{"server_port": 0}', 'invalid'])
def test_replay_bad_metadata_requires_explicit_port(tmp_path, contents):
    pcap = tmp_path / 'traffic.pcap'
    pcap.write_bytes(b'original')
    (tmp_path / 'answer_key.json').write_text(contents)
    with patch('main.interface_exists', return_value=True), patch('main.shutil.which', return_value='/bin/tool'), patch('main.subprocess.run') as run:
        result = CliRunner().invoke(main.cli, ['replay', 'lo', str(pcap), '--target-port', '80'])
    assert result.exit_code == 1
    assert '--source-port' in result.output
    run.assert_not_called()


@patch('generator.shell.PcapLabShell.clear_screen')
@patch('builtins.input', return_value='')
@patch('questionary.confirm')
@patch('questionary.select')
def test_shell_clean_refuses_unrelated_data(select, confirm, prompt, clear, tmp_path, monkeypatch, capsys):
    from generator.shell import PcapLabShell
    monkeypatch.chdir(tmp_path)
    output = tmp_path / 'output'
    output.mkdir()
    sentinel = output / 'important.txt'
    sentinel.write_text('keep')
    select.return_value.ask.side_effect = ['Clean Output', 'Quit']
    confirm.return_value.ask.return_value = True
    PcapLabShell().run_menu()
    assert sentinel.read_text() == 'keep'
    assert 'refusing to delete' in capsys.readouterr().out


def test_replay_rejects_silent_bsd_loopback_rewrite(tmp_path):
    import struct
    pcap = tmp_path / 'traffic.pcap'
    pcap.write_bytes(struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 0))
    with patch('main.interface_exists', return_value=True), patch('main.shutil.which', return_value='/bin/tool'), patch('main.subprocess.run') as run:
        result = CliRunner().invoke(main.cli, ['replay', 'lo0', str(pcap), '--target-port', '80'])
    assert result.exit_code == 1
    assert 'DLT_NULL' in result.output
    run.assert_not_called()

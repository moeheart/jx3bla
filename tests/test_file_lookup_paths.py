"""Resolve formal-client paths without reading or modifying the real registry."""
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from FileLookUp import FileLookUp


MODERN = r'SOFTWARE\Kingsoft\SeasunGame\JX3'
LEGACY = r'SOFTWARE\Kingsoft\JX3'
INSTALLER = r'SOFTWARE\JX3Installer'
WORKSPACE_TEMP = Path(__file__).resolve().parents[1] / 'build/file-lookup-path-tests'


class RegistryKey:
    def __init__(self, registry, identity, values):
        self.registry, self.identity, self.values = registry, identity, values
        self.close_count = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.Close()

    def Close(self):
        self.close_count += 1
        if self.close_count != 1:
            raise AssertionError('Registry handle was closed more than once')

    close = Close


class FakeRegistry:
    HKEY_LOCAL_MACHINE = 'HKLM'
    HKEY_CURRENT_USER = 'HKCU'
    KEY_READ = 0x20019
    KEY_WOW64_64KEY = 0x0100
    KEY_WOW64_32KEY = 0x0200
    REG_SZ, REG_EXPAND_SZ, REG_DWORD, REG_MULTI_SZ = 1, 2, 4, 7

    def __init__(self, entries=None):
        self.entries = entries or {}
        self.attempts, self.opened = [], []

    def OpenKey(self, hive, path, reserved=0, access=KEY_READ):
        identity = (hive, path, access & (self.KEY_WOW64_64KEY | self.KEY_WOW64_32KEY))
        self.attempts.append(identity)
        if identity not in self.entries:
            raise FileNotFoundError(path)
        values = self.entries[identity]
        if isinstance(values, BaseException):
            raise values
        key = RegistryKey(self, identity, values)
        self.opened.append(key)
        return key

    @staticmethod
    def QueryValueEx(key, name):
        value = key.values.get(name, FileNotFoundError(name))
        if isinstance(value, BaseException):
            raise value
        return value

    @staticmethod
    def CloseKey(key):
        key.Close()

    @staticmethod
    def ExpandEnvironmentStrings(value):
        return os.path.expandvars(value)


class FileLookupPathTests(unittest.TestCase):
    def setUp(self):
        WORKSPACE_TEMP.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=WORKSPACE_TEMP)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def formal_install(self, name, old_layout=False):
        install = self.root / name
        game = install / 'Game/JX3' if old_layout else install
        data = game / 'bin/zhcn_hd/interface/MY#DATA'
        data.mkdir(parents=True)
        return install, data

    def add_player(self, data, player='Recorder'):
        account = data / 'account@zhcn_hd'
        (account / player).mkdir(parents=True)
        logs = account / 'userdata/combat_logs'
        logs.mkdir(parents=True)
        (account / 'manifest.jx3dat').touch()
        return logs

    def assert_path(self, actual, expected):
        self.assertTrue(actual)
        self.assertEqual(Path(actual).resolve(), expected.resolve())

    def assert_closed(self, registry):
        self.assertTrue(registry.opened)
        self.assertTrue(all(key.close_count == 1 for key in registry.opened))

    @staticmethod
    def config(basepath='', jx3path='', playername='Recorder'):
        return SimpleNamespace(item={'general': dict(basepath=str(basepath), jx3path=str(jx3path),
                                                     playername=playername, datatype='jcl')})

    def test_modern_hkcu_32_install_wins_over_old_hklm_64_install(self):
        modern, expected = self.formal_install('modern')
        legacy, _ = self.formal_install('old-install', old_layout=True)
        registry = FakeRegistry({
            ('HKCU', MODERN, 0x0200): {'InstallPath': (str(modern), FakeRegistry.REG_SZ)},
            ('HKLM', LEGACY, 0x0100): {'InstallPath': (str(legacy), FakeRegistry.REG_SZ)},
        })
        lookup = FileLookUp()
        with patch('FileLookUp.winreg', registry):
            found = lookup.getPathFromWinreg()
            self.assertEqual(found, lookup.jx3path)
            self.assert_path(lookup.getDataFolder(), expected)
        self.assert_closed(registry)

    def test_each_hive_and_registry_view_can_supply_the_modern_install(self):
        install, expected = self.formal_install('both-views')
        for hive in ('HKLM', 'HKCU'):
            for view in (0x0100, 0x0200):
                with self.subTest(hive=hive, view=view):
                    registry = FakeRegistry({
                        (hive, MODERN, view): {'InstallPath': (str(install), FakeRegistry.REG_SZ)},
                    })
                    with patch('FileLookUp.winreg', registry):
                        self.assert_path(FileLookUp().getDataFolder(), expected)
                    self.assertIn((hive, MODERN, view), registry.attempts)
                    self.assert_closed(registry)

    def test_stale_denied_and_non_string_values_fall_through_and_close_handles(self):
        legacy, expected = self.formal_install('legacy-valid', old_layout=True)
        installer, _ = self.formal_install('installer-lower-priority')
        stale_file = self.root / 'removed-client.exe'
        stale_file.touch()
        registry = FakeRegistry({
            ('HKLM', MODERN, 0x0100): {'InstallPath': (str(stale_file), FakeRegistry.REG_SZ)},
            ('HKLM', MODERN, 0x0200): PermissionError('inaccessible registry view'),
            ('HKCU', MODERN, 0x0100): {'InstallPath': (str(installer), FakeRegistry.REG_DWORD)},
            ('HKCU', MODERN, 0x0200): {'InstallPath': ([str(installer)], FakeRegistry.REG_MULTI_SZ)},
            ('HKLM', LEGACY, 0x0100): {'InstallPath': (str(self.root / 'removed'), FakeRegistry.REG_SZ)},
            ('HKLM', LEGACY, 0x0200): {'InstallPath': (123, FakeRegistry.REG_SZ)},
            ('HKCU', LEGACY, 0x0100): {'InstallPath': PermissionError('value access denied')},
            ('HKCU', LEGACY, 0x0200): {'InstallPath': ('  " %JX3_PATH_TEST_ROOT% "  ', FakeRegistry.REG_EXPAND_SZ)},
            ('HKLM', INSTALLER, 0x0100): {'InstPath': (str(installer), FakeRegistry.REG_SZ)},
        })
        with patch.dict(os.environ, {'JX3_PATH_TEST_ROOT': str(legacy)}), patch('FileLookUp.winreg', registry):
            self.assert_path(FileLookUp().getDataFolder(), expected)
        self.assert_closed(registry)

    def test_installer_instpath_is_used_after_both_installpath_keys_fail(self):
        installer, expected = self.formal_install('old-installer-layout', old_layout=True)
        registry = FakeRegistry({
            ('HKCU', INSTALLER, 0x0200): {'InstPath': (str(installer), FakeRegistry.REG_SZ)},
        })
        with patch('FileLookUp.winreg', registry):
            self.assert_path(FileLookUp().getDataFolder(), expected)
        self.assert_closed(registry)

    def test_manual_root_and_each_formal_subdirectory_resolve_the_same_data(self):
        install, expected = self.formal_install('manual-prefix', old_layout=True)
        candidates = [install, install / 'Game', install / 'Game/JX3',
                      install / 'Game/JX3/bin', install / 'Game/JX3/bin/zhcn_hd',
                      expected.parent, expected]
        registry = FakeRegistry()
        with patch('FileLookUp.winreg', registry):
            for candidate in candidates:
                with self.subTest(path=candidate):
                    lookup = FileLookUp()
                    lookup.jx3path = '  "%s"  ' % candidate.as_posix()
                    self.assert_path(lookup.getDataFolder(), expected)
        self.assertEqual(registry.attempts, [])

    def test_other_client_flavors_and_launcher_are_not_registry_fallbacks(self):
        for game, mode in (('JX3_EXP', 'zhcn_exp'), ('JX3_CLASSIC', 'zhcn'), ('JX3_WJ', 'zhcn_wj')):
            (self.root / 'Game' / game / 'bin' / mode / 'interface/MY#DATA').mkdir(parents=True)
        launcher = self.root / 'launcher'
        launcher.mkdir()
        unrelated, _ = self.formal_install('unrelated-formal')
        registry = FakeRegistry({
            ('HKLM', MODERN, 0x0100): {'InstallPath': (str(launcher), FakeRegistry.REG_SZ)},
            ('HKLM', r'SOFTWARE\Kingsoft\JX3_EXP', 0x0100): {'InstallPath': (str(unrelated), FakeRegistry.REG_SZ)},
            ('HKLM', r'SOFTWARE\Kingsoft\JX3_CLASSIC', 0x0100): {'InstallPath': (str(unrelated), FakeRegistry.REG_SZ)},
            ('HKLM', r'SOFTWARE\Kingsoft\JX3_WJ', 0x0100): {'InstallPath': (str(unrelated), FakeRegistry.REG_SZ)},
        })
        with patch('FileLookUp.winreg', registry):
            lookup = FileLookUp()
            self.assertEqual(lookup.getPathFromWinreg(), '')
            self.assertEqual(lookup.datapath, '')
            lookup.jx3path = str(self.root / 'Game')
            self.assertEqual(lookup.getDataFolder(), '')
            self.assertEqual(lookup.getAllPlayers(), [])
        self.assertTrue(all(key in (MODERN, LEGACY, INSTALLER) for _, key, _ in registry.attempts))
        self.assert_closed(registry)

    def test_failed_manual_lookup_clears_previous_data_and_hides_stale_players(self):
        _, previous = self.formal_install('previous-install')
        self.add_player(previous)
        lookup = FileLookUp()
        lookup.datapath = str(previous)
        lookup.jx3path = str(self.root / 'uninstalled')
        with patch('FileLookUp.winreg', FakeRegistry()):
            self.assertEqual(lookup.getDataFolder(), '')
            self.assertEqual(lookup.datapath, '')
            self.assertEqual(lookup.getAllPlayers(), [])

    def test_unreadable_player_directory_returns_empty_list(self):
        install, data = self.formal_install('no-permission')
        self.add_player(data)
        lookup = FileLookUp()
        lookup.jx3path = str(install)
        real_listdir = os.listdir

        def deny_data_folder(path):
            if Path(path).resolve() == data.resolve():
                raise PermissionError('directory access denied')
            return real_listdir(path)

        with patch('FileLookUp.winreg', FakeRegistry()), patch('FileLookUp.os.listdir', side_effect=deny_data_folder):
            self.assertEqual(lookup.getAllPlayers(), [])

    def test_configured_basepath_takes_precedence_over_player_and_registry(self):
        direct_logs = self.root / 'chosen-logs'
        direct_logs.mkdir()
        install, _ = self.formal_install('configured-install')
        registry = FakeRegistry()
        lookup = FileLookUp()
        with patch('FileLookUp.winreg', registry):
            self.assert_path(lookup.initFromConfig(self.config(basepath=direct_logs, jx3path=install)), direct_logs)
        self.assertEqual(lookup.dataType, 'jcl')
        self.assertEqual(registry.attempts, [])

    def test_newer_empty_account_and_metadata_file_do_not_replace_real_player_logs(self):
        install, data = self.formal_install('partly-initialized-accounts')
        logs = self.add_player(data)
        stale = data / 'new-account-without-logs'
        (stale / 'Recorder').mkdir(parents=True)
        os.utime(stale, (2000000000, 2000000000))
        notes = data / 'account@zhcn_hd/notes.txt'
        notes.write_text('metadata is not a player directory', encoding='utf-8')
        os.utime(notes, (2000000010, 2000000010))
        lookup = FileLookUp()
        lookup.jx3path, lookup.dataType = str(install), 'jcl'
        with patch('FileLookUp.winreg', FakeRegistry()):
            lookup.getBasePath('Recorder')
            self.assert_path(lookup.basepath, logs)
            players = lookup.getAllPlayers()
        self.assertIn('Recorder', players)
        self.assertNotIn('notes.txt', players)

    def test_explicit_install_is_kept_for_player_selection_even_without_recorder(self):
        install, data = self.formal_install('selected-install')
        logs = self.add_player(data)
        automatic, _ = self.formal_install('registry-install')
        for player in ('Recorder', ''):
            with self.subTest(player=player):
                registry = FakeRegistry({
                    ('HKLM', MODERN, 0x0100): {'InstallPath': (str(automatic), FakeRegistry.REG_SZ)},
                })
                lookup = FileLookUp()
                with patch('FileLookUp.winreg', registry):
                    result = lookup.initFromConfig(self.config(jx3path=install, playername=player))
                    if player:
                        self.assert_path(result, logs)
                    else:
                        self.assertEqual(result, '.')
                    self.assertEqual(lookup.getAllPlayers(), ['Recorder'])
                    self.assert_path(lookup.datapath, data)
                self.assertEqual(registry.attempts, [])


if __name__ == '__main__':
    unittest.main()

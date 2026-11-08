"""Exercise delayed responses without sleeping or permitting network I/O."""
import io
import json
import unittest
from unittest.mock import Mock, patch


class VirtualDelayedResponse(io.StringIO):
    def __init__(self, timeout, delay):
        super().__init__(json.dumps({'status': 'success', 'data': [
            {'result': 'success', 'shortID': 123, 'num': 1, 'scoreRank': -1}]}))
        self.timeout, self.delay = timeout, delay

    def read(self, *args, **kwargs):
        if self.delay > self.timeout:
            raise TimeoutError('virtual delayed socket read exceeded its timeout')
        return super().read(*args, **kwargs)


class UploadTimeoutTests(unittest.TestCase):
    def setUp(self):
        self.network = patch('socket.socket.connect', side_effect=AssertionError('network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.http = patch('urllib.request.urlopen', side_effect=AssertionError('HTTP forbidden'))
        self.http.start()
        self.addCleanup(self.http.stop)

    def test_actual_upload_accepts_response_after_old_30_second_limit(self):
        from MainWindow import MainWindow
        # The same delayed socket read fails with the former timeout.
        with self.assertRaises(TimeoutError):
            json.load(VirtualDelayedResponse(timeout=30, delay=35))
        for size in (1_700_000, 1_800_000):
            with self.subTest(payload_bytes=size):
                app = MainWindow.__new__(MainWindow)
                app.setNotice = Mock()
                anchor = {'overall': {}}
                app.uploadData = [{'id': 0, 'type': 'replay',
                    'data': {'statistics': {'timeline': 'x' * size}}, 'anchor': anchor}]
                observed = []

                def delayed_upload(url, *, data, timeout):
                    observed.append((len(data), timeout))
                    return VirtualDelayedResponse(timeout, delay=35)

                with patch('MainWindow.get_api_url', return_value='offline://upload'), \
                        patch('MainWindow.urllib.request.urlopen', side_effect=delayed_upload):
                    app.executeUploadData()
                payload_bytes, timeout = observed[0]
                self.assertGreaterEqual(timeout, payload_bytes / (16 * 1024) + 60)
                self.assertLessEqual(timeout, 600)
                self.assertEqual(anchor['overall']['shortID'], 123)
                self.assertEqual(app.uploadData, [])

    def test_response_exceeding_new_budget_retains_queue_and_anchors(self):
        from MainWindow import MainWindow
        app = MainWindow.__new__(MainWindow)
        app.setNotice = Mock()
        anchor = {'overall': {}}
        queue = [{'id': 0, 'type': 'replay', 'data': {}, 'anchor': anchor}]
        app.uploadData = queue
        with patch('MainWindow.get_api_url', return_value='offline://upload'), \
                patch('MainWindow.urllib.request.urlopen',
                      side_effect=lambda url, *, data, timeout: VirtualDelayedResponse(timeout, delay=601)):
            app.executeUploadData()
        self.assertIs(app.uploadData, queue)
        self.assertEqual(anchor, {'overall': {}})
        self.assertIn('失败', app.setNotice.call_args.args[0]['t1'])
        self.assertIn('保留', app.setNotice.call_args.args[0]['t2'])

    def test_timeout_is_bounded_for_small_and_maximum_forms(self):
        from MainWindow import get_upload_timeout
        self.assertEqual(get_upload_timeout(0), 120)
        self.assertEqual(get_upload_timeout(200 * 1024 * 1024), 600)


if __name__ == '__main__':
    unittest.main()

"""Logs address migration preserves API routing and explicit remote targets."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import ServerAddress
from serverFunc.jx3bla_address_server import ADDRESS_DATA


class ServerAddressTests(unittest.TestCase):
    def setUp(self):
        cache = patch.object(ServerAddress, "_address_cache", None)
        cache.start()
        self.addCleanup(cache.stop)
        network = patch("socket.socket.connect", side_effect=AssertionError("network forbidden"))
        network.start()
        self.addCleanup(network.stop)

    def response(self, data):
        return patch("ServerAddress.urllib.request.urlopen",
                     return_value=io.BytesIO(json.dumps(data).encode("utf-8")))

    def test_offline_fallback_uses_https_logs_and_unchanged_api(self):
        with patch("ServerAddress.urllib.request.urlopen", side_effect=OSError("offline")):
            self.assertEqual(ServerAddress.get_logs_url("/xiangzhi/123"),
                             "https://jx3bla.moeheart.cn:443/xiangzhi/123")
            self.assertEqual(ServerAddress.get_api_url("/uploadCombinedData"),
                             "http://jx3bla.moeheart.cn:80/uploadCombinedData")

    def test_address_service_defaults_route_logs_links_and_encode_query(self):
        self.assertEqual(ADDRESS_DATA["api"], {"host": "jx3bla.moeheart.cn", "port": 80})
        with self.response(ADDRESS_DATA):
            url = urlsplit(ServerAddress.get_logs_url("/getMultiRank.html",
                          {"server": "唯我独尊", "ids": "角色+测试"}))
            self.assertEqual((url.scheme, url.hostname, url.port, url.path),
                             ("https", "jx3bla.moeheart.cn", 443, "/getMultiRank.html"))
            self.assertEqual(parse_qs(url.query), {"server": ["唯我独尊"], "ids": ["角色+测试"]})
            self.assertEqual(ServerAddress.get_api_url("/getAnnouncement"),
                             "http://jx3bla.moeheart.cn:80/getAnnouncement")

    def test_explicit_remote_overrides_are_preserved(self):
        with self.response({"api": {"scheme": "http", "host": "127.0.0.1", "port": 8009},
                            "logs": {"scheme": "http", "host": "127.0.0.1", "port": 5173}}):
            self.assertEqual(ServerAddress.get_logs_url(), "http://127.0.0.1:5173/")
            self.assertEqual(ServerAddress.get_api_url(), "http://127.0.0.1:8009/")

    def test_legacy_remote_targets_without_scheme_still_mean_http(self):
        with self.response({"logs": {"host": "legacy.example", "port": 80}}):
            self.assertEqual(ServerAddress.get_logs_url(), "http://legacy.example:80/")

    def test_remote_https_without_port_defaults_to_443(self):
        with self.response({"logs": {"scheme": "https", "host": "preview.example"}}):
            self.assertEqual(ServerAddress.get_logs_url(), "https://preview.example:443/")

    def test_missing_logs_uses_new_fallback(self):
        with self.response({"api": {"host": "api.example", "port": 8009}}):
            self.assertEqual(ServerAddress.get_logs_url(), "https://jx3bla.moeheart.cn:443/")
            self.assertEqual(ServerAddress.get_api_url(), "http://api.example:8009/")


if __name__ == "__main__":
    unittest.main()

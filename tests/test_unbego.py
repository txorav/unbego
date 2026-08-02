import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unbego_host
import unbego_detect
import unbego_flash


class TestUnbegoHost(unittest.TestCase):
    @patch('subprocess.run')
    def test_run_cmd(self, mock_run):
        # Setup mock
        mock_result = MagicMock()
        mock_result.stdout = "mocked_output\n"
        mock_run.return_value = mock_result

        # Test
        result = unbego_host.run_cmd("echo 'mocked_output'")
        self.assertEqual(result, "mocked_output")

    @patch('unbego_host.run_cmd')
    def test_get_host_info(self, mock_run_cmd):
        # Setup mock to return a predictable string
        mock_run_cmd.return_value = "TestValue"

        info = unbego_host.get_host_info()

        # Verify info dictionary has expected keys
        self.assertEqual(info['manufacturer'], "TestValue")
        self.assertEqual(info['model'], "TestValue")
        self.assertTrue('rooted' in info)
        self.assertTrue('usb_otg_supported' in info)


class TestUnbegoDetect(unittest.TestCase):
    def test_mtk_modes(self):
        # Verify the MTK constants are correct
        self.assertEqual(unbego_detect.MTK_VENDOR_ID, "0e8d")
        self.assertIn("0003", unbego_detect.MTK_MODES)
        self.assertEqual(unbego_detect.MTK_MODES["0003"], "BROM (Boot ROM) Mode")

    @patch('subprocess.run')
    def test_get_usb_devices_termux(self, mock_run):
        # Mock termux-usb -l output
        mock_result = MagicMock()
        mock_result.stdout = '["/dev/bus/usb/001/002", "/dev/bus/usb/001/003"]'
        mock_run.return_value = mock_result

        devices = unbego_detect.get_usb_devices_termux()
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0], "/dev/bus/usb/001/002")


class TestUnbegoFlash(unittest.TestCase):
    @patch('builtins.print')
    @patch('os.path.isdir')
    def test_check_mtkclient_not_found(self, mock_isdir, mock_print):
        mock_isdir.return_value = False
        self.assertFalse(unbego_flash.check_mtkclient())

    @patch('builtins.print')
    @patch('os.path.isfile')
    @patch('os.path.isdir')
    def test_check_mtkclient_found(self, mock_isdir, mock_isfile, mock_print):
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        self.assertTrue(unbego_flash.check_mtkclient())


class TestUnbegoCore(unittest.TestCase):
    def test_core_constants(self):
        # We can't easily test the interactive loop, but we can verify
        # constants and imports are valid
        import unbego_core
        self.assertEqual(unbego_core.DEVICE_CODENAME, "begonia")
        self.assertEqual(unbego_core.VERSION, "1.0.0")

    @patch('builtins.print')
    def test_banner(self, mock_print):
        import unbego_core
        unbego_core.banner()
        self.assertTrue(mock_print.called)

    @patch('builtins.print')
    def test_menu(self, mock_print):
        import unbego_core
        unbego_core.menu()
        self.assertTrue(mock_print.called)


if __name__ == '__main__':
    unittest.main()

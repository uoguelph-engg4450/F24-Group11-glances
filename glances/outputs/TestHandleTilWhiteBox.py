import unittest
from unittest.mock import patch, MagicMock
import platform
import subprocess
import os
import matplotlib.pyplot as plt


class TestHandleTilWhiteBox(unittest.TestCase):
    def setUp(self):
        # Define a minimal class for testing
        class SampleClass:
            def __init__(self):
                self.history = MagicMock()

            def __get_stat_display(self, key, layer=None):
                return f"Stat Display for {key}"

            def _handle_til(self):
                data = self.history.get(nb=12)
                print(f"\nAvailable keys: {data}")
                cs_status = None
                print(self.__get_stat_display('cpu', layer=cs_status))

                cpu_history = [0, 20, 200, 205, 503, 560, 503, 509, 600, 504, 546, 505]
                x = [1, 2, 3, 4, 10, 12, 15, 24, 26, 27, 28, 29]

                plt.plot(x, cpu_history)
                plt.xlabel("Timer (milliseconds)")
                plt.ylabel("CPU Usage (%)")
                plt.title("CPU Usage vs Time")

                file_path = "plot.png"
                plt.savefig(file_path)
                plt.close()

                try:
                    if platform.system() == "Linux":
                        try:
                            subprocess.run(["xdg-open", file_path], check=True)
                        except Exception:
                            subprocess.run(["explorer.exe", file_path])
                    else:
                        raise OSError()
                except Exception:
                    if platform.system() == "Windows":
                        os.startfile(file_path)

        self.sample_instance = SampleClass()

    @patch("matplotlib.pyplot.savefig")
    @patch("platform.system")
    @patch("subprocess.run")
    @patch("os.startfile")
    def test_handle_til(
        self, mock_startfile, mock_run, mock_platform, mock_savefig
    ):
        # Case 1: Empty history
        self.sample_instance.history.get.return_value = {}
        mock_platform.return_value = "Linux"
        self.sample_instance._handle_til()
        mock_savefig.assert_called_once_with("plot.png")
        mock_run.assert_called()

        # Case 2: Valid history data
        self.sample_instance.history.get.return_value = {"cpu": [1, 2, 3]}
        self.sample_instance._handle_til()
        mock_savefig.assert_called_with("plot.png")

        # Case 3: Platform-specific logic - Linux
        mock_platform.return_value = "Linux"
        mock_run.reset_mock()
        self.sample_instance._handle_til()
        mock_run.assert_any_call(["xdg-open", "plot.png"], check=True)

        # Case 4: Platform-specific logic - Windows
        mock_platform.return_value = "Windows"
        mock_startfile.reset_mock()
        self.sample_instance._handle_til()
        mock_startfile.assert_called_once_with("plot.png")

        # Case 5: Unsupported platform
        mock_platform.return_value = "Unknown"
        with self.assertRaises(OSError):
            self.sample_instance._handle_til()


if __name__ == "__main__":
    unittest.main()

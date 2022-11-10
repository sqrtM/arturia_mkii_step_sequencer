from distutils.core import setup
import py2exe

setup(
  console=['main.py'],
  options = {
    'py2exe': {
      'packages': ['rtmidi', 'mido', 'mido.backends.rtmidi', 'pythonosc.udp_client']
    }
  }
)
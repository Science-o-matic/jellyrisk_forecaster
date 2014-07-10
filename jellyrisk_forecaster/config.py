import os
import importlib

SETTINGS_MODULE = os.environ.get('JELLYRISK_SETTINGS_MODULE')

try:
    mod = importlib.import_module(SETTINGS_MODULE)
except ImportError, e:
    raise ImportError("Could not import settings '%s' (Is it on sys.path?): %s" % (SETTINGS_MODULE, e))

settings = mod

# defaults
settings.LIMIT_ROWS = getattr(settings, 'SETTINGS_LIMIT_ROWS', 15000)

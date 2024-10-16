import os
import shutil
from pathlib import Path

default_credentials = '~/.fabfed/fabfed_credentials.yml'

def absolute_path(path):
    from pathlib import Path
    
    path = Path(path).expanduser().absolute()
    return os.path.realpath(str(path))


def default_credentials_location():
    return absolute_path(default_credentials)

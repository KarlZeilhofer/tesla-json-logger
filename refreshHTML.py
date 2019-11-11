#!/usr/local/bin/python3

__version__ = '1.0'

import os

import tesla

code = tesla.getDataInHTML(5)
with open(os.path.expanduser(base.appDataPath), 'w') as fid:
    fid.write(code)
    fid.close()
tesla.logger.info('HTML calendar updated.')

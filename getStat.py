#!/usr/local/bin/python3

__version__ = '1.3'

"""
    getStat.py
    Tesla Data Logger

    @author: Boonleng Cheong

    Updates

    1.3.   - 9/4/2019
           - Updated logging
           - Logs are now in local time
           - Improved handling of empty data logs

    1.2.1  - 8/7/2019
           - Decided to mave all modules into ./tesla

    1.2    - 8/6/2019
           - Moved a lot of reusable functions to tesla.py

    1.1    - 8/5/2019
           - Moved a lot of reusable functions to foundation.py

    1.0    - 8/2/2019
           - It is working. We can schedule this to run routinely through a cronjob

    0.1    - 7/21/2019
           - Started

"""

import os
import time
import json
import argparse
import shutil

import tesla

#
#     M  A  I  N
#

if __name__ == '__main__':
    # First things first, parse all the arguments
    usage = '''
        getStat.py [options]

        examples:

        getStat.py
        getStat.py -v
        '''
    parser = argparse.ArgumentParser(prog='getStat', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', default=0, action='count', help='increase the verbosity level')
    parser.add_argument('-u', default=False, action="store_true", help='updates the HTML calendar')
    parser.add_argument('-w', default=False, action="store_true", help='writes the results to a file')
    # TODO: parser.add_argument('-uscs', default=False, action="store_true", help='use United States customary system (miles and Farenheit)')
    args = parser.parse_args()

    # Set the logger to output something if verbosity flag is set
    if args.v > 1:
        tesla.showDebugMessages()
    elif args.v:
        tesla.showInfoMessages()

    # Log an entry
    tesla.logger.debug('--- Started ----------')
    tesla.logger.info('Tesla Data Logger {}'.format(__version__))

    dat = tesla.requestData()

    if dat is None:
        tesla.logger.info('Vehicle is sleeping')
    else:
        jsonString = json.dumps(dat, indent=4)

        tesla.logger.info('Data received. battery_level = {}%   range = {} / {} mi   write = {}'.format(
            dat['charge_state']['battery_level'],
            dat['charge_state']['battery_range'],
            dat['charge_state']['ideal_battery_range'],
            args.w))
        if args.w:
            now = time.localtime(time.time())
            path = '{}/{}'.format(tesla.dataLogHome, time.strftime('%Y%m%d', now))
            if not os.path.exists(path):
                os.mkdir(path)
            filename = '{}/{}'.format(path, time.strftime('%Y%m%d-%H%M.json', now))
            with open(filename, 'w') as fid:
                fid.write(jsonString)
                fid.close()
        if args.u:
            blobPath = os.path.join(tesla.appDataPath, 'blob')
            if not os.path.exists(blobPath):
                shutil.copytree('./blob', blobPath)
            code = tesla.getDataInHTML()
            with open(os.path.join(tesla.appDataPath, 'calendar.html'), 'w') as fid:
                fid.write(code)
                fid.close()
            tesla.logger.info('HTML calendar updated.')

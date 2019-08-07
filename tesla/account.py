import os
import json
import requests
import configparser

from . import base

def getConfig():
    if not os.path.exists(base.rcFile):
        base.logger.info('No configuration file. Setting up ...')
        try:
            username = input('Enter username: ')
            if len(username) == 0:
                base.logger.info('Setup aborted. No username provided.')
                return None
        except KeyboardInterrupt:
            base.logger.exception('Setup aborted. User aborted the setup.')
            return None

        import getpass
        import keyring

        password = keyring.get_password(base.site, username)
        if not password:
            password = getpass.getpass('Enter password: ')
            if not password:
                base.logger.info('Setup aborted. No password provided.')
                return None
            keyring.set_password(base.site, username, password)
            base.logger.info('Password saved to Keychain Access')

        # Retrieve a token using the login provided
        url = 'https://{}/oauth/token'.format(base.site)
        payload = {
            'grant_type': 'password',
            'client_id': '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384',
            'client_secret': 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3',
            'email': username,
            'password': password
        }
        headers = {
            'Host': base.site,
            'User-Agent': 'Learning',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            base.logger.exception('Unable to retrieve token. r = {}'.format(r.status_code))
            return None
        token = r.json()

        # Retrieve a list of vehicles
        url = 'https://owner-api.teslamotors.com/api/1/vehicles'
        headers = {
            'Authorization': 'Bearer {}'.format(token['access_token'])
        }
        r = requests.get(url, headers=headers)
        cars = []
        if r.status_code == 200:
            cars = r.json()['response']
        else:
            base.logger.exception('Unable to retrieve list of vehicles.')

        # Save username and token into the configuration
        config = configparser.ConfigParser()
        config.add_section('user')
        config.add_section('token')
        config['user'] = {'username': username}
        config['token'] = token
        if len(cars):
            for car in cars:
                key = car['vin']
                config.add_section(key)
                config[key] = {'id': car['id'],
                               'vid': car['vehicle_id'],
                               'name': car['display_name']}
        with open(base.rcFile, 'w') as fid:
            config.write(fid)

        base.logger.info('Config setup complete')

    # Make a config and load the configuration
    config = configparser.ConfigParser()
    try:
        config.read(base.rcFile)
    except configparser.ParsingError as e:
        base.logger.exception('Bad config file.')
        raise ConfigError from e

    # Assess the completeness
    if not all(sec in config.sections() for sec in ['user', 'token']):
        base.logger.exception('Bad config file. Try removing it and rerun this script.')
        return None

    cars = []
    for sec in config.sections():
        if sec not in ['user', 'token']:
            cars.append(dict(config[sec]))
    return {'username':config['user']['username'], 'token':dict(config['token']), 'cars':cars}

def refreshToken():
    # Load the current configuration
    config = configparser.ConfigParser()
    try:
        config.read(base.rcFile)
    except configparser.ParsingError as e:
        base.logger.exception('Bad config file.')
        raise ConfigError from e
    url = 'https://{}/oauth/token'.format(base.site)
    payload = {
        'grant_type': 'refresh_token',
        'client_id': '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384',
        'client_secret': 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3',
        'refresh_token': config['token']['refresh_token']
    }
    headers = {
        'Host': base.site,
        'User-Agent': 'Learning',
        'Content-Type': 'application/json'
    }
    #r = requests.post(url, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        token = r.json()
        # Update config
        config['token'] = r.json()
        print(config)
        with open(base.rcFile, 'w') as fid:
            config.write(fid)

"""Helpers for loading basic configs, settings, and interfaces."""

import configparser
import os
import yaml

from py3cw import request as cw_req

CODEHOME = os.environ.get("CODEHOME")


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config_path = os.path.join(CODEHOME, "config_files/config.ini")
    config.read(config_path)
    return config


def get_settings() -> dict:
    settings_path = os.path.join(CODEHOME, "config_files/settings.yaml")
    with open(settings_path) as settings_f:
        settings = yaml.load(settings_f, Loader=yaml.Loader)
    return settings


def get_3c_interface():
    config = get_config()
    py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])
    return py3cw

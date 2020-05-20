import os
import logging
#import urllib2
import platform
import subprocess

""" Network class """
class Network:
    """ Check if the server has a connection to xxx """
    @staticmethod
    def check_netwerk_status(ip = "8.8.8.8"):
        try:
            param = '-n' if platform.system().lower()=='windows' else '-c'
            command = ['ping', param, '1', ip]
            return subprocess.call(command) == 0
        except Exception as ex:
            logging.error(ex)
            raise ex
#! /usr/bin/python3
# -*- coding:utf-8 -*-

import json
import os

import pymysql

CONFIG_FILEPATH = 'kekosync_config.json'


class KeKoSync:
    def __init__(self):
        self._load_config()

    def create_connection(self):
        return pymysql.connect(host=self._settings['db_host'],
                               database=self._settings['db_name'],
                               user=self._settings['db_username'],
                               password=self._settings['db_password'])

    def _load_config(self):
        if os.path.exists(CONFIG_FILEPATH):
            with open(CONFIG_FILEPATH) as json_file:
                self._settings = json.load(json_file)
        else:
            self._settings = {'db_host': 'localhost',
                              'db_name': 'arma3',
                              'db_username': 'username',
                              'db_password': 'password'}

            with open(CONFIG_FILEPATH, 'w') as outfile:
                json.dump(self._settings, outfile, sort_keys=True, indent=4)

    def get_addon_groups(self):
        connection = self.create_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM addon_group;"
        cursor.execute(query)
        row = cursor.fetchall()
        cursor.close()
        connection.close()
        return row

    def get_addons(self):
        connection = self.create_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM addon;"
        cursor.execute(query)
        row = cursor.fetchall()
        cursor.close()
        connection.close()
        return row

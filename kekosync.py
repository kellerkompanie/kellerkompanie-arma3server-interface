#! /usr/bin/python3
# -*- coding:utf-8 -*-

import json
import os
import uuid
from datetime import datetime

import pymysql
import pymysql.cursors

CONFIG_FILEPATH = 'kekosync_config.json'


class KeKoSync:
    def __init__(self):
        self._load_config()

    def create_connection(self):
        return pymysql.connect(host=self._settings['db_host'],
                               database=self._settings['db_name'],
                               user=self._settings['db_username'],
                               password=self._settings['db_password'],
                               cursorclass=pymysql.cursors.DictCursor)

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

    def get_addon_group_id_from_uuid(self, uuid):
        connection = self.create_connection()
        cursor = connection.cursor()

        sql = "SELECT addon_group_id FROM addon_group WHERE addon_group_uuid=%s;"
        cursor.execute(sql, (uuid,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row['addon_group_id']

    def update_addon_group(self, existing_uuid, name, author, addon_list):
        sql = "UPDATE addon_group SET name = %s, author = %s WHERE addon_group_uuid=%s;"
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (name, author, existing_uuid))
        cursor.close()

        addon_group_id = self.get_addon_group_id_from_uuid(existing_uuid)
        self._update_addons(connection, addon_group_id, addon_list)

        connection.close()
        return "OK"

    def create_addon_group(self, name, author, addon_list):
        sql = "INSERT INTO addon_group (addon_group_uuid, addon_group_version, addon_group_name, addon_group_author) " \
              "VALUES (%s, %s, %s, %s);"

        connection = self.create_connection()
        cursor = connection.cursor()
        new_uuid = str(uuid.uuid4())
        version = datetime.now().strftime("%Y%m%d-%H%M%S")
        cursor.execute(sql, (new_uuid, version, name, author))
        addon_group_id = cursor.lastrowid
        cursor.close()
        self._update_addons(connection, addon_group_id, addon_list)
        connection.close()
        return "OK"

    def _update_addons(self, connection, addon_group_id, addon_list):
        vals = []
        addon_dict = dict()
        addons = self.get_addons()
        for addon in addons:
            addon_uuid = addon['addon_uuid']
            addon_id = addon['addon_id']
            addon_dict[addon_uuid] = addon_id

        for addon in addon_list:
            addon_id = addon_dict[addon]
            vals.append([addon_group_id, addon_id])

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM addon_group_member WHERE addon_group_id=%s;", (addon_group_id,))
            cursor.executemany("INSERT INTO addon_group_member(addon_group_id, addon_id) values (%s, %s);", vals)
            connection.commit()

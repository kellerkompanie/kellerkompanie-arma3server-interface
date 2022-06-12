#! /usr/bin/python3
# -*- coding:utf-8 -*-
import json
import os
import re
import uuid
from datetime import datetime

import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup

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
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows

    def get_addon_group(self, uuid):
        connection = self.create_connection()
        cursor = connection.cursor()

        sql = "SELECT * FROM addon_group WHERE addon_group_uuid=%s;"
        cursor.execute(sql, (uuid,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()

        addon_group_id = row['addon_group_id']
        group_addons = self.get_group_addons(addon_group_id)

        row['addons'] = group_addons
        return row

    def delete_addon_group(self, uuid):
        addon_group_id = self.get_addon_group_id_from_uuid(uuid)

        connection = self.create_connection()
        cursor = connection.cursor()

        query = "DELETE FROM addon_group_member WHERE addon_group_id = %s;"
        cursor.execute(query, (addon_group_id,))

        query = "DELETE FROM addon_group WHERE addon_group_id = %s;"
        cursor.execute(query, (addon_group_id,))

        connection.commit()
        cursor.close()
        connection.close()
        return "OK"

    def get_all_addons(self) -> dict:
        connection = self.create_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM addon;")
        rows = cursor.fetchall()

        addons_map = {}
        for row in rows:
            row['addon_dependencies'] = []
            row['addon_steamid'] = None
            addons_map[row['addon_id']] = row

        cursor.execute("SELECT * FROM addon_dependency;")
        rows = cursor.fetchall()
        for row in rows:
            addon = addons_map[row['addon_id']]
            addon['addon_dependencies'].push(row['addon_dependency'])

        cursor.execute("SELECT * FROM addon_meta;")
        row = cursor.fetchone()
        if row:
            addon = addons_map[row['addon_id']]
            addon['addon_steamid'] = row['addon_steamid']

        cursor.close()
        connection.close()
        return addons_map

    def get_addon(self, addon_id):
        connection = self.create_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM addon WHERE addon_id = %s;", (addon_id,))
        row = cursor.fetchone()

        addon = row
        addon['addon_dependencies'] = []
        addon['addon_steamid'] = None

        cursor.execute("SELECT * FROM addon_dependency WHERE addon_id = %s;", (addon_id,))
        rows = cursor.fetchall()
        for row in rows:
            addon['addon_dependencies'].push(row['addon_dependency'])

        cursor.execute("SELECT * FROM addon_meta WHERE addon_id = %s;", (addon_id,))
        row = cursor.fetchone()
        if row:
            addon['addon_steamid'] = row['addon_steamid']

        cursor.close()
        connection.close()
        return addon

    def get_group_addons(self, addon_group_id):
        connection = self.create_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM addon_group_member LEFT JOIN addon ON addon_group_member.addon_id=addon.addon_id " \
                "WHERE addon_group_member.addon_group_id=%s;"
        cursor.execute(query, (addon_group_id,))
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
        sql = "UPDATE addon_group SET addon_group_name = %s, addon_group_author = %s WHERE addon_group_uuid=%s;"
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (name, author, existing_uuid))
        cursor.close()

        addon_group_id = self.get_addon_group_id_from_uuid(existing_uuid)
        self._update_addons(connection, addon_group_id, addon_list)

        connection.commit()
        connection.close()
        return "OK"

    def create_addon_group(self, name, author, addon_list):
        sql = "INSERT INTO addon_group (addon_group_uuid, addon_group_version, addon_group_name, addon_group_author) " \
              "VALUES (%s, %s, %s, %s);"

        connection = self.create_connection()
        cursor = connection.cursor()
        new_uuid = self._generate_uuid()
        version = datetime.now().strftime("%Y%m%d-%H%M%S")
        cursor.execute(sql, (new_uuid, version, name, author))
        addon_group_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        self._update_addons(connection, addon_group_id, addon_list)
        connection.close()
        return "OK"

    def get_addon_dependencies(self):
        connection = self.create_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM addon_dependency;"
        cursor.execute(query)
        row = cursor.fetchall()
        cursor.close()
        connection.close()
        return row

    def get_addon_dependency(self, addon_id):
        connection = self.create_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM addon_dependency WHERE addon_id = %s;"
        cursor.execute(query, (addon_id,))
        row = cursor.fetchall()
        cursor.close()
        connection.close()
        return row

    def insert_addon_dependency(self, addon_id, addon_dependency):
        connection = self.create_connection()
        cursor = connection.cursor()

        sql = "INSERT INTO addon_dependency (addon_id, addon_dependency) " \
              "VALUES (%s, %s);"
        cursor.execute(sql, (addon_id, addon_dependency))
        connection.commit()
        cursor.close()
        connection.close()
        return "OK"

    def delete_addon_dependency(self, addon_id, addon_dependency):
        connection = self.create_connection()
        cursor = connection.cursor()

        sql = "DELETE FROM addon_dependency WHERE addon_id = %s AND addon_dependency = %s;"
        cursor.execute(sql, (addon_id, addon_dependency))
        connection.commit()
        cursor.close()
        connection.close()
        return "OK"

    @staticmethod
    def _generate_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def _generate_version():
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    @staticmethod
    def _is_name_similar(addon_name1, addon_name2):
        return addon_name1.lower() == addon_name2.lower()

    def match_addon_name(self, addon_name) -> str:
        for addon_id, addon in self.get_all_addons().items():
            other_addon_name = addon["addon_name"]
            if self._is_name_similar(addon_name, other_addon_name):
                return addon["addon_uuid"]

        return self.insert_addon(addon_name)

    def insert_addon(self, addon_name):
        sql = "INSERT INTO addon (addon_uuid, addon_version, addon_foldername, addon_name) " \
              "VALUES (%s, %s, %s, %s);"

        addon_uuid = self._generate_uuid()
        addon_foldername = addon_name
        addon_version = self._generate_version()

        connection = self.create_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql, (addon_uuid, addon_version, addon_foldername, addon_name))
            # addon_id = cursor.lastrowid

        connection.commit()
        connection.close()
        return addon_uuid

    def update_addons(self, updated_addons_json):
        updated_addons = json.loads(updated_addons_json)
        sql = "UPDATE addon " \
              "SET addon_version = %s " \
              "WHERE addon_uuid = %s;"
        connection = self.create_connection()
        for addon_uuid, addon_version in updated_addons.items():
            with connection.cursor() as cursor:
                cursor.execute(sql, (addon_version, addon_uuid))

        connection.commit()
        connection.close()
        return "OK"

    def _update_addons(self, connection, addon_group_id, addon_list):
        vals = []
        addon_dict = dict()
        addons = self.get_all_addons()
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

    @staticmethod
    def get_workshopitem_info(workshopitem_id: str):
        """
        Example:
        curl --location --request POST 'https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/' \
            --form 'itemcount="1"' \
            --form 'publishedfileids[0]="705986840"'
        """
        if not bool(re.match(r'^\d+$', workshopitem_id)):
            raise ValueError('expected numeric workshopitem_id, but got: ' + workshopitem_id)

        url = 'https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/'

        response = requests.post(url, data={'itemcount': '1', 'publishedfileids[0]': workshopitem_id},
                                 allow_redirects=True)

        if response.status_code != 200:
            raise RuntimeError('expected status code 200 for {}, but got {}'.format(url, response.status_code))
        if '<div class="error_ctn">' in response.text:
            raise RuntimeError('request to {} resulted in unexpected error')

        return response.json()

    @staticmethod
    def get_workshopitem_dependencies(workshopitem_id: str):
        if not bool(re.match(r'^\d+$', workshopitem_id)):
            raise ValueError('expected numeric workshopitem_id, but got: ' + workshopitem_id)

        url = "https://steamcommunity.com/workshop/filedetails/?id={}".format(workshopitem_id)
        response = requests.get(url)

        if response.status_code != 200:
            raise RuntimeError('expected status code 200 for {}, but got {}'.format(url, response.status_code))
        if '<div class="error_ctn">' in response.text:
            raise RuntimeError('request to {} resulted in unexpected error')

        soup = BeautifulSoup(response.text, 'html.parser')
        required_items_div = soup.find("div", {"id": "RequiredItems"})

        if required_items_div is None:
            return []

        required_items_hrefs = required_items_div.findChildren("a", recursive=False)
        dependencies = []
        for required_item_href in required_items_hrefs:
            dependency_name = required_item_href.text.strip()
            dependency_url = required_item_href['href']
            dependency_workshopitem_id = re.search(r'https://steamcommunity\.com/workshop/filedetails/\?id=([0-9]*)',
                                                   dependency_url).group(1)
            dependencies.append({
                'name': dependency_name,
                'url': dependency_url,
                'workshopitem_id': dependency_workshopitem_id
            })
        return dependencies

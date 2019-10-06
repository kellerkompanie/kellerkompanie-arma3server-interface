#! /usr/bin/python3
# -*- coding:utf-8 -*-

__author__ = "Gunk"

import datetime
import json
import os
import sys
from collections import Counter
from datetime import timedelta

import pymysql

CONFIG_FILEPATH = 'stammspieler_config.json'


class Stammspieler:
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

    def get_missionen(self):
        if len(sys.argv) == 5 or len(sys.argv) == 4:
            if sys.argv[3].isdigit() and len(sys.argv[3]) == 8:
                arg = "vonBis"
            else:
                arg = "von"
        elif len(sys.argv) == 3:
            if sys.argv[2].isdigit() and len(sys.argv[2]) == 8:
                arg = "von"
            else:
                arg = "alles"
        else:
            arg = "alles"

        connection = self.create_connection()
        cursor = connection.cursor()

        if arg == "von":
            date_from = sys.argv[2]
            query = "SELECT CAST(StartTime as date) AS Datum, " \
                    "CAST(StartTime as time) AS Von, " \
                    "CAST(EndTime as time) AS Bis, MissionName, WorldName AS Map " \
                    "FROM (SELECT DISTINCT main.EventID as StartID, main.Time as StartTime, " \
                    "main.MissionName, main.WorldName, sub.EndID, sub.EndTime FROM mission main " \
                    "LEFT JOIN (SELECT EventID as EndID, Time as EndTime, MissionName FROM mission " \
                    "WHERE EventType = 'END') as sub USING (MissionName) WHERE EventType = 'START' AND Time > " \
                    + date_from + " GROUP BY StartID) as zw WHERE EndID - StartID = 1 AND " \
                                  "CAST(StartTime as time) > 183000;"
            cursor.execute(query)
            row = cursor.fetchall()
            cursor.close()
            connection.close()
            return row

        elif arg == "vonBis":
            date_from = sys.argv[2]
            date_to = sys.argv[3]
            query = "SELECT CAST(StartTime as date) AS Datum, " \
                    "CAST(StartTime as time) AS Von, " \
                    "CAST(EndTime as time) AS Bis, MissionName, " \
                    "WorldName AS Map FROM (SELECT DISTINCT main.EventID as StartID, main.Time as StartTime, " \
                    "main.MissionName, main.WorldName, sub.EndID, sub.EndTime FROM mission main " \
                    "LEFT JOIN (SELECT EventID as EndID, Time as EndTime, MissionName FROM mission " \
                    "WHERE EventType = 'END') as sub USING (MissionName) WHERE EventType = 'START' AND Time BETWEEN " \
                    + date_from + " AND " + date_to + " GROUP BY StartID) as zw WHERE EndID - StartID = 1 AND " \
                                                      "CAST(StartTime as time) > 183000;"
            cursor.execute(query)
            row = cursor.fetchall()
            cursor.close()
            connection.close()
            return row

        elif arg == "alles":
            date_to = datetime.datetime.now()
            date_from = date_to - timedelta(days=90)
            date_to = date_to.strftime("%Y%m%d")
            date_from = date_from.strftime("%Y%m%d")
            query = "SELECT CAST(StartTime as date) AS Datum, " \
                    "CAST(StartTime as time) AS Von, CAST(EndTime as time) AS Bis, " \
                    "MissionName, WorldName AS Map FROM (SELECT DISTINCT main.EventID as StartID, " \
                    "main.Time as StartTime, main.MissionName, main.WorldName, sub.EndID, sub.EndTime " \
                    "FROM mission main LEFT JOIN (SELECT EventID as EndID, Time as EndTime, MissionName " \
                    "FROM mission WHERE EventType = 'END') as sub USING (MissionName) WHERE EventType = 'START' AND " \
                    "Time BETWEEN " + date_from + " AND " + date_to \
                    + " GROUP BY StartID) as zw WHERE EndID - StartID = 1 AND CAST(StartTime as time) > 183000;"
            cursor.execute(query)
            row = cursor.fetchall()
            cursor.close()
            connection.close()
            return row

    def get_spieler(self):
        if len(sys.argv) == 5 or len(sys.argv) == 4:
            if sys.argv[3].isdigit() and len(sys.argv[3]) == 8:
                arg = "vonBis"
            else:
                arg = "von"
        elif len(sys.argv) == 3:
            if sys.argv[2].isdigit() and len(sys.argv[2]) == 8:
                arg = "von"
            else:
                arg = "alles"
        else:
            arg = "alles"

        connection = self.create_connection()
        cursor = connection.cursor()

        if arg == "von":
            date_from = sys.argv[2]
            query = "SELECT PlayerName, PlayerUID, CAST(Time as date) as Datum FROM session " \
                    "WHERE EventType = 'CONNECTED' AND Time > " + date_from \
                    + " AND CAST(Time as time) BETWEEN 190000 AND 203000 AND PlayerName " \
                      "NOT LIKE 'headlessclient%' GROUP BY PlayerName, CAST(Time as date) ORDER BY PlayerUID;"
            cursor.execute(query)
            row = cursor.fetchall()
            cursor.close()
            connection.close()
            return row

        elif arg == "vonBis":
            date_from = sys.argv[2]
            date_to = sys.argv[3]
            query = "SELECT PlayerName, PlayerUID, CAST(Time as date) as Datum FROM session " \
                    "WHERE EventType = 'CONNECTED' AND Time BETWEEN " + date_from \
                    + " AND " + date_to \
                    + " AND CAST(Time as time) BETWEEN 190000 AND 203000 AND PlayerName " \
                      "NOT LIKE 'headlessclient%' GROUP BY PlayerName, CAST(Time as date) ORDER BY PlayerUID;"
            cursor.execute(query)
            row = cursor.fetchall()
            cursor.close()
            connection.close()
            return row

        elif arg == "alles":
            date_to = datetime.datetime.now()
            date_from = date_to - timedelta(days=90)
            date_to = date_to.strftime("%Y%m%d")
            date_from = date_from.strftime("%Y%m%d")
            query = "SELECT PlayerName, PlayerUID, CAST(Time as date) as Datum FROM session " \
                    "WHERE EventType = 'CONNECTED' AND Time BETWEEN " + date_from + " AND " + date_to \
                    + " AND CAST(Time as time) BETWEEN 190000 AND 203000 AND PlayerName " \
                      "NOT LIKE 'headlessclient%' GROUP BY PlayerName, CAST(Time as date) ORDER BY PlayerUID;"
            cursor.execute(query)
            row = cursor.fetchall()
            cursor.close()
            connection.close()
            return row

    @staticmethod
    def aktivitaet(missionen, spieler):
        teilnehmer = []
        zeitpunkt = []

        for x in missionen:
            zeitpunkt.append((x[0]))

        for item in spieler:
            if item[2] in zeitpunkt:
                teilnehmer.append((item[1], item[0]))
            else:
                continue

        spieler_anzahl = Counter(teilnehmer)
        spieler_anzahl = sorted(spieler_anzahl.items(), key=lambda k: (-k[1], k[0]))

        for x in range(len(spieler_anzahl)):
            spieler_anzahl[x] = list(spieler_anzahl[x])

        for x in spieler_anzahl:
            for y in spieler_anzahl:
                if x[0][0] == y[0][0] and x[0][1] != y[0][1]:
                    x[1] += y[1]
                    spieler_anzahl.remove(y)
                else:
                    continue

        spieler_anzahl = sorted(spieler_anzahl, key=lambda k: (-k[1], k[0][1]))

        return spieler_anzahl

    def ausgabe_stammspieler(self, steam_id):
        # Get raw SQL data as list of tuples (mission_name, player_name, mission_date, steam_id).
        participation = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())

        # Calculate the dates to determine the 3 intervals: last 30 days, 30-60 days ago and 60-90 days ago.
        date_today = datetime.datetime.now()
        date_90days_ago = (date_today - timedelta(days=90))
        date_60days_ago = (date_today - timedelta(days=60))
        date_30days_ago = (date_today - timedelta(days=30))

        # Counters for how many mission have been played in total during that interval.
        total_missions_0to30days_ago = 0
        total_missions_30to60days_ago = 0
        total_missions_60to90days_ago = 0

        participated_missions_0to30days_ago = 0
        participated_missions_30to60days_ago = 0
        participated_missions_60to90days_ago = 0

        current_mission = ""

        for mission_name, player_name, mission_date, participants_steam_id in participation:
            if date_90days_ago.date() < mission_date <= date_60days_ago.date():
                if current_mission != mission_name:
                    current_mission = mission_name
                    total_missions_60to90days_ago += 1
                if steam_id in participants_steam_id:
                    participated_missions_60to90days_ago += 1
            elif date_60days_ago.date() < mission_date <= date_30days_ago.date():
                if current_mission != mission_name:
                    current_mission = mission_name
                    total_missions_30to60days_ago += 1
                if steam_id in participants_steam_id:
                    participated_missions_30to60days_ago += 1
            elif date_30days_ago.date() < mission_date <= date_today.date():
                if current_mission != mission_name:
                    current_mission = mission_name
                    total_missions_0to30days_ago += 1
                if steam_id in participants_steam_id:
                    participated_missions_0to30days_ago += 1
            else:
                continue

        condition1 = participated_missions_60to90days_ago >= int(total_missions_60to90days_ago / 3) \
                     and participated_missions_30to60days_ago >= int(total_missions_30to60days_ago / 3) \
                     and participated_missions_0to30days_ago >= int(total_missions_0to30days_ago / 3)
        condition2 = participated_missions_60to90days_ago >= (total_missions_60to90days_ago / 2) \
                     and participated_missions_30to60days_ago >= (total_missions_30to60days_ago / 2)
        condition3 = participated_missions_60to90days_ago >= (total_missions_60to90days_ago / 2) \
                     and participated_missions_0to30days_ago >= (total_missions_0to30days_ago / 2)
        condition4 = participated_missions_30to60days_ago >= (total_missions_30to60days_ago / 2) \
                     and participated_missions_0to30days_ago >= (total_missions_0to30days_ago / 2)

        output = ''
        if condition1 or condition2 or condition3 or condition4:
            output += "Ja! Du bist Stammspieler. \nMelde dich bei einem Admin deines Vertrauens."
        else:
            output += "Nein, frag doch einfach später nochmal.\n"

        output += "\nDu hast mitgespielt: " + str(participated_missions_60to90days_ago) + " / " + str(
            total_missions_60to90days_ago) + " - " + str(
            participated_missions_30to60days_ago) + " / " + str(total_missions_30to60days_ago) + "  -  " + str(
            participated_missions_0to30days_ago) + " / " + str(total_missions_0to30days_ago) + '\n'
        return output

    def ausgabe_stammspieler_admin(self):
        # Get raw SQL data as list of tuples (mission_name, player_name, mission_date, steam_id).
        participation = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())

        # Calculate the dates to determine the 3 intervals: last 30 days, 30-60 days ago and 60-90 days ago.
        date_today = datetime.datetime.now().date()
        date_90days_ago = (date_today - timedelta(days=90))
        date_60days_ago = (date_today - timedelta(days=60))
        date_30days_ago = (date_today - timedelta(days=30))

        # Counters for how many mission have been played in total during that interval.
        total_missions_0to30days_ago = 0
        total_missions_30to60days_ago = 0
        total_missions_60to90days_ago = 0

        # Since the raw SQL data contains each mission a number of times (for every player that participated) we need
        # to limit the amount, so that each mission at a specific date only appears once in our set.
        unique_missions = set()
        for mission_name, player_name, mission_date, steam_id in participation:
            unique_missions.add((mission_name, mission_date))

        # For each of the mission determine in which of the intervals it took place and increase the mission counter
        # for that interval.
        for mission_name, mission_date in unique_missions:
            if date_90days_ago < mission_date <= date_60days_ago:
                total_missions_60to90days_ago += 1
            elif date_60days_ago < mission_date <= date_30days_ago:
                total_missions_30to60days_ago += 1
            elif date_30days_ago < mission_date <= date_today:
                total_missions_0to30days_ago += 1

        # Similar to the missions we iterate over the raw SQL data from the viewpoint of the players, counting how many
        # times they participated in each of the intervals. For human readable output we also memorize the names of the
        # corresponding SteamIDs, since they are unique, but player's names may repeat.
        player_participations = dict()
        player_names = dict()
        for mission_name, player_name, mission_date, steam_id in participation:
            player_names[steam_id] = player_name
            if steam_id not in player_participations:
                player_participations[steam_id] = [0, 0, 0]

            if date_30days_ago < mission_date <= date_today:
                player_participations[steam_id][0] += 1
            elif date_60days_ago < mission_date <= date_30days_ago:
                player_participations[steam_id][1] += 1
            elif date_90days_ago < mission_date <= date_60days_ago:
                player_participations[steam_id][2] += 1

        # Regular players are players that participated a certain percentage of the maximum possible missions in each
        # interval. We iterate over the participations and check if the players fulfill these constraints.
        regular_players = set()
        for steam_id in player_participations:
            if player_participations[steam_id][2] >= int(total_missions_60to90days_ago / 3) and \
                    player_participations[steam_id][1] >= int(total_missions_30to60days_ago / 3) and \
                    player_participations[steam_id][0] >= int(total_missions_0to30days_ago / 3):
                regular_players.add(steam_id)
            elif player_participations[steam_id][2] >= (
                    total_missions_60to90days_ago / 2) and player_participations[steam_id][1] >= (
                    total_missions_30to60days_ago / 2):
                regular_players.add(steam_id)
            elif player_participations[steam_id][2] >= (
                    total_missions_60to90days_ago / 2) and player_participations[steam_id][0] >= (
                    total_missions_0to30days_ago / 2):
                regular_players.add(steam_id)
            elif player_participations[steam_id][2] >= (
                    total_missions_30to60days_ago / 3) and player_participations[steam_id][0] >= (
                    total_missions_0to30days_ago / 3):
                regular_players.add(steam_id)

        header = "Stammspieler:"
        output = header + '\n'
        output += "-" * (len(header) + 14) + '\n'
        # output += '\n'.join(sorted(regular_players))
        for steam_id in regular_players:
            participations = player_participations[steam_id]
            output += player_names[steam_id] + ' ' + ' | '.join(participations) + '\n'
        output += "\n\nAnzahl Stammspieler: " + str(len(regular_players)) + '\n'
        return output

    @staticmethod
    def get_karten(missionen):
        karten_liste = []

        for x in missionen:
            karten_liste.append(x[4])

        karte_anzahl = Counter(karten_liste)
        karte_anzahl = sorted(karte_anzahl.items(), key=lambda k: (-k[1], k[0]))
        return karte_anzahl

    @staticmethod
    def get_teilnehmer(missionen, spieler):
        mission = []
        teilnehmer = []
        mitgespielt = []

        for x in missionen:
            mission.append(list((x[0], x[3].rsplit(".", 3)[0])))

        for x in spieler:
            teilnehmer.append(list((x[0], x[2], x[1])))

        for x in mission:
            for y in teilnehmer:
                if x[0] == y[1]:
                    mitgespielt.append(list((x[1], y[0], x[0], y[2])))

        return mitgespielt

    def ausgabe_mission(self):
        missionen = self.get_missionen()
        date = datetime.datetime.now()
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        check = 0
        maxlen = 0
        for x in range(len(missionen)):
            mlen = len(missionen[x][3].rsplit(".", 3)[0])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Datum:".ljust(13) + "Von:".ljust(11) + "Bis:".ljust(11) + "Mission:".ljust(maxlen + 2) + "Map:")
        output = header + '\n'
        output += "-" * (len(header) + 14) + '\n'

        for x in range(len(missionen)):
            mlen = len(missionen[x][3].rsplit(".", 3)[0])
            if missionen[x][0] > date_from1.date() and check == 0 or missionen[x][0] > date_from.date() and check == 1:
                output += "-" * (len(header) + 14) + '\n'
                check += 1
            output += missionen[x][0].strftime("%d.%m.%Y") + " | "
            output += str(missionen[x][1]) + " | " + str(missionen[x][2]) + " | "
            output += missionen[x][3].rsplit(".", 3)[0] + " | ".rjust(maxlen + 1 - mlen)
            output += Stammspieler.replace_map_name(missionen[x][4]) + '\n'

        output += "\nAnzahl Missionen: " + str(len(missionen)) + "\n\n"
        return output

    @staticmethod
    def replace_map_name(mapname):
        map_translations = {
            "pulau": "Pulau", "chernarus_summer": "Chernarus Summer", "sara": "Sahrani", "takistan": "Takistan",
            "utes": "Utes", "chernarus_winter": "Chernarus Winter", "mcn_hazarkot": "Hazar Kot Valley",
            "rura_penthe": "Rura Penthe", "abramia": "Isla Abramia", "chernarusredux": "Chernarus Redux",
            "lythium": "Lythium", "tem_ihantalaw": "Ihantala Winter", "zargabad": "Zargabad",
            "wl_route191": "Schwemlitz", "cup_kunduz": "Kunduz", "pabst_yellowstone": "Yellowstone",
            "tem_anizay": "Anizay", "wl_rosche": "Rosche", "prei_khmaoch_luong": "Prei Khmaoch Luong",
            "bootcamp_acr": "Bootcamp", "fallujah": "Fallujah", "chernarus": "Chernarus", "lingor3": "Lingor",
            "ruha": "Ruha", "dingor": "Dingor", "iron_excelsior_tobruk": "Libyen (IFA3)",
            "tem_kujari": "Kujari", "tem_summa": "Summa", "isladuala3": "Isla Duala", "porto": "Porto",
            "swu_kokoda_map": "Kokoda Trail (IFA3)", "enoch": "Livonia", "thirsk": "Thirsk", "tembelan": "Tembelan",
            "woodland_acr": "Bystrica", "i44_merderet_v2": "Merderet (IFA3)", "mcn_neaville": "Neaville (IFA3)",
            "swu_greece_pella_region": "Greece (IFA3)", "clafghan": "CLA Afghan", "fdf_isle1_a": "Podagorsk"}

        if mapname.lower() in map_translations:
            return map_translations[mapname.lower()]
        else:
            return mapname

    def ausgabe_karten(self):
        karten = Stammspieler.get_karten(self.get_missionen())
        maxlen = 0
        for x in karten:
            mlen = len(x[0])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Karte:".ljust(maxlen + 2) + "Gespielt:")
        output = header + '\n'
        output += "-" * (len(header) + 5) + '\n'

        for x in karten:
            mapname = Stammspieler.replace_map_name(x[0])
            mlen = len(mapname)
            output += mapname + " | ".rjust(maxlen + 1 - mlen) + str(x[1]) + '\n'

        output += "\nAnzahl Karten: " + str(len(karten)) + '\n'
        return output

    def ausgabe_aktivitaet(self):
        spieler_anzahl = Stammspieler.aktivitaet(self.get_missionen(), self.get_spieler())
        maxlen = 0
        for x in spieler_anzahl:
            mlen = len(x[0][1])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Spieler:".ljust(maxlen + 2) + "Teilnahmen: ")
        output = header + '\n'
        output += "-" * (len(header) + 5) + '\n'

        for x in spieler_anzahl:
            mlen = len(x[0][1])
            output += str(x[0][1]) + " | ".rjust(maxlen + 1 - mlen) + str(x[1]) + '\n'

        output += "\nVerschiedene Teilnehmer: " + str(len(spieler_anzahl)) + "\n"
        return output

    def ausgabe_mitgespielt(self, steam_id):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())
        date = datetime.datetime.now()
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        zaehler = 0
        check = 0
        spieler = ""
        output = ''

        for x in mitgespielt:
            if steam_id in (x[3]):
                if spieler != x[3]:
                    spieler = x[3]
                    output += "\nDatum: ".ljust(13) + "Mission: \n"
                    output += "-" * 40 + '\n'
                if x[2] > date_from1.date() and check == 0 or x[2] > date_from.date() and check == 1:
                    output += "-" * 40 + '\n'
                    check += 1
                output += x[2].strftime("%d.%m.%Y") + " | " + x[0] + '\n'
                zaehler += 1
        output += "\nAnzahl Mitgespielt: " + str(zaehler) + "\n\n"
        return output

    def ausgabe_teilnehmer(self):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())
        mission = ""
        output = ''
        for x in mitgespielt:
            if mission != x[0]:
                mission = x[0]
                output += "\nMission: " + mission + '\n'
                output += "-" * (len(mission) + 10) + '\n'
            output += str(x[1]) + '\n'
        return output

    def ausgabe_teilnehmer_mission(self, mission_param):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())
        mission = ""
        output = ''
        for x in mitgespielt:
            if mission_param in (x[0]):
                if mission != x[0]:
                    mission = x[0]
                    output += "\nMission: " + str(mission) + " | " + x[2].strftime("%d.%m.%Y") + '\n'
                    output += "-" * (len(mission) + 23) + '\n'
                output += str(x[1]) + '\n'
        return output


if __name__ == "__main__":
    stammspieler = Stammspieler()

    if sys.argv[1] == "missionen":
        print(stammspieler.ausgabe_mission())

    elif sys.argv[1] == "aktivitaet":
        print(stammspieler.ausgabe_aktivitaet())

    elif sys.argv[1] == "stammspieler":
        print(stammspieler.ausgabe_stammspieler(steam_id=sys.argv[2]))

    elif sys.argv[1] == "stammspielerAdmin":
        print(stammspieler.ausgabe_stammspieler_admin())

    elif sys.argv[1] == "karten":
        print(stammspieler.ausgabe_karten())

    elif sys.argv[1] == "teilnehmer":
        print(stammspieler.ausgabe_teilnehmer())

    elif sys.argv[1] == "spieler":
        print(stammspieler.ausgabe_mitgespielt(steam_id=sys.argv[2]))

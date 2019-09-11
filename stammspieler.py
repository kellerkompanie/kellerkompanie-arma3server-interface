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
        self._connection = pymysql.connect(host=self._settings['db_host'],
                                           database=self._settings['db_name'],
                                           user=self._settings['db_username'],
                                           password=self._settings['db_password'])
        self._cursor = self._connection.cursor()

    def close(self):
        self._connection.close()

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
            self._cursor.execute(query)
            row = self._cursor.fetchall()
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
            self._cursor.execute(query)
            row = self._cursor.fetchall()
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
            self._cursor.execute(query)
            row = self._cursor.fetchall()
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

        if arg == "von":
            date_from = sys.argv[2]
            query = "SELECT PlayerName, PlayerUID, CAST(Time as date) as Datum FROM session " \
                    "WHERE EventType = 'CONNECTED' AND Time > " + date_from \
                    + " AND CAST(Time as time) BETWEEN 190000 AND 203000 AND PlayerName " \
                      "NOT LIKE 'headlessclient%' GROUP BY PlayerName, CAST(Time as date) ORDER BY PlayerUID;"
            self._cursor.execute(query)
            row = self._cursor.fetchall()
            return row

        elif arg == "vonBis":
            date_from = sys.argv[2]
            date_to = sys.argv[3]
            query = "SELECT PlayerName, PlayerUID, CAST(Time as date) as Datum FROM session " \
                    "WHERE EventType = 'CONNECTED' AND Time BETWEEN " + date_from \
                    + " AND " + date_to \
                    + " AND CAST(Time as time) BETWEEN 190000 AND 203000 AND PlayerName " \
                      "NOT LIKE 'headlessclient%' GROUP BY PlayerName, CAST(Time as date) ORDER BY PlayerUID;"
            self._cursor.execute(query)
            row = self._cursor.fetchall()
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
            self._cursor.execute(query)
            row = self._cursor.fetchall()
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
        spieler_anzahl = sorted(spieler_anzahl.items(), key=lambda x: (-x[1], x[0]))

        for x in range(len(spieler_anzahl)):
            spieler_anzahl[x] = list(spieler_anzahl[x])

        for x in spieler_anzahl:
            for y in spieler_anzahl:
                if x[0][0] == y[0][0] and x[0][1] != y[0][1]:
                    x[1] += y[1]
                    spieler_anzahl.remove(y)
                else:
                    continue

        spieler_anzahl = sorted(spieler_anzahl, key=lambda x: (-x[1], x[0][1]))

        return spieler_anzahl

    def ausgabe_stammspieler(self, steam_id):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())

        date = datetime.datetime.now()
        date_from2 = date - timedelta(days=90)
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        zaehler = 0
        zaehler1 = 0
        zaehler2 = 0
        zaehler_mission = 0
        zaehler_mission1 = 0
        zaehler_mission2 = 0
        mission = ""

        for x in mitgespielt:
            if date_from2.date() < x[2] <= date_from1.date():
                if mission != x[0]:
                    mission = x[0]
                    zaehler_mission2 += 1
                if steam_id in (x[3]):
                    zaehler2 += 1
            elif date_from1.date() < x[2] <= date_from.date():
                if mission != x[0]:
                    mission = x[0]
                    zaehler_mission1 += 1
                if steam_id in (x[3]):
                    zaehler1 += 1
            elif date_from.date() < x[2] <= date.date():
                if mission != x[0]:
                    mission = x[0]
                    zaehler_mission += 1
                if steam_id in (x[3]):
                    zaehler += 1
            else:
                continue

        condition1 = zaehler2 >= int(zaehler_mission2 / 3) and zaehler1 >= int(zaehler_mission1 / 3) and zaehler >= int(
            zaehler_mission / 3)
        condition2 = zaehler2 >= (zaehler_mission2 / 2) and zaehler1 >= (zaehler_mission1 / 2)
        condition3 = zaehler2 >= (zaehler_mission2 / 2) and zaehler >= (zaehler_mission / 2)
        condition4 = zaehler1 >= (zaehler_mission1 / 2) and zaehler >= (zaehler_mission / 2)

        output = ''
        if condition1 or condition2 or condition3 or condition4:
            output += "Ja! Du bist Stammspieler. \nMelde dich bei einem Admin deines Vertrauens."
        else:
            output += "Nein, frag doch einfach später nochmal.\n"
        output += "\nDu hast mitgespielt: " + str(zaehler2) + " / " + str(zaehler_mission2) + " - " + str(
            zaehler1) + " / " + str(zaehler_mission1) + "  -  " + str(zaehler) + " / " + str(zaehler_mission) + '\n'
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
        regular_players = dict()
        for steam_id in player_participations:
            if player_participations[steam_id][2] >= int(
                    total_missions_60to90days_ago / 3) and player_participations[steam_id][1] >= int(
                    total_missions_30to60days_ago / 3) and player_participations[steam_id][0] >= int(
                    total_missions_0to30days_ago / 3):
                regular_players[steam_id] = player_names[steam_id]
            elif player_participations[steam_id][2] >= (
                    total_missions_60to90days_ago / 2) and player_participations[steam_id][1] >= (
                    total_missions_30to60days_ago / 2):
                regular_players[steam_id] = player_names[steam_id]
            elif player_participations[steam_id][2] >= (
                    total_missions_60to90days_ago / 2) and player_participations[steam_id][0] >= (
                    total_missions_0to30days_ago / 2):
                regular_players[steam_id] = player_names[steam_id]
            elif player_participations[steam_id][2] >= (
                    total_missions_30to60days_ago / 3) and player_participations[steam_id][0] >= (
                    total_missions_0to30days_ago / 3):
                regular_players[steam_id] = player_names[steam_id]

        header = "Stammspieler:"
        output = header + '\n'
        output += "-" * (len(header) + 14) + '\n'
        output += '\n'.join(sorted(regular_players.values()))
        output += "\n\nAnzahl Stammspieler: " + str(len(regular_players)) + '\n'
        return output

    @staticmethod
    def get_karten(missionen):
        karten_liste = []

        for x in missionen:
            karten_liste.append(x[4])

        karte_anzahl = Counter(karten_liste)
        karte_anzahl = sorted(karte_anzahl.items(), key=lambda x: (-x[1], x[0]))
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
            output += missionen[x][1] + " | " + missionen[x][2] + " | "
            output += missionen[x][3].rsplit(".", 3)[0] + " | ".rjust(maxlen + 1 - mlen)
            output += Stammspieler.replace_map_name(missionen[x][4]) + '\n'

        output += "\nAnzahl Missionen: " + str(len(missionen)) + "\n\n"
        return output

    @staticmethod
    def replace_map_name(mapname):
        mapname = mapname.lower()

        if mapname == "pulau":
            return "Pulau"
        elif mapname == "chernarus_summer":
            return "Chernarus Summer"
        elif mapname == "sara":
            return "Sahrani"
        elif mapname == "takistan":
            return "Takistan"
        elif mapname == "utes":
            return "Utes"
        elif mapname == "chernarus_winter":
            return "Chernarus Winter"
        elif mapname == "mcn_hazarkot":
            return "Hazar Kot Valley"
        elif mapname == "rura_penthe":
            return "Rura Penthe"
        elif mapname == "abramia":
            return "Isla Abramia"
        elif mapname == "chernarusredux":
            return "Chernarus Redux"
        elif mapname == "lythium":
            return "Lythium"
        elif mapname == "tem_ihantalaw":
            return "Ihantala Winter"
        elif mapname == "zargabad":
            return "Zargabad"
        elif mapname == "wl_route191":
            return "Schwemlitz"
        elif mapname == "cup_kunduz":
            return "Kunduz"
        elif mapname == "pabst_yellowstone":
            return "Yellowstone"
        elif mapname == "tem_anizay":
            return "Anizay"
        elif mapname == "wl_rosche":
            return "Rosche"
        elif mapname == "prei_khmaoch_luong":
            return "Prei Khmaoch Luong"
        elif mapname == "bootcamp_acr":
            return "Bootcamp"
        elif mapname == "fallujah":
            return "Fallujah"
        elif mapname == "chernarus":
            return "Chernarus"
        elif mapname == "lingor3":
            return "Lingor"
        elif mapname == "ruha":
            return "Ruha"
        elif mapname == "dingor":
            return "Dingor"
        elif mapname == "iron_excelsior_tobruk":
            return "Libyen (IFA3)"
        elif mapname == "tem_kujari":
            return "Kujari"
        elif mapname == "tem_summa":
            return "Summa"
        elif mapname == "isladuala3":
            return "Isla Duala"
        elif mapname == "porto":
            return "Porto"
        elif mapname == "swu_kokoda_map":
            return "Kokoda Trail (IFA3)"
        elif mapname == "enoch":
            return "Livonia"
        elif mapname == "malden":
            return "Malden"
        elif mapname == "altis":
            return "Altis"
        elif mapname == "tanoa":
            return "Tanoa"
        elif mapname == "thirsk":
            return "Thirsk"
        elif mapname == "tembelan":
            return "Tembelan"
        elif mapname == "woodland_acr":
            return "Bystrica"
        elif mapname == "i44_merderet_v2":
            return "Merderet (IFA3)"
        elif mapname == "mcn_neaville":
            return "Neaville (IFA3)"
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

    stammspieler.close()

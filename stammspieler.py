#! /usr/bin/python3
# -*- coding:utf-8 -*-

__author__ = "Gunk, Schwaggot"

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

    def get_missions(self):
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

        else:
            cursor.close()
            connection.close()
            raise ValueError("unknown arg: " + repr(arg))

    def get_player(self):
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

        else:
            cursor.close()
            connection.close()
            raise ValueError("unknown arg: " + repr(arg))

    @staticmethod
    def activity(missionen, spieler):
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

    @staticmethod
    def _format_participation(player_missions, total_missions):
        assert len(player_missions) == len(total_missions)

        output = ''
        for i in range(len(total_missions)):
            output += str(player_missions[i]) + ' / ' + str(total_missions[i]) + '  ~  '
        return output[:-5]

    @staticmethod
    def _deserves_stammspieler(player_missions, total_missions):
        assert len(player_missions) == len(total_missions)

        condition1 = player_missions[0] >= total_missions[0] / 3 and player_missions[1] >= total_missions[1] / 3 and \
                     player_missions[2] >= total_missions[2] / 3
        condition2 = player_missions[2] >= total_missions[2] / 2 and player_missions[1] >= total_missions[1] / 2
        condition3 = player_missions[2] >= total_missions[2] / 2 and player_missions[0] >= total_missions[0] / 2
        condition4 = player_missions[1] >= total_missions[1] / 2 and player_missions[0] >= total_missions[0] / 2

        return condition1 or condition2 or condition3 or condition4

    def output_stammspieler(self, steam_id=None):
        # Get raw SQL data as list of tuples (mission_name, player_name, mission_date, steam_id).
        participation = Stammspieler.get_participations(self.get_missions(), self.get_player())

        # Tuples of (mission, mission date) sorted into the 3 time intervals. Has to be sets because mission may appear
        # more than once during iteration.
        total_missions = [set(), set(), set()]

        # Similar to total_mission will contain [set(), set(), set(), playername] with tuples (mission, mission date)
        # sorted per player. Key is player's steam_id
        missions_per_player = dict()

        # Reference date of today to calculate the intervals.
        date_today = datetime.datetime.now().date()
        for mission_name, player_name, mission_date, player_steam_id in participation:
            # Establish the interval index
            #       0 -> 0 - 30 days ago
            #       1 -> 30 - 60 days ago
            #       2 -> 60 - 90 days ago
            if (date_today - timedelta(days=30)) <= mission_date <= date_today:
                interval_idx = 0
            elif (date_today - timedelta(days=60)) <= mission_date <= (date_today - timedelta(days=30)):
                interval_idx = 1
            elif (date_today - timedelta(days=90)) <= mission_date <= (date_today - timedelta(days=60)):
                interval_idx = 2
            else:
                # There might be mission outside of the intervals, ignore them.
                continue

            # Mission is counted for the according interval.
            total_missions[interval_idx].add((mission_name, mission_date))

            # Optimization in order to use same method for both individual and admin interface output. If input steam_id
            # was provided and current steam_id matches, then count, otherwise skip.
            if steam_id and steam_id != player_steam_id:
                continue

            # If this is the first occurence of a particular steam_id, then create the empty entry in the dict.
            if player_steam_id not in missions_per_player:
                missions_per_player[player_steam_id] = [set(), set(), set(), player_name]

            # Finally count the mission for the player and corresponding interval.
            missions_per_player[player_steam_id][interval_idx].add((mission_name, mission_date))

        # Adjust output depending on admin or individual Stammspieler output mode.
        if steam_id:
            output = "Darf ich Stammspieler haben? - "
        else:
            output = "Stammspieler:" + '\n' + '-' * 24 + '\n'

        # Convert the tuples of missions into actual total numbers for each time interval. Index:
        #       0 -> number of missions 0 - 30 days ago
        #       1 -> number of missions 30 - 60 days ago
        #       2 -> number of missions 60 - 90 days ago
        total_missions = [len(total_missions[0]), len(total_missions[1]), len(total_missions[2])]

        # Iterate through all counted player participations and sort by player names if needed. In case steam_id was
        # supplied as input to this method, this loop should be finished after the first iteration.
        for player_steam_id, player_missions in sorted(missions_per_player.items(), key=lambda x: x[1][3].lower()):
            # Retrieve the name of the player that we audaciously stored into the tuple as well.
            player_name = player_missions[3]

            # Similar to the calculation of total missions we counted player's participations per time interval and
            # now convert these into actual numbers
            player_missions = [len(player_missions[0]), len(player_missions[1]), len(player_missions[2])]

            # To hopefully bring some order into the chaos, the actual logic of determining if someone is worthy of
            # Stammspieler was extracted into an extra method that takes only player's participations and total missions
            # per time interval into account.
            deserves_stammspieler = self._deserves_stammspieler(player_missions, total_missions)

            # Finally output formatting depending on admin or individual mode.
            if steam_id:
                if deserves_stammspieler:
                    output += 'Ja! Du bist Stammspieler. \n\n'
                else:
                    output += 'Nein, frag doch einfach später nochmal.\n\n'
                output += 'Du hast mitgespielt: ' + self._format_participation(player_missions, total_missions)
            elif deserves_stammspieler:
                output += player_name + '\n'

        return output

    def dict_stammspieler(self, steam_id=None):
        # Get raw SQL data as list of tuples (mission_name, player_name, mission_date, steam_id).
        participation = Stammspieler.get_participations(self.get_missions(), self.get_player())

        # Tuples of (mission, mission date) sorted into the 3 time intervals. Has to be sets because mission may appear
        # more than once during iteration.
        total_missions = [set(), set(), set()]

        # Similar to total_mission will contain [set(), set(), set(), playername] with tuples (mission, mission date)
        # sorted per player. Key is player's steam_id
        missions_per_player = dict()

        # Reference date of today to calculate the intervals.
        date_today = datetime.datetime.now().date()
        for mission_name, player_name, mission_date, player_steam_id in participation:
            # Establish the interval index
            #       0 -> 0 - 30 days ago
            #       1 -> 30 - 60 days ago
            #       2 -> 60 - 90 days ago
            if (date_today - timedelta(days=30)) <= mission_date <= date_today:
                interval_idx = 0
            elif (date_today - timedelta(days=60)) <= mission_date <= (date_today - timedelta(days=30)):
                interval_idx = 1
            elif (date_today - timedelta(days=90)) <= mission_date <= (date_today - timedelta(days=60)):
                interval_idx = 2
            else:
                # There might be mission outside of the intervals, ignore them.
                continue

            # Mission is counted for the according interval.
            total_missions[interval_idx].add((mission_name, mission_date))

            # Optimization in order to use same method for both individual and admin interface output. If input steam_id
            # was provided and current steam_id matches, then count, otherwise skip.
            if steam_id and steam_id != player_steam_id:
                continue

            # If this is the first occurence of a particular steam_id, then create the empty entry in the dict.
            if player_steam_id not in missions_per_player:
                missions_per_player[player_steam_id] = [set(), set(), set(), player_name]

            # Finally count the mission for the player and corresponding interval.
            missions_per_player[player_steam_id][interval_idx].add((mission_name, mission_date))

        # Convert the tuples of missions into actual total numbers for each time interval. Index:
        #       0 -> number of missions 0 - 30 days ago
        #       1 -> number of missions 30 - 60 days ago
        #       2 -> number of missions 60 - 90 days ago
        total_missions = [len(total_missions[0]), len(total_missions[1]), len(total_missions[2])]

        output = {'interval_participations': []}

        # Iterate through all counted player participations and sort by player names if needed. In case steam_id was
        # supplied as input to this method, this loop should be finished after the first iteration.
        for player_steam_id, player_missions in sorted(missions_per_player.items(), key=lambda x: x[1][3].lower()):
            # Retrieve the name of the player that we audaciously stored into the tuple as well.
            player_name = player_missions[3]

            # Similar to the calculation of total missions we counted player's participations per time interval and
            # now convert these into actual numbers
            player_missions = [len(player_missions[0]), len(player_missions[1]), len(player_missions[2])]

            # To hopefully bring some order into the chaos, the actual logic of determining if someone is worthy of
            # Stammspieler was extracted into an extra method that takes only player's participations and total missions
            # per time interval into account.
            deserves_stammspieler = self._deserves_stammspieler(player_missions, total_missions)

            # Finally output formatting depending on admin or individual mode.
            if steam_id:
                if deserves_stammspieler:
                    output['stammspieler'] = True
                else:
                    output['stammspieler'] = False
                for i in range(len(total_missions)):
                    output['interval_participations'].append(
                        {'played_missions': player_missions[i], 'total_missions': total_missions[i]})

        return output

    @staticmethod
    def get_maps(missions):
        maps = []

        for x in missions:
            maps.append(x[4])

        maps_count = Counter(maps)
        maps_count = sorted(maps_count.items(), key=lambda k: (-k[1], k[0]))
        return maps_count

    @staticmethod
    def get_participations(missionen, players):
        missions = []
        participants = []
        participations = []

        for mission in missionen:
            missions.append(list((mission[0], mission[3].rsplit(".", 3)[0])))

        for player in players:
            participants.append(list((player[0], player[2], player[1])))

        for mission in missions:
            for participant in participants:
                if mission[0] == participant[1]:
                    participations.append(list((mission[1], participant[0], mission[0], participant[2])))

        return participations

    def output_mission(self):
        missions = self.get_missions()
        date = datetime.datetime.now()
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        check = 0
        maxlen = 0
        for x in range(len(missions)):
            mlen = len(missions[x][3].rsplit(".", 3)[0])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Datum:".ljust(13) + "Von:".ljust(11) + "Bis:".ljust(11) + "Mission:".ljust(maxlen + 2) + "Map:")
        output = header + '\n'
        output += "-" * (len(header) + 14) + '\n'

        for x in range(len(missions)):
            mlen = len(missions[x][3].rsplit(".", 3)[0])
            if missions[x][0] > date_from1.date() and check == 0 or missions[x][0] > date_from.date() and check == 1:
                output += "-" * (len(header) + 14) + '\n'
                check += 1
            output += missions[x][0].strftime("%d.%m.%Y") + " | "
            output += str(missions[x][1]) + " | " + str(missions[x][2]) + " | "
            output += missions[x][3].rsplit(".", 3)[0] + " | ".rjust(maxlen + 1 - mlen)
            output += Stammspieler.replace_map_name(missions[x][4]) + '\n'

        output += "\nAnzahl Missionen: " + str(len(missions)) + "\n\n"
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
            "swu_greece_pella_region": "Greece (IFA3)", "clafghan": "CLA Afghan", "fdf_isle1_a": "Podagorsk",
            "cam_lao_nam": "Cam Lao Nam (VN DLC)", "cup_chernarus_a3": "Chernarus 2020", "sefrouramal": "Sefrou Ramal",
            "vn_khe_sanh": "Khe Sanh (VN DLC)", "rhspkl": "Prei Khmaoch Luong (RHSPKL)"}

        if mapname.lower() in map_translations:
            return map_translations[mapname.lower()]
        else:
            return mapname

    def output_maps(self):
        maps = Stammspieler.get_maps(self.get_missions())
        maxlen = 0
        for x in maps:
            mlen = len(x[0])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Karte:".ljust(maxlen + 2) + "Gespielt:")
        output = header + '\n'
        output += "-" * (len(header) + 5) + '\n'

        for m in maps:
            mapname = Stammspieler.replace_map_name(m[0])
            mlen = len(mapname)
            output += mapname + " | ".rjust(maxlen + 1 - mlen) + str(m[1]) + '\n'

        output += "\nAnzahl Karten: " + str(len(maps)) + '\n'
        return output

    def output_activity(self):
        spieler_anzahl = Stammspieler.activity(self.get_missions(), self.get_player())
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
        mitgespielt = Stammspieler.get_participations(self.get_missions(), self.get_player())
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

    def dict_mitgespielt(self, steam_id):
        participations = Stammspieler.get_participations(self.get_missions(), self.get_player())
        date = datetime.datetime.now()
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        count = 0
        check = 0
        player = ""
        output = {'missions': []}

        for participation in participations:
            if steam_id in (participation[3]):
                if player != participation[3]:
                    player = participation[3]
                if participation[2] > date_from1.date() and check == 0 or participation[
                    2] > date_from.date() and check == 1:
                    check += 1
                date_str = participation[2].strftime("%d.%m.%Y")
                mission_name = participation[0]
                output['missions'].append({'date': date_str, 'name': mission_name})
                count += 1

        output['total'] = count
        return output

    def output_participants(self):
        mitgespielt = Stammspieler.get_participations(self.get_missions(), self.get_player())
        mission = ''
        output = ''
        for x in mitgespielt:
            if mission != x[0]:
                if mission != '':
                    output += '</div>'
                    output += '</pre>'
                mission = x[0]
                output += '<div class="head">'
                output += '\nMission: ' + mission + '\n'
                output += '<pre class="body hide">'
                output += '-' * (len(mission) + 10) + '\n'
            output += str(x[1]) + '\n'
        return output

    def output_participants_mission(self, mission_param):
        mitgespielt = Stammspieler.get_participations(self.get_missions(), self.get_player())
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

    def get_username(self, steam_id: str):
        connection = self.create_connection()
        cursor = connection.cursor()
        query = "SELECT PlayerName FROM session WHERE PlayerUID = %s ORDER BY Time DESC LIMIT 1;"
        cursor.execute(query, (steam_id,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()

        if row is not None:
            return row[0]
        else:
            return None


if __name__ == "__main__":
    stammspieler = Stammspieler()

    if sys.argv[1] == "missionen":
        print(stammspieler.output_mission())

    elif sys.argv[1] == "aktivitaet":
        print(stammspieler.output_activity())

    elif sys.argv[1] == "stammspieler":
        print(stammspieler.output_stammspieler(steam_id=sys.argv[2]))

    elif sys.argv[1] == "stammspielerAdmin":
        print(stammspieler.ausgabe_stammspieler_admin())

    elif sys.argv[1] == "karten":
        print(stammspieler.output_maps())

    elif sys.argv[1] == "teilnehmer":
        print(stammspieler.output_participants())

    elif sys.argv[1] == "spieler":
        print(stammspieler.ausgabe_mitgespielt(steam_id=sys.argv[2]))

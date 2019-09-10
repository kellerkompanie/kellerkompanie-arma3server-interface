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

        if zaehler2 >= int(zaehler_mission2 / 3) and zaehler1 >= int(zaehler_mission1 / 3) and zaehler >= int(
                zaehler_mission / 3):
            print("Ja! Du bist Stammspieler. \nMelde dich bei einem Admin deines Vertrauens.")
            print("\nDu hast mitgespielt:", zaehler2, "/", zaehler_mission2, " - ", zaehler1, "/", zaehler_mission1,
                  " - ",
                  zaehler, "/", zaehler_mission)
        elif zaehler2 >= (zaehler_mission2 / 2) and zaehler1 >= (zaehler_mission1 / 2):
            print("Ja! Du bist Stammspieler. \nMelde dich bei einem Admin deines Vertrauens.")
            print("\nDu hast mitgespielt:", zaehler2, "/", zaehler_mission2, " - ", zaehler1, "/", zaehler_mission1,
                  " - ",
                  zaehler, "/", zaehler_mission)
        elif zaehler2 >= (zaehler_mission2 / 2) and zaehler >= (zaehler_mission / 2):
            print("Ja! Du bist Stammspieler. \nMelde dich bei einem Admin deines Vertrauens.")
            print("\nDu hast mitgespielt:", zaehler2, "/", zaehler_mission2, " - ", zaehler1, "/", zaehler_mission1,
                  " - ",
                  zaehler, "/", zaehler_mission)
        elif zaehler1 >= (zaehler_mission1 / 2) and zaehler >= (zaehler_mission / 2):
            print("Ja! Du bist Stammspieler. \nMelde dich bei einem Admin deines Vertrauens.")
            print("\nDu hast mitgespielt:", zaehler2, "/", zaehler_mission2, " - ", zaehler1, "/", zaehler_mission1,
                  " - ",
                  zaehler, "/", zaehler_mission)
        else:
            print("Nein, frag doch einfach später nochmal.")
            print("\nDu hast mitgespielt:", zaehler2, "/", zaehler_mission2, " - ", zaehler1, "/", zaehler_mission1,
                  " - ",
                  zaehler, "/", zaehler_mission)

    def ausgabe_stammspieler_admin(self):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())

        stammi = []
        date = datetime.datetime.now()
        date_from2 = date - timedelta(days=90)
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        spieler_input = ""
        mission = ""

        zaehler_mission = 0
        zaehler_mission1 = 0
        zaehler_mission2 = 0

        for x in mitgespielt:
            if date_from2.date() < x[2] <= date_from1.date():
                if mission != x[0]:
                    mission = x[0]
                    zaehler_mission2 += 1
            elif date_from1.date() < x[2] <= date_from.date():
                if mission != x[0]:
                    mission = x[0]
                    zaehler_mission1 += 1
            elif date_from.date() < x[2] <= date.date():
                if mission != x[0]:
                    mission = x[0]
                    zaehler_mission += 1

        mitgespielt = sorted(mitgespielt, key=lambda x: x[3])

        for x in mitgespielt:
            zaehler = 0
            zaehler1 = 0
            zaehler2 = 0

            if spieler_input != x[3]:
                spieler_input = x[3]
                zaehler = 0
                zaehler1 = 0
                zaehler2 = 0

            if date_from2.date() < x[2] <= date_from1.date():
                zaehler2 += 1
            elif date_from1.date() < x[2] <= date_from.date():
                zaehler1 += 1
            elif date_from.date() < x[2] <= date.date():
                zaehler += 1

            if zaehler2 >= int(zaehler_mission2 / 3) and zaehler1 >= int(zaehler_mission1 / 3) and zaehler >= int(
                    zaehler_mission / 3):
                if x[3] not in stammi:
                    stammi.append(x[1])
                    stammi.append(x[3])
            elif zaehler2 >= (zaehler_mission2 / 2) and zaehler1 >= (zaehler_mission1 / 2):
                if x[3] not in stammi:
                    stammi.append(x[1])
                    stammi.append(x[3])
            elif zaehler2 >= (zaehler_mission2 / 2) and zaehler >= (zaehler_mission / 2):
                if x[3] not in stammi:
                    stammi.append(x[1])
                    stammi.append(x[3])
            elif zaehler1 >= (zaehler_mission1 / 3) and zaehler >= (zaehler_mission / 3):
                if x[3] not in stammi:
                    stammi.append(x[1])
                    stammi.append(x[3])

        header = "Stammspieler: "
        print(header)
        print("-" * (len(header) + 14))

        stammi = sorted(stammi)
        n = len(stammi) / 2
        del stammi[:int(n)]

        for x in stammi:
            print(x)

        print("\nAnzahl Stammspieler:", len(stammi))

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
        print(header)
        print("-" * (len(header) + 14))

        for x in range(len(missionen)):
            mlen = len(missionen[x][3].rsplit(".", 3)[0])
            if missionen[x][0] > date_from1.date() and check == 0 or missionen[x][0] > date_from.date() and check == 1:
                print("-" * (len(header) + 14))
                check += 1
            print(missionen[x][0].strftime("%d.%m.%Y"), "|", missionen[x][1], "|", missionen[x][2], "|",
                  missionen[x][3].rsplit(".", 3)[0], "|".rjust(maxlen + 1 - mlen),
                  Stammspieler.replace_map_name(missionen[x][4]))

        print("\nAnzahl Missionen: ", len(missionen), "\n")

    @staticmethod
    def replace_map_name(mapname):
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
        elif mapname == "Chernarus_winter":
            return "Chernarus Winter"
        elif mapname == "MCN_HazarKot":
            return "Hazar Kot Valley"
        elif mapname == "Rura_Penthe":
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
        elif mapname == "WL_Route191":
            return "Schwemlitz"
        elif mapname == "CUP_Kunduz":
            return "Kunduz"
        elif mapname == "pabst_yellowstone":
            return "Yellowstone"
        elif mapname == "tem_anizay":
            return "Anizay"
        elif mapname == "WL_Rosche":
            return "Rosche"
        elif mapname == "prei_khmaoch_luong":
            return "Prei Khmaoch Luong"
        elif mapname == "Bootcamp_ACR":
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
        else:
            return mapname

    def ausgabe_karten(self):
        karten = Stammspieler.get_karten(self.get_missionen())
        maxlen = 0
        for x in karten:
            mlen = len(x[0])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Karte:".ljust(maxlen + 2) + "Gespielt: ")
        print(header)
        print("-" * (len(header) + 5))

        for x in karten:
            mapname = Stammspieler.replace_map_name(x[0])
            mlen = len(mapname)
            print(mapname, "|".rjust(maxlen + 1 - mlen), x[1])

        print("\nAnzahl Karten:", len(karten))

    def ausgabe_aktivitaet(self):
        spieler_anzahl = Stammspieler.aktivitaet(self.get_missionen(), self.get_spieler())
        maxlen = 0
        for x in spieler_anzahl:
            mlen = len(x[0][1])
            if mlen > maxlen:
                maxlen = mlen

        header = ("Spieler:".ljust(maxlen + 2) + "Teilnahmen: ")
        print(header)
        print("-" * (len(header) + 5))

        for x in spieler_anzahl:
            mlen = len(x[0][1])
            print(x[0][1], "|".rjust(maxlen + 1 - mlen), x[1])

        print("\nVerschiedene Teilnehmer: ", len(spieler_anzahl), "\n")

    def ausgabe_mitgespielt(self, steam_id):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())
        date = datetime.datetime.now()
        date_from1 = date - timedelta(days=60)
        date_from = date - timedelta(days=30)

        zaehler = 0
        check = 0
        spieler = ""

        for x in mitgespielt:
            if steam_id in (x[3]):
                if spieler != x[3]:
                    spieler = x[3]
                    print("\nDatum: ".ljust(13) + "Mission: ")
                    print("-" * 40)
                if x[2] > date_from1.date() and check == 0 or x[2] > date_from.date() and check == 1:
                    print("-" * 40)
                    check += 1
                print(x[2].strftime("%d.%m.%Y"), "|", x[0])
                zaehler += 1
        print("\nAnzahl Mitgespielt: ", zaehler, "\n")

    def ausgabe_teilnehmer(self):
        mitgespielt = Stammspieler.get_teilnehmer(self.get_missionen(), self.get_spieler())
        mission = ""
        if sys.argv[2].isdigit():
            for x in mitgespielt:
                if mission != x[0]:
                    mission = x[0]
                    print("\nMission: ", mission)
                    print("-" * (len(mission) + 10))
                print(x[1])
        else:
            mission_input = sys.argv[2]
            for x in mitgespielt:
                if mission_input in (x[0]):
                    if mission != x[0]:
                        mission = x[0]
                        print("\nMission: ", mission, "|", x[2].strftime("%d.%m.%Y"))
                        print("-" * (len(mission) + 23))
                    print(x[1])


if __name__ == "__main__":
    stammspieler = Stammspieler()

    if sys.argv[1] == "missionen":
        stammspieler.ausgabe_mission()

    elif sys.argv[1] == "aktivitaet":
        stammspieler.ausgabe_aktivitaet()

    elif sys.argv[1] == "stammspieler":
        stammspieler.ausgabe_stammspieler(steam_id=sys.argv[2])

    elif sys.argv[1] == "stammspielerAdmin":
        stammspieler.ausgabe_stammspieler_admin()

    elif sys.argv[1] == "karten":
        stammspieler.ausgabe_karten()

    elif sys.argv[1] == "teilnehmer":
        stammspieler.ausgabe_teilnehmer()

    elif sys.argv[1] == "spieler":
        stammspieler.ausgabe_mitgespielt(steam_id=sys.argv[2])

    stammspieler.close()

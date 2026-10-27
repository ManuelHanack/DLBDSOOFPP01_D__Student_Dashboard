# -*- coding: utf-8 -*-
"""
Modul: database.py
Autor: Manuel Hanack (Matrikelnummer: IU14156336)
Studiengang: B.Sc. Cyber Security
Beschreibung:
    Data Access Layer (DAL) für das IU Studium-Dashboard.
    Kapselt alle SQLite-Datenbankoperationen (Connection Management, Schema-Erstellung,
    Data Seeding, Laden und Speichern der Objektstrukturen).
"""
import sqlite3
import os
from typing import Dict, Any, List, Optional
from models import Studiengang, Semester, Modul, Pruefungsleistung, ModulStatus

class DatabaseManager:
    """
    Verwaltet die Verbindung und den Datenzugriff auf die SQLite-Datenbank 'dashboard.db'.
    Dient als Data Access Object (DAO) für das Fachmodell.
    """
    def __init__(self, db_path: str = "dashboard.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self) -> None:
        """Erstellt die Tabellen student_info und module_progress, falls sie nicht existieren."""
        db_already_exists = os.path.exists(self.db_path)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    matrikelnummer TEXT NOT NULL UNIQUE,
                    studiengang TEXT NOT NULL,
                    regelsesemester INTEGER DEFAULT 8
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS module_progress (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    ects INTEGER NOT NULL,
                    semester INTEGER NOT NULL,
                    note REAL,
                    status TEXT NOT NULL,
                    versuch INTEGER DEFAULT 1
                );
            """)
            conn.commit()

        if not db_already_exists:
            self.seed_data()

    def seed_data(self) -> None:
        """Befüllt die Datenbank beim Erststart mit den 29 Modulen von Manuel Hanack."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO student_info (name, matrikelnummer, studiengang, regelsesemester)
                VALUES ('Manuel Hanack', 'IU14156336', 'B.Sc. Cyber Security', 8);
            """)
            modules = [
                ('DLBIBRVS01', 'Betriebssysteme, Rechnernetze und verteilte Systeme', 5, 1, 2.7, 'Bestanden', 1),
                ('DLBISIC01', 'Einführung in Datenschutz und IT-Sicherheit', 5, 1, 2.0, 'Bestanden', 1),
                ('DLBDSIPWP01_D', 'Einführung in die Programmierung mit Python', 5, 1, 1.7, 'Bestanden', 1),
                ('DLBWIRITT01', 'Einführung in das wissenschaftliche Arbeiten für IT und Technik', 5, 1, 1.7, 'Bestanden', 1),
                ('DLBDSOOFPP01_D', 'Projekt: Objektorientierte und funktionale Programmierung mit Python', 5, 1, None, 'In Bearbeitung', 1),
                ('DLBCSEINF01_D', 'Einführung in die Netzwerkforensik', 5, 2, None, 'Offen', 1),
                ('DLBDSSPDS01_D', 'Statistik - Wahrscheinlichkeit und deskriptive Statistik', 5, 2, None, 'Offen', 1),
                ('IREN01', 'Requirements Engineering', 5, 2, None, 'Offen', 1),
                ('DLBDBAPM01', 'Projekt: Agiles Projektmanagement', 5, 2, None, 'Offen', 1),
                ('DLBAN01', 'Mathematik Grundlagen I', 5, 2, 3.7, 'Bestanden', 1),
                ('DLBDSSPDS01-01_D', 'Statistik - Wahrscheinlichkeit und deskriptive Statistik (Erweiterung)', 5, 2, None, 'Offen', 1),
                ('DLBCSESPB01_D', 'Grundzüge des System-Pentestings', 5, 3, None, 'Offen', 1),
                ('DLBITIML01', 'Theoretische Informatik und Mathematische Logik', 5, 3, None, 'Offen', 1),
                ('DLBCSEESE01_D', 'Social Engineering und Insider Threats', 5, 3, None, 'Offen', 1),
                ('DLBCSEEISC01_D', 'Technische und betriebliche IT-Sicherheitskonzeptionen', 5, 3, None, 'Offen', 1),
                ('DLBCSEDCSW01_D', 'Projekt: Social Engineering', 5, 3, None, 'Offen', 1),
                ('DLBCSEDSOSW01_D', 'DevSecOps und gängige Software-Schwachstellen', 5, 4, None, 'Offen', 1),
                ('DLBISIC02-01', 'Kryptografische Verfahren', 5, 4, None, 'Offen', 1),
                ('DLBCSEHSF01_D', 'Host- und Softwareforensik', 5, 4, None, 'Offen', 1),
                ('DLBCSSCTCS01_D', 'Seminar: Aktuelle Themen in Computer Science', 5, 4, None, 'Offen', 1),
                ('DLBCSEEISC02_D', 'Projekt: Einsatz und Konfiguration von SIEM-Systemen', 5, 4, None, 'Offen', 1),
                ('DLBCSEEFT01_D', 'Threat Modeling', 5, 5, None, 'Offen', 1),
                ('DLBCSEISS01_D', 'Standards der Informationssicherheit', 5, 5, None, 'Offen', 1),
                ('DLBCSEEFT02_D', 'Projekt: Threat Modeling', 10, 5, None, 'Offen', 1),
                ('WAHL01', 'Wahlpflichtmodule A', 10, 5, None, 'Offen', 1),
                ('BBAK01', 'Bachelorarbeit', 9, 6, None, 'Offen', 1),
                ('BBAK02', 'Kolloquium Bachelorarbeit', 1, 6, None, 'Offen', 1),
                ('DLBMINPAPCC01', 'Projekt: Allgemeine Programmierung mit C/C++', 5, 6, None, 'Offen', 1),
                ('WAHL02', 'Wahlpflichtmodule B', 10, 6, None, 'Offen', 1)
            ]
            cursor.executemany("""
                INSERT OR IGNORE INTO module_progress 
                (code, name, ects, semester, note, status, versuch)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, modules)
            conn.commit()

    def get_student_info(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, matrikelnummer, studiengang, regelsesemester FROM student_info LIMIT 1;")
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {"name": "Manuel Hanack", "matrikelnummer": "IU14156336", "studiengang": "B.Sc. Cyber Security", "regelsesemester": 8}

    def load_studiengang(self) -> Studiengang:
        """Rekonstruiert die vollständige Objektstruktur aus der SQLite-Datenbank."""
        info = self.get_student_info()
        studiengang = Studiengang(
            name=info["studiengang"],
            gesamt_ects_ziel=180,
            regelsemester=info["regelsesemester"]
        )

        # 6 Semester erzeugen
        sem_dict: Dict[int, Semester] = {}
        for s_num in range(1, 7):
            sem = Semester(nummer=s_num)
            studiengang.add_semester(sem)
            sem_dict[s_num] = sem

        # Module aus DB laden und den Semestern zuordnen
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, ects, semester, note, status, versuch FROM module_progress ORDER BY semester, code;")
            rows = cursor.fetchall()

            for r in rows:
                code = r["code"]
                m_name = r["name"]
                ects = r["ects"]
                sem_num = r["semester"]
                note = r["note"]
                status_str = r["status"]
                versuch = r["versuch"]

                status_enum = ModulStatus.OFFEN
                for s in ModulStatus:
                    if s.value.lower() == status_str.lower():
                        status_enum = s
                        break

                pl = Pruefungsleistung(name=f"Prüfung {m_name}", ects=ects)
                if note is not None:
                    pl.note = note
                pl.versuch = versuch

                modul = Modul(code=code, name=m_name, status=status_enum, pruefungsleistung=pl)
                
                if sem_num in sem_dict:
                    sem_dict[sem_num].add_modul(modul)

        return studiengang

    def save_module_grade(self, code: str, note: Optional[float], status_str: str, versuch: int) -> bool:
        """Speichert die Notenänderung eines Moduls dauerhaft in der SQLite-Datenbank."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE module_progress 
                SET note = ?, status = ?, versuch = ?
                WHERE code = ?;
            """, (note, status_str, versuch, code))
            conn.commit()
            return cursor.rowcount > 0

    def update_module_grade(self, code: str, note: Optional[float], status: str, versuch: int) -> bool:
        return self.save_module_grade(code, note, status, versuch)

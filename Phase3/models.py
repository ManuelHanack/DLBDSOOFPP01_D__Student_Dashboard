# -*- coding: utf-8 -*-
"""
Modul: models.py
Autor: Manuel Hanack (Matrikelnummer: IU14156336)
Studiengang: B.Sc. Cyber Security
Beschreibung:
    Fachliches Domänenmodell des IU Studium-Dashboards.
    Implementiert Studiengang, Semester, Modul, Pruefungsleistung und ModulStatus.
"""
from enum import Enum
from typing import List, Optional

class ModulStatus(Enum):
    """Enumeration für den eindeutigen Bearbeitungsstatus eines Moduls."""
    OFFEN = "Offen"
    IN_BEARBEITUNG = "In Bearbeitung"
    BESTANDEN = "Bestanden"

class Pruefungsleistung:
    """
    Kapselt Note, ECTS und Versuche.
    Inklusive Notenvalidierung gemäß IU-Notenskala und abgeleitetem Attribut /bestanden.
    """
    def __init__(self, name: str, ects: int):
        self._name = name
        self._ects = ects
        self._note: Optional[float] = None
        self._bestanden: bool = False
        self._versuch: int = 1

    @property
    def name(self) -> str:
        return self._name

    @property
    def ects(self) -> int:
        return self._ects

    @property
    def note(self) -> Optional[float]:
        return self._note

    @note.setter
    def note(self, value: Optional[float]) -> None:
        """
        Kapselung und Validierung der Note gemäß offizieller IU-Notenskala.
        Das Attribut /bestanden wird automatisch berechnet.
        """
        if value is None:
            self._note = None
            self._bestanden = False
            return

        erlaubte_noten = {1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0}
        
        matched = False
        for n in erlaubte_noten:
            if abs(value - n) < 1e-5:
                value = n
                matched = True
                break
                
        if not matched:
            raise ValueError(f"Ungültige Note: {value}. Note muss der IU-Notenskala entsprechen (z.B. 1.0, 1.3, 1.7 etc.).")

        self._note = value
        self._bestanden = value <= 4.0

    @property
    def bestanden(self) -> bool:
        """Abgeleitetes Attribut /bestanden (berechnet aus note <= 4.0)."""
        return self._bestanden

    @property
    def versuch(self) -> int:
        return self._versuch

    @versuch.setter
    def versuch(self, value: int) -> None:
        if value < 1 or value > 3:
            raise ValueError("Die Anzahl der Versuche muss zwischen 1 und 3 liegen.")
        self._versuch = value

class Modul:
    """
    Klasse Modul.
    Verwendet Komposition zu Pruefungsleistung und führt den ModulStatus Enum.
    """
    def __init__(self, code: str, name: str, pruefungsleistung: Pruefungsleistung, status: ModulStatus = ModulStatus.OFFEN):
        self.code = code
        self.name = name
        self.pruefungsleistung = pruefungsleistung
        self.status = status

    @property
    def ects(self) -> int:
        return self.pruefungsleistung.ects

    @property
    def note(self) -> Optional[float]:
        return self.pruefungsleistung.note

    @property
    def bestanden(self) -> bool:
        return self.pruefungsleistung.bestanden

class Semester:
    """
    Klasse Semester.
    Aggregation zu Modulen (Module existieren unabhängig vom Semester).
    """
    def __init__(self, nummer: int):
        self.nummer = nummer
        self.module: List[Modul] = []

    def add_modul(self, modul: Modul) -> None:
        self.module.append(modul)

    def get_ects_gesamt(self) -> int:
        return sum(m.ects for m in self.module)

    def get_ects_bestanden(self) -> int:
        return sum(m.ects for m in self.module if m.bestanden)

class Studiengang:
    """
    Zentrale Aggregationsklasse für den Studiengang (B.Sc. Cyber Security).
    """
    def __init__(self, name: str, gesamt_ects_ziel: int = 180, regelsemester: int = 8):
        self.name = name
        self.gesamt_ects_ziel = gesamt_ects_ziel
        self.regelsemester = regelsemester
        self.semester_liste: List[Semester] = []

    def add_semester(self, semester: Semester) -> None:
        self.semester_liste.append(semester)

    def get_alle_module(self) -> List[Modul]:
        alle = []
        for sem in self.semester_liste:
            alle.extend(sem.module)
        return alle

    def get_ects_aktuell(self) -> int:
        return sum(sem.get_ects_bestanden() for sem in self.semester_liste)

    def get_fortschritt_prozent(self) -> float:
        return round((self.get_ects_aktuell() / self.gesamt_ects_ziel) * 100, 1)

    def get_ects_soll(self, aktuelles_semester: int = 2) -> int:
        ects_pro_sem = self.gesamt_ects_ziel / self.regelsemester
        return int(round(aktuelles_semester * ects_pro_sem))

    def get_notenschnitt(self) -> float:
        bestandene_module = [m for m in self.get_alle_module() if m.bestanden and m.note is not None]
        if not bestandene_module:
            return 0.0
        
        summe_gewichtet = sum(m.note * m.ects for m in bestandene_module)
        summe_ects = sum(m.ects for m in bestandene_module)
        return round(summe_gewichtet / summe_ects, 2)

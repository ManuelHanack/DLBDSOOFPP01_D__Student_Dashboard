"""
Modul: controller.py
Autor: Manuel Hanack (Matrikelnummer: IU14156336)
Studiengang: B.Sc. Cyber Security
Beschreibung:
    Steuerungsschicht (Controller) im MVC-Entwurfsmuster.
    Koordinierte Ablaufsteuerung zwischen View (gui.py), Data Access (database.py) und Domain Model (models.py).
"""
from typing import Dict, Any, List, Optional
from database import DatabaseManager
from models import Studiengang, Modul, ModulStatus

class DashboardController:
    """
    Zentraler Anwendungs-Controller.
    Empfängt Steuerungsanfragen der View, steuert das Fachmodell und speichert über den DatabaseManager.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.studiengang: Studiengang = self.db.load_studiengang()

    def reload_data(self) -> None:
        """Lädt die Objektstruktur komplett neu aus der Datenbank."""
        self.studiengang = self.db.load_studiengang()

    def get_student_info(self) -> Dict[str, Any]:
        return self.db.get_student_info()

    def get_kpis(self) -> Dict[str, Any]:
        """Berechnet alle Kennzahlen für die KPI-Karten der View."""
        aktuell_ects = self.studiengang.get_ects_aktuell()
        ziel_ects = self.studiengang.gesamt_ects_ziel
        soll_ects = self.studiengang.get_ects_soll(aktuelles_semester=2)
        notenschnitt = self.studiengang.get_notenschnitt()
        fortschritt = self.studiengang.get_fortschritt_prozent()

        alle_module = self.studiengang.get_alle_module()
        offen_cnt = sum(1 for m in alle_module if m.status == ModulStatus.OFFEN)
        in_bearbeitung_cnt = sum(1 for m in alle_module if m.status == ModulStatus.IN_BEARBEITUNG)
        bestanden_cnt = sum(1 for m in alle_module if m.status == ModulStatus.BESTANDEN)

        return {
            "aktuell_ects": aktuell_ects,
            "ziel_ects": ziel_ects,
            "soll_ects": soll_ects,
            "notenschnitt": notenschnitt,
            "fortschritt_prozent": fortschritt,
            "offen_cnt": offen_cnt,
            "in_bearbeitung_cnt": in_bearbeitung_cnt,
            "bestanden_cnt": bestanden_cnt,
            "gesamt_module": len(alle_module)
        }

    def get_filtered_modules(self, sem_filter: str = "Alle", status_filter: str = "Alle") -> List[Modul]:
        """Filtert die Module des Fachmodells nach Semester und Status."""
        module = self.studiengang.get_alle_module()

        if sem_filter != "Alle":
            try:
                sem_num = int(sem_filter.replace("Semester ", "").strip())
                module = [m for m in module if any(m in sem.module for sem in self.studiengang.semester_liste if sem.nummer == sem_num)]
            except ValueError:
                pass

        if status_filter != "Alle":
            module = [m for m in module if m.status.value == status_filter]

        return module

    def update_module_grade(self, code: str, note_val: Optional[float], status_str: str, versuch: int) -> bool:
        """
        Aktualisiert eine Prüfungsleistung im Fachmodell und speichert sie in der SQLite-Datenbank.
         Validierung erfolgt im Fachmodell (Pruefungsleistung.note Setter).
        """
        # In-Memory Modell suchen und validieren
        target_modul: Optional[Modul] = None
        for m in self.studiengang.get_alle_module():
            if m.code == code:
                target_modul = m
                break

        if not target_modul:
            raise ValueError(f"Modul mit Code '{code}' nicht im Fachmodell gefunden.")

        # Validierung über den Setter der Pruefungsleistung erzwingen
        target_modul.pruefungsleistung.note = note_val
        target_modul.pruefungsleistung.versuch = versuch

        # Status anpassen
        for s in ModulStatus:
            if s.value.lower() == status_str.lower():
                target_modul.status = s
                break

        # Persistieren via Data Access Layer
        success = self.db.save_module_grade(code, note_val, target_modul.status.value, versuch)
        return success

# -*- coding: utf-8 -*-
"""
Modul: main.py
Autor: Manuel Hanack (Matrikelnummer: IU14156336)
Studiengang: B.Sc. Cyber Security
Beschreibung:
    Haupt-Einstiegspunkt (Bootstrapper) für das IU Studium-Dashboard.
    Initialisiert den DatabaseManager (Data Access Layer), den
    DashboardController (Controller Layer) und startet die Tkinter-GUI
    (StudentDashboardApp, View Layer).
"""
import sys
import tkinter as tk
from database import DatabaseManager
from controller import DashboardController
from gui import StudentDashboardApp

def main() -> None:
    print("Starte IU Studium-Dashboard...")
    
    try:
        # 1. Data Access Layer initialisieren
        db_manager = DatabaseManager("dashboard.db")
        print("1. Data Access Layer (DatabaseManager) erfolgreich initialisiert.")
        
        # 2. Controller Layer initialisieren
        controller = DashboardController(db_manager)
        print("2. Controller Layer (DashboardController) erfolgreich initialisiert.")
        
        # 3. View Layer (Tkinter GUI) initialisieren & starten
        root = tk.Tk()
        app = StudentDashboardApp(root, controller)
        print("3. View Layer (StudentDashboardApp) erfolgreich gestartet.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Schwerwiegender Fehler beim Anwendungsstart: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

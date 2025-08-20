#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Account Live Checker mit Hiker API
Prüft ob Instagram-Accounts verfügbar sind oder nicht
Liest Usernames aus usernames.txt Datei
"""

import json
import time
import os
import csv
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from hikerapi import Client

class InstagramAccountChecker:
    def __init__(self):
        # Hiker API Token
        self.token = "z8a221z0zonceh0yno8armzrrsxpeoz7"
        self.client = Client(token=self.token)
        self.total_api_calls = 0
        self.live_accounts = []
        self.dead_accounts = []
        
    def read_usernames_from_file(self, filename: str = "usernames.txt") -> List[str]:
        """
        Liest Usernames aus einer Textdatei
        """
        usernames = []
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    usernames = [line.strip() for line in f if line.strip()]
                print(f"✅ {len(usernames)} Usernames aus {filename} gelesen:")
                for username in usernames:
                    print(f"   - @{username}")
            else:
                print(f"❌ Datei {filename} nicht gefunden!")
        except Exception as e:
            print(f"❌ Fehler beim Lesen der Datei {filename}: {e}")
        
        return usernames

    def check_account_status(self, username: str) -> Dict[str, Any]:
        """
        Prüft ob ein Instagram-Account verfügbar ist (live) oder nicht
        """
        result = {
            'username': username,
            'is_live': False,
            'status': 'UNBEKANNT',
            'error_message': None
        }
        
        try:
            print(f"🔍 Prüfe @{username}...")
            user_info = self.client.user_by_username_v1(username)
            self.total_api_calls += 1
            
            # Debug: API-Antwort ausgeben (nur für Entwicklung)
            if user_info:
                print(f"  🐛 Debug - API Antwort: {type(user_info)}")
                if isinstance(user_info, dict):
                    key_info = {
                        'pk': user_info.get('pk'),
                        'full_name': user_info.get('full_name'),
                        'follower_count': user_info.get('follower_count'),
                        'following_count': user_info.get('following_count'),
                        'biography': user_info.get('biography', '')[:50] if user_info.get('biography') else None
                    }
                    print(f"  🐛 Debug - Schlüsseldaten: {key_info}")
            
            if user_info and isinstance(user_info, dict):
                # Zusätzliche Validierung für echte Live-Accounts
                user_id = user_info.get("pk")
                full_name = user_info.get("full_name")
                
                # Robuste Prüfung für echte Live-Accounts
                # Ein echter Account sollte mindestens eine user_id haben
                if user_id and user_id != 0:
                    # Zusätzliche Plausibilitätsprüfung
                    follower_count = user_info.get("follower_count", 0)
                    following_count = user_info.get("following_count", 0)
                    
                    # Wenn ein Account existiert, sollte er zumindest realistische Werte haben
                    # oder zumindest einen Namen/Bio haben
                    if (follower_count >= 0 and following_count >= 0 and 
                        (full_name is not None or user_info.get("biography") is not None)):
                        
                        # Account existiert und ist verfügbar
                        result.update({
                            'is_live': True,
                            'status': 'LIVE ✅'
                        })
                        
                        print(f"  ✅ LIVE - @{username}")
                        self.live_accounts.append(result)
                    else:
                        # Account-Daten sind inkonsistent oder unvollständig
                        result.update({
                            'is_live': False,
                            'status': 'NICHT VERFÜGBAR ❌',
                            'error_message': 'Account-Daten unvollständig oder Account nicht verfügbar'
                        })
                        
                        print(f"  ❌ NICHT VERFÜGBAR - @{username}")
                        self.dead_accounts.append(result)
                else:
                    # Keine gültige User-ID
                    result.update({
                        'is_live': False,
                        'status': 'NICHT VERFÜGBAR ❌',
                        'error_message': 'Account existiert nicht oder ist nicht verfügbar'
                    })
                    
                    print(f"  ❌ NICHT VERFÜGBAR - @{username}")
                    self.dead_accounts.append(result)
                
            else:
                # Account nicht gefunden oder nicht verfügbar
                result.update({
                    'is_live': False,
                    'status': 'NICHT VERFÜGBAR ❌',
                    'error_message': 'Account existiert nicht oder ist nicht verfügbar'
                })
                
                print(f"  ❌ NICHT VERFÜGBAR - @{username}")
                self.dead_accounts.append(result)
                
        except Exception as e:
            # Fehler beim API-Aufruf
            result.update({
                'is_live': False,
                'status': 'FEHLER ⚠️',
                'error_message': str(e)
            })
            
            print(f"  ⚠️ FEHLER - @{username}: {e}")
            self.dead_accounts.append(result)
        
        return result

    def save_results_to_csv(self):
        """
        Speichert die Ergebnisse in separate CSV-Dateien
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Live Accounts CSV
        if self.live_accounts:
            live_file = f"live_accounts_{timestamp}.csv"
            with open(live_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Username', 'Status', 'Instagram_Link']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for account in self.live_accounts:
                    writer.writerow({
                        'Username': account['username'],
                        'Status': account['status'],
                        'Instagram_Link': f"https://instagram.com/{account['username']}"
                    })
            
            print(f"💾 Live Accounts gespeichert: {live_file}")
        
        # Dead Accounts CSV
        if self.dead_accounts:
            dead_file = f"dead_accounts_{timestamp}.csv"
            with open(dead_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Username', 'Status', 'Error_Message', 'Instagram_Link']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for account in self.dead_accounts:
                    writer.writerow({
                        'Username': account['username'],
                        'Status': account['status'],
                        'Error_Message': account.get('error_message', ''),
                        'Instagram_Link': f"https://instagram.com/{account['username']}"
                    })
            
            print(f"💾 Nicht verfügbare Accounts gespeichert: {dead_file}")

    def check_all_accounts(self, usernames_file: str = "usernames.txt"):
        """
        Prüft alle Accounts aus der usernames.txt Datei
        """
        print(f"🚀 Starte Account-Live-Check mit Hiker API...")
        print("=" * 60)
        print("💡 Keine Instagram-Anmeldung erforderlich!")
        
        # Usernames aus Datei lesen
        usernames = self.read_usernames_from_file(usernames_file)
        
        if not usernames:
            print(f"❌ Keine Usernames in {usernames_file} gefunden!")
            return
        
        print(f"\n🎯 Prüfe {len(usernames)} Accounts...")
        print("-" * 50)
        
        # Jeden Username prüfen
        for i, username in enumerate(usernames, 1):
            print(f"\n[{i}/{len(usernames)}] Prüfe @{username}...")
            
            result = self.check_account_status(username)
            
            # Kurze Pause zwischen Anfragen
            if i < len(usernames):
                pause_time = random.uniform(1.0, 2.0)
                print(f"⏱️ Pause: {pause_time:.1f}s...")
                time.sleep(pause_time)
        
        # Ergebnisse zusammenfassen
        self.print_summary()
        
        # Als CSV speichern
        self.save_results_to_csv()

    def print_summary(self):
        """
        Druckt eine Zusammenfassung der Ergebnisse
        """
        total_accounts = len(self.live_accounts) + len(self.dead_accounts)
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print("=" * 60)
        print(f"📊 Geprüfte Accounts: {total_accounts}")
        print(f"✅ Live Accounts: {len(self.live_accounts)}")
        print(f"❌ Nicht verfügbare Accounts: {len(self.dead_accounts)}")
        print(f"📡 API-Calls verwendet: {self.total_api_calls}")
        
        if total_accounts > 0:
            live_percentage = (len(self.live_accounts) / total_accounts) * 100
            print(f"📈 Live-Rate: {live_percentage:.1f}%")
        
        if self.live_accounts:
            print(f"\n✅ LIVE ACCOUNTS:")
            for account in self.live_accounts:
                print(f"   • @{account['username']}")
        
        if self.dead_accounts:
            print(f"\n❌ NICHT VERFÜGBARE ACCOUNTS:")
            for account in self.dead_accounts:
                print(f"   • @{account['username']} - {account['status']}")

def main():
    """
    Hauptfunktion - Account Live Check
    """
    print("=" * 80)
    print("🔍 INSTAGRAM ACCOUNT LIVE CHECKER MIT HIKER API")
    print("=" * 80)
    print("💡 Prüft ob Instagram-Accounts verfügbar sind!")
    print("💡 Keine Instagram-Anmeldung erforderlich!")
    
    checker = InstagramAccountChecker()
    
    # Usernames-Datei prüfen
    usernames_file = "usernames.txt"
    if not os.path.exists(usernames_file):
        print(f"❌ Datei {usernames_file} nicht gefunden!")
        print(f"💡 Erstelle eine {usernames_file} Datei mit einem Username pro Zeile")
        return
    
    print(f"\n⚙️ KONFIGURATION:")
    print(f"   Usernames-Datei: {usernames_file}")
    print(f"   API: Hiker API (kein Instagram-Login nötig)")
    print(f"   Export-Format: CSV (Live + Nicht verfügbare getrennt)")
    print(f"   Speicherort: Aktueller Ordner")
    
    # Automatischer Start ohne Bestätigung
    checker.check_all_accounts(usernames_file)
    print("\n🎉 Account-Check erfolgreich abgeschlossen!")
    print(f"💾 CSV-Dateien wurden im aktuellen Ordner gespeichert")

if __name__ == "__main__":
    main()
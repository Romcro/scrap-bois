import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

class GoodForestScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GoodForest Scraper")
        self.root.geometry("800x600")
        self.setup_ui()
        self.set_style()
        self.stop_event = threading.Event()
        self.protocol_steps = [
            ("scolytes", "scolytes+france"),
            ("prix_bois", "prix+bois+m3+sur+pied+2025"),
            ("pathogenes", "pathogènes+bois+recherches")
        ]

    def set_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', 
                      font=('Helvetica', 10, 'bold'), 
                      padding=10,
                      foreground='white',
                      background='#2ecc71')
        style.map('TButton', 
                background=[('active', '#27ae60'), ('disabled', '#bdc3c7')])
        style.configure('Header.TLabel',
                      font=('Helvetica', 14, 'bold'),
                      foreground='#2c3e50',
                      background='#f0f0f0',
                      padding=10)

    def setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="🌳 GoodForest Scraper", style='Header.TLabel').pack(side=tk.LEFT)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        self.control_frame = ttk.Frame(main_frame)
        self.control_frame.pack(fill=tk.X, pady=5)
        self.scrape_btn = ttk.Button(self.control_frame, 
                                   text="Lancer la collecte", 
                                   command=self.start_scraping_thread)
        self.scrape_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(self.control_frame,
                                 text="Arrêter",
                                 command=self.stop_scraping,
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.progress = ttk.Progressbar(main_frame, 
                                      orient=tk.HORIZONTAL, 
                                      mode='determinate',
                                      maximum=100)
        self.progress.pack(fill=tk.X, pady=10)
        self.log_area = scrolledtext.ScrolledText(main_frame,
                                                height=15,
                                                wrap=tk.WORD,
                                                font=('Menlo', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.tag_config('success', foreground='#27ae60')
        self.log_area.tag_config('error', foreground='#e74c3c')
        self.log_area.tag_config('warning', foreground='#f39c12')
        self.status = ttk.Label(self.root, 
                              text="Prêt",
                              relief=tk.SUNKEN,
                              anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def start_scraping_thread(self):
        self.scrape_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.stop_event.clear()
        threading.Thread(target=self.run_protocols, daemon=True).start()

    def stop_scraping(self):
        self.stop_event.set()
        self.log_message("Arrêt demandé...", 'warning')

    def log_message(self, message, tag=None):
        self.root.after(0, self._update_log, message, tag)

    def _update_log(self, message, tag):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def update_progress(self, value):
        self.root.after(0, self._update_progress_bar, value)

    def _update_progress_bar(self, value):
        self.progress['value'] = value
        self.status.config(text=f"Progression : {int(value)}%")
        self.root.update_idletasks()

    def run_protocols(self):
        try:
            total_steps = len(self.protocol_steps) * 3
            current_step = 0
            
            for protocol_id, (category, query) in enumerate(self.protocol_steps, 1):
                if self.stop_event.is_set():
                    break
                
                # Étape 1: Initialisation
                current_step += 1
                self.update_progress((current_step / total_steps) * 100)
                self.log_message(f"PROTOCOLE {protocol_id} - {category.upper()} : Initialisation")
                
                # Étape 2: Scraping Web
                current_step += 1
                self.update_progress((current_step / total_steps) * 100)
                web_results = self.execute_scraping_step(
                    f"PROTOCOLE {protocol_id} - Google Search", 
                    self.scrape_google, 
                    query
                )
                
                # Étape 3: Scraping Scholar
                current_step += 1
                self.update_progress((current_step / total_steps) * 100)
                scholar_results = self.execute_scraping_step(
                    f"PROTOCOLE {protocol_id} - Google Scholar", 
                    self.scrape_scholar, 
                    query
                )
                
                # Sauvegarde
                if not self.stop_event.is_set():
                    self.save_results(category, web_results + scholar_results)
                    for url in web_results + scholar_results:
                        self.log_message(f"URL trouvée : {url}", 'success')
            
            if not self.stop_event.is_set():
                self.log_message("Collecte terminée avec succès !", 'success')
                self.update_progress(100)
                
        except Exception as e:
            self.log_message(f"ERREUR : {str(e)}", 'error')
        finally:
            self.scrape_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def execute_scraping_step(self, step_name, scraping_function, query):
        self.log_message(f"{step_name} : Démarrage")
        try:
            results = scraping_function(query)
            self.log_message(f"{step_name} : {len(results)} résultats trouvés", 'success')
            return results
        except Exception as e:
            self.log_message(f"{step_name} : Échec - {str(e)}", 'error')
            return []

    def save_results(self, category, urls):
        try:
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            filename = os.path.join(desktop_path, f"GF_{category}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Catégorie', 'URL'])
                writer.writerows([[category, url] for url in urls])
            
            self.log_message(f"Sauvegarde réussie : {filename}", 'success')
        except Exception as e:
            self.log_message(f"Échec sauvegarde : {str(e)}", 'error')

    def scrape_google(self, query):
        options = Options()
        # Désactive le mode headless pour voir ce qui se passe à l'écran
        # options.add_argument("--headless=new")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")
        
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        try:
            driver.get(f"https://www.google.com/search?q={query}&tbs=qdr:w")
            # Sauvegarde la page pour vérifier si Google bloque
            with open("last_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            # Vérifie si Google a bloqué l'accès
            if "verification" in driver.title.lower() or "captcha" in driver.title.lower():
                self.log_message("Google a bloqué l'accès : CAPTCHA ou vérification demandée", 'error')
                return []
            
            results_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
            if not results_elements:
                self.log_message("Aucun résultat trouvé : Google a peut-être bloqué l'accès", 'warning')
                return []
            
            results = []
            for result in results_elements:
                try:
                    link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
                    if link and not link.startswith("https://www.google.com/"):
                        results.append(link)
                except:
                    continue
            return results
        finally:
            driver.quit()

    def scrape_scholar(self, query):
        options = Options()
        # options.add_argument("--headless=new")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15")
        
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        try:
            driver.get(f"https://scholar.google.com/scholar?q={query}&as_ylo=2023")
            # Sauvegarde la page pour vérifier si Google Scholar bloque
            with open("last_page_scholar.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            # Vérifie si Google Scholar a bloqué l'accès
            if "verification" in driver.title.lower() or "captcha" in driver.title.lower():
                self.log_message("Google Scholar a bloqué l'accès : CAPTCHA ou vérification demandée", 'error')
                return []
            
            results_elements = driver.find_elements(By.CSS_SELECTOR, "div.gs_ri")
            if not results_elements:
                self.log_message("Aucun résultat trouvé : Google Scholar a peut-être bloqué l'accès", 'warning')
                return []
            
            results = []
            for result in results_elements:
                try:
                    link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
                    if link:
                        results.append(link)
                except:
                    continue
            return results
        finally:
            driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = GoodForestScraperApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.stop_scraping(), root.destroy()])
    root.mainloop()

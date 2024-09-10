import os
import pygame
import sys
import datetime
import requests
import matplotlib.pyplot as plt
import re
import logging
import time
from dotenv import load_dotenv

# Configurazione del logger
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Inizializzazione di Pygame
pygame.init()

# Dimensioni dello schermo
screen = pygame.display.set_mode((800, 480))

# Colori
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Variabili globali
current_duration = "Caricamento durata..."
current_distance = "Caricamento distanza..."
gm_api_timer = 600
directions_timer = 600
last_directions_update = "Mai"
updating_directions = False

# Carica la chiave API da un file o variabile di ambiente per sicurezza

# Carica il file .env
load_dotenv()

# Leggi la chiave API dal file .env
API_KEY = os.getenv("API_KEY")

# Usa la chiave API nel codice
print(API_KEY)  # Per verificare che la chiave sia caricata correttamente

origin = "via penate 16, 6850 mendrisio"
destination = "via como 151, 22038 tavernerio"
travel_mode = "DRIVING"

# Percorso del file di log
LOG_PATH = "api_calls_log.txt"

def log_directions_call(duration):
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    new_log_line = f"Timestamp: {current_time_str}, Durata: {duration}\n"
    
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as file:
            lines = file.readlines()
    else:
        lines = []
    
    limit_date = current_time - datetime.timedelta(days=7)
    
    filtered_lines = [
        line for line in lines if datetime.datetime.strptime(line.split(",")[0].split(": ")[1], "%Y-%m-%d %H:%M:%S") > limit_date
    ]
    
    with open(LOG_PATH, "w") as file:
        file.writelines(filtered_lines)
        file.write(new_log_line)

def get_durations_from_log():
    week_days = ["Lun", "Mar", "Mer", "Gio", "Ven"]
    data_by_day_and_time = []

    try:
        with open(LOG_PATH, "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(", ")
                timestamp = parts[0].split(": ")[1]
                duration_match = re.search(r'(\d+) mins', parts[1])
                if duration_match:
                    duration = int(duration_match.group(1))
                    date_obj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    time = date_obj.strftime("%H:%M")
                    week_day_index = date_obj.weekday()
                    if 0 <= week_day_index <= 4:
                        week_day = week_days[week_day_index]
                        data_by_day_and_time.append((week_day, time, duration))
    except FileNotFoundError:
        logging.error("File di log non trovato.")

    return data_by_day_and_time

def is_within_operating_hours():
    now = datetime.datetime.now()
    return now.weekday() < 5 and 9 <= now.hour < 20

def fetch_directions():
    global updating_directions, current_duration, current_distance, last_directions_update, directions_timer

    if not is_within_operating_hours() or updating_directions:
        return

    updating_directions = True
    start_time = time.time()

    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&departure_time=now&traffic_model=best_guess&key={API_KEY}&mode={travel_mode}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_duration = data['rows'][0]['elements'][0]['duration_in_traffic']['text']
            current_distance = data['rows'][0]['elements'][0]['distance']['text']
            log_directions_call(current_duration)
            last_directions_update = datetime.datetime.now().strftime("%H:%M:%S")
            update_graph()  # Aggiorna il grafico solo quando ci sono nuovi dati
        else:
            current_duration = "Non disponibile"
            current_distance = "Non disponibile"
    finally:
        elapsed_time = time.time() - start_time
        updating_directions = False
        directions_timer = gm_api_timer - int(elapsed_time)

# Variabile globale per memorizzare l'immagine del grafico
graph_image = None

def update_graph():
    global graph_image
    plt.figure(figsize=(8, 2.8))
    days = ["Lun", "Mar", "Mer", "Gio", "Ven"]
    colors = ['b', 'g', 'r', 'c', 'm']
    day_data = {day: [] for day in days}
    structured_data = get_durations_from_log()
    max_duration = 0
    max_time = ''
    for day, time, duration in structured_data:
        if day in day_data:
            day_data[day].append((time, duration))
            if duration > max_duration:
                max_duration = duration
                max_time = time

    for i, day in enumerate(days):
        if day_data[day]:
            times, durations = zip(*day_data[day])
            times = [float(t.split(':')[0]) + float(t.split(':')[1])/60 for t in times]
            plt.plot(times, durations, marker='o', linestyle='-', color=colors[i], label=day, markersize=2, linewidth=1)

    now = datetime.datetime.now()
    current_time_decimal = now.hour + now.minute / 60
    plt.axvline(x=current_time_decimal, color='k', linestyle='--', label='Orario attuale')

    plt.title('Tempo di Percorrenza per Giorno e Ora')
    if max_time:
        plt.annotate('Punto massimo', xy=(float(max_time.split(':')[0]) + float(max_time.split(':')[1])/60, max_duration),
                     xytext=(float(max_time.split(':')[0]) + 0.5, max_duration + 5),
                     arrowprops=dict(facecolor='black', shrink=0.05))
    plt.xlabel('Ora del Giorno')
    plt.ylabel('Durata (min)')
    plt.xticks(range(10, 20), fontsize=8)
    plt.yticks(range(0, 61, 5), fontsize=8)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('traffic_graph.png')
    plt.close()

    graph_image = pygame.image.load('traffic_graph.png')

def draw_clock():
    current_time = datetime.datetime.now().strftime("%H:%M")
    font = pygame.font.Font(None, 36)
    text = font.render(current_time, True, WHITE)
    screen.blit(text, (20, 10))

def draw_directions():
    font = pygame.font.Font(None, 24)
    duration_minutes = int(current_duration.split()[0]) if 'min' in current_duration else 0
    color = GREEN if duration_minutes < 30 else YELLOW if duration_minutes <= 45 else RED
    duration_text = font.render(f"Durata con traffico: {current_duration}", True, color)
    distance_text = font.render(f"Distanza: {current_distance}", True, WHITE)
    screen.blit(duration_text, (20, 40))
    screen.blit(distance_text, (20, 70))

def draw_addresses():
    font = pygame.font.Font(None, 24)
    
    # Testo dell'indirizzo di partenza
    origin_text = font.render(f"Partenza: {origin}", True, WHITE)
    screen.blit(origin_text, (20, 100))
    
    # Testo dell'indirizzo di arrivo
    destination_text = font.render(f"Arrivo: {destination}", True, WHITE)
    screen.blit(destination_text, (20, 130))


def draw_status():
    font = pygame.font.Font(None, 20)
    base_y = 80
    line_spacing = 20
    start_x = 450

    directions_status = "Aggiornamento direzioni..." if updating_directions else f"Ultimo aggiornamento direzioni: {last_directions_update}"
    directions_timer_text = f"Aggiornamento direzioni in: {directions_timer}s"

    directions_update_text = font.render(directions_status, True, WHITE)
    directions_timer_render = font.render(directions_timer_text, True, WHITE)

    screen.blit(directions_update_text, (start_x, base_y))
    screen.blit(directions_timer_render, (start_x, base_y + line_spacing))

def draw_progress_bar():
    left = 440
    top = 10
    width = 350
    height = 30
    progress_length = ((gm_api_timer - directions_timer) / gm_api_timer) * width
    pygame.draw.rect(screen, GREEN, (left, top, progress_length, height))

def update_ui():
    screen.fill(BLACK)
    draw_clock()
    draw_directions()
    draw_status()
    draw_progress_bar()
    draw_addresses()
    if graph_image:
        screen.blit(graph_image, (0, 180))
    pygame.display.flip()

# Eventi personalizzati
FETCH_DIRECTIONS = pygame.USEREVENT + 1
UPDATE_UI = pygame.USEREVENT + 2

pygame.time.set_timer(FETCH_DIRECTIONS, gm_api_timer * 1000)  # Ogni 10 minuti
pygame.time.set_timer(UPDATE_UI, 1000)  # Ogni secondo

running = True
try:
    update_graph()  # Genera il grafico iniziale
    fetch_directions() # aggiorna subito le api
    while running:
        for event in pygame.event.get([pygame.QUIT, FETCH_DIRECTIONS, UPDATE_UI]):
            if event.type == pygame.QUIT:
                running = False
            elif event.type == FETCH_DIRECTIONS:
                fetch_directions()
            elif event.type == UPDATE_UI:
                directions_timer = max(0, directions_timer - 1)
                update_ui()
        
        pygame.time.wait(10)

except Exception as e:
    logging.error("Errore imprevisto: %s", str(e))

finally:
    pygame.quit()
    sys.exit()

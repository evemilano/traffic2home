
# Real-time Traffic and Distance Monitor using Pygame and Google Maps API

This project is a real-time traffic and distance monitor that fetches travel data from the Google Maps API and displays it using Pygame. It visualizes the traffic duration and distance between two addresses and generates a historical graph based on logged data.

## Features

- **Real-time traffic updates:** Fetches traffic data between two locations using the Google Maps API.
- **Customizable:** You can easily change the origin and destination addresses as well as the travel mode.
- **Graphical visualization:** Displays a dynamic graph showing travel time trends based on the log history.
- **Log system:** Keeps a log of traffic duration for the past 7 days.
- **Progress bar:** Visualizes the remaining time until the next API update.
- **User Interface:** Displays the current time, traffic duration, distance, and the addresses in a graphical interface.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/traffic-monitor-pygame.git
   cd traffic-monitor-pygame
   ```

2. **Install dependencies:**

   Make sure you have Python installed. Then install the required libraries using:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the Google Maps API key:**

   Create a `.env` file in the root directory and add your Google Maps API key:

   ```bash
   API_KEY=your_google_maps_api_key
   ```

## Usage

To start the program, simply run:

```bash
python main.py
```

### How it works:

- **Google Maps API:** The script uses the Distance Matrix API to fetch real-time traffic data.
- **Logging:** It logs the duration of the traffic data into a file `api_calls_log.txt`, and only keeps data from the past 7 days.
- **Graph Generation:** A graph is generated to display the trends of traffic durations over time.
- **Pygame UI:** The interface displays the current traffic duration, distance, addresses, and a graph in real-time.

## Configuration

- **Addresses:**
   You can modify the `origin` and `destination` variables in the script to customize the route.
   
   ```python
   origin = "your_origin_address"
   destination = "your_destination_address"
   ```

- **Travel Mode:**
   The `travel_mode` variable can be set to one of the following:
   - `DRIVING`
   - `WALKING`
   - `BICYCLING`
   - `TRANSIT`

   Example:

   ```python
   travel_mode = "DRIVING"
   ```

## Requirements

- Python 3.x
- Libraries listed in `requirements.txt`
- Google Maps Distance Matrix API key

## Logging

All traffic data is logged into `api_calls_log.txt`. The log is automatically cleaned up to only keep entries from the past 7 days.

## Troubleshooting

If you encounter any issues with the Google Maps API or other parts of the program, check the `error_log.txt` file for error details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

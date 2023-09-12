# RSS Display for Pimoroni Galactic Unicorn (53x11)

This repository contains a script tailored for the Pimoroni Galactic Unicorn 53x11 display, allowing it to fetch and showcase RSS feed data. The script is written in MicroPython and is optimized for the unique capabilities and resolution of the Galactic Unicorn display.

## Features:
- Fetches RSS data from over 20 popular predefined sources. (Includes CNN, BBC, NASA, TechCrunch, BuzzFeed, and much more!)
- Parses and cleans the RSS data for optimal display on the 53x11 resolution.
- Provides a user interface to navigate through different RSS items and sources.
- Handles errors gracefully and provides feedback on the display.
- Designed specifically for the Pimoroni Galactic Unicorn 53x11 display.

## Requirements:
- A Pimoroni Galactic Unicorn 53x11 display.
- A device running MicroPython that's compatible with the display.
- Internet connectivity for fetching RSS data.

## Installation:
1. Clone this repository to your local machine.
2. Upload the python files to your Unicorn. (You can find the latest version of network_manager.py from https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/common)
3. Edit secrets.py with your SSID and Wi-Fi password.
4. Ensure you have enough free memory (at least 256kb).
5. Run the rss_display.py script to start displaying RSS feeds on your Galactic Unicorn.

## Usage:
- Upon starting the script, it will automatically fetch and display RSS data from the predefined sources on the Galactic Unicorn display.
- Use the device's buttons to navigate through different RSS items and sources.

## Button Functions

| Button         | Function                                           |
|----------------|----------------------------------------------------|
| Lux (+)        | Increase brightness                                |
| Lux (-)        | Decrease brightness                                |
| Vol (+)        | Switch to the next RSS feed                        |
| Vol (-)        | Switch to the previous RSS feed                    |

## Customization:
- Add or remove RSS sources by modifying the `rss_feeds` dictionary in the script.
- Adjust display settings such as font, color, and duration to fit your preferences.

## Contributing:
Contributions are always welcome! Fork this repository and submit pull requests for any enhancements, fixes, or features you'd like to add.

## License:
This project is open-source and available under the MIT License. Check out the LICENSE file for more details.

## Acknowledgments:
- A big shoutout to the MicroPython community and Pimoroni for creating the Galactic Unicorn display.
- Thanks to all contributors and users for their support and feedback.

---

For any issues, suggestions, or feedback, please open an issue on GitHub.

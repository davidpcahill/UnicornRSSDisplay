from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN
import network
import time
import urequests as requests
import re
import os
import gc

# Initialize the display
gu = GalacticUnicorn()
display = PicoGraphics(display=DISPLAY_GALACTIC_UNICORN)
WIDTH, HEIGHT = display.get_bounds()
gu.set_brightness(0.5)

# Default settings
TEXT_COLOR = display.create_pen(255, 255, 255)  # White
OUTLINE_COLOR = display.create_pen(50, 50, 50)  # Black
BACKGROUND_COLOR = display.create_pen(0, 0, 0)  # Dark gray
FONT = "bitmap8"
display.set_font(FONT)
SCROLL_SPEED = 1  # Adjust as needed
TIME_BETWEEN_ITEMS = 2  # Seconds

# Text settings
source_outline = True
source_font_name = "bitmap8"
source_text_color = display.create_pen(64, 64, 127)
source_outline_color = display.create_pen(255, 255, 255)
source_bg_color = display.create_pen(31, 37, 59)

title_outline = False
title_font_name = "bitmap8"
title_text_color = display.create_pen(255, 255, 255)
title_outline_color = display.create_pen(64, 64, 127)
title_bg_color = display.create_pen(64, 0, 0)

description_outline = False
description_font_name = "bitmap8"
description_text_color = display.create_pen(239, 245, 191)
description_outline_color = display.create_pen(32, 32, 32)
description_bg_color = display.create_pen(0, 0, 0)

# RSS feeds
# Some commented out due to memory
rss_feeds = {
    # News
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "rss.cnn.com/rss/edition.rss",
    "HuffPost": "https://www.huffpost.com/news/world-news/feed",
    "HuffPostUS": "https://www.huffpost.com/section/us-news/feed",
    
    # Tech
    "Engadget": "https://engadget.com/rss.xml",
    #"Gizmodo": "https://gizmodo.com/rss",
    "Mashable": "https://in.mashable.com/",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    #"ArsTechnica": "http://feeds.arstechnica.com/arstechnica/index",
    "TechCrunch": "https://techcrunch.com/feed",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    #"WIRED": "https://www.wired.com/feed/rss",
    #"Lifehacker": "https://lifehacker.com/rss",
    
    # Science
    "SciAmerica": "http://rss.sciam.com/ScientificAmerican-Global",
    
    # Entertainment
    "RollinStone": "http://www.rollingstone.com/rss",
    #"Billboard": "https://billboard.com/feed",
    
    # Business
    "Forbes": "https://www.forbes.com/business/",
    #"FoolWatch": "https://www.fool.com/feeds/foolwatch/default.aspx",
    # "HBR": "http://feeds.hbr.org/harvardbusiness",
    
    # Other
    #"Buzzfeed": "https://www.buzzfeed.com/index.xml",
    "ESPN": "https://www.espn.com/espn/rss/news",
    "FeedBurner": "http://feeds.feedburner.com/seriouseats/recipes",
}


def categorize(feed_name):
    # Categorize each feed into a type
    categories = {
        "Tech": [
            "ArsTechnica",
            "Engadget",
            "Gizmodo",
            "Lifehacker",
            "Mashable",
            "TechCrunch",
            "The Verge",
            "WIRED",
        ],
        "News": ["BBC", "CNN", "HuffPost", "HuffPostUS"],
        "Science": ["NASA", "SciAmerica"],
        "Entertainment": ["Billboard", "RollinStone"],
        "Business": ["FoolWatch", "Forbes", "HBR"],
        "Other": ["Buzzfeed", "ESPN", "FeedBurner"],
    }

    for category, feeds in categories.items():
        if feed_name in feeds:
            return category
    return "Other"


# Sort the dictionary by type and then alphabetically within each type
sorted_rss_feeds = dict(
    sorted(rss_feeds.items(), key=lambda x: (categorize(x[0]), x[0]))
)

print(sorted_rss_feeds)

# Constants for scrolling
PADDING = 10
HOLD_TIME = 2  # seconds
STEP_TIME = 0.025  # seconds

# States for scrolling
STATE_PRE_SCROLL = 0
STATE_SCROLLING = 1
STATE_POST_SCROLL = 2

state = STATE_PRE_SCROLL
shift = 0
last_scroll_time = time.ticks_ms()

# Define a variable to keep track of the current RSS source at the global scope
current_source_index = 0


def connect_to_wifi():
    try:
        from secrets import WIFI_SSID, WIFI_PASSWORD
    except ImportError:
        print("Create secrets.py with your WiFi credentials")
        return False

    print("Connecting to WiFi...")
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        print("Already connected to WiFi.")
        return True

    wlan.active(True)
    wlan.config(pm=0xA11140)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(0.2)

    if wlan.isconnected():
        print("Connected to WiFi successfully.")
    else:
        print("Failed to connect to WiFi.")
    return wlan.isconnected()


def fetch_rss_data(url, filename="rss_data.xml"):
    try:
        response = requests.get(url)
        with open(filename, "w") as f:
            f.write(response.text)
            print(f"RSS data written to {filename}.")
        response.close()

        # Check if the file exists and has content
        file_stat = os.stat(filename)
        if file_stat[6] == 0:  # Check if the file size is 0
            print(f"Error: Unable to save RSS data from {url}. Possible space issue.")
            exit()  # Exit the program

        print(f"Successfully fetched and saved RSS data from {url} to {filename}")
    except Exception as e:
        print(f"Error fetching RSS data from {url}: {e}")


def parse_rss_data_from_file(filename="rss_data.xml"):
    items = []
    try:
        with open(filename, "r") as f:
            data = f.read()

        # Check if it's an Atom feed
        if "<feed" in data and "<entry>" in data:
            split_data = data.split("<entry>")
            tag_start = "<content"
            tag_end = "</content>"
        else:  # Assume it's an RSS feed
            split_data = data.split("<item>")
            tag_start = "<description>"
            tag_end = "</description>"

        for item in split_data[1:]:
            title = extract_between(item, "<title>", "</title>")

            # Extract content/description
            description = extract_between(item, tag_start, tag_end)
            if tag_start == "<content":
                # Since <content> can have attributes, we need to further clean the content
                description = re.sub(
                    r"^.*?>", "", description
                )  # Remove everything before the closing '>'

            items.append((title, description))
    except Exception as e:
        print(f"Error parsing RSS data from file: {e}")
    return items


def extract_between(data, start, end):
    start_index = data.find(start) + len(start)
    end_index = data.find(end)
    return data[start_index:end_index].strip()


def cleanup_text(text):
    # Remove CDATA sections
    text = remove_cdata(text)

    # Replace HTML entities
    text = replace_html_entities(text)

    # Remove HTML tags
    text = remove_html_tags(text)

    # Clean up whitespace
    text = clean_whitespace(text)

    # Replace curly single quotes with straight single quotes
    text = text.replace("‘", "'").replace("’", "'")

    return text


def remove_cdata(text):
    cdata_pattern = r"<!\[CDATA\[(.*?)\]\]>"
    return re.sub(cdata_pattern, r"\1", text)


def replace_html_entities(text):
    replacements = {
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;mdash;": "—",
        "&amp;ndash;": "–",
        "&amp;": "&",
        "&quot;": '"',
        "&#39;": "'",
        "&ldquo;": '"',
        "&rdquo;": '"',
        "&lsquo;": "'",
        "&rsquo;": "'",
        "&hellip;": "...",
        "&euro;": ":Euro:",
        "&pound;": ":Pound:",
        "&yen;": ":Yen:",
        "&#8216;": "'",
        "&#8217;": "'",
        "&#038;": "&",
        "&#8230;": "...",
    }

    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)
    return text


def remove_html_tags(text):
    """Remove HTML tags from a given text using a loop-based approach."""
    while "<" in text and ">" in text:
        start = text.find("<")
        end = text.find(">")
        if start < end:
            text = text[:start] + text[end + 1 :]
        else:
            break
    return text


def clean_whitespace(text):
    """Remove excessive whitespace from a given text."""
    text = re.sub(
        r"\s+", " ", text
    )  # Replace multiple spaces, newlines, and tabs with a single space
    return text.strip()  # Remove leading and trailing whitespace


def get_font_height(font_name):
    font_heights = {
        "bitmap6": 6,
        "bitmap8": 8,
        "bitmap14_outline": 14,
        "sans": 20,  # These values are estimates for the Hershey fonts
        "gothic": 20,
        "cursive": 20,
        "serif_italic": 20,
        "serif": 20,
    }
    return font_heights.get(font_name, 8)  # Default to 8 if font is not recognized


def outline_text(
    text,
    x,
    y,
    scale=1,
    font_name="bitmap8",
    text_color=TEXT_COLOR,
    outline_color=OUTLINE_COLOR,
    bg_color=BACKGROUND_COLOR,
):
    """Draws the text with an outline."""
    # Set the font
    display.set_font(font_name)

    # Get the estimated height of the font
    text_height = get_font_height(font_name)

    # Adjust y for vertical centering based on the estimated height
    y_centered = int(HEIGHT / 2 - (scale * text_height) / 2) + 1

    # Draw the text in the outline color, offset by one pixel in each direction
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    display.set_pen(outline_color)
    for dx, dy in offsets:
        display.text(text, x + dx, y_centered + dy, -1, scale)

    # Draw the text in the main color at the original position
    display.set_pen(text_color)
    display.text(text, x, y_centered, -1, scale)


def display_text(
    text,
    centered=False,
    duration=None,
    outline=False,
    font_name="bitmap8",
    text_color=TEXT_COLOR,
    outline_color=OUTLINE_COLOR,
    bg_color=BACKGROUND_COLOR,
):
    global state, shift, last_scroll_time

    # Set the font
    display.set_font(font_name)

    # Get the estimated height of the font
    text_height = get_font_height(font_name)

    # Adjusting the y coordinate for vertical centering based on the estimated height
    y = (HEIGHT - text_height) // 2 + 1

    if centered:
        # Clear the display with the desired background color
        display.set_pen(bg_color)
        display.clear()

        w = display.measure_text(text, 1)
        x = int(WIDTH / 2 - w / 2 + 1)
        display.set_pen(text_color)
        if outline:
            outline_text(text, x, y, 1, font_name, text_color, outline_color, bg_color)
        else:
            display.text(text, x, y, -1, 1)
        gu.update(display)
        if duration:
            time.sleep(duration)
        return

    # Scrolling logic
    time_ms = time.ticks_ms()

    if state == STATE_PRE_SCROLL:
        shift = WIDTH  # Start off the screen to the right
        state = STATE_SCROLLING
        last_scroll_time = time_ms

    elif state == STATE_SCROLLING:
        if time_ms - last_scroll_time > STEP_TIME * 1000:
            shift -= SCROLL_SPEED
            msg_width = display.measure_text(text, 1)
            # Adjusting the condition to ensure all words are cleared from the display
            if shift <= -msg_width - PADDING:
                state = STATE_POST_SCROLL
            last_scroll_time = time_ms
            display.clear()
            display.set_pen(bg_color)
            display.clear()
            if outline:
                outline_text(
                    text,
                    PADDING + shift,
                    y,
                    1,
                    font_name,
                    text_color,
                    outline_color,
                    bg_color,
                )
            else:
                display.set_pen(text_color)
                display.text(text, PADDING + shift, y, -1, 1)
            gu.update(display)
            time.sleep(STEP_TIME)
            check_buttons()  # Check for button presses during scrolling

    elif state == STATE_POST_SCROLL:
        if time_ms - last_scroll_time > HOLD_TIME * 1000:
            state = STATE_PRE_SCROLL
            return True  # Return True to indicate that scrolling is done
    return False  # Return False to indicate that scrolling is still in progress


# Define a custom exception for switching sources
class SwitchSourceException(Exception):
    pass


def check_buttons():
    global current_source_index  # Declare the variable as global inside the function

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        print("Brightness up button pressed.")
        gu.adjust_brightness(+0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        print("Brightness down button pressed.")
        gu.adjust_brightness(-0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_VOLUME_UP):
        print("Volume up button pressed. Switching to next RSS feed.")
        current_source_index = (current_source_index + 1) % len(rss_feeds)
        display.set_pen(BACKGROUND_COLOR)  # Set pen to background color
        display.clear()  # Clear the display
        gu.update(display)
        raise SwitchSourceException

    if gu.is_pressed(GalacticUnicorn.SWITCH_VOLUME_DOWN):
        print("Volume down button pressed. Switching to previous RSS feed.")
        current_source_index = (current_source_index - 1 + len(rss_feeds)) % len(
            rss_feeds
        )
        display.set_pen(BACKGROUND_COLOR)  # Set pen to background color
        display.clear()  # Clear the display
        gu.update(display)
        raise SwitchSourceException


# Connect to WiFi
wifi_available = connect_to_wifi()
if not wifi_available:
    print("Failed to connect to WiFi. Exiting.")
    exit

# Main loop
while True:
    source, url = list(rss_feeds.items())[current_source_index]
    switch_source = False  # Flag to determine if we should switch sources

    try:
        # Display the RSS source name
        print(f"Displaying source: {source}")
        display_text(
            source,
            centered=True,
            duration=2,
            outline=source_outline,
            font_name=source_font_name,
            text_color=source_text_color,
            outline_color=source_outline_color,
            bg_color=source_bg_color,
        )

        # Fetch and parse the RSS data
        print(f"Fetching RSS data from: {url}")
        data = fetch_rss_data(url)
        gc.collect()
        # items = parse_rss_data(data)
        items = parse_rss_data_from_file()
        gc.collect()

        # Display each title and description
        for title, description in items:
            print("Raw title:", title)
            print("Raw description:", description)

            # Step-by-step cleaning process:
            # print("\n--- Cleaning Process ---")
            title = cleanup_text(title)
            description = cleanup_text(description)
            gc.collect()

            print(f"Displaying title: {title}")
            text_color = display.create_pen(255, 255, 255)
            outline_color = display.create_pen(64, 64, 127)
            bg_color = display.create_pen(32, 32, 64)

            while not display_text(
                title,
                outline=title_outline,
                font_name=title_font_name,
                text_color=title_text_color,
                outline_color=title_outline_color,
                bg_color=title_bg_color,
            ):
                pass

            print(f"Displaying description: {description}")
            text_color = display.create_pen(255, 255, 255)
            outline_color = display.create_pen(64, 64, 127)
            bg_color = display.create_pen(32, 32, 64)

            while not display_text(
                description,
                outline=description_outline,
                font_name=description_font_name,
                text_color=description_text_color,
                outline_color=description_outline_color,
                bg_color=description_bg_color,
            ):
                pass

            gc.collect()

        # Check for button presses
        check_buttons()

    except SwitchSourceException:
        switch_source = True

    # If the switch_source flag is set, move to the next source
    if switch_source:
        current_source_index = (current_source_index + 1) % len(rss_feeds)
    else:
        # If all items for the current source have been displayed, move to the next source
        current_source_index = (current_source_index + 1) % len(rss_feeds)

    display.set_pen(BACKGROUND_COLOR)  # Set pen to background color
    display.clear()  # Clear the display

# Cookie Extractor & API Config Builder

A desktop utility built with Python and Tkinter that automates the process of logging into target web panels using Selenium, extracting session cookies, and generating formatted API configuration headers.

## Features

- **Automated Login**: Automatically locates login fields, inputs credentials, and handles authentication.
- **Cookie Extraction**: Securely pulls session cookies via browser execution scripts.
- **API Configuration Formatter**: Automatically structures extracted cookies and CSRF tokens into ready-to-use Python dictionary headers for API requests.
- **Local Secure Configuration**: Saves user preferences locally in a hidden system directory (`.cookie_extractor_data`).
- **User-Friendly GUI**: Built-in status logs, progress bar, password visibility toggle, and full text-widget editing support (Copy/Paste/Select All).

## Prerequisites

Make sure you have Python 3.x installed on your system. You will also need the following Python libraries:

```bash
pip install selenium webdriver-manager
```

*(Note: This application utilizes Firefox and automatically manages GeckoDriver via `webdriver-manager`).*

## Usage

1. Clone or download the repository.
2. Run the script:
   ```bash
   python cookie_extractor.py
   ```
3. Enter your target URL, Username, and Password in the GUI.
4. Click **"Start Automation & Extract Cookies"**.
5. Once complete, copy the generated API headers from the output box for your backend or automation scripts.

## License

This project is open-source and available under the [MIT License](LICENSE).

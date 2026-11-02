import json
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".cookie_extractor_data")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.dat")

def make_text_widget_editable(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_separator()
    menu.add_command(label="Select All", command=lambda: widget.event_generate("<<SelectAll>>"))

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    if widget.tk.call("tk", "windowingsystem") == "aqua":
        widget.bind("<2>", show_menu)
        widget.bind("<Control-2>", show_menu)
    else:
        widget.bind("<Button-3>", show_menu)

    def handle_ctrl_a(event):
        widget.tag_add("sel", "1.0", "end-1c")
        return "break"

    widget.bind("<Control-a>", handle_ctrl_a)
    widget.bind("<Control-A>", handle_ctrl_a)

class CookieExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cookie Extractor & API Config Builder")
        self.root.geometry("750x700")
        self.root.minsize(650, 620)

        self.setup_ui()
        self.load_config()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        cred_frame = ttk.LabelFrame(self.root, text=" Credentials & Target URL ", padding=10)
        cred_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(cred_frame, text="Target URL:").grid(row=0, column=0, sticky="w", pady=5)
        self.url_entry = ttk.Entry(cred_frame, width=65)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        make_text_widget_editable(self.url_entry)

        ttk.Label(cred_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(cred_frame, width=30)
        self.user_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        make_text_widget_editable(self.user_entry)

        ttk.Label(cred_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.pass_entry = ttk.Entry(cred_frame, width=30, show="*")
        self.pass_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        make_text_widget_editable(self.pass_entry)

        self.show_pass_var = tk.BooleanVar(value=False)
        self.show_pass_chk = ttk.Checkbutton(
            cred_frame, text="Show Password", variable=self.show_pass_var, command=self.toggle_password
        )
        self.show_pass_chk.grid(row=2, column=2, sticky="w", padx=5, pady=5)

        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=15, pady=5)

        self.start_btn = ttk.Button(
            action_frame, text="Start Automation & Extract Cookies", command=self.start_thread
        )
        self.start_btn.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(action_frame, orient="horizontal", length=350, mode="determinate")
        self.progress.pack(side="right", padx=5)

        log_frame = ttk.LabelFrame(self.root, text=" Execution Logs ", padding=10)
        log_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.log_box = tk.Text(log_frame, height=6, wrap="word", bg="#f9f9f9")
        self.log_box.pack(side="left", fill="both", expand=True)

        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_box.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=log_scroll.set)
        make_text_widget_editable(self.log_box)

        output_frame = ttk.LabelFrame(self.root, text=" Final Output (Ready to Copy) ", padding=10)
        output_frame.pack(fill="both", expand=True, padx=15, pady=5)

        out_top_bar = ttk.Frame(output_frame)
        out_top_bar.pack(fill="x", pady=(0, 5))

        self.copy_btn = ttk.Button(out_top_bar, text="📋 Copy Output", command=self.copy_output_text)
        self.copy_btn.pack(side="left")

        self.output_box = tk.Text(output_frame, height=6, wrap="word", bg="#1e1e1e", fg="#00ff00")
        self.output_box.pack(side="left", fill="both", expand=True)

        out_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_box.yview)
        out_scroll.pack(side="right", fill="y")
        self.output_box.configure(yscrollcommand=out_scroll.set)
        make_text_widget_editable(self.output_box)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def copy_output_text(self):
        text_to_copy = self.output_box.get("1.0", "end-1c").strip()
        if text_to_copy:
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            messagebox.showinfo("Success", "Output copied to clipboard successfully!")
        else:
            messagebox.showwarning("Warning", "No content available to copy!")

    def load_config(self):
        default_url = "https://your-target-website.com/login/"
        default_user = ""
        default_pass = ""

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_url = data.get("url", default_url)
                    default_user = data.get("username", default_user)
                    default_pass = data.get("password", default_pass)
            except Exception:
                pass

        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, default_url)
        self.user_entry.delete(0, "end")
        self.user_entry.insert(0, default_user)
        self.pass_entry.delete(0, "end")
        self.pass_entry.insert(0, default_pass)

    def save_config(self):
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
            data = {
                "url": self.url_entry.get().strip(),
                "username": self.user_entry.get().strip(),
                "password": self.pass_entry.get().strip(),
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def on_close(self):
        self.save_config()
        self.root.destroy()

    def log(self, message):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see("end")

    def start_thread(self):
        self.start_btn.config(state="disabled")
        self.output_box.delete("1.0", "end")
        self.progress["value"] = 0
        threading.Thread(target=self.run_automation, daemon=True).start()

    def run_automation(self):
        driver = None
        try:
            self.log("Preparing Firefox browser...")
            self.progress["value"] = 10
            options = webdriver.FirefoxOptions()
            # options.add_argument("--headless")

            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            self.progress["value"] = 25
            self.log("Browser launched successfully.")

            target_url = self.url_entry.get().strip()
            username = self.user_entry.get().strip()
            password = self.pass_entry.get().strip()

            self.log(f"Navigating to URL: {target_url}")
            driver.get(target_url)
            self.progress["value"] = 40
            time.sleep(3)

            self.log("Checking authentication state and login fields...")
            try:
                user_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' or contains(@name, 'user') or contains(@name, 'email') or contains(@name, 'phone')]"))
                )
                pass_input = driver.find_element(By.XPATH, "//input[@type='password' or contains(@name, 'pass')]")

                self.log("Entering credentials...")
                user_input.clear()
                user_input.send_keys(username)
                pass_input.clear()
                pass_input.send_keys(password)

                login_btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(text(), 'Login') or contains(@class, 'login')]")
                login_btn.click()
                self.progress["value"] = 60
                self.log("Login form submitted, loading panel...")
                time.sleep(5)
            except Exception:
                self.log("Already logged in or fields structure differs. Checking current page...")

            driver.get(target_url)
            self.progress["value"] = 80
            time.sleep(3)

            self.log("Extracting cookies using document.cookie...")
            raw_cookies = driver.execute_script("return document.cookie;")

            if not raw_cookies:
                raise Exception("No cookies found from the browser!")

            self.log("Cookies extracted successfully.")

            csrf_token = ""
            for item in raw_cookies.split(";"):
                if "CSRF-TOKEN" in item:
                    csrf_token = item.split("=")[1].strip()

            base_url_api = target_url.replace("/shop/products/", "/api/shop/product")

            formatted_output = f"""BASE_URL = "{base_url_api}"

API_HEADERS = {{
    "Authorization": "Bearer YOUR_TOKEN_HERE",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRF-TOKEN": "{csrf_token}",
    "Cookie": "{raw_cookies}"
}}"""

            self.output_box.insert("1.0", formatted_output)
            self.progress["value"] = 100
            self.log("Operation completed successfully! Output is ready to copy.")
            messagebox.showinfo("Success", "Cookies extracted and formatted successfully!")

        except Exception as e:
            self.log(f"Error during execution: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            if driver:
                try:
                    driver.quit()
                    self.log("Browser closed.")
                except:
                    pass
            self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CookieExtractorApp(root)
    root.mainloop()

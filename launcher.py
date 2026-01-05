"""
Restaurant Finder - GUI Launcher
Easy-to-use launcher for non-technical users
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
import os
import sys
import subprocess
import time
from pathlib import Path


class RestaurantFinderLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Finder - Launcher")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Server process
        self.server_process = None
        self.server_running = False

        # Paths
        self.project_dir = Path(__file__).parent
        self.env_file = self.project_dir / '.env'
        self.venv_python = self._get_venv_python()

        # Setup UI
        self._create_ui()

        # Check initial setup
        self.root.after(100, self._check_setup)

    def _get_venv_python(self):
        """Get path to virtual environment Python"""
        if sys.platform == 'win32':
            return self.project_dir / 'venv' / 'Scripts' / 'python.exe'
        else:
            return self.project_dir / 'venv' / 'bin' / 'python'

    def _create_ui(self):
        """Create the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#0d6efd', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Restaurant Finder",
            font=('Arial', 24, 'bold'),
            bg='#0d6efd',
            fg='white'
        )
        title_label.pack(pady=20)

        # Main content frame
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Status section
        status_frame = tk.LabelFrame(content_frame, text="Status", padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = tk.Label(
            status_frame,
            text="● Server Stopped",
            font=('Arial', 12),
            fg='red'
        )
        self.status_label.pack()

        # API Key status section
        api_frame = tk.LabelFrame(content_frame, text="API Key Configuration", padx=10, pady=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))

        self.api_status_label = tk.Label(
            api_frame,
            text="Checking API key...",
            font=('Arial', 10),
            fg='#666'
        )
        self.api_status_label.pack(pady=5)

        tk.Label(
            api_frame,
            text="API key is stored in the .env file for security.",
            font=('Arial', 9),
            fg='#666'
        ).pack()

        tk.Button(
            api_frame,
            text="Open Google Cloud Console",
            command=lambda: webbrowser.open('https://console.cloud.google.com/'),
            font=('Arial', 9)
        ).pack(pady=5)

        # Server control section
        control_frame = tk.LabelFrame(content_frame, text="Server Control", padx=10, pady=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        button_frame = tk.Frame(control_frame)
        button_frame.pack()

        self.start_button = tk.Button(
            button_frame,
            text="Start Server",
            command=self._start_server,
            bg='#0d6efd',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
            height=2
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="Stop Server",
            command=self._stop_server,
            bg='#dc3545',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.open_browser_button = tk.Button(
            control_frame,
            text="Open in Browser",
            command=self._open_browser,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        self.open_browser_button.pack(pady=(10, 0))

        # Log section
        log_frame = tk.LabelFrame(content_frame, text="Server Log", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=('Courier', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Info section
        info_frame = tk.Frame(content_frame)
        info_frame.pack(fill=tk.X)

        tk.Label(
            info_frame,
            text="ℹ️ The app will open automatically at http://localhost:5000",
            font=('Arial', 9),
            fg='#666'
        ).pack()

    def _check_setup(self):
        """Check if setup is complete"""
        # Check for virtual environment
        if not self.venv_python.exists():
            self._log("⚠️ Virtual environment not found. Please run setup first.")
            self._log("Run: python -m venv venv")
            self._log("Then: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")
            self._log("Then: pip install -r requirements.txt")
            messagebox.showwarning(
                "Setup Required",
                "Virtual environment not found.\n\n"
                "Please run:\n"
                "1. python -m venv venv\n"
                "2. venv\\Scripts\\activate\n"
                "3. pip install -r requirements.txt"
            )
        else:
            self._log("✓ Virtual environment found")

        # Check for API key
        if not self._check_api_key():
            self._log("[WARNING] Google API Key not configured in .env file")
            self.api_status_label.config(text="⚠ API Key NOT configured", fg='red')
            messagebox.showwarning(
                "API Key Required",
                "Please configure your Google Places API Key in the .env file.\n\n"
                "1. Copy .env.example to .env\n"
                "2. Edit .env and add your API key\n"
                "3. Restart this launcher\n\n"
                "Click 'Open Google Cloud Console' to get an API key."
            )
        else:
            self._log("[OK] API Key configured")
            self.api_status_label.config(text="✓ API Key configured", fg='green')

    def _check_api_key(self):
        """Check if API key is configured in .env file"""
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_PLACES_API_KEY='):
                            key = line.split('=', 1)[1].strip()
                            if key and key != 'your_api_key_here':
                                return True
            except Exception as e:
                self._log(f"Error checking API key: {e}")
        return False

    def _start_server(self):
        """Start the Flask server"""
        if self.server_running:
            return

        # Check for API key
        if not self._check_api_key():
            messagebox.showerror(
                "API Key Required",
                "Please configure your API key in the .env file before starting the server.\n\n"
                "See the API Key Configuration section above for instructions."
            )
            return

        # Check for venv
        if not self.venv_python.exists():
            messagebox.showerror(
                "Setup Required",
                "Virtual environment not found. Please complete setup first."
            )
            return

        self._log("Starting server...")

        try:
            # Start server in separate thread
            thread = threading.Thread(target=self._run_server, daemon=True)
            thread.start()

            # Update UI
            self.server_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.open_browser_button.config(state=tk.NORMAL)
            self.status_label.config(text="● Server Running", fg='green')

            # Wait a moment then open browser
            self.root.after(2000, self._open_browser)

        except Exception as e:
            self._log(f"❌ Error starting server: {e}")
            messagebox.showerror("Error", f"Failed to start server:\n{e}")

    def _run_server(self):
        """Run the Flask server (in separate thread)"""
        try:
            # Change to project directory
            os.chdir(self.project_dir)

            # Start Flask server
            if sys.platform == 'win32':
                self.server_process = subprocess.Popen(
                    [str(self.venv_python), 'run.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.server_process = subprocess.Popen(
                    [str(self.venv_python), 'run.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

            # Read output
            for line in self.server_process.stdout:
                self._log(line.strip())

        except Exception as e:
            self._log(f"❌ Server error: {e}")
            self.server_running = False
            self.root.after(0, self._update_ui_stopped)

    def _stop_server(self):
        """Stop the Flask server"""
        if not self.server_running:
            return

        self._log("Stopping server...")

        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)

            self.server_running = False
            self._update_ui_stopped()
            self._log("✓ Server stopped")

        except Exception as e:
            self._log(f"❌ Error stopping server: {e}")
            messagebox.showerror("Error", f"Failed to stop server:\n{e}")

    def _update_ui_stopped(self):
        """Update UI when server stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.open_browser_button.config(state=tk.DISABLED)
        self.status_label.config(text="● Server Stopped", fg='red')

    def _open_browser(self):
        """Open the app in web browser"""
        if self.server_running:
            self._log("Opening browser...")
            webbrowser.open('http://localhost:5000')

    def _log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def on_closing(self):
        """Handle window closing"""
        if self.server_running:
            if messagebox.askokcancel("Quit", "Server is running. Stop server and quit?"):
                self._stop_server()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = RestaurantFinderLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()

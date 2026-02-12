"""
Peloton 2 Garmin Sync - Standalone Fluent Design App
Automatically syncs Peloton workouts to Garmin Connect with MFA support
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sys
import os
from datetime import datetime
from pathlib import Path
import json
import webbrowser
import requests

# Fluent Design Colors
FLUENT_DARK_BG = "#202020"
FLUENT_CARD_BG = "#2d2d2d"
FLUENT_HOVER = "#3d3d3d"
FLUENT_ACCENT = "#0078d4"
FLUENT_ACCENT_HOVER = "#106ebe"
FLUENT_TEXT = "#ffffff"
FLUENT_TEXT_SECONDARY = "#b0b0b0"
FLUENT_SUCCESS = "#107c10"
FLUENT_ERROR = "#d13438"
FLUENT_WARNING = "#ff8c00"


class PelotonBearerAuth:
    """Peloton API authentication using bearer token"""
    
    def __init__(self):
        self.bearer_token = None
        self.user_id = None
        self.session = requests.Session()
    
    def set_bearer_token(self, token):
        """Set the bearer token for API authentication"""
        self.bearer_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'peloton-platform': 'web',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Get user ID
        self.user_id = self._get_user_id()
        return bool(self.user_id)
    
    def _get_user_id(self):
        """Get user ID using bearer token"""
        try:
            response = self.session.get('https://api.onepeloton.com/api/me')
            if response.status_code == 200:
                data = response.json()
                return data.get('id')
            return None
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None
    
    def get_workouts(self, limit=20):
        """Fetch recent workouts"""
        if not self.bearer_token or not self.user_id:
            raise Exception("Not authenticated")
        
        try:
            url = f"https://api.onepeloton.com/api/user/{self.user_id}/workouts"
            params = {
                'joins': 'ride,ride.instructor',
                'limit': limit,
                'page': 0
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except Exception as e:
            print(f"Error fetching workouts: {e}")
            return []
    
    def get_workout_details(self, workout_id):
        """Fetch detailed workout performance data"""
        if not self.bearer_token:
            raise Exception("Not authenticated")
        
        try:
            url = f"https://api.onepeloton.com/api/workout/{workout_id}/performance_graph"
            params = {'every_n': 5}
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching workout details: {e}")
            return None


class FluentButton(tk.Canvas):
    """Fluent Design button with hover effects"""
    
    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.text = text
        self.command = command
        self.bg_color = kwargs.get('bg', FLUENT_ACCENT)
        self.hover_color = kwargs.get('hover', FLUENT_ACCENT_HOVER)
        self.text_color = kwargs.get('fg', FLUENT_TEXT)
        self.is_hovered = False
        
        self.configure(
            bg=self.bg_color,
            highlightthickness=0,
            relief='flat'
        )
        
        # Create text
        self.text_id = self.create_text(
            self.winfo_reqwidth() // 2,
            self.winfo_reqheight() // 2,
            text=self.text,
            fill=self.text_color,
            font=('Segoe UI', 10)
        )
        
        # Bind events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def on_enter(self, e):
        self.configure(bg=self.hover_color)
        
    def on_leave(self, e):
        self.configure(bg=self.bg_color)
        
    def on_click(self, e):
        if self.command:
            self.command()


class PelotonGarminSyncApp:
    """Main application with Fluent Design UI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Peloton 2 Garmin Sync")
        self.root.geometry("900x700")
        self.root.configure(bg=FLUENT_DARK_BG)
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'P2GIcon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Paths
        self.config_dir = Path.home() / '.peloton_garmin_sync'
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self.garmin_tokens_dir = self.config_dir / 'garmin_tokens'
        self.garmin_tokens_dir.mkdir(exist_ok=True)
        
        # State
        self.peloton_auth = None
        self.garmin_handler = None
        self.workout_data = []
        self.selected_workouts = []
        
        # Load config
        self.config = self.load_config()
        
        # Setup UI
        self.setup_ui()
        
        # ALWAYS run auto_login to check credentials
        # (It will show what's missing in the status log)
        self.root.after(500, self.auto_login)
    
    def load_config(self):
        """Load saved configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_ui(self):
        """Setup Fluent Design UI"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=FLUENT_CARD_BG, height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Peloton → Garmin",
            font=('Segoe UI', 20, 'bold'),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Automatic Workout Sync",
            font=('Segoe UI', 10),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT_SECONDARY
        )
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=15)
        
        # Connection status indicators
        self.status_indicators = tk.Frame(title_frame, bg=FLUENT_CARD_BG)
        self.status_indicators.pack(side=tk.RIGHT, padx=20)
        
        # Peloton status
        self.peloton_status = tk.Label(
            self.status_indicators,
            text="Peloton: ○",
            font=('Segoe UI', 9),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT_SECONDARY
        )
        self.peloton_status.pack(side=tk.LEFT, padx=10)
        
        # Garmin status
        self.garmin_status = tk.Label(
            self.status_indicators,
            text="Garmin: ○",
            font=('Segoe UI', 9),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT_SECONDARY
        )
        self.garmin_status.pack(side=tk.LEFT, padx=10)
        
        # Main container
        main_container = tk.Frame(self.root, bg=FLUENT_DARK_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Status card
        status_card = tk.Frame(main_container, bg=FLUENT_CARD_BG)
        status_card.pack(fill=tk.X, pady=(0, 15))
        
        status_label = tk.Label(
            status_card,
            text="Status",
            font=('Segoe UI', 12, 'bold'),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        )
        status_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        self.status_text = tk.Text(
            status_card,
            height=4,
            font=('Consolas', 9),
            bg=FLUENT_DARK_BG,
            fg=FLUENT_TEXT_SECONDARY,
            relief='flat',
            wrap=tk.WORD,
            state='disabled'
        )
        self.status_text.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Workouts card
        workouts_card = tk.Frame(main_container, bg=FLUENT_CARD_BG)
        workouts_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        workouts_header = tk.Frame(workouts_card, bg=FLUENT_CARD_BG)
        workouts_header.pack(fill=tk.X, padx=15, pady=15)
        
        workouts_label = tk.Label(
            workouts_header,
            text="Recent Workouts",
            font=('Segoe UI', 12, 'bold'),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        )
        workouts_label.pack(side=tk.LEFT)
        
        refresh_btn = tk.Button(
            workouts_header,
            text="📥 Fetch Workouts",
            font=('Segoe UI', 9),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=15,
            pady=5,
            command=self.fetch_workouts
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Treeview with Fluent styling
        tree_frame = tk.Frame(workouts_card, bg=FLUENT_CARD_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(tree_frame, bg=FLUENT_CARD_BG)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.workout_tree = ttk.Treeview(
            tree_frame,
            columns=('select', 'date', 'workout', 'duration', 'calories'),
            show='headings',
            selectmode='none',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.workout_tree.yview)
        
        # Define columns
        self.workout_tree.heading('select', text='☐')
        self.workout_tree.heading('date', text='Date')
        self.workout_tree.heading('workout', text='Workout')
        self.workout_tree.heading('duration', text='Duration')
        self.workout_tree.heading('calories', text='Calories')
        
        self.workout_tree.column('select', width=50)
        self.workout_tree.column('date', width=150)
        self.workout_tree.column('workout', width=350)
        self.workout_tree.column('duration', width=100)
        self.workout_tree.column('calories', width=80)
        
        self.workout_tree.pack(fill=tk.BOTH, expand=True)
        self.workout_tree.bind('<Button-1>', self.toggle_selection)
        
        # Action buttons
        action_frame = tk.Frame(main_container, bg=FLUENT_DARK_BG)
        action_frame.pack(fill=tk.X)
        
        sync_btn = tk.Button(
            action_frame,
            text="🔄 Sync to Garmin",
            font=('Segoe UI', 11, 'bold'),
            bg=FLUENT_ACCENT,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=30,
            pady=12,
            command=self.sync_to_garmin
        )
        sync_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = tk.Button(
            action_frame,
            text="📁 Export FIT Files",
            font=('Segoe UI', 11),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=30,
            pady=12,
            command=self.export_fit_files
        )
        export_btn.pack(side=tk.LEFT)
        
        settings_btn = tk.Button(
            action_frame,
            text="⚙ Settings",
            font=('Segoe UI', 11),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=20,
            pady=12,
            command=self.show_settings
        )
        settings_btn.pack(side=tk.RIGHT)
        
        # Initial status
        self.log_status("═" * 50)
        self.log_status("Peloton 2 Garmin Sync - Starting Up")
        self.log_status("═" * 50)
        self.log_status("Ready. Check status below for configuration needs.")
    
    def log_status(self, message):
        """Add message to status log"""
        self.status_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()
    
    def toggle_selection(self, event):
        """Toggle workout selection"""
        region = self.workout_tree.identify('region', event.x, event.y)
        if region == 'cell':
            item = self.workout_tree.identify_row(event.y)
            if item:
                current_values = list(self.workout_tree.item(item, 'values'))
                # Toggle checkbox
                if current_values[0] == '☐':
                    current_values[0] = '☑'
                    if item not in self.selected_workouts:
                        self.selected_workouts.append(item)
                else:
                    current_values[0] = '☐'
                    if item in self.selected_workouts:
                        self.selected_workouts.remove(item)
                
                self.workout_tree.item(item, values=current_values)
    
    def auto_login(self):
        """Automatically login with saved credentials"""
        self.log_status("Checking saved credentials...")
        self.log_status(f"Config file: {self.config_file}")
        self.log_status(f"Config file exists: {self.config_file.exists()}")
        
        if self.config_file.exists():
            self.log_status(f"Config contents: {json.dumps(self.config, indent=2)}")
        else:
            self.log_status("Config file doesn't exist yet - first run")
        
        # Check Peloton
        peloton_token = self.config.get('peloton_bearer_token')
        self.log_status(f"Peloton token in config: {bool(peloton_token)}")
        if peloton_token:
            self.log_status(f"Token starts with: {peloton_token[:20]}..." if len(peloton_token) > 20 else f"Token: {peloton_token}")
        
        if not peloton_token:
            self.log_status("⚠ No Peloton token found. Please configure in Settings.")
            self.peloton_status.config(text="Peloton: ○", fg=FLUENT_TEXT_SECONDARY)
        else:
            # Initialize and test Peloton auth automatically
            self.log_status("Validating Peloton token...")
            self.peloton_auth = PelotonBearerAuth()
            if self.peloton_auth.set_bearer_token(peloton_token):
                self.log_status("✓ Peloton token valid")
                self.peloton_status.config(text="Peloton: ●", fg=FLUENT_SUCCESS)
            else:
                self.log_status("✗ Peloton token invalid - please update in Settings")
                self.peloton_status.config(text="Peloton: ○", fg=FLUENT_ERROR)
                self.peloton_auth = None
        
        # Check Garmin tokens
        oauth1_path = self.garmin_tokens_dir / 'oauth1_token'
        oauth2_path = self.garmin_tokens_dir / 'oauth2_token'
        garmin_email = self.config.get('garmin_email')
        
        self.log_status(f"Checking Garmin tokens in: {self.garmin_tokens_dir}")
        self.log_status(f"OAuth1 exists: {oauth1_path.exists()}")
        self.log_status(f"OAuth2 exists: {oauth2_path.exists()}")
        self.log_status(f"Saved email: {garmin_email}")
        
        if oauth1_path.exists() and oauth2_path.exists() and garmin_email:
            self.log_status("✓ Garmin tokens found, attempting to resume session...")
            
            try:
                from garmin_handler_mfa import GarminDataHandler
                self.log_status("Imported GarminDataHandler successfully")
                
                # Initialize handler
                self.log_status(f"Creating handler with email: {garmin_email}")
                self.garmin_handler = GarminDataHandler(
                    email=garmin_email,
                    password='',  # Not needed for token resume
                    token_store_path=str(self.garmin_tokens_dir)
                )
                self.log_status("Handler created successfully")
                
                # Try to authenticate with tokens
                self.log_status("Calling authenticate()...")
                result = self.garmin_handler.authenticate(mfa_callback=None)
                
                self.log_status(f"Authenticate returned: {result}")
                
                if result and result.get('success'):
                    self.log_status("✓ Garmin session resumed successfully!")
                    self.garmin_status.config(text="Garmin: ●", fg=FLUENT_SUCCESS)
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                    self.log_status(f"✗ Garmin authentication failed: {error_msg}")
                    self.log_status("Tokens may have expired - please login again in Settings")
                    self.garmin_status.config(text="Garmin: ○", fg=FLUENT_WARNING)
                    self.garmin_handler = None
                    
            except ImportError as ie:
                self.log_status(f"✗ Failed to import garmin_handler_mfa: {str(ie)}")
                self.log_status("Make sure garmin_handler_mfa.py is in the same directory")
                self.garmin_status.config(text="Garmin: ○", fg=FLUENT_ERROR)
                self.garmin_handler = None
            except Exception as e:
                import traceback
                self.log_status(f"✗ Exception during Garmin auto-login: {type(e).__name__}: {str(e)}")
                # Show full traceback
                tb_lines = traceback.format_exc().split('\n')
                for line in tb_lines:
                    if line.strip():
                        self.log_status(f"  {line}")
                self.log_status("Please login manually in Settings")
                self.garmin_status.config(text="Garmin: ○", fg=FLUENT_ERROR)
                self.garmin_handler = None
        else:
            missing = []
            if not oauth1_path.exists():
                missing.append("oauth1_token")
            if not oauth2_path.exists():
                missing.append("oauth2_token")
            if not garmin_email:
                missing.append("email")
            
            self.log_status(f"⚠ Garmin login required - missing: {', '.join(missing)}")
            self.log_status("Please login to Garmin in Settings")
            self.garmin_status.config(text="Garmin: ○", fg=FLUENT_TEXT_SECONDARY)
            self.garmin_handler = None
        
        # Auto-fetch workouts if Peloton is configured
        if self.peloton_auth:
            self.root.after(1000, self.fetch_workouts)
        
        # Show configuration summary
        self.log_status("")
        self.log_status("─" * 50)
        self.log_status("Configuration Status:")
        
        peloton_ok = self.peloton_auth is not None
        garmin_ok = self.garmin_handler is not None
        
        if peloton_ok and garmin_ok:
            self.log_status("✓ Peloton: Configured")
            self.log_status("✓ Garmin: Logged in")
            self.log_status("✓ Ready to sync workouts!")
        elif peloton_ok and not garmin_ok:
            self.log_status("✓ Peloton: Configured")
            self.log_status("✗ Garmin: NOT logged in")
            self.log_status("→ Please go to Settings and login to Garmin")
        elif not peloton_ok and garmin_ok:
            self.log_status("✗ Peloton: NOT configured")
            self.log_status("✓ Garmin: Logged in")
            self.log_status("→ Please go to Settings and add Peloton token")
        else:
            self.log_status("✗ Peloton: NOT configured")
            self.log_status("✗ Garmin: NOT logged in")
            self.log_status("→ Please go to Settings to configure both accounts")
        
        self.log_status("─" * 50)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg=FLUENT_CARD_BG)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'P2GIcon.ico')
            if os.path.exists(icon_path):
                settings_window.iconbitmap(icon_path)
        except:
            pass
        
        # Title
        title = tk.Label(
            settings_window,
            text="Settings",
            font=('Segoe UI', 16, 'bold'),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        )
        title.pack(pady=20)
        
        # Peloton section
        peloton_frame = tk.Frame(settings_window, bg=FLUENT_DARK_BG)
        peloton_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            peloton_frame,
            text="Peloton Authentication",
            font=('Segoe UI', 11, 'bold'),
            bg=FLUENT_DARK_BG,
            fg=FLUENT_TEXT
        ).pack(anchor=tk.W, pady=(10, 5))
        
        tk.Label(
            peloton_frame,
            text="Bearer Token (paste from browser):",
            font=('Segoe UI', 9),
            bg=FLUENT_DARK_BG,
            fg=FLUENT_TEXT_SECONDARY
        ).pack(anchor=tk.W)
        
        peloton_token_entry = tk.Entry(
            peloton_frame,
            font=('Consolas', 9),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            width=50
        )
        peloton_token_entry.pack(fill=tk.X, pady=5)
        
        # Pre-fill with saved token
        if self.config.get('peloton_bearer_token'):
            peloton_token_entry.insert(0, self.config['peloton_bearer_token'])
        
        button_frame = tk.Frame(peloton_frame, bg=FLUENT_DARK_BG)
        button_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            button_frame,
            text="Get Token (Opens Browser)",
            font=('Segoe UI', 9),
            bg=FLUENT_ACCENT,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=15,
            pady=8,
            command=lambda: self.get_peloton_token_instructions()
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            button_frame,
            text="Save Token",
            font=('Segoe UI', 9),
            bg=FLUENT_SUCCESS,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=15,
            pady=8,
            command=lambda: self.save_peloton_token(peloton_token_entry)
        ).pack(side=tk.LEFT)
        
        # Garmin section
        garmin_frame = tk.Frame(settings_window, bg=FLUENT_DARK_BG)
        garmin_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            garmin_frame,
            text="Garmin Connect",
            font=('Segoe UI', 11, 'bold'),
            bg=FLUENT_DARK_BG,
            fg=FLUENT_TEXT
        ).pack(anchor=tk.W, pady=(10, 5))
        
        tk.Button(
            garmin_frame,
            text="Login to Garmin (with MFA support)",
            font=('Segoe UI', 9),
            bg=FLUENT_ACCENT,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=15,
            pady=8,
            command=self.login_garmin
        ).pack(anchor=tk.W, pady=5)
        
        # Close button
        tk.Button(
            settings_window,
            text="Close",
            font=('Segoe UI', 10),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=30,
            pady=10,
            command=settings_window.destroy
        ).pack(side=tk.BOTTOM, pady=20)
    
    def get_peloton_token_instructions(self):
        """Show instructions for getting Peloton token"""
        self.log_status("Opening Peloton login page...")
        webbrowser.open('https://members.onepeloton.com/login')
        
        messagebox.showinfo(
            "Get Peloton Token - Easy Method!",
            "Browser opened to Peloton login.\n\n"
            "EASIEST METHOD - Network Tab:\n"
            "1. Press F12 to open Developer Tools\n"
            "2. Click 'Network' tab at the top\n"
            "3. Login to Peloton (if not already)\n"
            "4. In the list, click on 'session'\n"
            "5. Click 'Headers' tab on the right\n"
            "6. Scroll down to 'Authorization' header\n"
            "7. Copy the LONG text after 'Bearer '\n"
            "   (everything after 'Bearer ', not including 'Bearer ')\n"
            "8. Paste in Settings and click Save Token\n\n"
            "The token is the long string starting with 'eyJ...'",
            icon='info'
        )

    
    def save_peloton_token(self, entry_widget):
        """Save and validate Peloton token"""
        token = entry_widget.get().strip()
        
        if not token:
            messagebox.showerror("Error", "Please enter a token")
            return
        
        # Clean token
        token = token.strip('"').strip("'")
        
        # Test the token
        self.log_status("Validating Peloton token...")
        test_auth = PelotonBearerAuth()
        
        if test_auth.set_bearer_token(token):
            # Save token
            self.config['peloton_bearer_token'] = token
            self.save_config()
            
            self.log_status(f"Saving to: {self.config_file}")
            self.log_status(f"Token saved: {token[:20]}...")
            
            # Verify it was saved
            with open(self.config_file, 'r') as f:
                saved_config = json.load(f)
                if saved_config.get('peloton_bearer_token') == token:
                    self.log_status("✓ Verified: Token written to disk successfully")
                else:
                    self.log_status("✗ ERROR: Token not found in saved file!")
            
            # Update main auth
            self.peloton_auth = test_auth
            
            # Update status
            self.peloton_status.config(text="Peloton: ●", fg=FLUENT_SUCCESS)
            self.log_status("✓ Peloton token saved and validated")
            
            messagebox.showinfo("Success", "Token saved! Close and reopen the app to test auto-login.")
        else:
            self.log_status("✗ Invalid Peloton token")
            messagebox.showerror("Invalid Token", "Token validation failed. Please check and try again.")
    
    def get_peloton_token(self, entry_widget):
        """DEPRECATED - keeping for compatibility"""
        self.get_peloton_token_instructions()
    
    def login_garmin(self):
        """Login to Garmin with MFA support"""
        # Show Garmin login dialog
        login_window = tk.Toplevel(self.root)
        login_window.title("Garmin Login")
        login_window.geometry("400x250")
        login_window.configure(bg=FLUENT_CARD_BG)
        login_window.transient(self.root)
        login_window.grab_set()
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'P2GIcon.ico')
            if os.path.exists(icon_path):
                login_window.iconbitmap(icon_path)
        except:
            pass
        
        tk.Label(
            login_window,
            text="Login to Garmin Connect",
            font=('Segoe UI', 14, 'bold'),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        ).pack(pady=20)
        
        # Email
        tk.Label(
            login_window,
            text="Email:",
            font=('Segoe UI', 10),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        ).pack(anchor=tk.W, padx=30)
        
        email_entry = tk.Entry(
            login_window,
            font=('Segoe UI', 10),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            width=40
        )
        email_entry.pack(padx=30, pady=5)
        
        if self.config.get('garmin_email'):
            email_entry.insert(0, self.config['garmin_email'])
        
        # Password
        tk.Label(
            login_window,
            text="Password:",
            font=('Segoe UI', 10),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        ).pack(anchor=tk.W, padx=30, pady=(10, 0))
        
        password_entry = tk.Entry(
            login_window,
            font=('Segoe UI', 10),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            width=40,
            show='*'
        )
        password_entry.pack(padx=30, pady=5)
        
        def do_login():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            
            if not email or not password:
                messagebox.showerror("Error", "Please enter email and password")
                return
            
            self.config['garmin_email'] = email
            self.save_config()
            
            self.log_status(f"Saving Garmin email to: {self.config_file}")
            self.log_status(f"Email: {email}")
            
            # Verify it was saved
            with open(self.config_file, 'r') as f:
                saved_config = json.load(f)
                if saved_config.get('garmin_email') == email:
                    self.log_status("✓ Verified: Email written to disk successfully")
                else:
                    self.log_status("✗ ERROR: Email not found in saved file!")
            
            login_window.destroy()
            
            self.perform_garmin_login(email, password)
        
        tk.Button(
            login_window,
            text="Login",
            font=('Segoe UI', 10, 'bold'),
            bg=FLUENT_ACCENT,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=40,
            pady=10,
            command=do_login
        ).pack(pady=20)
    
    def perform_garmin_login(self, email, password):
        """Perform Garmin login with MFA support"""
        self.log_status("Connecting to Garmin Connect...")
        
        try:
            # Import the Garmin handler with MFA support
            from garmin_handler_mfa import GarminDataHandler
            
            self.log_status("Initializing Garmin authentication...")
            self.garmin_handler = GarminDataHandler(
                email=email,
                password=password,
                token_store_path=str(self.garmin_tokens_dir)
            )
            
            # MFA callback
            def get_mfa_code():
                self.log_status("⏳ Waiting for MFA code...")
                code = self.show_mfa_dialog()
                if code:
                    self.log_status(f"✓ MFA code entered")
                return code
            
            self.log_status("Authenticating with Garmin...")
            result = self.garmin_handler.authenticate(mfa_callback=get_mfa_code)
            
            if result.get('success'):
                self.log_status("✓ Garmin authentication successful!")
                
                # Verify tokens were saved
                oauth1_path = self.garmin_tokens_dir / 'oauth1_token'
                oauth2_path = self.garmin_tokens_dir / 'oauth2_token'
                
                self.log_status(f"Checking token directory: {self.garmin_tokens_dir}")
                self.log_status(f"OAuth1 token exists: {oauth1_path.exists()}")
                self.log_status(f"OAuth2 token exists: {oauth2_path.exists()}")
                
                if oauth1_path.exists() and oauth2_path.exists():
                    self.log_status("✓ OAuth tokens saved successfully to disk!")
                    self.log_status(f"Token directory: {self.garmin_tokens_dir}")
                else:
                    self.log_status("✗ WARNING: OAuth tokens were NOT saved!")
                    self.log_status("Auto-login will not work on next startup")
                
                self.garmin_status.config(text="Garmin: ●", fg=FLUENT_SUCCESS)
                messagebox.showinfo(
                    "Success", 
                    "Successfully logged into Garmin Connect!\n\n"
                    "OAuth tokens saved - you won't need to login again.\n"
                    "Close and reopen the app to test auto-login."
                )
            elif result.get('mfa_required'):
                self.log_status("⏳ MFA code required - check your phone")
                # MFA callback will be triggered
            elif result.get('error'):
                self.log_status(f"✗ Garmin login failed: {result['error']}")
                self.garmin_status.config(text="Garmin: ○", fg=FLUENT_ERROR)
                messagebox.showerror("Login Failed", result['error'])
                
        except Exception as e:
            self.log_status(f"✗ Garmin login error: {str(e)}")
            self.garmin_status.config(text="Garmin: ○", fg=FLUENT_ERROR)
            messagebox.showerror("Error", f"Failed to login:\n\n{str(e)}")
    
    def show_mfa_dialog(self):
        """Show MFA code input dialog"""
        mfa_window = tk.Toplevel(self.root)
        mfa_window.title("Garmin MFA")
        mfa_window.geometry("400x200")
        mfa_window.configure(bg=FLUENT_CARD_BG)
        mfa_window.transient(self.root)
        mfa_window.grab_set()
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'P2GIcon.ico')
            if os.path.exists(icon_path):
                mfa_window.iconbitmap(icon_path)
        except:
            pass
        
        tk.Label(
            mfa_window,
            text="📱 MFA Code Required",
            font=('Segoe UI', 14, 'bold'),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT
        ).pack(pady=20)
        
        tk.Label(
            mfa_window,
            text="Enter the 6-digit code from your phone:",
            font=('Segoe UI', 10),
            bg=FLUENT_CARD_BG,
            fg=FLUENT_TEXT_SECONDARY
        ).pack()
        
        code_entry = tk.Entry(
            mfa_window,
            font=('Segoe UI', 18),
            bg=FLUENT_HOVER,
            fg=FLUENT_TEXT,
            relief='flat',
            width=15,
            justify='center'
        )
        code_entry.pack(pady=15)
        code_entry.focus()
        
        mfa_code = [None]
        
        def submit_code():
            code = code_entry.get().strip()
            if code and len(code) == 6 and code.isdigit():
                mfa_code[0] = code
                mfa_window.destroy()
            else:
                messagebox.showwarning("Invalid Code", "Please enter a 6-digit code")
        
        tk.Button(
            mfa_window,
            text="Submit",
            font=('Segoe UI', 10, 'bold'),
            bg=FLUENT_ACCENT,
            fg=FLUENT_TEXT,
            relief='flat',
            padx=40,
            pady=10,
            command=submit_code
        ).pack()
        
        code_entry.bind('<Return>', lambda e: submit_code())
        
        self.root.wait_window(mfa_window)
        return mfa_code[0]
    
    def fetch_workouts(self):
        """Fetch recent Peloton workouts"""
        if not self.peloton_auth:
            self.log_status("✗ Cannot fetch workouts - Peloton not configured")
            messagebox.showinfo(
                "Peloton Not Configured",
                "To fetch workouts, you need to:\n\n"
                "1. Click Settings (⚙)\n"
                "2. Click 'Get Token (Opens Browser)'\n"
                "3. Follow instructions to copy token from Network tab\n"
                "4. Paste token in the field\n"
                "5. Click 'Save Token'\n\n"
                "Then workouts will load automatically!",
                icon='info'
            )
            return
        
        self.log_status("Fetching workouts from Peloton...")
        
        try:
            # Fetch workouts
            workouts = self.peloton_auth.get_workouts(limit=20)
            self.workout_data = workouts
            
            # Clear tree
            for item in self.workout_tree.get_children():
                self.workout_tree.delete(item)
            
            # Populate tree
            for workout in workouts:
                workout_id = workout.get('id')
                created_at = workout.get('created_at', 0)
                date_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M')
                
                ride = workout.get('ride', {})
                title = ride.get('title', 'Untitled')
                instructor_data = ride.get('instructor', {})
                instructor = instructor_data.get('name', '')
                
                workout_type = ride.get('fitness_discipline', 'Workout').replace('_', ' ').title()
                
                if instructor:
                    display_name = f"{title} - {instructor}"
                else:
                    display_name = title
                
                duration_sec = ride.get('duration', 0)
                duration_min = duration_sec // 60
                
                calories = workout.get('calories', 0)
                
                self.workout_tree.insert('', tk.END, iid=workout_id,
                                       values=('☐', date_str, display_name,
                                              f"{duration_min} min", f"{calories:.0f}"))
            
            self.log_status(f"✓ Loaded {len(workouts)} workouts")
            
        except Exception as e:
            self.log_status(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to fetch workouts:\n\n{str(e)}")
    
    def sync_to_garmin(self):
        """Sync selected workouts to Garmin"""
        if not self.selected_workouts:
            messagebox.showwarning("No Selection", "Please select workouts to sync")
            return
        
        if not self.peloton_auth:
            messagebox.showwarning("Not Configured", "Please configure Peloton in Settings first")
            return
        
        # Check if Garmin handler exists and is authenticated
        if not self.garmin_handler:
            self.log_status("✗ Not logged into Garmin")
            messagebox.showwarning(
                "Not Logged In", 
                "Please login to Garmin in Settings first.\n\n"
                "The app should auto-login on startup if you've logged in before.\n"
                "If auto-login failed, check the status log for details."
            )
            return
        
        # Verify Garmin client exists
        if not hasattr(self.garmin_handler, 'client') or not self.garmin_handler.client:
            self.log_status("✗ Garmin client not initialized")
            messagebox.showwarning(
                "Connection Error",
                "Garmin connection not ready.\n\n"
                "Please try logging in again in Settings."
            )
            return
        
        self.log_status(f"Starting sync of {len(self.selected_workouts)} workouts...")
        
        try:
            import tempfile
            import shutil
            from datetime import datetime
            
            # Use simple TCX converter - bypasses FIT file issues
            from simple_fit_converter import SimpleFitConverter
            converter = SimpleFitConverter(self.peloton_auth, self.garmin_handler.client)
            
            success_count = 0
            failed_workouts = []
            
            for workout_id in self.selected_workouts:
                try:
                    # Find workout data
                    workout = next((w for w in self.workout_data if w['id'] == workout_id), None)
                    if not workout:
                        self.log_status(f"✗ Workout {workout_id} not found in data")
                        continue
                    
                    # Get workout details
                    ride = workout.get('ride', {})
                    title = ride.get('title', 'Peloton Workout')
                    instructor_data = ride.get('instructor', {})
                    instructor = instructor_data.get('name', '')
                    
                    display_name = f"{title} - {instructor}" if instructor else title
                    
                    self.log_status(f"Syncing: {display_name}")
                    
                    # Upload directly using TCX
                    result = converter.sync_workout(workout)
                    
                    if result.get('success'):
                        self.log_status(f"✓ Uploaded: {display_name}")
                        success_count += 1
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        self.log_status(f"✗ Upload failed: {display_name} - {error_msg}")
                        failed_workouts.append(f"{display_name}: {error_msg}")
                    
                except Exception as e:
                    import traceback
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # Get full traceback
                    tb = traceback.format_exc()
                    
                    self.log_status(f"✗ Error processing {workout_id}: {error_type}: {error_msg}")
                    
                    # Log the traceback to see exactly where it failed
                    for line in tb.split('\n'):
                        if line.strip():
                            self.log_status(f"  {line}")
                    
                    # Add to failed list with more context
                    if display_name:
                        failed_workouts.append(f"{display_name}: {error_msg}")
                    else:
                        failed_workouts.append(f"{workout_id}: {error_msg}")
            
            # Show summary
            if success_count == len(self.selected_workouts):
                messagebox.showinfo(
                    "Sync Complete", 
                    f"Successfully synced all {success_count} workouts to Garmin Connect!"
                )
                self.log_status(f"✓ Sync complete: {success_count}/{len(self.selected_workouts)} successful")
            elif success_count > 0:
                messagebox.showwarning(
                    "Partial Success",
                    f"Synced {success_count} of {len(self.selected_workouts)} workouts.\n\n"
                    f"Failed workouts:\n" + "\n".join(failed_workouts[:5])
                )
                self.log_status(f"⚠ Partial sync: {success_count}/{len(self.selected_workouts)} successful")
            else:
                messagebox.showerror(
                    "Sync Failed",
                    "Failed to sync any workouts. Check the status log for details."
                )
                self.log_status(f"✗ Sync failed: 0/{len(self.selected_workouts)} successful")
                
        except Exception as e:
            self.log_status(f"✗ Sync error: {str(e)}")
            messagebox.showerror("Error", f"Sync failed:\n\n{str(e)}")
    
    def export_fit_files(self):
        """Export selected workouts as FIT files"""
        if not self.selected_workouts:
            messagebox.showwarning("No Selection", "Please select workouts to export")
            return
        
        if not self.peloton_auth:
            messagebox.showwarning("Not Configured", "Please configure Peloton in Settings first")
            return
        
        # Ask user for export folder
        folder = filedialog.askdirectory(title="Select folder for FIT files")
        if not folder:
            return
        
        self.log_status(f"Exporting {len(self.selected_workouts)} FIT files to {folder}...")
        
        try:
            from datetime import datetime
            from fit_converter import PelotonToFitConverter
            
            converter = PelotonToFitConverter(self.peloton_auth)
            success_count = 0
            failed_workouts = []
            
            for workout_id in self.selected_workouts:
                try:
                    # Find workout data
                    workout = next((w for w in self.workout_data if w['id'] == workout_id), None)
                    if not workout:
                        self.log_status(f"✗ Workout {workout_id} not found")
                        continue
                    
                    # Get workout details
                    ride = workout.get('ride', {})
                    title = ride.get('title', 'Peloton Workout')
                    instructor_data = ride.get('instructor', {})
                    instructor = instructor_data.get('name', '')
                    created_at = workout.get('created_at', 0)
                    date_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d_%H%M')
                    
                    display_name = f"{title} - {instructor}" if instructor else title
                    
                    # Create safe filename
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    filename = f"{date_str}_{safe_title}_{workout_id}.fit"
                    fit_path = os.path.join(folder, filename)
                    
                    self.log_status(f"Exporting: {display_name}")
                    
                    # Convert to FIT
                    converter.convert_workout_to_fit(workout, fit_path)
                    
                    self.log_status(f"✓ Exported: {filename}")
                    success_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    self.log_status(f"✗ Error exporting {workout_id}: {error_msg}")
                    failed_workouts.append(f"{workout_id} - {error_msg}")
            
            # Show summary
            if success_count == len(self.selected_workouts):
                messagebox.showinfo(
                    "Export Complete",
                    f"Successfully exported {success_count} FIT files to:\n{folder}\n\n"
                    "You can now upload these files manually at connect.garmin.com"
                )
                self.log_status(f"✓ Export complete: {success_count}/{len(self.selected_workouts)} files")
            elif success_count > 0:
                messagebox.showwarning(
                    "Partial Success",
                    f"Exported {success_count} of {len(self.selected_workouts)} files to:\n{folder}\n\n"
                    f"Failed: {len(failed_workouts)} workouts"
                )
                self.log_status(f"⚠ Partial export: {success_count}/{len(self.selected_workouts)} successful")
            else:
                messagebox.showerror(
                    "Export Failed",
                    "Failed to export any files. Check the status log for details."
                )
                self.log_status(f"✗ Export failed: 0/{len(self.selected_workouts)} successful")
                
        except Exception as e:
            self.log_status(f"✗ Export error: {str(e)}")
            messagebox.showerror("Error", f"Export failed:\n\n{str(e)}")


def main():
    root = tk.Tk()
    app = PelotonGarminSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

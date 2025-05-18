import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from Crypto.Cipher import AES # pip install pycryptodome
from Crypto.Protocol.KDF import PBKDF2
import os

class GameSaveEditor(tk.Tk):
    def __init__(self, game_path):
        super().__init__()
        self.game_path = game_path

        style = ttk.Style(self)
        style.theme_use('xpnative')  # or 'alt', 'default', 'vista', 'clam', 'xpnative'

        # Customize notebook tabs
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10, 'bold'))

        default_font = ('Segoe UI', 10)
        self.option_add("*Font", default_font)
        self.option_add("*Background", "white")
        self.option_add("*Entry.Background", "white")
        self.option_add("*Entry.Relief", "flat")
        
        style.configure("Accent.TButton", foreground="white", background="#1f77b4", font=('Segoe UI', 10, 'bold'))

        self.title("Game Save Editor - R.E.P.O.")
        self.geometry("1200x800")
        self.configure(bg="white")

        self.data = {}
        self.game_info = {}
        self.player_data = {}
        self.item_data = {}
        self.player_keys = []
        
        self.expanded_items = set()
        self.entries = {}

        self.header_frame = tk.Frame(self, bg='white')
        self.header_frame.pack(fill=tk.X, padx=20, pady=10)

        self.create_header()

        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill='both', padx=10, pady=10)

        self.inventory_tab = ttk.Frame(self.tab_control)
        self.player_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.inventory_tab, text='Items')
        self.tab_control.add(self.player_tab, text='Players')

        self.create_inventory_tab()
        self.create_player_tab()
        self.create_footer()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Control-s>", lambda event: self.ask_save_file('save'))
        self.bind("<Control-o>", lambda event: self.ask_save_file('load'))
        self.bind("<Control-r>", lambda event: self.refresh_data())
        self.bind("<Control-q>", lambda event: self.on_close())

    def update_data(self, data):
        self.data = data
        self.game_info = {
            "playerNames": self.data.get("playerNames", {}).get("value", {}),
            "timePlayed": self.data.get("timePlayed", {}).get("value", 0),
            "date": self.data.get("dateAndTime", {}).get("value", ""),
            "teamName": self.data.get("teamName", {}).get("value", "")
        }

        game_data = self.data.get("dictionaryOfDictionaries", {}).get("value", {})
        self.game_info.update(game_data.get("runStats", {}))
        
        self.player_keys = [
            ("playerHealth", "Current Health"),
            ("playerUpgradeHealth", "Health"),
            ("playerUpgradeStamina", "Stamina"),
            ("playerUpgradeExtraJump", "Extra Jump"),
            ("playerUpgradeLaunch", "Launch"),
            ("playerUpgradeMapPlayerCount", "Map Player Count"),
            ("playerUpgradeSpeed", "Speed"),
            ("playerUpgradeStrength", "Strength"),
            ("playerUpgradeRange", "Range"),
            ("playerUpgradeThrow", "Throw Power"),
            ("playerHasCrown", "Has Crown")
        ]
        self.player_data = {}
        for player_id, player_name in self.game_info["playerNames"].items():
            self.player_data[player_id] = {}
            for key, label in self.player_keys:
                self.player_data[player_id][key] = game_data.get(key, {}).get(player_id, 0)

        self.item_keys = list(game_data.get("itemsPurchased", {}).keys())
        self.item_data = {}
        for key, value in game_data.get("item", {}).items():
            if '/' in key:
                item_id = key.split('/')[0]
                item_instance = key.split('/')[-1]
            else:
                item_id = key
                item_instance = 0
            self.item_data[item_id] = {
                "itemsPurchased": game_data.get("itemsPurchased", {}).get(item_id, 0),
                "itemsPurchasedTotal": game_data.get("itemsPurchasedTotal", {}).get(item_id, 0),
                "itemsUpgradesPurchased": game_data.get("itemsUpgradesPurchased", {}).get(item_id, 0),
                "itemBatteryUpgrades": game_data.get("itemBatteryUpgrades", {}).get(item_id, 0)
            }
            self.item_data[item_id]["instances"] = {}

            if item_instance:
                for i in range(1, int(item_instance) + 1):
                    self.item_data[item_id]["instances"][i] = {
                        "item": game_data.get("item", {}).get(f"{item_id}/{i}", 0),
                        "itemStatBattery": game_data.get("itemStatBattery", {}).get(f"{item_id}/{i}", 0)
                    }
            else:
                self.item_data[item_id]["instances"][0] = {
                    "item": game_data.get("item", {}).get(item_id, 0),
                    "itemStatBattery": game_data.get("itemStatBattery", {}).get(item_id, 0)
                }

    def create_header(self):
        # Logo
        try:
            self.logo_tk = tk.PhotoImage(file='logo-small.png')
            # logo_img = Image.open("logo.png").resize((80, 80), Image.ANTIALIAS)
            # self.logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self.header_frame, image=self.logo_tk, bg='white')
            logo_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            tk.Label(self.header_frame, text="[Logo Missing]", bg='white', fg='red').pack(side=tk.LEFT)

        if not hasattr(self, 'game_info') or not isinstance(self.game_info, dict):
            return

        info_frame = tk.Frame(self.header_frame, bg='white')
        info_frame.pack(side=tk.LEFT, padx=20)

        self.header_entries = {}

        def add_editable_row(parent, label, key, default):
            row = tk.Frame(parent, bg='white')
            row.pack(anchor='w')
            tk.Label(row, text=f"{label}:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side=tk.LEFT)
            entry = tk.Entry(row, width=12, font=('Segoe UI', 10), justify='left')
            entry.insert(0, str(default))
            entry.pack(side=tk.LEFT, padx=(5, 0))
            self.header_entries[key] = entry

        info = self.game_info
        add_editable_row(info_frame, "Team", "teamName", info.get("teamName", ""))
        add_editable_row(info_frame, "Date", "date", info.get("date", ""))
        add_editable_row(info_frame, "Time Played", "timePlayed", int(info.get("timePlayed", 0)))
        add_editable_row(info_frame, "Level", "level", info.get("level", 0))
        add_editable_row(info_frame, "Currency", "currency", info.get("currency", 0))
        add_editable_row(info_frame, "Lives", "lives", info.get("lives", 0))
        add_editable_row(info_frame, "Charges", "chargingStationCharge", info.get("chargingStationCharge", 0))
        add_editable_row(info_frame, "Total Haul", "totalHaul", info.get("totalHaul", 0))

    def add_tooltip(widget, text):
        tip = tk.Toplevel(widget)
        tip.withdraw()
        tip.overrideredirect(True)
        label = tk.Label(tip, text=text, background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()

        def show(event):
            tip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tip.deiconify()
        def hide(event):
            tip.withdraw()

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)


    def create_inventory_tab(self):
        container = tk.Frame(self.inventory_tab, bg="white")
        container.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="white")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = scroll_frame

        headers = ["", "Item", "Purchased", "Purchased Total", "Upgrade", "ItemID", "Battery"]
        for i, h in enumerate(headers):
            tk.Label(frame, text=h, width=15, font=('Arial', 10, 'bold'), bg="white", anchor='center').grid(row=0, column=i, padx=1, pady=2, sticky='ew')

        row = 1
        for item_name, item_info in sorted(self.item_data.items()):
            is_expanded = item_name in self.expanded_items
            toggle_text = "➖" if is_expanded else "➕"

            btn = tk.Button(frame, text=toggle_text, width=2, command=lambda name=item_name: self.toggle_item_instance(name))
            btn.grid(row=row, column=0, sticky='w', padx=1)

            tk.Label(frame, text=item_name, width=20, anchor='w', bg="white", ).grid(row=row, column=1, sticky='ew', padx=1, pady=1)

            self.entries[item_name] = {}
            values = [
                item_info.get("itemsPurchased", 0),
                item_info.get("itemsPurchasedTotal", 0),
                item_info.get("itemsUpgradesPurchased", 0)
            ]
            for col, (label, val) in enumerate(zip(headers[2:], values), start=2):
                entry = ttk.Entry(frame, width=10, justify='center', )
                entry.insert(0, str(val))
                entry.grid(row=row, column=col, padx=1, pady=1, sticky='ew')
                self.entries[item_name][label] = entry
            row += 1

            if is_expanded:
                for inst_id, inst_vals in sorted(item_info["instances"].items()):
                    if inst_id == 0:
                        continue
                    label = f"↳ {item_name}/{inst_id}"
                    tk.Label(frame, text=label, width=20, anchor='w', bg="#f9f9f9", ).grid(row=row, column=1, columnspan=4, sticky='ew', padx=1, pady=1)
                    self.entries[label] = {}
                    for col, key in enumerate(["item", "itemStatBattery"], start=5):
                        val = inst_vals.get(key, 0)
                        entry = ttk.Entry(frame, width=10, justify='center', )
                        entry.insert(0, str(val))
                        entry.grid(row=row, column=col, padx=1, pady=1, sticky='ew')
                        self.entries[label]["ItemID" if key == "item" else "Battery"] = entry
                    row += 1


    def create_player_tab(self):
        frame = tk.Frame(self.player_tab, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.player_entries = {}
        player_names = self.game_info.get("playerNames", {})


        for i, (pid, name) in enumerate(player_names.items()):
            box = tk.LabelFrame(frame, text=f"{name} ({pid})", font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
            # box.grid(row=i, column=0, sticky='ew', padx=10, pady=10) # vertical alignment
            box.grid(row=0, column=i, sticky='n', padx=10, pady=10)
            row = 0
            self.player_entries[pid] = {}
            for key, label in self.player_keys:
                val = self.player_data[pid].get(key, 0)
                tk.Label(box, text=label, bg='white').grid(row=row, column=0, sticky='w')
                entry = ttk.Entry(box, width=10, justify='center')
                entry.insert(0, str(val))
                entry.grid(row=row, column=1)
                self.player_entries[pid][key] = entry
                row += 1

    def toggle_item_instance(self, item_name):
        if item_name in self.expanded_items:
            self.expanded_items.remove(item_name)
        else:
            self.expanded_items.add(item_name)
        for widget in self.inventory_tab.winfo_children():
            widget.destroy()
        self.create_inventory_tab()

    def ask_save_file(self, mode='save'): # mode can be 'save' or 'load'
        # open the directory self.game_path
        if mode == 'save':
            file_path = filedialog.asksaveasfilename(
                                                    initialdir=self.game_path,
                                                    title="Save File",
                                                    initialfile="editable.es3",
                                                    defaultextension=".es3",
                                                    filetypes=[("Encrypted JSON", "*.es3"), ("All Files", "*.*")])
            if not file_path:
                messagebox.showerror("Error", "Please select a file to save.")
                return None
            self.save_data(file_path)
        elif mode == 'load':
            file_path = filedialog.askopenfilename(
                                                    initialdir=self.game_path,
                                                    title="Load File",
                                                    initialfile="editable.es3",
                                                    defaultextension=".es3",
                                                    filetypes=[("Encrypted JSON", "*.es3"), ("All Files", "*.*")])
            if not file_path:
                messagebox.showerror("Error", "Please select a file to load.")
                return None
            self.load_data(file_path)
        return file_path

    def create_footer(self):
        footer = tk.Frame(self, bg="white")
        footer.pack(fill=tk.X, padx=20, pady=10)
        # save button
        tk.Button(footer, text="Save", command=lambda: self.ask_save_file('save')).pack(side=tk.RIGHT)
        tk.Button(footer, text="Load", command=lambda: self.ask_save_file('load')).pack(side=tk.RIGHT)

    def save_data(self, file_path='./editable.es3'):
        try:
            for label, columns in self.entries.items():
                if label.startswith("↳"):
                    item, inst = label[2:].split('/')
                    inst = int(inst)
                    self.item_data[item]["instances"][inst]["item"] = int(columns["ItemID"].get())
                    self.item_data[item]["instances"][inst]["itemStatBattery"] = int(columns["Battery"].get())
                else:
                    self.item_data[label]["itemsPurchased"] = int(columns["Purchased"].get())
                    self.item_data[label]["itemsPurchasedTotal"] = int(columns["Purchased Total"].get())
                    self.item_data[label]["itemsUpgradesPurchased"] = int(columns["Upgrade"].get())

            for item, info in self.item_data.items():
                self.data['dictionaryOfDictionaries']['value']['itemsPurchased'][item] = info['itemsPurchased']
                self.data['dictionaryOfDictionaries']['value']['itemsPurchasedTotal'][item] = info['itemsPurchasedTotal']
                self.data['dictionaryOfDictionaries']['value']['itemsUpgradesPurchased'][item] = info['itemsUpgradesPurchased']
                self.data['dictionaryOfDictionaries']['value']['itemBatteryUpgrades'][item] = info['itemBatteryUpgrades']
                # Update instances
                for inst_id, inst_vals in info['instances'].items():
                    if inst_id == 0:
                        continue
                    key = f"{item}/{inst_id}" if inst_id != 0 else item # more than item count
                    self.data['dictionaryOfDictionaries']['value']['item'][key] = inst_vals['item']
                    self.data['dictionaryOfDictionaries']['value']['itemStatBattery'][key] = inst_vals['itemStatBattery']

            for label, columns in self.player_entries.items():
                for key, entry in columns.items():
                    entry_value = entry.get()
                    self.player_data[label][key] = int(entry_value)

            for player_id, player_info in self.player_data.items():
                for key, value in player_info.items():
                    self.data['dictionaryOfDictionaries']['value'][key][player_id] = value


            if hasattr(self, 'header_entries'):
                for key, entry in self.header_entries.items():
                    val = entry.get()
                    if key == "timePlayed":  # float
                        val = float(val)
                    elif key == "date" or key == "teamName":
                        pass  # keep as string
                    else:
                        val = int(val)
                    self.game_info[key] = val
                    if key in self.data:
                        self.data[key]["value"] = val
                    else:
                        self.data['dictionaryOfDictionaries']['value'].setdefault('runStats', {})[key] = val

            if file_path:
                # make a backup of the file
                if os.path.exists(file_path):
                    # check if the backup with same name exists
                    if os.path.exists(file_path + ".bak"):
                        # remove the backup file
                        os.remove(file_path + ".bak")
                    # rename the original file to backup
                    os.rename(file_path, file_path + ".bak")
                # save the file
                with open(file_path, 'wb') as f:
                    # Encrypt the data before saving
                    encrypted_data = encrypt_data(json.dumps(self.data).encode('utf-8'), PASSWORD)
                    f.write(encrypted_data)
                print("File saved successfully.")
                # messagebox.showinfo("Success", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def load_data(self, file_path='./editable.es3'):
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                    decrypted = decrypt_data(data, PASSWORD)
                    self.data = json.loads(decrypted.decode('utf-8'))
                    self.update_data(self.data)
                    # messagebox.showinfo("Success", "File loaded successfully.")
                    self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def refresh_data(self):
        self.entries.clear()
        self.player_entries.clear()

        for tab in [self.inventory_tab, self.player_tab]:
            for widget in tab.winfo_children():
                widget.destroy()

        # remove content of the header
        for widget in self.header_frame.winfo_children():
            widget.destroy()

        self.create_header()
        self.create_inventory_tab()
        self.create_player_tab()


    # on close, ask if user wants to save
    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to save your changes?"):
            self.ask_save_file('save')
        self.destroy()

def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def decrypt_data(data, password):
    iv = data[:16]
    key = PBKDF2(password, iv, dkLen=16, count=100)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(data[16:])
    return unpad_pkcs7(decrypted)

def pad_pkcs7(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - len(data) % block_size
    return data + bytes([pad_len] * pad_len)

def encrypt_data(data: bytes, password: str) -> bytes:
    iv = os.urandom(16)
    key = PBKDF2(password, iv, dkLen=16, count=100)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad_pkcs7(data)
    return iv + cipher.encrypt(padded)


PASSWORD = "Why would you want to cheat?... :o It's no fun. :') :'D"
# Sample usage
if __name__ == '__main__':
    user_name = os.getlogin()
    game_path = f"C:/Users/{user_name}/AppData/LocalLow/semiwork/Repo/saves";
    app = GameSaveEditor(game_path) 
    app.ask_save_file('load')
    app.mainloop()

# 🧠 R.E.P.O. Save Editor

<div align="center">
  <img src="logo.png" alt="R.E.P.O. Logo" style="max-height: 300px; height: auto; width: auto;" />
</div>

A minimalist and user-friendly GUI tool to decrypt, edit, and re-encrypt save files from the game **R.E.P.O.**  
Edit inventory, item instances, and player stats visually.
It works with the latest version of the game (v2022.3.21.2506) and is compatible with Windows 10/11.

---

## 🔍 Features

- 📦 View and edit item inventory, upgrades, and instances
- 👥 Edit player stats side-by-side

---

## 📸 Screenshots

### 🎮 Inventory Editor
![Inventory](screenshot_items.png)

### 🧍 Player Editor
![Players](screenshot_players.png)

---

## 🛠️ How to Use

### Approach-1: Run from the source 
1. Run:
   ```bash
   python repo_editor.py

### Approach-2: Use the executable
1. Download the latest release from [Releases](https://github.com/Aeunal/R.E.P.O.GameSaveEditor/releases).
2. Extract the zip file.
3. Run `repo_editor.exe`.

To use the editor:
1. Open the save file directory (usually located in `C:\Users\<username>\AppData\LocalLow\semiwork\R.E.P.O\save`, in which the folder will be opened automatically while loading).
2. Select the save file you want to edit.
3. Edit values.
4. Press Ctrl+S to save, select where to save the edited file, and choose a name. Then press Ctrl+Q to quit.

### 🔐 Password
The encryption key is hardcoded:
```python
"Why would you want to cheat?... :o It's no fun. :') :'D"
```

### 📦 Dependencies
- pycryptodome for AES:
```bash
pip install pycryptodome
```

## 💬 License
MIT – Do what you want. Ruin the fun responsibly 😂
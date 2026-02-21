# Office-GTK4

A lightweight GTK4/Adwaita wrapper that brings Microsoft 365 web apps into a native-feeling Linux desktop application. Word, Excel, PowerPoint, OneNote, and Outlook all live in a single tabbed window — no browser required.
<img width="2532" height="1750" alt="Screenshot-1" src="https://github.com/user-attachments/assets/009744d5-169b-4aea-b3b6-5eb6cdd11584" />
<img width="3148" height="2004" alt="Screenshot-2" src="https://github.com/user-attachments/assets/f76fecd9-294a-4e98-991d-9b7cca5f49f1" />
<img width="3128" height="1998" alt="Screenshot-3" src="https://github.com/user-attachments/assets/4dee98e5-24f2-4d50-9060-403a89688418" />
<img width="3128" height="1998" alt="Screenshot-4" src="https://github.com/user-attachments/assets/66705216-dc2a-419a-9bd7-85f232a8f302" />

## Requirements

- Python 3
- GTK 4.0
- libadwaita 1.x
- WebKitGTK 6.0
- python3-gi (GObject introspection bindings)

The installer will attempt to install these automatically on Debian/Ubuntu (`apt`), Fedora (`dnf`), and Arch (`pacman`) based systems.

## Installation

```bash
chmod +x install.sh
./install.sh
```

This installs the app to `~/.local/share/Office-GTK4/`, creates a launcher at `~/.local/bin/Office-GTK4`, registers a `.desktop` entry, and installs an icon. After installation you can launch it from your app menu or by running:

```bash
Office-GTK4
```

> **Note:** If `~/.local/bin` is not in your `PATH`, add `export PATH="$HOME/.local/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc`.

## Uninstallation

```bash
chmod +x uninstall.sh
./uninstall.sh
```

You will be prompted to confirm, and optionally to remove saved cookies and cached data as well.

## Apps Included

| App | URL |
|---|---|
| Office Home | office.com |
| Word | office.com/launch/word |
| Excel | office.com/launch/excel |
| PowerPoint | office.com/launch/powerpoint |
| OneNote | office.com/launch/onenote |
| Outlook | outlook.office.com |

## Notes

- Sessions and cookies are persisted between launches so you stay signed in.
- The app uses a Chrome-compatible user agent string to ensure full Office web app functionality.
- Tabs automatically track which Office app is active based on the current URL.

  [!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/mrks0001)

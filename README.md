# Office-GTK4

A lightweight GTK4/Adwaita wrapper that brings Microsoft 365 web apps into a native-feeling Linux desktop application. Word, Excel, PowerPoint, OneNote, and Outlook all live in a single tabbed window — no browser required.

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

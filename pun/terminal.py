"""
Builds the terminal command line that starts a system update.

Copyright (C) 2024 Tim Teichmann

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import shlex
import shutil

# known terminals and the arguments that make them run the command following
# them; "Automatic" tries them in this order after $TERMINAL
TERMINALS = {
    "xdg-terminal-exec": [],
    "konsole": ["-e"],
    "gnome-terminal": ["--"],
    "kgx": ["--"],
    "ptyxis": ["--"],
    "xfce4-terminal": ["-x"],
    "mate-terminal": ["-x"],
    "terminator": ["-x"],
    "alacritty": ["-e"],
    "kitty": [],
    "foot": [],
    "wezterm": ["start", "--"],
    "ghostty": ["-e"],
    "urxvt": ["-e"],
    "st": ["-e"],
    "xterm": ["-e"],
}

# placeholder for the update command in a custom terminal command line
PLACEHOLDER = "{cmd}"

def installed_terminals():
    """Returns the names of the known terminals that are installed."""
    return [name for name in TERMINALS if shutil.which(name)]

def update_argv(command, keep_open):
    """Returns the arguments that run the update command in a shell."""
    script = command
    if keep_open:
        # on separate lines, so a trailing comment or "&" can't swallow them
        script += "\necho\nprintf 'Press Enter to close... '\nread -r _"
    return ["sh", "-c", script]

def terminal_argv(terminal, argv):
    """Returns the full command line that runs argv in the given terminal.

    terminal is either a known terminal, optionally with extra arguments
    (e.g. "konsole --profile Updates"), or a command line containing {cmd}
    where argv goes. Raises ValueError if it is neither."""
    tokens = shlex.split(terminal)
    if not tokens:
        raise ValueError("No terminal given.")
    if PLACEHOLDER in terminal:
        result = []
        for token in tokens:
            if token == PLACEHOLDER:
                result.extend(argv)
            else:
                result.append(token.replace(PLACEHOLDER, shlex.join(argv)))
        return result
    name = os.path.basename(tokens[0])
    if name in TERMINALS:
        return tokens + TERMINALS[name] + argv
    raise ValueError("Unknown terminal \"%s\". Enter a command line containing %s "
                     "where the update command goes." % (name, PLACEHOLDER))

def automatic_terminal():
    """Returns the terminal to use when none is configured, or None."""
    if shutil.which("xdg-terminal-exec"):
        return "xdg-terminal-exec"
    env = os.environ.get("TERMINAL", "").strip()
    if env:
        try:
            tokens = shlex.split(env)
        except ValueError:
            tokens = []
        if tokens and shutil.which(tokens[0]):
            # most terminals not known to pun take a command after -e
            if os.path.basename(tokens[0]) in TERMINALS or PLACEHOLDER in env:
                return env
            return env + " -e " + PLACEHOLDER
    installed = installed_terminals()
    return installed[0] if installed else None

def launch_argv(settings):
    """Returns the command line that starts the update in a terminal.

    Raises ValueError if no terminal is found or the terminal is invalid."""
    terminal = settings["terminal"] or automatic_terminal()
    if not terminal:
        raise ValueError("No terminal found. Choose one in the settings.")
    argv = terminal_argv(terminal, update_argv(settings["command"], settings["keep_open"]))
    if not shutil.which(argv[0]):
        raise ValueError("Terminal \"%s\" not found." % argv[0])
    return argv

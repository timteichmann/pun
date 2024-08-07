#!/usr/bin/env python3

"""
pun - p(acman) u(pdate) n(otifier)
----------------------------------
Checks for pacman package updates and shows the status in the system tray.
    Intended to be used in Arch Linux (main target) and remixes (but without
    active support).

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
from setuptools import setup

print(__doc__)

setup(
    name = "pun",
    version = "1.0",
    description = "\n".join(__doc__.split("\n")[3:]).strip(),
    author = "Tim Teichmann",
    author_email = "onlineaccounts@mailbox.org",
    url = "https://github.com/timteichmann/pun/",
    packages = ["pun"],
    package_data = {"pun": ["icons/*.png"]},
    scripts = ["pun/pun"],
)

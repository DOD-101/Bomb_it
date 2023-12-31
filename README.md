# Bomb It!

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

<sub>Version: 0.1.0.28</sub>

## What is this?
Bomb it! is an open-source game written in python using the pygame module package.

The objective of the game is simple: **BOMB STUFF**.
There are 9 maps to choose from and 3 bombs that can be used to destroy the targets on each map. You get a certain number of points for destroying targets and get points subtracted for the amount of bombs you used (and the types of bombs) and hitting things other than the targets.

This is my first game and is intended, in large part, to further my coding capabilities.

## Contact

If you wish to help with development or want to contact me for any other reason:
@discord: .david101

## Style guide
The following rules are to be followed for all python code written for this project.

These rules are generally based on [PEP 8](https://peps.python.org/pep-0008) & [The Black Formatter](https://github.com/psf/black)

    1. Classes: PascalCase
    2. Variables: snake_case
    3. Functions/Methods: camelCase
    4. Modules: snake_case (but avoid underscores unless it improves readability)
    5. Whenever using abbreviations make sure that they are clear in their meaning or are explained (via comment) and
    should always improve readability not come at the cost of it.

    For any other uncertainties feel free to ask me.

It is required that everyone writing code for this repo use pylint and the black formatter.

Note 1: Bomb It is starting to use pylint and black hence there are still some inconsistencies.
Note 2: You need to whitelist pygame for pylint since it contains quite a lot of C code. "--extension-pkg-whitelist=pygame"

## Dependencies/Assets and Licenses

Bomb It (stylized as: "Bomb It!") is licensed under the [MIT license](LICENSES/LICENSE_BOMB_IT.txt).

### Dependencies

[Pygame](https://www.pygame.org/news) is licensed under the [LGPL license](LICENSES/LICENSE_PYGAME.txt)

[Pillow](https://pillow.readthedocs.io/en/stable/index.html) is licensed under the [open source HPND License](LICENSES/LICENSE_PILLOW.txt)

### Assets

[OpenSans](https://github.com/googlefonts/opensans) is licensed under the [OFL](LICENSES/LICENSE_OPENSANS.txt) license and comes with the game's source code.

[Game-icons](https://game-icons.net/) are licensed under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).

[Pixbay](https://pixabay.com/) content is licensed under [these Terms](https://pixabay.com/service/license-summary/).

## Credits

-Main Dev: David Thievon

And many thanks to anyone who has worked on any of the dependencies or assets used to make this game possible.

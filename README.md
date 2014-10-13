## elphel-preview-generator<br />Elphel panorama preview generator.

>Elphel panorama preview generator.

### Description
This tool creates preview panoramas from images created by the Elphel Eyesis 4π camera.

### Table of Contents
- [Elphel panorama preview generator.](#elphel-preview-generatorbr-elphel-panorama-preview-generator)
  - [Usage](#usage)
  - [Example usage scenarios](#example-usage-scenarios)
  - [Copyright](#copyright)
  - [License](#license)

### Usage
    Usage: ./preview_generator.py [OPTIONS]

    [Required arguments]
    -i --input          Input JP4 folder
    -o --output         Output JPEG folder

    [Optional arguments]
    -h --help           Prints this
    -p --parallel       Use GNU parallel
    -g --grayscale      Write grayscale images (without debayer)


### Example usage scenarios
    ./preview_generator.py -i data/footage/run1/0 -o /data/footage/run1/previews

### Copyright

Copyright (c) 2014 FOXEL SA - [http://foxel.ch](http://foxel.ch)<br />
This program is part of the FOXEL project <[http://foxel.ch](http://foxel.ch)>.

Please read the [COPYRIGHT.md](COPYRIGHT.md) file for more information.


### License

This program is licensed under the terms of the
[GNU Affero General Public License v3](http://www.gnu.org/licenses/agpl.html)
(GNU AGPL), with two additional terms. The content is licensed under the terms
of the
[Creative Commons Attribution-ShareAlike 4.0 International](http://creativecommons.org/licenses/by-sa/4.0/)
(CC BY-SA) license.

Please read <[http://foxel.ch/license](http://foxel.ch/license)> for more
information.

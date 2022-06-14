## Contents of this repo

Script that demonstrates automatic identification of physical storage media using Python and the Windows API. Only works on Windows! Requires the win32 api module, which can be installed using:

```
pip install pywin32
```

(Apparently at some point in time there was an alternative package named "pypiwin32", but I'm not entirely sure if it's still used).

## Usage

```
python detectStorageMediaType.py [-h] drives [drives ...]
```

Positional arguments:

- drives: one or more logical drive names

Example:

```
python detectStorageMediaType.py A D E
```

Result:

```
Drive:                   A
Media type:              F3_1Pt44_512

Drive:                   D
Media type:              RemovableMedia
Device type:             FILE_DEVICE_CD_ROM
Supported media types:
                         CD_ROM
                         RemovableMedia

Drive:                   E
Media type:              RemovableMedia
Device type:             FILE_DEVICE_DISK
Supported media types:
                         RemovableMedia
```
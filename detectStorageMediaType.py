import sys
import struct
import argparse
import win32api
import win32file
import winioctlcon

"""
Script that demonstrates how to identify the media type of storage media attached to logical
Windows drives using Python's Windows API wrapper interface.
Johan van der Knijff, KB, National Library of the Netherlands
"""


def parseCommandLine(parser):
    """Parse command line"""
    # Add arguments
    parser.add_argument('drives',
                        action="store",
                        type=str,
                        nargs='+',
                        help="logical drive name (repeatable")
    # Parse arguments
    args = parser.parse_args()

    return args


def getMediaTypes(drive):
    """
    Returns a list with one or more strings that identify the media type of a
    logical Windows drive. Function uses both the IOCTL_STORAGE_GET_MEDIA_TYPES_EX
    and IOCTL_DISK_GET_DRIVE_GEOMETRY methods (either of which may fail under certain)
    conditions).

    Codes are documented here:

    https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-media_type

    and here:

    https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_media_type
    """

    # List with returned mediatype values
    mediaTypesOut = []

    # Low-level device name of device assigned to logical drive
    driveDevice =  "\\\\.\\" + drive + ":"

    # Create a handle to access the device
    try:
        handle = win32file.CreateFile(driveDevice,
                                      0,
                                      win32file.FILE_SHARE_READ,
                                      None,
                                      win32file.OPEN_EXISTING,
                                      0,
                                      None)
    except:
        # Report error message if device handle cannot be created
        sys.stderr.write("Error, cannot access device for drive " + drive + "\n")

    # Get media types using IOCTL_DISK_GET_DRIVE_GEOMETRY method
    try:
        diskGeometry = win32file.DeviceIoControl(handle,
                                                 winioctlcon.IOCTL_DISK_GET_DRIVE_GEOMETRY,
                                                 None,
                                                 24)

        # Resulting output (diskGeometry) documented here:
        #
        # https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-disk_geometry

        offset = 8
        mediaTypeCode = struct.unpack("<I", diskGeometry[offset:offset + 4])[0]
        # Lookup corresponding media type string and add to output list
        mediaType = lookupMediaType(mediaTypeCode)
        mediaTypesOut.append(mediaType)

    except:
        pass

    # Get media types using IOCTL_STORAGE_GET_MEDIA_TYPES_EX method
    try:
        mediaTypes = win32file.DeviceIoControl(handle,
                                               winioctlcon.IOCTL_STORAGE_GET_MEDIA_TYPES_EX,
                                               None,
                                               2048)

        # Resulting output (mediaTypes) documented here:
        #
        # https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-get_media_types

        # Number of DEVICE_MEDIA_INFO structures to read
        mediaInfoCount = struct.unpack("<I", mediaTypes[4:8])[0]

        # Remaining bytes are one or more 32-byte DEVICE_MEDIA_INFO structures.
        # documented here:
        #
        # https://docs.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-device_media_info
        #
        # This describes a union of 3 possible structures. Two of them  (DiskInfo, RemovableDiskInfo)
        # are identical, only TapeInfo is different (with MediaType at 0 offset instead of 8!), but not
        # relevant if we're not dealing with tape. 

        offset = 8

        # Loop over DEVICE_MEDIA_INFO structures
        for _ in range(mediaInfoCount):
            # Skip 8 byte cylinders value
            offset += 8
            mediaTypeCode = struct.unpack("<I", mediaTypes[offset:offset + 4])[0]
            # Lookup corresponding media type string and add to output list
            mediaType = lookupMediaType(mediaTypeCode)
            mediaTypesOut.append(mediaType)
            # Skip to position of next DEVICE_MEDIA_INFO structure
            offset += 24
        
    except:
        pass

    # Remove duplicate entries from output list
    mediaTypesOut = list(set(mediaTypesOut))

    return mediaTypesOut


def lookupMediaType(mediaTypeCode):
    """
    Return media type string from mediaType code.

    Below dictionary maps Windows media type codes against the MEDIA_TYPE and STORAGE_MEDIA_TYPE
    output codes.
  
    Based on:

    https://github.com/mhammond/pywin32/blob/main/win32/Lib/winioctlcon.py
    """
    mediaTypes = {
        0: "Unknown",
        1: "F5_1Pt2_512",
        2: "F3_1Pt44_512",
        3: "F3_2Pt88_512",
        4: "F3_20Pt8_512",
        5: "F3_720_512",
        6: "F5_360_512",
        7: "F5_320_512",
        8: "F5_320_1024",
        9: "F5_180_512",
        10: "F5_160_512",
        11: "RemovableMedia",
        12: "FixedMedia",
        13: "F3_120M_512",
        14: "F3_640_512",
        15: "F5_640_512",
        16: "F5_720_512",
        17: "F3_1Pt2_512",
        18: "F3_1Pt23_1024",
        19: "F5_1Pt23_1024",
        20: "F3_128Mb_512",
        21: "F3_230Mb_512",
        22: "F8_256_128",
        23: "F3_200Mb_512",
        24: "F3_240M_512",
        25: "F3_32M_512",
        32: "DDS_4mm",
        33: "MiniQic",
        34: "Travan",
        35: "QIC",
        36: "MP_8mm",
        37: "AME_8mm",
        38: "AIT1_8mm",
        39: "DLT",
        40: "NCTP",
        41: "IBM_3480",
        42: "IBM_3490E",
        43: "IBM_Magstar_3590",
        44: "IBM_Magstar_MP",
        45: "STK_DATA_D3",
        46: "SONY_DTF",
        47: "DV_6mm",
        48: "DMI",
        49: "SONY_D2",
        50: "CLEANER_CARTRIDGE",
        51: "CD_ROM",
        52: "CD_R",
        53: "CD_RW",
        54: "DVD_ROM",
        55: "DVD_R",
        56: "DVD_RW",
        57: "MO_3_RW",
        58: "MO_5_WO",
        59: "MO_5_RW",
        60: "MO_5_LIMDOW",
        61: "PC_5_WO",
        62: "PC_5_RW",
        63: "PD_5_RW",
        64: "ABL_5_WO",
        65: "PINNACLE_APEX_5_RW",
        66: "SONY_12_WO",
        67: "PHILIPS_12_WO",
        68: "HITACHI_12_WO",
        69: "CYGNET_12_WO",
        70: "KODAK_14_WO",
        71: "MO_NFR_525",
        72: "NIKON_12_RW",
        73: "IOMEGA_ZIP",
        74: "IOMEGA_JAZ",
        75: "SYQUEST_EZ135",
        76: "SYQUEST_EZFLYER",
        77: "SYQUEST_SYJET",
        78: "AVATAR_F2",
        79: "MP2_8mm",
        80: "DST_S",
        81: "DST_M",
        82: "DST_L",
        83: "VXATape_1",
        84: "VXATape_2",
        85: "STK_9840",
        86: "LTO_Ultrium",
        87: "LTO_Accelis",
        88: "DVD_RAM",
        89: "AIT_8mm",
        90: "ADR_1",
        91: "ADR_2",
        92: "STK_9940"
    }

    try:
        mediaType = mediaTypes[mediaTypeCode]
    except KeyError:
        mediaType = "Unknown"
    return mediaType


def main():
    """
    Get media type for list of logical Windows drive. First we
    get the drive geometry, then we use that to get
    the actual media type
    """

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="detect storage media type of logical drive")
    
    args = parseCommandLine(parser)

    # List of drives as entered by user
    myDrives = args.drives   

    print("------------------------")

    for drive in myDrives:
        # Strip any trailing colons
        drive = drive.strip(":")
        mediaTypes = getMediaTypes(drive)
        print("Drive " + drive + ":")
        for mediaType in mediaTypes:
            print("            " + mediaType)
        print("------------------------")

if __name__ == "__main__":
    main()
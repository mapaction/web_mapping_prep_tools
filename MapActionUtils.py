__author__ = 'Mr Greg Vaughan'

import os
import arcpy
import time
import datetime
import json
import zipfile


"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Functions to support the MapAction web mapping data preparation tools.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""


def get_date():
    return datetime.today()


def get_formatted_date_time():
    today = datetime.datetime.now()
    formatted_datetime = str(today.strftime('%A %d %B %Y, %H:%M:%S'))
    return formatted_datetime


def get_time():
    """
    :return: A floating point number rounded to two decimal places of the time in seconds since the epoch
    """
    timestamp = time.time()
    return timestamp


def get_elapsed_time(start_time, end_time):
    """
    :param start_time: A numerical field that defines the start time as time since the epoch in seconds
    :param end_time: A numerical field that defines the end time as time since the epoch in seconds
    :return: A floating point number rounded to 2 decimal places of the time elapsed given a start and finish time
    """
    elapsed_time = round(end_time - start_time, 2)
    return elapsed_time


def get_tools_install_directory():
    """
    Gets the directory of the installed tools
    :return: returns a string of the path
    """
    path = os.path.dirname(os.path.realpath(__file__))
    return path


def write_to_json(path_filename, data):
    """
    Given a python dictionary type it will output correctly formatted json to the specified file
    :param path: path of the output file
    :param filename: file name of the output file
    :param data: the pyton dictionary with the key value pairs to be written to json
    :return: returns boolean based on whether the file has been opened written to
    """
    try:
        with open(path_filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
            outfile.close()
            success = True
            arcpy.AddMessage("Success writing output JSON file.")
    except:
        success = False
        arcpy.AddMessage("Error writing output JSON file.")

    return success


def config_file_path_exists():
    filepath = get_tools_install_directory() + os.sep + "docs" + os.sep + "config.json"
    if os.path.isfile(filepath):
        return True
    else:
        return False


def config_file_path():
    """
    :return: a string of the configuration file path, to be used in conjunction with config_file_path_exists()
    """
    filepath = get_tools_install_directory() + os.sep + "docs" + os.sep + "config.json"
    return filepath


def read_from_json_file_to_dict(json_path):
    if os.path.isfile(json_path):
        json_data = open(json_path)
        data = json.load(json_data)
        json_data.close()
        return data
    else:
        arcpy.AddMessage("Failed to read data from JSON file!")
        return False


def create_zip(path_layername, output_folder):

    base_name = os.path.basename(path_layername).split('.')[0]
    base_folder = os.path.split(path_layername)[0]
    zip_file = output_folder + os.sep + base_name + ".zip"

    with zipfile.ZipFile(file=zip_file, mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as myzip:
            for f in os.listdir(base_folder):
                splitF = os.path.splitext(f)
                if splitF[0].upper() == base_name.upper() and splitF[1].upper() != '.LOCK':
                    myzip.write(os.path.join(base_folder, f), f)
                del f
                del splitF
    del base_name
    del base_folder


def layer_metadata_to_dict(layer, tags, new_tags, description, access_info, culture, license_info, snippet):
    #get the extent of the layer
    extent = layer_extent_to_dict(layer)
    extent_string = extent["xmin"] + " " + extent["ymin"] + " " + extent["xmax"] + " " + extent["ymax"]
    #Checks if new_tags has any values, if not ignores it
    if not new_tags:
        tag_str = tags
    else:
        tag_str = tags + ", " + new_tags
    #Strips whitespace and comma's from the end of tags string
    tag_str1 = tag_str.rstrip()
    tags_final = tag_str1.rstrip(',')

    #set the snippet to blank string to prevent 'null' being returned
    if not snippet:
        snippet = ""

    #create the output dictionary and add values
    dict = {}
    desc = arcpy.Describe(layer)
    dict["title"] = str(desc.baseName) + ".zip"
    dict["type"] = str(desc.dataType).title()
    dict["snippet"] = snippet
    dict["description"] = description
    dict["tags"] = tags_final
    dict["extent"] = extent_string
    dict["spatialReference"] = desc.spatialReference.name
    dict["accessInformation"] = access_info
    dict["licenseInfo"] = license_info
    dict["culture"] = culture

    return dict


def pdf_metadata_to_dict(mxd, pdf_name, tags, new_tags, description, access_info, culture, license_info, snippet):
    #get the extent of the layer
    extent = map_frame_extent_to_dict(mxd)
    extent_string = extent["xmin"] + " " + extent["ymin"] + " " + extent["xmax"] + " " + extent["ymax"]
    #Checks if new_tags has any values, if not ignores it
    if not new_tags:
        tag_str = tags
    else:
        tag_str = tags + ", " + new_tags
    #Strips whitespace and comma's from the end of tags string
    tag_str1 = tag_str.rstrip()
    tags_final = tag_str1.rstrip(',')

    #set the snippet to blank string to prevent 'null' being returned
    if not snippet:
        snippet = ""

    #create the output dictionary and add values
    dict = {}
    dict["title"] = pdf_name + ".pdf"
    dict["type"] = "PDF"
    dict["snippet"] = snippet
    dict["description"] = description
    dict["tags"] = tags_final
    dict["extent"] = extent_string
    dict["spatialReference"] = spatial_reference_string_from_dataframe(mxd)
    dict["accessInformation"] = access_info
    dict["licenseInfo"] = license_info
    dict["culture"] = culture

    return dict


def get_web_staging_mxd_path():
    """
    :return: a string of the path to the web staging mxd set in the config file
    """
    if config_file_path():
        data = read_from_json_file_to_dict(config_file_path())
        staging_mxd_path = data["web_mxd_path"]
        return staging_mxd_path
    else:
        return False

def get_web_staging_spatial_ref():
    mxd_path = get_web_staging_mxd_path()
    mxd = arcpy.mapping.MapDocument(mxd_path)
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    df_sr = str(df.spatialReference.name)
    return df_sr

def layer_extent_to_dict(layer):
    extent_dict = {}
    desc = arcpy.Describe(layer)
    extent_dict["xmin"] = str(desc.extent.XMin)
    extent_dict["xmax"] = str(desc.extent.XMax)
    extent_dict["ymin"] = str(desc.extent.YMin)
    extent_dict["ymax"] = str(desc.extent.YMax)
    return extent_dict

def map_frame_extent_to_dict(mxd):
    frame = arcpy.mapping.ListDataFrames(mxd)[0]
    extent_dict = {}
    extent_dict["xmin"] = str(frame.extent.XMin)
    extent_dict["xmax"] = str(frame.extent.XMax)
    extent_dict["ymin"] = str(frame.extent.YMin)
    extent_dict["ymax"] = str(frame.extent.YMax)
    return extent_dict


def read_txt_to_list(file_name_path):
    """
    Takes the lookup CSV file for the data naming tool and creates a list to show the user
    with the long name and abbreviation in brackets afterwards.
    :param file_name_path:
    :return:
    """
    list = []
    file = open(file_name_path, 'r')

    for line in file:
        new_line = line.replace("'", "")
        list.append(new_line.rstrip())

    return list

def export_to_pdf(mxd, path, pdf_resolution, pdf_quality):
    """
    Calls the ArcGIS geoprocessing tool ExportToPDF and passes the parameters supplied.
    """
    arcpy.mapping.ExportToPDF(mxd, path, resolution=pdf_resolution, image_quality=pdf_quality)


def spatial_reference_from_dataframe(mxd):
    """
    :param mxd: the map document to retrieve the spatial reference from.  Takes the first data frame in the mxd.
    :return: a spatial reference object of the data frame.  See the function spatial_reference_string_from_dataframe() to return a string.
    """
    map_doc = arcpy.mapping.MapDocument(mxd)
    df = arcpy.mapping.ListDataFrames(map_doc)[0]
    sr = df.spatialReference
    return sr

def spatial_reference_string_from_dataframe(mxd):
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    sr = str(df.spatialReference.name)
    return sr

def create_spatial_ref_factory_from_code(code):
    sr = arcpy.SpatialReference()
    sr.factoryCode = code
    sr.create()
    return sr

def get_metadata_permissions_list():
    """
    :return: A list of the MapAction permissions.
    """
    hh = 'Both the data and any derived products may only be distributed amongst the humanitarian community.'
    hp = 'This data may be distributed amogst the humanitarian community. Derived products can be freely distributed'
    mh = 'The dataset may not be given to anyone outside MapAction. Derived maps may only be distributed amogst the humanitarian community.'
    mm = 'This dataset is for MapAction internal use only.'
    mp = 'The dataset may not be given to anyone outside MapAction. Only derived maps can be freely distributed.'
    pp = 'This dataset is avaiable in the public domain. Derived products can be freely distributed.'
    list = [hh, hp, mh, mm, mp, pp]
    return list


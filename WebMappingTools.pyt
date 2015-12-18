import arcpy
import os
import MapActionUtils as utils
from LayerValidation import EvaluateLayer
import webbrowser


class Toolbox(object):
    def __init__(self):

        """Toolbox definition"""

        self.label = "MapAction Web Mapping Kiosk Tools (version 0.1)"
        self.alias = "WebMappingTools"

        # List of tool classes associated with this toolbox
        self.tools = [ConfigTool, LayerValidationTool, DeleteFieldsReprojectCopyDataToWebStagingTool,
                      CreateZipLayerMetadata, CreatePdfLayerMetadata, CreateReprojectZipMetadata]


"""
Each tool in the toolbox is defined below as a class
The tools call on the custom classes MapActionUtils and LayerValidation as well as the standard Python libraries and
ESRI's arcpy libarary.
Note: The WebAnalyzeResults is not currently loaded into the toolbox.
"""

class CreateLayerFile(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create layer file"
        self.description = "Create a layer file with updated field aliases."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Select feature class to create a layer file",
            name="input_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        parameters = [parameter0]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return


    def updateMessages(self, parameters):
        return


    def execute(self, parameters, messages):
        """

        """
        input_layer = parameters[0].valueAsText

        fields = arcpy.ListFields(input_layer)

        # save a layer file in the same directory as the input shapefile

        desc = arcpy.Describe(input_layer)
        output_filename = os.path.splitext(desc.name)[0] + '.lyr'
        output_layer = desc.path + os.sep + output_filename
        arcpy.SaveToLayerFile_management(input_layer, output_layer, "RELATIVE")

        return


class LayerValidationTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "02 - Layer validation"
        self.description = "Checks a feature class for suitablitiy for export as a web service."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Select layer to be validated",
            name="input_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        parameter1 = arcpy.Parameter(
            displayName="Validation results (file will display after script has run)",
            name="web_layer_destination",
            datatype="DETextfile",
            parameterType="Optional",
            direction="Input",
            enabled="False")

        try:
            if utils.config_file_path_exists():
                data = utils.read_from_json_file_to_dict(utils.config_file_path())
                if 'layer_validation_path' in data:
                    if os.path.exists(data["layer_validation_path"]):
                        parameter1.value = data["layer_validation_path"]
            else:
                if os.path.exists(utils.get_tools_install_directory() + os.sep + "docs" + os.sep + "layer_validation.txt"):
                    parameter1.value = utils.get_tools_install_directory() + os.sep + "docs" + os.sep + \
                        "layer_validation.txt"
                else:
                    parameter1.value = "Close tool and set layer validtion path in the config tool"
        except:
            print arcpy.GetMessages(2)

        parameters = [parameter0, parameter1]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return


    def updateMessages(self, parameters):
        return


    def execute(self, parameters, messages):
        """

        """

        p0 = parameters[0].valueAsText

        layer = EvaluateLayer(p0)
        # Get the path to the layer_validation.txt file from the config tool
        if utils.config_file_path():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            path = data["layer_validation_path"]
        else:
            path = utils.get_tools_install_directory() + os.sep + "docs" + os.sep + "layer_validation.txt"

        with open(path, 'a') as text_file:
            text_file.write("\n\n")
            text_file.write("---- Start of layer validation -------------------------------------->\n\n")
            text_file.write(utils.get_formatted_date_time() + "\n")
            text_file.write("Layer: " + layer.name + "\n\n")
            text_file.write("Tests: \n")
            counter = 0
            for x in layer.eval_results:
                test = layer.eval_tests[counter]
                result = layer.eval_results[counter]
                message = layer.eval_messages[counter]
                #text_file.write(test + " \t\t: " + result + " - " + message + "\n")
                # If the test is 'Spatial reference' only add 1 tab for formatting aesthetics
                if counter != 2:
                    text_file.write(test + "\t  : " + result + " - " + message + "\n")
                else:
                    text_file.write(test + " : " + result + " - " + message + "\n")
                counter += 1
            text_file.write("\n---- End of evaluation results -------------------------------------->")
        text_file.close()
        webbrowser.open(path)

        return


class CreateReprojectZipMetadata(object):
    def __init__(self):
        self.label = "03 - Layer preparation"
        self.description = "Takes an input shapefile and zips it and saves it to the 'zip_data_path' path set in the config tool."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Input layer",
            name="input_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            enabled="True",)

        parameter1 = arcpy.Parameter(
            displayName="Select fields to delete",
            name="delete_fields",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            enabled="True",
            multiValue=True)

        parameter2 = arcpy.Parameter(
            displayName="Staging data location",
            name="web_layer_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            enabled="False")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            parameter2.value = data["staging_data_path"]
        else:
            parameter2.value = "Close tool and set 'staging_data_path' using the config tool."

        #Values for the second part of the tool
        parameter3 = arcpy.Parameter(
            displayName="Metadata layer description",
            name="metadata_description",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter4 = arcpy.Parameter(
            displayName="Metadata tags",
            name="metadata_tags",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            enabled="True",
            multiValue=True)

        parameter4.filter.list = utils.read_txt_to_list(utils.get_tools_install_directory() + os.sep + "docs" + os.sep + "metadata_tags.txt")

        parameter5 = arcpy.Parameter(
            displayName="Add custom tags, comma separated value",
            name="metadata_custom_tags",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        parameter5.value = "MapAction, "

        parameter6 = arcpy.Parameter(
            displayName="Metadata access information",
            name="metadata_access",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter6.filter.list = utils.get_metadata_permissions_list()

        parameter7 = arcpy.Parameter(
            displayName="Metadata license information",
            name="metadata_license",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter7.value = "Copyright MapAction 2014"

        parameter8 = arcpy.Parameter(
            displayName="Metadata culture information",
            name="metadata_culture",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter8.value = "English (united kingdom)"

        parameter9 = arcpy.Parameter(
            displayName="Metadata snippet",
            name="metadata_snippet",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter10 = arcpy.Parameter(
            displayName="Zip data directory (Set in the web mapping config tool)",
            name="zip_metadata_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            enabled="False")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            parameter10.value = data["zip_data_path"]
        else:
            parameter10.value = "Close tool and set the 'zip_data_path' using the config tool."

        parameters = [parameter0, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8,
                      parameter9, parameter10]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        layer = parameters[0].valueAsText
        fields = []
        if layer is not None:
            for x in arcpy.ListFields(layer):
                fields.append(str(x.name))
            #after getting a list of the fields in the table
            #remove required fields from the list so they cannot be deleted
            remove_fields = ["FID", "OBJECTID", "Shape", "Shape_Area", "Shape_Length"]
            for field in remove_fields:
                if field in fields:
                    fields.remove(field)
            parameters[1].filter.list = fields

        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        """

        :param parameters:
        :param messages:
        :return:
        """
        #Assign the parameter values from the tool
        layer = parameters[0].valueAsText
        select_fields = parameters[1].valueAsText
        folder = parameters[2].valueAsText

        desc = arcpy.Describe(layer)
        layer_name = os.path.splitext(str(desc.name))[0]
        #layer_type = str(desc.type)

        #Set the output file path
        file_path = folder + os.sep + layer_name #+ ".shp"
        #create the spatial reference object (from the data frame[0] of web staging)
        mxd_path = utils.get_web_staging_mxd_path()
        spatial_ref = utils.spatial_reference_from_dataframe(mxd_path)

        #reproject the selected feature class and save into memory
        #Delete the selected fields in the GUI
        #rename the file
        #save the file as a shapefile to the data folder in web staging area
        #Delete the in memory file

        try:
            fc = arcpy.Project_management(layer, "in_memory", spatial_ref)
            try:
                arcpy.DeleteField_management(fc, select_fields)
            except:
                if arcpy.Exists(fc) and select_fields is not None:
                    arcpy.Delete_management(fc)
                    arcpy.AddMessage("Selected fields deleted.  Commencing next geoprocessing function.")
                arcpy.AddMessage("No fields selected to be deleted.  Commencing next geoprocessing function.")
            fc_rename = arcpy.Rename_management(fc, layer_name)
            arcpy.FeatureClassToShapefile_conversion(fc_rename, folder)
            if arcpy.Exists(fc_rename):
                arcpy.Delete_management(fc_rename)
            arcpy.AddMessage("Tool stage 1 complete: feature class reprojectd, selected fields deleted, shapefile saved.")
        except:
            if arcpy.Exists(fc_rename):
                arcpy.Delete_management(fc_rename)
            arcpy.AddMessage("Tool stage 1 incomplete.")

        #Create zip and layer metadata
        description = parameters[3].valueAsText
        tags = parameters[4].valueAsText
        new_tags = parameters[5].valueAsText
        access_info = parameters[6].valueAsText
        culture = parameters[7].valueAsText
        license_info = parameters[8].valueAsText
        snippet = parameters[9].valueAsText
        zip_folder = parameters[10].valueAsText

        #format tags
        tags_formatted = tags.replace("'", "").replace(";", ", ")

        # new_desc = arcpy.Describe(new_layer)
        # layer_name = new_desc.baseName
        layer_path = folder + os.sep + layer_name
        full_path = layer_path + '.shp'
        arcpy.AddMessage("layer path: " + layer_path)
        #create zip
        utils.create_zip(layer_path, zip_folder)
        #create metadata
        layer_dict = utils.layer_metadata_to_dict(full_path, tags_formatted, new_tags, description, access_info, culture, license_info, snippet)
        json_path_filename = zip_folder + os.sep + layer_name + ".zip.metadata.txt"
        utils.write_to_json(json_path_filename, layer_dict)
        arcpy.AddMessage("Tool stage 2 complete: zip created with metadata")
        # except:
        #     arcpy.AddMessage("Failed to execute tool. Check the input file has a defined projection.")

        ##################################################################################################

        return


class CreateZipLayerMetadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Layer preparation part 2: Zip shapefile with metadata for web kiosk download"
        self.description = "Takes an input shapefile and zips it and saves it to the 'zip_data_path' path set in the config tool."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Shapefile to zip",
            name="input_layer",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")

        parameter1 = arcpy.Parameter(
            displayName="Metadata layer description",
            name="metadata_description",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter2 = arcpy.Parameter(
            displayName="Metadata tags",
            name="metadata_tags",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            enabled="True",
            multiValue=True)

        parameter2.filter.list = utils.read_txt_to_list(utils.get_tools_install_directory() + os.sep + "docs" + os.sep + "metadata_tags.txt")

        parameter3 = arcpy.Parameter(
            displayName="Add custom tags, comma separated value",
            name="metadata_custom_tags",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        parameter3.value = "MapAction, "

        parameter4 = arcpy.Parameter(
            displayName="Metadata access information",
            name="metadata_access",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter4.filter.list = utils.get_metadata_permissions_list()

        parameter5 = arcpy.Parameter(
            displayName="Metadata license information",
            name="metadata_license",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter5.value = "Copyright MapAction 2014"

        parameter6 = arcpy.Parameter(
            displayName="Metadata culture information",
            name="metadata_culture",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter6.value = "English (united kingdom)"

        parameter7 = arcpy.Parameter(
            displayName="Metadata snippet",
            name="metadata_snippet",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter8 = arcpy.Parameter(
            displayName="Zip data directory (Set in the web mapping config tool)",
            name="web_layer_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            enabled="False")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            parameter8.value = data["zip_data_path"]
        else:
            parameter8.value = "Close tool and set the 'zip_data_path' using the config tool."

        parameters = [parameter0, parameter1, parameter2, parameter3, parameter4,
                      parameter5, parameter6, parameter7, parameter8]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return


    def updateMessages(self, parameters):
        return


    def execute(self, parameters, messages):
        """

        """
        layer = parameters[0].valueAsText
        description = parameters[1].valueAsText
        tags = parameters[2].valueAsText
        new_tags = parameters[3].valueAsText
        access_info = parameters[4].valueAsText
        culture = parameters[5].valueAsText
        license_info = parameters[6].valueAsText
        snippet = parameters[7].valueAsText
        folder = parameters[8].valueAsText

        #format tags
        tags_formatted = tags.replace("'", "").replace(";", ", ")

        desc = arcpy.Describe(layer)
        layer_name = desc.baseName

        #this is only used if the drop down facility in the tool gui is used.
        # If the first parameter is datatype="DEShapefile" then this is not true.
        if not os.path.isfile(layer):
            layer = desc.path + os.sep + desc.file
            arcpy.AddMessage(str(layer))

        #create zip
        utils.create_zip(layer, folder)
        #create metadata
        layer_dict = utils.layer_metadata_to_dict(layer, tags_formatted, new_tags, description, access_info, culture, license_info, snippet)
        json_path_filename = folder + os.sep + layer_name + ".zip.metadata.txt"
        utils.write_to_json(json_path_filename, layer_dict)
        return


class CreatePdfLayerMetadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "01 - Create PDF"
        self.description = "Creates a pdf of the current mxd layout, use the form to fill in metadata that will be saved with the pdf."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Metadata description",
            name="metadata_description",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter1 = arcpy.Parameter(
            displayName="Metadata tags",
            name="metadata_tags",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            enabled="True",
            multiValue=True)

        parameter1.filter.list = utils.read_txt_to_list(utils.get_tools_install_directory() + os.sep + "docs" + os.sep + "metadata_tags.txt")

        parameter2 = arcpy.Parameter(
            displayName="Add custom tags, comma separated value",
            name="metadata_custom_tags",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        parameter2.value = "MapAction, "

        parameter3 = arcpy.Parameter(
            displayName="Metadata access information",
            name="metadata_access",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter3.value = "No access restrictions"

        parameter4 = arcpy.Parameter(
            displayName="Metadata license information",
            name="metadata_license",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter4.value = "Copyright MapAction 2014"

        parameter5 = arcpy.Parameter(
            displayName="Metadata culture information",
            name="metadata_culture",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter5.value = "English (united kingdom)"

        parameter6 = arcpy.Parameter(
            displayName="Metadata snippet",
            name="metadata_snippet",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        parameter7 = arcpy.Parameter(
            displayName="Path to save current mxd layout to PDF (set in the web mapping config tool)",
            name="web_layer_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            enabled="False")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            parameter7.value = data["pdf_data_path"]
        else:
            parameter7.value = "Close tool and set the 'pdf_data_path' using the config tool."

        parameter8 = arcpy.Parameter(
            displayName="PDF quality",
            name="pdf_quality",
            datatype="GPString",
            parameterType="required",
            direction="Input",
            enabled="true",
            category="PDF Options")

        parameter8.filter.list = ["BEST", "BETTER", "NORMAL", "FASTER", "FASTEST"]
        parameter8.value = "BEST"

        parameter9 = arcpy.Parameter(
            displayName="PDF resolution(dpi)",
            name="pdf_resolution",
            datatype="GPLong",
            parameterType="Required",
            direction="Input",
            enabled="true",
            category="PDF Options")

        parameter9.filter.list = range(25, 625, 25)
        parameter9.value = 300

        parameters = [parameter0, parameter1, parameter2, parameter3, parameter4,
                      parameter5, parameter6, parameter7, parameter8, parameter9]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return


    def updateMessages(self, parameters):
        return


    def execute(self, parameters, messages):
        """

        """
        description = parameters[0].valueAsText
        tags = parameters[1].valueAsText
        new_tags = parameters[2].valueAsText
        access_info = parameters[3].valueAsText
        culture = parameters[4].valueAsText
        license_info = parameters[5].valueAsText
        snippet = parameters[6].valueAsText
        folder = parameters[7].valueAsText
        pdf_quality = parameters[8].valueAsText
        pdf_resolution = parameters[9].valueAsText

        #format tags
        tags_formatted = tags.replace("'", "").replace(";", ", ")

        #map document name
        mxd = arcpy.mapping.MapDocument("CURRENT")
        file_path = mxd.filePath
        path, file = os.path.split(file_path)
        base_name = os.path.splitext(file)[0]


        #create metadata
        layer_dict = utils.pdf_metadata_to_dict(mxd, base_name, tags_formatted, new_tags, description, access_info, culture, license_info, snippet)
        json_path_filename = folder + os.sep + base_name + ".pdf.metadata.txt"
        utils.write_to_json(json_path_filename, layer_dict)
        pdf_path = folder + os.sep + base_name + ".pdf"
        utils.export_to_pdf(mxd, pdf_path, pdf_resolution, pdf_quality)
        return


class ConfigTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Configuration tool"
        self.description = "Set the config paths for the toolset."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Output zip and metadata folder",
            name="zip_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            if 'zip_data_path' in data:
                parameter0.value = data["zip_data_path"]

        parameter1 = arcpy.Parameter(
            displayName="Output pdf and metadata folder",
            name="pdf_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            if 'pdf_data_path' in data:
                parameter1.value = data["pdf_data_path"]

        parameter2 = arcpy.Parameter(
            displayName="Staging data location",
            name="web_layer_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            if 'staging_data_path' in data:
                parameter2.value = data["staging_data_path"]

        parameter3 = arcpy.Parameter(
            displayName="Web staging map document(.mxd)",
            name="web_staging_mxd",
            datatype="DEMapDocument",
            parameterType="Required",
            direction="Input")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            if 'web_mxd_path' in data:
                parameter3.value = data["web_mxd_path"]

        parameter4 = arcpy.Parameter(
            displayName="Layer validation results(.txt)",
            name="layer_validation_filepath",
            datatype="DETextfile",
            parameterType="Required",
            direction="Input")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            if 'layer_validation_path' in data:
                parameter4.value = data["layer_validation_path"]
        else:
            if os.path.exists(utils.get_tools_install_directory() + os.sep + "docs" + os.sep + "layer_validation.txt"):
                parameter4.value = utils.get_tools_install_directory() + os.sep + "docs" + os.sep + \
                    "layer_validation.txt"

        parameters = [parameter0, parameter1, parameter2, parameter3, parameter4]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return


    def updateMessages(self, parameters):
        return


    def execute(self, parameters, messages):
        """
        Desc: Get the values from the input parameters, create a python dictionary
        to store the configuration key / value pairs that will get written into
        JSON.  Create a new file path / name inside the config folder in the
        tools install directory.  Write the python dictionary to the JSON file.
        """

        p0 = parameters[0].valueAsText
        p1 = parameters[1].valueAsText
        p2 = parameters[2].valueAsText
        p3 = parameters[3].valueAsText
        p4 = parameters[4].valueAsText

        data = {'zip_data_path': p0, 'pdf_data_path': p1, 'staging_data_path': p2, 'web_mxd_path': p3, 'layer_validation_path': p4}
        utils.write_to_json(utils.config_file_path(), data)

        # import the current toolbox and launch scripts programatically
        # arcpy.ImportToolbox(r"C:\Users\Greg\Desktop\MapActionWebMappingToolsRepo\WebMappingTools.pyt")
        # #try:
        #     # Run tool in the custom toolbox.  The tool is identified by
        #     #  the tool name and the toolbox alias.
        #     # arcpy.WebAnalyzeResults_WebMappingTools()
        # arcpy.CreatePdfLayerMetadata_WebMappingTools()
        # #except arcpy.ExecuteError:
        #    # print(arcpy.GetMessages(2))

        return


class DeleteFieldsReprojectCopyDataToWebStagingTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Layer preparation part 1: Reproject, delete fields & copy to web staging data folder"
        self.description = "Copy a feature class to the web staging folder for using as a web service.  Delete " \
                           "unnecessary fields to limit file size and reproject the data if required."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""


        parameter0 = arcpy.Parameter(
            displayName="Input layer",
            name="input_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        parameter1 = arcpy.Parameter(
            displayName="Select fields to delete",
            name="delete_fields",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            enabled="True",
            multiValue=True)
            #category="Delete fields")

        parameter2 = arcpy.Parameter(
            displayName="Staging data location",
            name="web_layer_destination",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            enabled="False")

        if utils.config_file_path_exists():
            data = utils.read_from_json_file_to_dict(utils.config_file_path())
            parameter2.value = data["staging_data_path"]
        else:
            parameter2.value = "Close tool and set 'staging_data_path' using the config tool."

        parameters = [parameter0, parameter1, parameter2]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        layer = parameters[0].valueAsText
        fields = []
        if layer is not None:
            for x in arcpy.ListFields(layer):
                fields.append(str(x.name))
            #after getting a list of the fields in the table
            #remove required fields from the list so they cannot be deleted
            remove_fields = ["FID", "OBJECTID", "Shape", "Shape_Area", "Shape_Length"]
            for field in remove_fields:
                if field in fields:
                    fields.remove(field)
            parameters[1].filter.list = fields


        return


    def updateMessages(self, parameters):
        return


    def execute(self, parameters, messages):
        """

        :param parameters:
        :param messages:
        :return:
        """
        #Assign the parameter values from the tool
        layer = parameters[0].valueAsText
        select_fields = parameters[1].valueAsText
        folder = parameters[2].valueAsText

        desc = arcpy.Describe(layer)
        layer_name = os.path.splitext(str(desc.name))[0]
        #layer_type = str(desc.type)

        #Set the output file path
        file_path = folder + os.sep + layer_name #+ ".shp"
        #create the spatial reference object (from the data frame[0] of web staging)
        mxd_path = utils.get_web_staging_mxd_path()
        spatial_ref = utils.spatial_reference_from_dataframe(mxd_path)

        #reproject the selected feature class and save into memory
        #Delete the selected fields in the GUI
        #rename the file
        #save the file as a shapefile to the data folder in web staging area
        #Delete the in memory file
        try:
            fc = arcpy.Project_management(layer, "in_memory", spatial_ref)
            arcpy.DeleteField_management(fc, select_fields)
            fc_rename = arcpy.Rename_management(fc, layer_name)
            arcpy.FeatureClassToShapefile_conversion(fc_rename, folder)
            arcpy.Delete_management(fc_rename)
        except:
            arcpy.AddMessage("Failed to execute tool. Check the input file has a defined projection.")

        return


class WebAnalyzeResults(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "06 - Analyse web map & MA validation to text"
        self.description = "Exports a text file, given a location of the arcpy 'AnalyzeForSD' function."
        self.canRunInBackground = False


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        #msg = arcpy.addMessage("Test output message from custom tool")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # parameter1 = parameters[0].valueAsText
        mxd = arcpy.mapping.MapDocument("CURRENT")
        service = os.path.splitext(os.path.basename(mxd.filePath))[0]
        output = utils.get_tools_install_directory() + os.sep + "docs"  + os.sep
        sddraft = output + service + ".sddraft"
        output_file = output + os.sep + "web_analyse.txt"
        analysis = arcpy.mapping.CreateMapSDDraft(mxd, sddraft, service, 'ARCGIS_SERVER')

        with open(output_file, 'w') as text_file:
            for key in ('errors', 'warnings', 'messages'):
                text_file.write("----" + key.upper() + "----\n\n")
                vars = analysis[key]
                for ((message, code), layerlist) in vars.iteritems():
                    text_file.write("    " + message + " (CODE %i)" % code + "\n")
                    text_file.write("       applies to:\n"),
                    for layer in layerlist:
                        text_file.write("           " + layer.name + "\n"),
                    text_file.write("\n")
                print
            text_file.write("\n" + "MapAction tests: " + "\n")
            for key, value in analysis['messages'].iteritems():
                text_file.write("key: " + str(key) + "value: " + str(value) + "\n")
            dict_len = str(len(analysis['warnings']))
            text_file.write("\n" + "Some further tests: " + "warnings count: " + dict_len + "\n")

        text_file.close()

        webbrowser.open(output_file)
        os.remove(sddraft)
        #analyse the service definition draft
        #analysis = arcpy.mapping.AnalyzeForSD(sddraft)

        # with open(parameters[0].valueAsText, 'w') as text_file:
        #     text_file.write(mxd_name)
        #     text_file.close()

        return
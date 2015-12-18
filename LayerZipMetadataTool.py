import arcpy
import json


class LayerZipMetadata(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Greg's test WebMappingTools.pyt"
        self.description = "This tool is proper awesome: Greg's tool"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameter0 = arcpy.Parameter(
            displayName="Input feature class",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        parameter1 = arcpy.Parameter(
            displayName="Your name",
            name="name_field",
            datatype="String",
            parameterType="Required",
            direction="Input")

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
        #msg = arcpy.addMessage("Test output message from custom tool")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        parameter1 = parameters[0].valueAsText

        arcpy.mapping.Layer(parameter1).visible = False
        arcpy.RefreshActiveView()
        arcpy.AddMessage("message...testing 1,2,3,..")
        feature_count = str(arcpy.GetCount_management(parameter1))
        spatial_ref = str(arcpy.Describe(parameter1).spatialReference.factoryCode)
        data = {'feature count': feature_count, 'Spatial reference': spatial_ref}

        with open('c://temp/data.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        return
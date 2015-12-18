__author__ = 'Mr Greg Vaughan'

import arcpy
import MapActionUtils as utils


class LayerProperties:
    """ Layer properties class """

    def __init__(self, layer):
        self.layer = layer
        self.name = self.get_layer_name()
        self.type = self.get_layer_type()
        self.sr_name = self.get_layer_spatial_reference_name()
        self.sr_code = self.get_layer_spatial_reference_code()
        self.feature_count = self.get_feature_count()
        self.field_count = self.get_field_count()
        self.extent = self.get_spatial_extent()

    def get_layer_name(self):
        return arcpy.Describe(self.layer).baseName

    def get_layer_type(self):
        return arcpy.Describe(self.layer).dataType

    def get_layer_spatial_reference_name(self):
        return arcpy.Describe(self.layer).spatialReference.name

    def get_layer_spatial_reference_code(self):
        return arcpy.Describe(self.layer).spatialReference.factoryCode

    def get_feature_count(self):
        feature_count = arcpy.GetCount_management(self.layer)
        return str(feature_count)

    def get_field_count(self):
        field_list = arcpy.ListFields(self.layer)
        return len(field_list)

    def get_spatial_extent(self):
        extent = {}
        extent["XMax"] = arcpy.Describe(self.layer).extent.XMax
        extent["XMin"] = arcpy.Describe(self.layer).extent.XMin
        extent["YMax"] = arcpy.Describe(self.layer).extent.YMax
        extent["YMin"] = arcpy.Describe(self.layer).extent.YMin
        return extent

    def __str__(self):
        return "%s is a %s layer" % (self.name, self.type)


class EvaluateLayer(LayerProperties):
    """ Layer validation class """

    def __init__(self, layer):
        LayerProperties.__init__(self, layer)
        self.warnings = {}
        self.errors = {}
        self.eval_features = self.evaluate_feature_count()
        self.eval_fields = self.evaluate_field_count()
        self.eval_sr = self.evaluate_spatial_ref_web_staging_mxd()
        self.eval_results = self.evaluation_results()[0]
        self.eval_messages = self.evaluation_results()[1]
        self.eval_tests = self.evaluation_results()[2]

    ###Validations tests
    #def check feature count is <= 1000
    #def check spatial reference == web staging mxd spatial reference
    #def check count of attribute fields <= 20 (20???)

    def evaluate_feature_count(self):
        """
        Checks that the feature count is <1000
        :return: True if the count is <1000
        """
        feature_max = 1000
        if int(self.feature_count) < feature_max:
            return True
        else:
            return False

    def evaluate_field_count(self):
        """
        Checks that the field count is <20
        :return: True if the count is <20
        """
        field_max = 20
        if int(self.field_count) < field_max:
            return True
        else:
            return False

    def evaluate_spatial_ref_web_staging_mxd(self):
        """
        Checks that the spatial reference of the layer against the spatial reference of
        the first data frame in the web staging mxd
        :return: a dictionary with a key of the data frame name in web staging mxd and a
        boolean value if it is the same as the layer.  True means they are the same.
        """
        if self.sr_name == utils.get_web_staging_spatial_ref():
            return True
        else:
            return False

    def evaluation_results(self):
        """
        Results of several evaluation tests for defined for the web map process (feature count, spatial reference and field count).
        :return: lists of the tests, results and messages with values depending on the results of the if statements
        """
        list = []
        results = []
        messages = []
        tests = ["Feature count", "Field count", "Spatial reference"]

        if self.eval_features:
            results.append("Pass")
            messages.append("The feature count (%s) is within than the recommended <1000 features." % self.feature_count)
        else:
            results.append("Fail")
            messages.append("The feature count (%s) is greater than the recommended <1000 features." % self.feature_count)

        if self.eval_fields:
            results.append("Pass")
            messages.append("The field count (%s) is within the recommended maximum of 20 fields." % self.field_count)
        else:
            results.append("Fail")
            messages.append("The field count (%s) is greater than the recommended <20 fields." % self.field_count)

        if self.eval_sr:
            results.append("Pass")
            messages.append("The spatial reference %s is the same as the web staging map document %s." % (self.sr_name, utils.get_web_staging_spatial_ref()))
        else:
            results.append("Fail")
            messages.append("The spatial reference %s is not the same as the web staging map document %s." % (self.sr_name, utils.get_web_staging_spatial_ref()))

        list.append(results)
        list.append(messages)
        list.append(tests)
        return list




"""
vector_prep.py
POC - chaz.mateer@gmail.com

Vector prep is an in-progress module of utility functions for preparing vector
data for further processing.  See individual docstrings for more information.
"""

# Import modules
import arcpy
import os
import traceback

# Repair vector geometries
def repair_geom(vector_list, workspace, solo_fc=False):
    """Runs the repair geometry tool on all input feature classes.

    Only requries ArcBasic.  Runs repair geometry on all input feature classes.  Requires a list of feature class paths. Copies FC to workspace first, then runs repair geom.

    Args:
        arg1 (list): A list of feature class path strings.
        arg2 (str): Path to output workspace.  FC will be copied to this location.

    Returns:
        bool: True if completed, False if it did not complete correctly.

    """
    # Can maybe get rid of this expression if I use GetParameter instead of get as text
    # vector_list = vector_list.split(";")
    new_fc_list = []
    if solo_fc:
        vector_list = [vector_list]
    for fc in vector_list:
        og_name = os.path.split(str(fc))[1]
        new_name = os.path.join(workspace, og_name)
        # Copy FC to a new location
        handled_name = old_to_new(fc, new_name)
        new_fc_list.append(handled_name)
        arcpy.RepairGeometry_management(handled_name)
    if solo_fc:
        return new_fc_list[0]
    else:
        return new_fc_list

# Copy old to new
def old_to_new(old, new):
    new_name = handle_name(new)
    arcpy.CopyFeatures_management(old, new_name)
    return new_name

# Unify SRS
def unify_srs(fc_list, workspace, solo_fc=False):
    """Set SRS of input list of FC to specified SRS.

    Takes in a list of feature classes and checks to see if they are in the specified SRS.  If not, they are reprojected.

    Args:
        arg1

    Returns:
        bool: True if completed, False if it did not complete correctly.

    """
    new_fc_list = []
    if solo_fc:
        fc_list = [fc_list]
    for fc in fc_list:
        og_name = os.path.split(fc)[1]
        new_name = handle_name(os.path.join(workspace, og_name))
        new_fc_list.append(new_name)
        # WGS 1984 GCS
        srs = arcpy.SpatialReference(4326)
        arcpy.Project_management(fc, new_name, srs)
    if solo_fc:
        return new_fc_list[0]
    else:
        return new_fc_list

# Handle names
def handle_name(input_name):
    """
    Don't try this with shapefiles yet.  Will need to add some functionality first because of the file extension being in the way.

    Need to test if this respects environment settings.  For now you have to pass in the full path I think.

    """
    counter = 1
    og_name = input_name
    while arcpy.Exists(input_name):
        input_name = og_name + "_{0}".format(counter)
        counter += 1
    return input_name

# For testing
def main():
    pass

if __name__ == '__main__':
    main()

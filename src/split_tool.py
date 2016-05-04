"""
ShapeSPlitter
POC - Chaz Mateer chaz.mateer@gmail.com

Python Script that requires the arcpy module and the advanced license.  Created to split and input polygon's geometry by one or many input polygons.  Splits the dataset whiel maintaining original attributes and removes duplicate geometries.

Arguments (script tool data type):
argv(0) = List of input polygons to split the main polygon (Multivalue Feature Class)
argv(1) = Main polygon (Feature Class)
argv(2) = Output folder (Folder)

This script is meant to be added to an ArcGIS toolbox and run as a script
tool.  There will be three main input dialogues.

You can run this script tool in either ArcBasic or ArcAdvanced, though it will
run faster in ArcAdvanced and will end up doing more work for you.  The script
attempts to use ArcAdvanced tools to clean up the resulting dataset (removing
junk fields, identical features, and null values) using ArcAdvanced tools.  If
you are using Advanced then no problem.  If you are not the script will try to
do the same, although slower, with XTools Pro.  If you do not have XTools, have
an old version, or did not install XTools in the default directory this step
will not work.  The script will tell you this in the message log and you will
have to clean up the dataset manually, install XTools and re-run, or re-run on
the Advanced VM.

"""

# Import modules
import os
import arcpy
import traceback
from vector_prep import \
repair_geom,\
unify_srs,\
handle_name

##################

# Split input data using geoprocessing
def split_input(input_criteria, input_parcel, output):
    """
    TODO

    """
    # Local var
    merge_temp = "MergedCriteria_Scratch"
    clip_temp = "ClippedParcels_Scratch"

    # Merge input criteria together
    arcpy.AddMessage("Merging criteria...")
    arcpy.Merge_management(input_criteria, merge_temp)
    # Clip parcels by merged criteria
    arcpy.AddMessage("Clipping parcels to criteria extent...")
    arcpy.Clip_analysis(input_parcel, merge_temp, clip_temp)
    # Union merged criteria with parcel dataset
    arcpy.AddMessage("Unioning criteria and parcels...")
    arcpy.Union_analysis([clip_temp, merge_temp], output)

    # Clean up
    clean_up_fc([merge_temp, clip_temp])

# Delete duplicates
def delete_dupeys(input_fc):
    """
    TODO

    """
    # Local var
    shape_field = "Shape"
    ep_dupeys_temp = handle_name("ep_dupeys_temp")
    duplicates_deleted = False
    xtools_path = r"C:\Program Files (x86)\DataEast\XTools Pro\Toolbox\XTools Pro.tbx" # Default location of XTools Pro

    # Try to use ArcAdvanced tools
    arcpy.AddMessage("Attempting to delete duplicates using ArcAdvanced tools...")
    if arcpy.ProductInfo() == "ArcInfo":
        arcpy.DeleteIdentical_management(input_fc, [shape_field])
        duplicates_deleted = True
    else:
        arcpy.AddMessage("You do not have access to ArcAdvanced, attempting to use XTools...")
        try:
            # Try to pull in the Xtools toolbox.  Assumes default, will need to be updated on new install
            arcpy.ImportToolbox(xtools_path)
            # Find and remove duplicates
            arcpy.XToolsPro_FindDuplicates(input_fc, [shape_field], ep_dupeys_temp, True, True)
            # Delete og EP FC, copy the temp, delete the temp
            arcpy.Delete_management(input_fc)
            arcpy.CopyFeatures_management(ep_dupeys_temp, input_fc)
            arcpy.Delete_management(ep_dupeys_temp)
            duplicates_deleted = True
        except:
            arcpy.AddMessage("XTools not found, you may not have XTools or may need to specify your install location in the script, SEE GIS SUPPORT FOR ASSISTANCE OR REMOVE DUPLICATES MANUALLY.")
            # If none of the above work the user will have to delete dupeys manually
            arcpy.AddMessage("!!! SOMETHING WENT WRONG.  YOU WILL NEED TO DELETE DUPLICATE FEATURES MANUALLY.")
            duplicates_deleted = False
    # This is a bit 'magical' not sure why the del call above doesn't work
    try:
        arcpy.Delete_management(ep_dupeys_temp)
    except:
        pass

    return duplicates_deleted

# Remove nulls
def remove_nulls(main_input, input_parcels):
    """
    TODO

    """
    # Local var
    main_lyr = handle_name("main_lyr")
    clipped_lyr = handle_name("clipped_lyr")
    ep_dupe_temp = handle_name("ep_dupe_temp")

    # Remove nulls (areas that do not intersect with parcels)
    arcpy.MakeFeatureLayer_management(main_input, main_lyr)
    arcpy.MakeFeatureLayer_management(input_parcels, clipped_lyr)
    arcpy.SelectLayerByLocation_management(main_lyr, "WITHIN", clipped_lyr)
    arcpy.CopyFeatures_management(main_lyr, ep_dupe_temp)
    # Clean up temporary fields and feature classes
    arcpy.Delete_management(main_input)
    arcpy.CopyFeatures_management(ep_dupe_temp, main_input)
    clean_up_fc([main_lyr, clipped_lyr, ep_dupe_temp])

# Clean up intermediate feature classes
def clean_up_fc(fc_list):
    """
    TODO

    """
    for fc in fc_list:
        arcpy.Delete_management(fc)

# Clean up unnecessary fields
def clean_up_fields(junk_fc_list, main_fc, specific_fields=None):
    """
    TODO

    """
    # If the user does not use arg3 make an empty list, otherwise use the list that they passed in
    if specific_fields is None:
        junk_fields = []
    else:
        junk_fields = specific_fields

    for fc in junk_fc_list:
        field_list = arcpy.ListFields(fc)
        for field in field_list:
            if not field.required:
                junk_fields.append(field.baseName)

    arcpy.DeleteField_management(main_fc, junk_fields)

    return junk_fields

##################

def main():
    """
    TODO

    """
    # Unpack arguments
    input_criteria = arcpy.GetParameter(0)
    input_parcel = arcpy.GetParameterAsText(1)
    output_gdb = arcpy.GetParameterAsText(2)
    preventative = arcpy.GetParameter(3)

    # Set environment settings
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = output_gdb

    # Instantiate local variables
    split_parcels = handle_name("ShapeSplitter")
    duplicates_deleted = False
    junk_fields = None

    # Attempt preventative maintenance if it was specified
    if preventative:
        arcpy.AddMessage("Attempting preventative maintenance, this may take some time...")
        # Repair geom
        repaired_criteria = repair_geom(input_criteria, output_gdb)
        repaired_parcel = repair_geom(input_parcel, output_gdb, solo_fc=True)
        # Unify SRS
        input_criteria = unify_srs(repaired_criteria, output_gdb)
        input_parcel = unify_srs(repaired_parcel, output_gdb, solo_fc=True)

    # Preform the merge, clip, and split
    arcpy.AddMessage("Performing the split...")
    split_input(input_criteria, input_parcel, split_parcels)

    # Delete dupeys
    arcpy.AddMessage("Deleting duplicates...")
    duplicates_deleted = delete_dupeys(split_parcels)

    # Remove nulls
    arcpy.AddMessage("Removing null features...")
    remove_nulls(split_parcels, input_parcel)

    # Repair Geom
    arcpy.AddMessage("Repairing geometries in EPSplitParcels...")
    arcpy.RepairGeometry_management(split_parcels)

    # Clean up junk fields and FCs
    arcpy.AddMessage("Cleaning up temporary files...")
    junk_fields = clean_up_fields(input_criteria, split_parcels, ["FID_ClippedParcels_Scratch", "FID_MergedCriteria_Scratch"])

    if preventative:
        clean_up_list = [repaired_parcel, input_parcel]
        clean_up_list.extend(repaired_criteria)
        clean_up_list.extend(input_criteria)
        clean_up_fc(clean_up_list)

    if duplicates_deleted:
        dupeys_message = "Duplicates have been deleted.  No need to delete them manually."
    else:
        dupeys_message = "Duplicates have NOT been deleted.  You will need to remove them manually or re-run this script on an ArcAdvanced machine/one with XTools installed in the defualt location."

    final_output_message = """
    Parcels split successfully!

    {0}

    Null values have been removed successfully.

    The following fields have been removed:
    {1}

    Your output feature class: {2} is ready to be used as your analysis layer!
    """.format(dupeys_message, junk_fields, split_parcels)

    arcpy.AddMessage(final_output_message)

    # For testing
    return final_output_message

if __name__ == '__main__':
    try:
        main()
    except:
        arcpy.AddMessage("OPERATION FAILED!")
        arcpy.AddMessage(traceback.format_exc())

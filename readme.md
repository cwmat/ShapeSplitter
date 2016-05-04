#ShapeSplitter
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

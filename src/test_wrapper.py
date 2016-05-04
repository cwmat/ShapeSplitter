import arcpy
import traceback
import split_tool

name_mod = arcpy.GetParameterAsText(4)
output_file = "G:\\GIS\\Models_Tools\\Production\\EPModel\\tests\\testing\\test_zone\\ep_model_testing\\errors\\{0}_errors.txt".format(name_mod)
messages_file = "G:\\GIS\\Models_Tools\\Production\\EPModel\\tests\\testing\\test_zone\\ep_model_testing\\errors\\{0}_messages.txt".format(name_mod)

try:
    final_message = split_tool.main()
    with open(messages_file, "w+") as w_file:
        w_file.write(final_message)
except:
    with open(output_file, "w+") as w_file:
        w_file.write(traceback.format_exc());

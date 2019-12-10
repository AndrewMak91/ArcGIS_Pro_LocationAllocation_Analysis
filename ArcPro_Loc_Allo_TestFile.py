#################################################
"""
Create an Location - Allocation model for ArcPro
Python v 3.6.6
Current ArcPro 2.3.2 NA
Model type -- Maximize Coverage
Candidate, Required and 1 Chosen DC Facility
Travel Time
Impedance cutoff = 320 min
Weight = Demand
"""
#################################################

try:
    # Import libraries
    import arcpy
    from arcpy import env
    import arcpy.na
    import os
    import json
    import numpy as np
    
    # Check for NA Extension
    if arcpy.CheckExtension("network") == "Available":
        arcpy.CheckOutExtension("network")
    else:
        raise arcpy.ExecuteError("Network Analyst Extension not available.")

    # Environment settings
    output_dir = r'D:\Python_Tools_Code\Location_Allocation' # switch out with your workspace file path
    env.workspace = os.path.join(output_dir, "Loc_Alloc_py.gdb")
    env.overwriteOutput = True
    
    # Set network route feature dataset and input data -- set local environment parameters
    na_network_data_source = r'C:\ArcGIS\Business Analyst\US_2018\Data\Streets Data\NorthAmerica.gdb\Routing\Routing_ND' # point to Routing_ND feature dataset
    input_gdb = r'D:\Python_Tools_Code\Location_Allocation\Loc_Alloc_py\Loc_Alloc_py.gdb' # point to user geodatabase file path

    # User input variables for layer name and travel mode
    layer_name = str(input("Enter location allocation layer name: ")) # create layer name for Location Allocation model
    travel_modes = {1 : "Driving Time", 2 : "Driving Distance", 3 : "Trucking Time", 4 : "Trucking Distance", 5 : "Walking Time", 6 : "Walking Distance", 7 : "Rural Driving Time", 8 : "Rural Driving Distance"}
    # travel_modes = travel_modes.items()
    travel_mode = float(input(
        "Select number for travel mode type:" '\n'
        "[1] Driving Time" '\n'
        "[2] Driving Distance" '\n'
        "[3] Trucking Time" '\n'
        "[4] Trucking Distance" '\n'
        "[5] Walking Time" '\n'
        "[6] Walking Distance" '\n'
        "[7] Rural Driving Time" '\n'
        "[8] Rural Driving Distance" '\n'
    ))

    '''
    # Test travel mode consolidated build
    '''
    
    get_travel_modes = arcpy.na.GetTravelModes(na_network_data_source)
    travel_mode = [1, 2, 3, 4, 5, 6, 7, 8]
    travel_mode_selected = [get_travel_modes['Driving Time'], get_travel_modes['Driving Distance'], get_travel_modes['Trucking Time'], get_travel_modes['Trucking Distance'], get_travel_modes['Walking Time'], get_travel_modes['Walking Distance'], get_travel_modes['Rural Driving Time'], get_travel_modes['Rural Driving Distance']]

    '''
    # End Test travel mode consolidated build
    '''
    
    # Build comprehensive list to loop through TravelMode and select user input
    get_travel_modes = arcpy.na.GetTravelModes(na_network_data_source)
        
    if travel_mode == 1:
        travel_mode_selected = get_travel_modes['Driving Time']
        pass
    elif travel_mode == 2:
        travel_mode_selected = get_travel_modes['Driving Distance']
        pass
    elif travel_mode == 3:
        travel_mode_selected = get_travel_modes['Trucking Time']
        pass
    elif travel_mode == 4:
        travel_mode_selected = get_travel_modes['Trucking Distance']
        pass
    elif travel_mode == 5:
        travel_mode_selected = get_travel_modes['Walking Time']
        pass
    elif travel_mode == 6:
        travel_mode_selected = get_travel_modes['Walking Distance']
        pass
    elif travel_mode == 7:
        travel_mode_selected = get_travel_modes['Rural Driving Time']
        pass
    elif travel_mode == 8:
        travel_mode_selected = get_travel_modes['Rural Driving Distance']
        pass
    else:
        print("You did not select a travel mode option")

    # travel_mode_selected = [get_travel_modes[travel_mode].name for travel_mode in travel_modes]

    # # Create an Apply Travel Mode function JSON to be used as a method
    # get_travel_modes = arcpy.na.GetTravelModes(na_network_data_source)
    # dd_travel_modes = get_travel_modes["Driving Distance"]
    # travel_mode_json = json.loads(str(dd_travel_modes))
    # travel_mode_json["restrictionAttributeNames"] = "Driving an Automobile"
    # travel_mode_json["name"] = 'Driving Distance with Automobile'
    # new_travel_mode_object = arcpy.na.TravelMode(json.dumps(travel_mode_json))

    # point to assigned facilities, demand, and/or existing stores shapefile, currently file structure pointing to database --> feature dataset --> point shapefile
    facilities = os.path.join(input_gdb, "Sites", "Facilities") # add facilities shapefile for candidate facilities
    required_facilities = os.path.join(input_gdb, "Sites", "ExistingStore") # add required facilities
    demand_points = os.path.join(input_gdb, "Sites", "Demand") # add demand sites

    # impedanceAttribute = "TravelTime" # impedance factor for location-allocation layer
    
    output_layer_file = os.path.join(output_dir, layer_name + ".lyrx") # results output directory and layer file type for Location Allocation model

    # User input variables
    impedance_value = float(input("Enter cutoff value: "))
    find_facilities = float(input("Enter number of facilities to find: "))

    # Create network analysis location allocation layer
    result_object = arcpy.na.MakeLocationAllocationAnalysisLayer(na_network_data_source, layer_name, travel_mode_selected, "FROM_FACILITIES", "MAXIMIZE_COVERAGE", impedance_value, find_facilities) # creating the location allocaiton model layer and assigning the model to solve a Maximize Capacitated Coverage
    layer_object = result_object.getOutput(0) # get layer object from result so that the network layer can be referenced
    print("Location-Allocation layer created for network locations")
    

    sublayer_names = arcpy.na.GetNAClassNames(layer_object)
    print("Sublayer Names: ", sublayer_names)

    facilities_layer_name = sublayer_names["Facilities"]
    demand_points_layer_name = sublayer_names["DemandPoints"]
    print("Facilities layer name: ", facilities_layer_name)
    print("Demand Points layer name: ", demand_points_layer_name)

    # Load Candidate store locations as facilities and assign ID
    field_mapping_facilities = arcpy.na.NAClassFieldMappings(layer_object, facilities_layer_name)
    field_mapping_facilities["Name"].mappedFieldName = "DC_ID"  # establish DC_ID as the "Name" primary key to rectify facility location data after analysis
    arcpy.na.AddLocations(layer_object, facilities_layer_name, facilities, field_mapping_facilities, "", "", exclude_restricted_elements = "EXCLUDE")
    print("facilities added to layer")

    
    # Load existing store locations as required facilities. Use field mapping to set facility type required, append required facilities to existing
    field_mappings_existing_facility = arcpy.na.NAClassFieldMappings(layer_object, facilities_layer_name)
    field_mappings_existing_facility["FacilityType"].defaultValue = 1
    arcpy.na.AddLocations(layer_object, facilities_layer_name, required_facilities, field_mappings_existing_facility, "", append="APPEND", exclude_restricted_elements="EXCLUDE")

    
    # Load demand point locations as Demand and assign ID
    field_mapping_demand = arcpy.na.NAClassFieldMappings(layer_object, demand_points_layer_name)
    field_mapping_demand["Name"].mappedFieldName = "SC_ID" # establish SC_ID as the "Name" primary key to rectify demand point data after analysis
    field_mapping_demand["Weight"].mappedFieldName = "Demand" # assign weight value from demand field attribute to demand points
    arcpy.na.AddLocations(layer_object, demand_points_layer_name, demand_points, field_mapping_demand, "", exclude_restricted_elements="EXCLUDE")

    print("Demand field mapping: ", field_mapping_demand, "Demand points added to layer")

    # Solve location allocation
    arcpy.na.Solve(layer_object)

    layer_object.saveACopy(output_layer_file)

    print("Location allocation model has been solved.")
 
    
    # arcpy.FeatureClassToFeatureClass_conversion(selected_data_lines,output_dir)
    
    # # Exporting selected facilities and straight lines
    # print("OutNALayer Type: ", type(layer_object))
    # print(layer_object)
    # selected_data_facilities = arcpy.SelectData_management(layer_object, "Facilities")
    # print(selected_data_facilities) 
    # output_path = output_dir
    # arcpy.FeatureClassToFeatureClass_conversion(selected_data_facilities, output_path, "Facilities")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print("An error occured on line %i" % tb.tb_lineno)
    print(str(e))

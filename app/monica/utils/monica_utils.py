def msg_to_json(msg):
    """
    the json output of Monica is processed in this function so that every output 
    is a flat array with the length of the base array e.g. of dates for each output. 
    This is applied to all outputs such as 'daily', 'monthly, 'crop' etc.
    """
    # aggregation constants as dictionary from monica_io3.py
    aggregation_constants = {
        0: "AVG",
        1: "MEDIAN",
        2: "SUM",
        3: "MIN",
        4: "MAX",
        5: "FIRST",
        6: "LAST",
        7: "NONE",
        8: "UNDEFINED_OP"
    }
    # organ constants as dictionary from monica_io3.py
    organ_constants = {
        0: "ROOT",
        1: "LEAF",
        2: "SHOOT",
        3: "FRUIT",
        4: "STRUCT",
        5: "SUGAR",
        6: "UNDEFINED_ORGAN"
    }

    # processed_msg = {}
    for_chart = {}
    for data_ in msg.get("data", []):
        results = data_.get("results", [])
        orig_spec = data_.get("origSpec", "")
        output_ids = data_.get("outputIds", [])
        # print('origSpec', orig_spec, 'output_ids', output_ids)

        orig_spec = orig_spec.replace("\"", "")
        
        for_chart[orig_spec] = {}
        for output_id, result_list in zip(output_ids, results):
            output_id["result"] = result_list
            try:
                output_id["jsonInput"] = json.loads(output_id["jsonInput"])
            except:
                pass
            # soil has layers, yield, LAI etc does not have layers
            if output_id["fromLayer"] == output_id["toLayer"] == -1:
                output_id["result_dict"] = {}
                name = output_id["name"]
                if output_id["organ"] != 6:
                    name = name + "_" + organ_constants[output_id["organ"]]
                    
                output_id["result_dict"][name] = result_list

                for_chart[orig_spec][name] = result_list
            elif output_id["layerAggOp"] != 7:
                output_id["result_dict"] = {}
                output_id["result_dict"][f"{output_id['name']}_{aggregation_constants[output_id['layerAggOp']]}"] = result_list

                for_chart[orig_spec][f"{output_id['name']}_{aggregation_constants[output_id['layerAggOp']]}"] = result_list
            elif (output_id["fromLayer"] != output_id["toLayer"]) and (output_id["layerAggOp"] == 7):
                # no aggregation of layers, but calculations for several layers
                output_id["result_dict"] = {}
                try:
                    for i in range(output_id["fromLayer"], output_id["toLayer"]+1):
                        # print("I: ", i)
                        output_id["result_dict"][f"{output_id['name']}_{i+1}"] = []
                        for j in range(len(result_list)): 
                            output_id["result_dict"][f"{output_id['name']}_{i+1}"].append(result_list[j][i])
                        for_chart[orig_spec][f"{output_id['name']}_{i+1}"] = output_id["result_dict"][f"{output_id['name']}_{i+1}"]
                except:
                    output_id["result_dict"]["error"] = "Error in processing results"
                    

    return for_chart
import datetime

import Constant
from Database import DB
from Database.safety import DB_Hazards, DB_Components_Links, DB_Actions, DB_Components, DB_Losses, \
    DB_Safety_Constraints, DB_Variables, DB_Variables_Values, DB_Projects, DB_Goals, DB_Actions_Components, \
    DB_Assumptions, DB_UCA
from Objects.Loss import Loss_Scenery
from Objects.Requirement import Requirement
from Objects.Var_Values_Aux import Var_Name_Val, Var_Context_list
from Tools import General_tools, Dictionary


# present the analysis of safety requirements
def get_context_a(var_list, position, context, result_list, is_new):

    if len(var_list) == position:
        # analysis_file.write(init_text + " " + context + "\n")
        result_list.append(Var_Context_list("Line " + str(position), context))
        context = []
    else:

        # if len(var_list[position].values_list) == 0:
        #     position_aux = position + 1
        #
        #     if len(var_list) != position_aux and len(var_list[position_aux].values_list) == 0:
        #         position_aux += 1
        #
        #     get_context_a(var_list, position_aux, context, result_list, False)
        # else:
        for val in var_list[position].values_list:
            aux_context = []
            if not is_new:
                aux_context.extend(context)
            aux_context.append(Var_Name_Val(var_list[position].var_name, val.value, val.id_variable, val.id))
            position_aux = position + 1

            if len(var_list) != position_aux and len(var_list[position_aux].values_list) == 0:
                position_aux += 1

            get_context_a(var_list, position_aux, aux_context, result_list, False)

def get_step_four(onto, id_project, controller):
    loss_A_list = ['Algorithm', 'Process_model', 'Sensor', 'Feedback_of_controller', 'External-information-received', 'Controller', 'Feedback_of_CP']
    loss_B_list = ['Actuator', 'Environmental_disturbances', 'Input', 'Control_action_actuator', 'Control_action_CP', 'Control_action_HLC_CP', 'Control_action_HLC_controller']
    result_list = []

    for name_individual in loss_A_list:
        r_list = get_reason_component(onto, controller, name_individual, id_project, Constant.CAUSAL_FACTOR_A, "A")
        if len(r_list) > 0:
            result_list.extend(r_list)

    for name_individual in loss_B_list:
        r_list = get_reason_component(onto, controller, name_individual, id_project, Constant.CAUSAL_FACTOR_B, "B")
        if len(r_list) > 0:
            result_list.extend(r_list)
    return result_list

def get_reason_component(onto, controller, name_individual, id_project, destination, side):
    # print right explanations to factors - components
    list_reason = []
    # reason_list = DB_Components.select_component_by_name_thing_project_analysis(name_individual, id_project)
    # for rc in reason_list:
    object_properties_list = General_tools.get_property_list_ontology(onto, name_individual, destination)
    for cause in get_causal_factor_list(name_individual, id_project, controller, object_properties_list, side):
        list_reason.append(cause)

    return list_reason

# Creates the main list of causal factor
def get_causal_factor_list(causal_factor_name, id_project, controller, object_property_list, side):
    result = []

    if causal_factor_name == Constant.ACTUATOR:
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_ACTUATOR, controller.id, True)
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)

        for comp in comp_list:
            actuator = DB_Components.select_component_by_id(comp.id_component_dst)
            for obj in object_property_list:

                if obj.replace("-", " ") == "delayed":
                    cause = "The issued control action delays to be enforced by the " + actuator.name + "."
                    req = "The " + actuator.name + " shall be reliable and have periodic maintenance."
                    result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))

                if obj.replace("-", " ") == "executed":
                    cause = actuator.name + " performs (" + obj.replace("-", " ") + ") a non-issued control action."
                    req = "The " + actuator.name + " shall be reliable and have periodic maintenance."
                    result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))

                if obj.replace("-", " ") == "not executed" and cp != None:
                    cause = actuator.name + " did not received the control action, from " + controller.name + ", or cannot act (" + obj.replace("-", " ") + ") in " + cp.name + "."
                    req = "The " + actuator.name + " shall be reliable and have periodic maintenance."
                    result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))

                if obj.replace("-", " ") == "failure":
                    cause = "The " + actuator.name + " does not perform its functions."
                    req = "The " + actuator.name + " shall have ongoing analysis after system modification."
                    result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))

        return result

    if causal_factor_name == Constant.ALGORITHM:
        comp_list = DB_Components.select_component_by_project_father_thing(id_project, controller.id, Constant.DB_ID_ALGORITHM)

        for alg in comp_list:
            for obj in object_property_list:
                if obj.replace("-", " ") == "incorrect":
                    cause = "An incorrect " + alg.name + " was designed."
                    req = "The " + alg.name + " shall be revised AND tested when updated."
                    result.append(Loss_Scenery(side, causal_factor_name + "/Logic", alg.name, cause, req, controller.id, alg.id, alg.id, controller.id, alg.name, controller.name, "", Constant.STPA_UNSAFE_CONTROLLER_BEHAVIOR))


                if obj.replace("-", " ") == "ineffective":
                    cause = alg.name + " ineffective after process changes."
                    req = "The " + alg.name + " shall be updated AND revised AND tested."
                    result.append(Loss_Scenery(side, causal_factor_name + "/Logic", alg.name, cause, req, controller.id, alg.id, alg.id, controller.id, alg.name, controller.name, "", Constant.STPA_UNSAFE_CONTROLLER_BEHAVIOR))


                if obj.replace("-", " ") == "updated":
                    cause = alg.name + " updated incorrectly."
                    req = "The " + alg.name + " shall be revised AND tested when updated."
                    result.append(Loss_Scenery(side, causal_factor_name + "/Logic", alg.name, cause, req, controller.id, alg.id, alg.id, controller.id, alg.name, controller.name, "", Constant.STPA_UNSAFE_CONTROLLER_BEHAVIOR))

        return result

    if causal_factor_name == Constant.CONTROL_ACTION_ACTUATOR:
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_ACTUATOR, controller.id, True)
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)

        if cp == None:
            return result

        for comp in comp_list:
            actions_list = DB_Actions_Components.select_actions_by_component_and_project_join_link(comp.id_component_src, id_project, comp.id_component_dst)
            actuator = DB_Components.select_component_by_id(comp.id_component_dst)

            for obj in object_property_list:
                if len(actions_list) > 0:
                    text = ""
                    position = len(actions_list)

                    for act in actions_list:
                        position -= 1
                        text += act.name

                        if position >= 2:
                            text += ", "
                        elif position >= 1:
                            text += " or "

                    if obj.replace("-", " ") == "missing" and cp != None:
                        cause = controller.name + " does not provide (" + obj.replace("-", " ") + ") control action: " + text + "; to " + actuator.name + "."
                        req = "The process model in " + controller.name + " shall represent the " + cp.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))

                    if obj.replace("-", " ") == "missing":
                        cause = "The control action: " + text + " from " + controller.name + " to " + actuator.name + " is " + obj.replace("-"," ") + "."
                        req = "The communication from " + controller.name + " to " + actuator.name + " shall be improved."
                        result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))

                    if obj.replace("-", " ") == "inappropriate" and cp != None:
                        cause = controller.name + " issued an incorrect (" + obj.replace("-", " ") + ") control action: " + text + "; to " + actuator.name + "."
                        req = "The process model in " + controller.name + " shall represent the " + cp.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, actuator.name, cause, req, controller.id, actuator.id, controller.id, actuator.id, controller.name, actuator.name, "", Constant.STPA_CONTROL_PATH))


        return result

    if causal_factor_name == Constant.CONTROL_ACTION_CP:
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_CP, controller.id, True)

        if cp == None:
            return result

        for comp in comp_list:
            # actions_list = DB_Actions_Components.select_actions_by_component_and_project(comp.id_component_src, id_project)
            actions_list = DB_Actions_Components.select_actions_by_component_and_project_join_link(comp.id_component_src, id_project, comp.id_component_dst)

            for obj in object_property_list:
                if len(actions_list) > 0:
                    text = ""
                    position = len(actions_list)

                    for act in actions_list:
                        position -= 1
                        text += act.name

                        if position >= 2:
                            text += ", "
                        elif position >= 1:
                            text += " or "

                    if obj.replace("-", " ") == "missing" and cp != None:
                        cause = controller.name + " does not provide (" + obj.replace("-", " ") + ") the control action: " + text + "; to " + cp.name + "."
                        req = "The process model in " + controller.name + " shall represent the " + cp.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, cp.name, cause, req, controller.id, cp.id, controller.id, cp.id, controller.name, cp.name, "", Constant.STPA_CONTROL_PATH))

                    if obj.replace("-", " ") == "inappropriate" and cp != None:
                        cause = controller.name + " issued an incorrect (" + obj.replace("-", " ") + ") control action: " + text + "; to " + cp.name + "."
                        req = "The process model in " + controller.name + " shall represent the " + cp.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, cp.name, cause, req, controller.id, cp.id, controller.id, cp.id, controller.name, cp.name, "", Constant.STPA_CONTROL_PATH))
        return result

    if causal_factor_name == Constant.CONTROLLER:
        for obj in object_property_list:
            if obj.replace("-", " ") == "failure":
                cause = "The " + controller.name + " controller does not perform its functions to send control actions or receive feedback."
                req = "The " + controller.name + " shall have ongoing analysis after system modification."
                result.append(Loss_Scenery(side, causal_factor_name, controller.name, cause, req, controller.id, controller.id, controller.id, controller.id, controller.name, controller.name, "", Constant.STPA_UNSAFE_CONTROLLER_BEHAVIOR))

        return result

    # OK
    # if causal_factor_name == Constant.EXTERNAL_INFORMATION:
    # if causal_factor_name == Constant.EXTERNAL_INFORMATION_SENT or causal_factor_name == Constant.EXTERNAL_INFORMATION_RECEIVED:
    if causal_factor_name == Constant.EXTERNAL_INFORMATION_RECEIVED:
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_EXT_INFORMATION, controller.id, False)

        for comp in comp_list:
            variables_list = DB_Variables.select_variables_with_value_by_component_project(comp.id_component_src, id_project)

            for obj in object_property_list:
                text = ""

                if len(variables_list) > 0:
                    position = len(variables_list)

                    for var in variables_list:
                        position -= 1
                        text += var.var_name

                        if position >= 2:
                            text += ", "
                        elif position >= 1:
                            text += " or "

                cause = comp.name_src + " is " + obj.replace("-", " ")
                if text != "":
                    cause += " value of: " + text + "."
                else:
                    cause += "."

                if obj.replace("-", " ") == "wrong" or obj.replace("-", " ") == "missing":
                    req = "The communication of the external system to " + controller.name + " shall be improved."
                    result.append(Loss_Scenery(side, causal_factor_name, comp.name_src, cause, req, controller.id, comp.id_component_src, comp.id_component_src, controller.id, comp.name_src, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))


        return result

    if causal_factor_name == Constant.ENVIRONMENTAL_DISTURBANCES:
        cp_list = DB_Components.select_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)

        for cp in cp_list:
            env_dist_list = DB_Components.select_component_by_project_father_thing(id_project, cp.id, Constant.DB_ID_ENV_DISTURBANCES)
            for env_dist in env_dist_list:
                for obj in object_property_list:
                    if obj.replace("-", " ") == "unidentified disturbance":
                        cause = cp.name + " affected by natural or man made disasters."
                        req = "The " + cp.name + " shall be resistant to disasters."
                        result.append(Loss_Scenery(side, causal_factor_name, cp.name, cause, req, controller.id, env_dist.id, env_dist.id, cp.id, env_dist.name, cp.name, "", Constant.STPA_OTHER_FACTORS))

        return result

    if causal_factor_name == Constant.FEEDBACK_OF_CP:
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_SENSOR, controller.id, False)
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)

        if cp == None:
            return result

        comp_list_cp = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_CP, controller.id, False)

        # link controlled process -> controller
        for link2 in comp_list_cp:
            variables_list = DB_Variables.select_variables_with_value_by_component_project(link2.id_component_src, id_project)

            for obj in object_property_list:
                text = ""
                if len(variables_list) > 0:
                    position = len(variables_list)

                    for var in variables_list:
                        position -= 1
                        text += var.var_name

                        if position >= 2:
                            text += ", "
                        elif position >= 1:
                            text += " or "

                if obj.replace("-", " ") == "delayed" and cp != None:
                        cause = "Temporary obstruction does not allow the reading of the " + cp.name + " by " + link2.name_dst + "."
                        req = "The feedback from " + cp.name + " to " + link2.name_dst + " shall have alternative link."
                        result.append(Loss_Scenery(side, causal_factor_name + " by " + cp.name, cp.name, cause, req, controller.id, cp.id, link2.id_component_src, link2.id_component_dst, "", "", "", Constant.STPA_INADEQUATE_FEEDBACK))

                if (obj.replace("-", " ") == "inadequate" or obj.replace("-", " ") == "missing") and cp != None:
                        cause = "Feedback of " + cp.name + " to " + link2.name_dst
                        if text != "":
                            cause += " (" + text + ")"
                        cause += " is " + obj.replace("-", " ") + "."
                        req = "The communication from " + cp.name + " to " + link2.name_dst + " shall be improved."
                        result.append(Loss_Scenery(side, causal_factor_name + " by " + cp.name, cp.name, cause, req, controller.id, cp.id, link2.id_component_src, link2.id_component_dst, "", "", "", Constant.STPA_INADEQUATE_FEEDBACK))

        return result

    if causal_factor_name == Constant.FEEDBACK_OF_CONTROLLER:
        list_controllers = DB_Components.select_component_by_thing_project_exceptId(Constant.DB_ID_CONTROLLER, id_project, controller.id)

        for ctl in list_controllers:
            comp_list_cp = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_CONTROLLER, controller.id, False)
            for link2 in comp_list_cp:
                if ctl.id == link2.id_component_src:
                    variables_list = DB_Variables.select_variables_with_value_by_controller_project_link(link2.id_component_dst, id_project, link2.id)

                    if len(variables_list) > 0:
                        for obj in object_property_list:
                            text = ""
                            if len(variables_list) > 0:
                                position = len(variables_list)

                                for var in variables_list:
                                    position -= 1
                                    text += var.var_name

                                    if position >= 2:
                                        text += ", "
                                    elif position >= 1:
                                        text += " or "

                            if obj.replace("-", " ") == "delayed":
                                cause = "Feedback"
                                if text != "":
                                    cause += " (" + text + ")"
                                cause += " from " + ctl.name + " to " + controller.name + " is delayed."
                                req = "The feedback from " + ctl.name + " to " + controller.name + " shall have alternative link."
                                result.append(Loss_Scenery(side, causal_factor_name + " by " + ctl.name, ctl.name, cause, req, controller.id, ctl.id, ctl.id, controller.id, ctl.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

                            elif obj.replace("-", " ") == "missing":
                                cause = "Feedback from " + ctl.name + " to " + controller.name
                                if text != "":
                                    cause += " (" + text + ")"
                                cause += " is " + obj.replace("-", " ") + "."
                                req = "The communication from " + ctl.name + " to " + controller.name + " shall be improved."
                                result.append(Loss_Scenery(side, causal_factor_name + " by " + ctl.name, ctl.name, cause, req, controller.id, ctl.id, ctl.id, controller.id, ctl.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

        return result

    if causal_factor_name == Constant.PROCESS_MODEL:
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)
        ec = DB_Components.select_component_by_project_father_thing(id_project, controller.id, Constant.DB_ID_EXT_INFORMATION)
        comp_list = DB_Components.select_component_by_project_father_thing(id_project, controller.id, Constant.DB_ID_PROCESS_MODEL)

        if cp != None:
            for pm in comp_list:
                for obj in object_property_list:
                    cause = "Current state of " + pm.name + " is " + obj.replace("-", " ") + "."

                    if obj.replace("-", " ") == "wrong":
                        req = "The process model of " + controller.name + " shall represent the " + cp.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, pm.name, cause, req, controller.id, pm.id, pm.id, controller.id, pm.name, controller.name, "", Constant.STPA_UNSAFE_CONTROLLER_BEHAVIOR))
        return result

    if causal_factor_name == Constant.INPUT:
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)

        if cp == None:
            return result

        list_controlled_process_input = DB_Components.select_component_by_project_father_thing(id_project, cp.id, Constant.DB_ID_INPUT)

        if len(list_controlled_process_input) > 0:
            input = list_controlled_process_input[0]

            list_controlled_process_input_variables = DB_Variables.select_variables_by_component_project(input.id, id_project)

            if len(list_controlled_process_input_variables) > 0:
                variables_list = DB_Variables_Values.select_values_by_variable(list_controlled_process_input_variables[0].id)

                for obj in object_property_list:
                    text = ""
                    position = len(variables_list)
                    for val in variables_list:
                        position -= 1
                        text += val.value

                        if position >= 2:
                            text += ", "
                        elif position >= 1:
                            text += " or "

                    cause = input.name
                    if text != "":
                        cause += " (" + text + ")"
                    cause += " is " + obj.replace("-", " ") + "."

                    if (obj.replace("-", " ") == "missing" or obj.replace("-", " ") == "wrong") and cp != None:
                        req = "The " + cp.name + " shall support the input == " + input.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, input.name, cause, req, controller.id, input.id, input.id, cp.id, input.name, cp.name, "", Constant.STPA_OTHER_FACTORS))

        return result

    if causal_factor_name == Constant.SENSOR:
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_SENSOR, controller.id, False)
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)

        for comp in comp_list:
            sensor = DB_Components.select_component_by_id(comp.id_component_src)

            variables_list = DB_Variables.select_variables_with_value_by_controller_project_link(comp.id_component_dst, id_project, comp.id)
            var_text = ""
            if len(variables_list) > 0:
                    var_text = ""
                    if len(variables_list) > 0:
                        position = len(variables_list)
                        for var in variables_list:
                            position -= 1
                            var_text += var.var_name
                            if position >= 2:
                                var_text += ", "
                            elif position >= 1:
                                var_text += " or "


            for obj in object_property_list:
                if obj.replace("-", " ") == "delayed":
                    if cp != None:
                        cause = "Temporary obstruction does not allow the reading of the " + cp.name + " by " + sensor.name + "."
                        req = "The " + sensor.name + " shall have alternative way to read " + cp.name + "."
                        result.append(Loss_Scenery(side, causal_factor_name, sensor.name, cause, req, controller.id, sensor.id, sensor.id, controller.id, sensor.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

                    cause = "Feedback ("+ var_text +") delays between " + sensor.name + " and " + controller.name + "."
                    req = "The communication of " + sensor.name + " to " + controller.name + " shall be improved."
                    result.append(Loss_Scenery(side, causal_factor_name, sensor.name, cause, req, controller.id, sensor.id, sensor.id, controller.id, sensor.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

                if obj.replace("-", " ") == "wrong" and cp != None:
                    cause = "Current state of the " + cp.name+ " cannot be read accurately by " + sensor.name + "."
                    req = "The " + sensor.name + " shall have accuracy == 0.0x."
                    result.append(Loss_Scenery(side, causal_factor_name, sensor.name, cause, req, controller.id, sensor.id, sensor.id, controller.id, sensor.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

                if obj.replace("-", " ") == "missing":
                    if cp != None:
                        cause = "Feedback of " + sensor.name + " is missing (" + obj.replace("-", " ") + ")."
                        req = "The " + sensor.name + " shall be maintained when time of use == x."
                        result.append(Loss_Scenery(side, causal_factor_name, sensor.name, cause, req, controller.id, sensor.id, sensor.id, controller.id, sensor.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

                    cause = "Feedback ("+ var_text +") lost or corrupted."
                    req = "Communication of " + sensor.name + " to " + controller.name + " shall be improved."
                    result.append(Loss_Scenery(side, causal_factor_name, sensor.name, cause, req, controller.id, sensor.id, sensor.id, controller.id, sensor.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

                if obj.replace("-", " ") == "failure" and cp != None:
                    cause = cp.name + " cannot be read (" + obj.replace("-", " ") + ") by the " + sensor.name + "."
                    req = "The " + sensor.name + " shall be maintained when time of use == x."
                    result.append(Loss_Scenery(side, causal_factor_name, sensor.name, cause, req, controller.id, sensor.id, sensor.id, controller.id, sensor.name, controller.name, "", Constant.STPA_INADEQUATE_FEEDBACK))

        return result

    if causal_factor_name == Constant.CONTROL_ACTION_HLC_CP:
        list_controllers = DB_Components.select_component_by_thing_project_exceptId(Constant.DB_ID_CONTROLLER, id_project, controller.id)

        for ctl in list_controllers:
            cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)
            comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller(id_project, Constant.DB_ID_CP, ctl.id, True)

            if cp == None:
                return result

            for comp in comp_list:
                actions_list = DB_Actions_Components.select_actions_by_component_and_project(comp.id_component_src, id_project)

                for obj in object_property_list:
                    if len(actions_list) > 0:
                        text = ""
                        position = len(actions_list)

                        for act in actions_list:
                            position -= 1
                            text += act.name

                            if position >= 2:
                                text += ", "
                            elif position >= 1:
                                text += " or "

                        cause = ctl.name + " issues a control action (" + text + ") that conflicts with the one provided by the " + controller.name + "."

                        if obj.replace("-", " ") == "conflicting":
                            req = "The " + ctl.name + " shall have conflict analysis for control actions."
                            result.append(Loss_Scenery(side, causal_factor_name, ctl.name, cause, req, controller.id, ctl.id, ctl.id, cp.id, ctl.name, cp.name, "", Constant.STPA_CONTROL_PATH))
        return result

    if causal_factor_name == Constant.CONTROL_ACTION_HLC_CONTROLLER:
        cp = DB_Components.select_one_component_by_thing_project_analysis(Constant.DB_ID_CP, id_project)
        comp_list = DB_Components_Links.select_component_links_by_project_and_thing_and_controller_CA_ONLY(id_project, Constant.DB_ID_CONTROLLER, controller.id, True)

        for comp in comp_list:
            actions_list = DB_Actions_Components.select_actions_by_component_and_project_and_destiny(comp.id_component_src, id_project, comp.id_component_dst)

            for obj in object_property_list:
                if len(actions_list) > 0:
                    text = ""
                    position = len(actions_list)

                    for act in actions_list:
                        position -= 1
                        text += act.name

                        if position >= 2:
                            text += ", "
                        elif position >= 1:
                            text += " or "

                    if obj.replace("-", " ") == "inappropriate" and cp != None:
                        cause = controller.name + " issued an incorrect (" + obj.replace("-", " ") + ") control action: " + text + "; to " + comp.name_dst + "."
                        req = "The process model in " + controller.name + " shall represent the " + cp.name + " and " + comp.name_dst + "."
                        result.append(Loss_Scenery(side, causal_factor_name, comp.name_dst, cause, req, controller.id, controller.id, comp.id_component_src, comp.id_component_dst, comp.name_src, comp.name_dst, "", Constant.STPA_CONTROL_PATH))

                    if obj.replace("-", " ") == "missing":
                        cause = controller.name + " does not provide (" + obj.replace("-", " ") + ") the control action: " + text + "; to " + comp.name_dst + "."
                        req = "The communication of " + controller.name + " to " + comp.name_dst + " shall be improved."
                        result.append(Loss_Scenery(side, causal_factor_name, comp.name_dst, cause, req, controller.id, controller.id, comp.id_component_src, comp.id_component_dst, comp.name_src, comp.name_dst, "", Constant.STPA_CONTROL_PATH))
                        # correct ^
                        cause = comp.name_dst + " does not provide the received control action (" + text + ") from " + controller.name + "."
                        req = "The " + comp.name_dst + " shall have ongoing analysis after system modification."
                        result.append(Loss_Scenery(side, causal_factor_name, comp.name_dst, cause, req, controller.id, comp.id_component_dst, comp.id_component_src, comp.id_component_dst, comp.name_src, comp.name_dst, "", Constant.STPA_CONTROL_PATH))

                    if obj.replace("-", " ") == "conflicting" and cp != None:
                        cause = controller.name + " issued an conflicting control action: " + text + "; to " + comp.name_dst + "."
                        req = "The process model in " + controller.name + " shall represent the " + cp.name + " and " + comp.name_dst + "."
                        result.append(Loss_Scenery(side, causal_factor_name, comp.name_dst, cause, req, controller.id, controller.id, comp.id_component_src, comp.id_component_dst, comp.name_src, comp.name_dst, "", Constant.STPA_CONTROL_PATH))
#(side, onto_name, component, causes, requirement, id_controller, id_component, id_component_src, id_component_dst, name_src = "", name_dst = "", mechanism = ""):
        return result

    # print(causal_factor_name + " is not identified.")
    return result

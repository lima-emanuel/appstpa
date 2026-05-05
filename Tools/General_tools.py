import Constant

def find_individuals_of_class_return_idThing(onto, name_class, filter):

    if filter == 'Link_CP_':
        return [Constant.DB_ID_SENSOR, Constant.DB_ID_CONTROLLER, Constant.DB_ID_CONTROLLER] #controller and higher-level-controller

    if filter == 'Link_controller_':
        return [Constant.DB_ID_ACTUATOR, Constant.DB_ID_CP, Constant.DB_ID_CONTROLLER, Constant.DB_ID_EXT_INFORMATION]

    if filter == 'Link_actuator_':
        return [Constant.DB_ID_CP]

    if filter == 'Link_sensor_':
        return [Constant.DB_ID_CONTROLLER, Constant.DB_ID_CONTROLLER] #controller and higher-level-controller

    if filter == 'Link_External-information_':
        return [Constant.DB_ID_CONTROLLER]

def get_property_list_ontology(onto, name_source, name_destiny):

    if name_source == 'Algorithm' and name_destiny == 'Saf_Causal_factor_A':
        return ['incorrect', 'ineffective', 'updated']

    if name_source == 'Process_model' and name_destiny == 'Saf_Causal_factor_A':
        return ['wrong']

    if name_source == 'Sensor' and name_destiny == 'Saf_Causal_factor_A':
        return ['delayed', 'wrong', 'missing', 'failure']

    if name_source == 'Feedback_of_controller' and name_destiny == 'Saf_Causal_factor_A':
        return ['inadequate', 'missing', 'delayed']

    if name_source == 'External-information-received' and name_destiny == 'Saf_Causal_factor_A':
        return ['wrong', 'missing']

    if name_source == 'Controller' and name_destiny == 'Saf_Causal_factor_A':
        return ['failure']

    if name_source == 'Feedback_of_CP' and name_destiny == 'Saf_Causal_factor_A':
        return ['inadequate', 'missing', 'delayed']

    if name_source == 'Actuator' and name_destiny == 'Saf_Causal_factor_B':
        return ['delayed', 'executed', 'not-executed', 'failure']

    if name_source == 'Environmental_disturbances' and name_destiny == 'Saf_Causal_factor_B':
        return ['unidentified-disturbance']

    if name_source == 'Input' and name_destiny == 'Saf_Causal_factor_B':
        return ['missing', 'wrong']

    if name_source == 'Control_action_actuator' and name_destiny == 'Saf_Causal_factor_A':
        return ['inappropriate', 'missing']

    if name_source == 'Control_action_CP' and name_destiny == 'Saf_Causal_factor_B':
        return ['inappropriate', 'missing']

    if name_source == 'Control_action_HLC_CP' and name_destiny == 'Saf_Causal_factor_B':
        return ['conflicting']

    if name_source == 'Control_action_HLC_controller' and name_destiny == 'Saf_Causal_factor_B':
        return ['inappropriate', 'conflicting', 'missing']

    return []

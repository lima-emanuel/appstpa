import Constant


def get_dfd_element_only(onto, name_comp):

    if name_comp == 'Controller':
        return ['Data store', 'External entity', 'Process']

    if name_comp == 'CP':
        return ['Data store', 'Process']

    if name_comp == 'Sensor':
        return ['Data store', 'Process']

    if name_comp == 'Actuator':
        return ['Data store', 'Process']

    return []

def get_dfd_connection(dfd_name):
    if dfd_name == Constant.SEC_IS_DATA_FLOW_NAME:
        return Constant.SEC_IS_DATA_FLOW
    elif dfd_name == Constant.SEC_IS_DATA_STORE_NAME:
        return Constant.SEC_IS_DATA_STORE
    elif dfd_name == Constant.SEC_IS_EXTERNAL_ENTITY_NAME:
        return Constant.SEC_IS_EXTERNAL_ENTITY
    elif dfd_name == Constant.SEC_IS_PROCESS_NAME:
        return Constant.SEC_IS_PROCESS
    return ""

def get_dfd_name(dfd_id):
    if dfd_id == Constant.DB_ID_EXTERNAL_ENTITY:
        return Constant.SEC_IS_EXTERNAL_ENTITY_NAME
    elif dfd_id == Constant.DB_ID_DATA_FLOW:
        return Constant.SEC_IS_DATA_FLOW_NAME
    elif dfd_id == Constant.DB_ID_DATA_STORE:
        return Constant.SEC_IS_DATA_STORE_NAME
    elif dfd_id == Constant.DB_ID_PROCESS:
        return Constant.SEC_IS_PROCESS_NAME
    return ""

def get_threats(onto, name_comp):
    name_comp = get_dfd_connection(name_comp)

    if name_comp == 'Sec_External_entity':
        return ['Spoofing', 'Repudiation']

    if name_comp == 'Sec_Data_flow':
            return ['Tampering', 'Information disclosure', 'Denial of service']

    if name_comp == 'Sec_Process':
            return ['Spoofing', 'Tampering', 'Repudiation', 'Information disclosure', 'Denial of service', 'Elevation of privilege']

    if name_comp == 'Sec_Data_store':
            return ['Tampering', 'Repudiation', 'Information disclosure', 'Denial of service']

    return []

def get_subclass_of_countermeasure_class(onto, attack):

    if attack == Constant.DB_NAME_SPOOFING:
        return 'authentication OR protect secret data OR secure channel', []

    if attack == Constant.DB_NAME_TAMPERING:
        return 'data encryption OR digital signatures OR hash OR input validation approach OR tamper-resistant protocols', []

    if attack == Constant.DB_NAME_REPUDIATION:
        return 'audit OR digital signatures OR logging OR summary of received data OR timestamps', []

    if attack == Constant.DB_NAME_INFORMATION_DISCLOSURE:
        return 'authorization OR data encryption OR privacy-enhanced protocols OR protect the secrets', []

    if attack == Constant.DB_NAME_DENIAL_OF_SERVICE:
        return 'appropriated authentication OR appropriated authorization OR filtering OR rate limit OR replication OR throttling', []

    if attack == Constant.DB_NAME_ELEVATION_OF_PRIVILEGE:
        return 'restrict inputs OR role-based access OR run with least privilege OR source authentication OR strong password', []


    return "", []

def generate_description_source(onto, source, destiny, context, attack):
    mechanism = ""

    if attack == Constant.DB_NAME_SPOOFING:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_SPOOFING)
        consider = source + " must/shall have " + son_text + " for data sent."
        return source + " may be spoofed by an attacker and this may lead to unauthorized access to " + destiny + ".", consider, mechanism, son_list
    if attack == Constant.DB_NAME_TAMPERING:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_TAMPERING)
        consider = source + " must/shall have " + son_text + " for data sent."
        return "Data flowing across " + context + " may be tampered with by an attacker. This may lead to a denial of service attack against " + source + \
                        " or an elevation of privilege attack against " + source + " or an information disclosure by " + source + ". Failure to verify " \
                        "that input is as expected is a root cause of a very large number of exploitable issues.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_REPUDIATION:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_REPUDIATION)
        consider = source + " must/shall have " + son_text + " for data sent."
        return source + " claims that it did not sends data (" + context + ").", consider, mechanism, son_list
    if attack == Constant.DB_NAME_INFORMATION_DISCLOSURE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_INFORMATION_DISCLOSURE)
        consider = source + " must/shall have " + son_text + " for data sent."
        return "Data flowing across " + context + " from " + source + " may be sniffed by an attacker. Depending on what type of data an attacker can read, it may be used to attack other " \
                        "parts of the system or simply be a disclosure of information leading to compliance violations.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_DENIAL_OF_SERVICE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_DENIAL_OF_SERVICE)
        consider = source + " must/shall have " + son_text + " for data sent."
        return source + " crashes, halts, stops or runs slowly; in all cases violating an availability metric. " \
                        "An external agent interrupts data flowing across a trust boundary in either direction.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_ELEVATION_OF_PRIVILEGE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_ELEVATION_OF_PRIVILEGE)
        consider = source + " must/shall have " + son_text + " for data sent."
        return source + " may be able to impersonate the context of " + context + " in order to gain additional privilege. " \
                        "An attacker may pass data into " + source + " in order to change the flow of program execution within " + destiny + " to the attacker's choosing. " \
                        + source + " may be able to remotely execute code for " + destiny + ".", consider, mechanism, son_list
    return "", "", "", []

def generate_description_destiny(onto, destiny, source, context, attack):
    mechanism = ""

    if attack == Constant.DB_NAME_SPOOFING:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_SPOOFING)
        consider = destiny + " must/shall have " + son_text + " for data received."
        return destiny + " may be spoofed by an attacker and this may lead to information disclosure by " + source + ".", consider, mechanism, son_list
    if attack == Constant.DB_NAME_TAMPERING:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_TAMPERING)
        consider = destiny + " must/shall have " + son_text + " for data received."
        return "Data flowing across " + context + " may be tampered with by an attacker. This may lead to a denial of service attack against " + destiny + \
                        " or an elevation of privilege attack against " + destiny + " or an information disclosure by " + destiny + ". Failure to verify " \
                        "that input is as expected is a root cause of a very large number of exploitable issues.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_REPUDIATION:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_REPUDIATION)
        consider = destiny + " must/shall have " + son_text + " for data received."
        return destiny + " claims that it did not receive data (" + context + ").", consider, mechanism, son_list
    if attack == Constant.DB_NAME_INFORMATION_DISCLOSURE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_INFORMATION_DISCLOSURE)
        consider = destiny + " must/shall have " + son_text + " for data received."
        return "Data flowing across " + context + " to " + destiny + " may be sniffed by an attacker. Depending on what type of data an attacker can read, it may be used to attack other " \
                        "parts of the system or simply be a disclosure of information leading to compliance violations.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_DENIAL_OF_SERVICE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_DENIAL_OF_SERVICE)
        consider = destiny + " must/shall have " + son_text + " for data received."
        return destiny + " crashes, halts, stops or runs slowly; in all cases violating an availability metric. " \
                        "An external agent interrupts data flowing across a trust boundary in either direction.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_ELEVATION_OF_PRIVILEGE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_ELEVATION_OF_PRIVILEGE)
        consider = destiny + " must/shall have " + son_text + " for data received."
        return destiny + " may be able to impersonate the context of " + destiny + " in order to gain additional privilege. " \
                        "An attacker may pass data into " + source + " in order to change the flow of program execution within " + destiny + " to the attacker's choosing. " \
                        + source + " may be able to remotely execute code for " + destiny + ".", consider, mechanism, son_list
    return "", "", "", []

def generate_description_link(onto, link, context, attack):
    mechanism = ""

    if attack == Constant.DB_NAME_SPOOFING:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_SPOOFING)
        consider = "Link " + link + " must/shall have " + son_text + " for data flow."
        return link + " may be spoofed by an attacker and this may lead to unauthorized access to an attacker.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_TAMPERING:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_TAMPERING)
        consider = "Link " + link + " must/shall have " + son_text + " for data flow."
        return "Data flowing across " + context + " may be tampered with by an attacker. This may lead to a denial of service attack or an elevation" \
                        " of privilege attack against " + link + ", or an information disclosure by " + link + ". Failure to verify " \
                        "that input is as expected is a root cause of a very large number of exploitable issues.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_REPUDIATION:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_REPUDIATION)
        consider = "Link " + link + " must/shall have " + son_text + " for data flow."
        return link + " claims that it did not sends data (" + context + ").", consider, mechanism, son_list
    if attack == Constant.DB_NAME_INFORMATION_DISCLOSURE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_INFORMATION_DISCLOSURE)
        consider = "Link " + link + " must/shall have " + son_text + " for data flow."
        return "Data flowing across " + context + " may be sniffed by an attacker. Depending on what type of data an attacker can read, it may be used to attack other " \
                        "parts of the system or simply be a disclosure of information leading to compliance violations.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_DENIAL_OF_SERVICE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_DENIAL_OF_SERVICE)
        consider = "Link " + link + " must/shall have " + son_text + " for data flow."
        return link + " crashes, halts, stops or runs slowly; in all cases violating an availability metric. " \
                        "An external agent interrupts data flowing across a trust boundary in either direction.", consider, mechanism, son_list
    if attack == Constant.DB_NAME_ELEVATION_OF_PRIVILEGE:
        son_text, son_list = get_subclass_of_countermeasure_class(onto, Constant.DB_NAME_ELEVATION_OF_PRIVILEGE)
        consider = "Link " + link + " must/shall have " + son_text + " for data flow."
        return link + " may be able to impersonate the context of " + context + " in order to gain additional privilege.", consider, mechanism, son_list

    return "", "", "", []


import os
import sys
import topologyvalidator

from toscaparser.utils.gettextutils import _
import toscaparser.utils.urlutils


#Return the errors
def printError(errorList):
    codeError = errorList[0]
    if codeError == 1.1:
        message = '1.1 - MISSING_REQUIREMENT_DEFINITION: The requirement is assigned but not defined.'
    elif codeError == 1.2:
        message='1.2 - NODE_TYPE_NOT_COHERENT: The type '+'"'+errorList[1]+'"'+' of the target node '+errorList[2]+' is not valid (as it differs from that indicated in the requirement definition).'
    elif codeError == 1.3:
        message= '1.3 - CAPABILITY_TYPE_NOT_COHERENT: The type of the target capability is not valid (as it differs from that indicated in the requirement definition).'
    elif codeError == 1.4:
        message= '1.4 - MISSING_CAPABILITY_ERROR: The target node template '+'"' +errorList[1]+'"'+ 'is not offering any capability whose type is compatible with '+'"' +errorList[2]+'"'+ ' (indicated in the requirement definition).'
    elif codeError == 1.5:
        message= '1.5 - RELATIONSHIP_TYPE_NOT_COHERENT: The type of the outgoing relationship is not valid (as it differs from that indicated in the requirement definition).'
    elif codeError == 2.1:
        message= '2.1 - CAPABILITY_VALID_TARGET_TYPE_ NOT_COHERENT: The type of the target capability '+'"' +errorList[1]+'"'+ ' is not valid (as it differs from that indicated in the definition of the type of the outgoing relationship).'
    elif codeError == 2.2:
        message= '2.2 - MISSING_CAPABILITY_VALID_TARGET_TYPE: The target node template '+'"' +errorList[1]+'"'+ ' is not offering any capability whose type is compatible with those indicated as valid targets for the type of the outgoing relationship.'
    elif codeError == 3.1:
        message= '3.1 - CAPABILITY_VALID_SOURCE_TYPE_ NOT_COHERENT: The node type '+'"' +errorList[1]+'"'+ ' is not a valid source type for the capability targeted by the outgoing relationship (as it differs from those indicated in the capability type).'
    elif codeError == 3.2:
        message =  '3.2 - CAPABILITY_DEFINITION_VALID_SOURCE_TYPE_NOT_COHERENT: The node type '+'"' +errorList[1]+'"'+ ' is not a valid source type for the capability targeted by the outgoing relationship (as it differs from those indicated in the capability definitions in the type of '+'"' +errorList[2]+'"'+ ').'


    return message
# Returns the result of the validation
def printValidation(validation):
    isCorrect = True
    for nodeName in validation:
        reqs = validation.get(nodeName).keys()
        for req in reqs:
            infoList = validation.get(nodeName).get(req)
            if infoList != []:
                print("\nNODE TEMPLATE: ", nodeName)
                print("REQUIREMENT: ", req)
            for info in infoList:
                isCorrect = False
                message = printError(info)
    if isCorrect:
        message = "The application model is valid."

    return message, isCorrect


def validation(path):
    if os.path.isfile(path):
        v = topologyvalidator.TopologyValidator()
        validation = v.validate(path)
        message, isCorrect = printValidation(validation)
    else:
        raise ValueError(_('"%(path)s" is not a valid file.')
                         % {'path': path})
    return message, isCorrect
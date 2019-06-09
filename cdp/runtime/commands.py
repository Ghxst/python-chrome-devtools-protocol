'''
DO NOT EDIT THIS FILE

This file is generated from the CDP definitions. If you need to make changes,
edit the generator and regenerate all of the modules.

Domain: runtime
Experimental: False
'''

from dataclasses import dataclass, field
import typing

from .types import *


class Runtime:
    @staticmethod
    def await_promise(promise_object_id: RemoteObjectId, return_by_value: bool, generate_preview: bool) -> dict:
        '''
        Add handler to promise with given promise object id.
        
        :param promise_object_id: Identifier of the promise.
        :param return_by_value: Whether the result is expected to be a JSON object that should be sent by value.
        :param generate_preview: Whether preview should be generated for the result.
        :returns: a dict with the following keys:
            * result: Promise result. Will contain rejected value if promise was rejected.
            * exceptionDetails: Exception details if stack strace is available.
        '''

        cmd_dict = {
            'method': 'Runtime.awaitPromise',
            'params': {
                'promiseObjectId': promise_object_id,
                'returnByValue': return_by_value,
                'generatePreview': generate_preview,
            }
        }
        response = yield cmd_dict
        return {
                'result': RemoteObject.from_response(response['result']),
                'exceptionDetails': ExceptionDetails.from_response(response['exceptionDetails']),
            }

    @staticmethod
    def call_function_on(function_declaration: str, object_id: RemoteObjectId, arguments: typing.List['CallArgument'], silent: bool, return_by_value: bool, generate_preview: bool, user_gesture: bool, await_promise: bool, execution_context_id: ExecutionContextId, object_group: str) -> dict:
        '''
        Calls function with given declaration on the given object. Object group of the result is
        inherited from the target object.
        
        :param function_declaration: Declaration of the function to call.
        :param object_id: Identifier of the object to call function on. Either objectId or executionContextId should
        be specified.
        :param arguments: Call arguments. All call arguments must belong to the same JavaScript world as the target
        object.
        :param silent: In silent mode exceptions thrown during evaluation are not reported and do not pause
        execution. Overrides `setPauseOnException` state.
        :param return_by_value: Whether the result is expected to be a JSON object which should be sent by value.
        :param generate_preview: Whether preview should be generated for the result.
        :param user_gesture: Whether execution should be treated as initiated by user in the UI.
        :param await_promise: Whether execution should `await` for resulting value and return once awaited promise is
        resolved.
        :param execution_context_id: Specifies execution context which global object will be used to call function on. Either
        executionContextId or objectId should be specified.
        :param object_group: Symbolic group name that can be used to release multiple objects. If objectGroup is not
        specified and objectId is, objectGroup will be inherited from object.
        :returns: a dict with the following keys:
            * result: Call result.
            * exceptionDetails: Exception details.
        '''

        cmd_dict = {
            'method': 'Runtime.callFunctionOn',
            'params': {
                'functionDeclaration': function_declaration,
                'objectId': object_id,
                'arguments': arguments,
                'silent': silent,
                'returnByValue': return_by_value,
                'generatePreview': generate_preview,
                'userGesture': user_gesture,
                'awaitPromise': await_promise,
                'executionContextId': execution_context_id,
                'objectGroup': object_group,
            }
        }
        response = yield cmd_dict
        return {
                'result': RemoteObject.from_response(response['result']),
                'exceptionDetails': ExceptionDetails.from_response(response['exceptionDetails']),
            }

    @staticmethod
    def compile_script(expression: str, source_url: str, persist_script: bool, execution_context_id: ExecutionContextId) -> dict:
        '''
        Compiles expression.
        
        :param expression: Expression to compile.
        :param source_url: Source url to be set for the script.
        :param persist_script: Specifies whether the compiled script should be persisted.
        :param execution_context_id: Specifies in which execution context to perform script run. If the parameter is omitted the
        evaluation will be performed in the context of the inspected page.
        :returns: a dict with the following keys:
            * scriptId: Id of the script.
            * exceptionDetails: Exception details.
        '''

        cmd_dict = {
            'method': 'Runtime.compileScript',
            'params': {
                'expression': expression,
                'sourceURL': source_url,
                'persistScript': persist_script,
                'executionContextId': execution_context_id,
            }
        }
        response = yield cmd_dict
        return {
                'scriptId': ScriptId.from_response(response['scriptId']),
                'exceptionDetails': ExceptionDetails.from_response(response['exceptionDetails']),
            }

    @staticmethod
    def disable() -> None:
        '''
        Disables reporting of execution contexts creation.
        '''

        cmd_dict = {
            'method': 'Runtime.disable',
        }
        response = yield cmd_dict

    @staticmethod
    def discard_console_entries() -> None:
        '''
        Discards collected exceptions and console API calls.
        '''

        cmd_dict = {
            'method': 'Runtime.discardConsoleEntries',
        }
        response = yield cmd_dict

    @staticmethod
    def enable() -> None:
        '''
        Enables reporting of execution contexts creation by means of `executionContextCreated` event.
        When the reporting gets enabled the event will be sent immediately for each existing execution
        context.
        '''

        cmd_dict = {
            'method': 'Runtime.enable',
        }
        response = yield cmd_dict

    @staticmethod
    def evaluate(expression: str, object_group: str, include_command_line_api: bool, silent: bool, context_id: ExecutionContextId, return_by_value: bool, generate_preview: bool, user_gesture: bool, await_promise: bool, throw_on_side_effect: bool, timeout: TimeDelta) -> dict:
        '''
        Evaluates expression on global object.
        
        :param expression: Expression to evaluate.
        :param object_group: Symbolic group name that can be used to release multiple objects.
        :param include_command_line_api: Determines whether Command Line API should be available during the evaluation.
        :param silent: In silent mode exceptions thrown during evaluation are not reported and do not pause
        execution. Overrides `setPauseOnException` state.
        :param context_id: Specifies in which execution context to perform evaluation. If the parameter is omitted the
        evaluation will be performed in the context of the inspected page.
        :param return_by_value: Whether the result is expected to be a JSON object that should be sent by value.
        :param generate_preview: Whether preview should be generated for the result.
        :param user_gesture: Whether execution should be treated as initiated by user in the UI.
        :param await_promise: Whether execution should `await` for resulting value and return once awaited promise is
        resolved.
        :param throw_on_side_effect: Whether to throw an exception if side effect cannot be ruled out during evaluation.
        :param timeout: Terminate execution after timing out (number of milliseconds).
        :returns: a dict with the following keys:
            * result: Evaluation result.
            * exceptionDetails: Exception details.
        '''

        cmd_dict = {
            'method': 'Runtime.evaluate',
            'params': {
                'expression': expression,
                'objectGroup': object_group,
                'includeCommandLineAPI': include_command_line_api,
                'silent': silent,
                'contextId': context_id,
                'returnByValue': return_by_value,
                'generatePreview': generate_preview,
                'userGesture': user_gesture,
                'awaitPromise': await_promise,
                'throwOnSideEffect': throw_on_side_effect,
                'timeout': timeout,
            }
        }
        response = yield cmd_dict
        return {
                'result': RemoteObject.from_response(response['result']),
                'exceptionDetails': ExceptionDetails.from_response(response['exceptionDetails']),
            }

    @staticmethod
    def get_isolate_id() -> str:
        '''
        Returns the isolate id.
        :returns: The isolate id.
        '''

        cmd_dict = {
            'method': 'Runtime.getIsolateId',
        }
        response = yield cmd_dict
        return str.from_response(response['id'])

    @staticmethod
    def get_heap_usage() -> dict:
        '''
        Returns the JavaScript heap usage.
        It is the total usage of the corresponding isolate not scoped to a particular Runtime.
        :returns: a dict with the following keys:
            * usedSize: Used heap size in bytes.
            * totalSize: Allocated heap size in bytes.
        '''

        cmd_dict = {
            'method': 'Runtime.getHeapUsage',
        }
        response = yield cmd_dict
        return {
                'usedSize': float.from_response(response['usedSize']),
                'totalSize': float.from_response(response['totalSize']),
            }

    @staticmethod
    def get_properties(object_id: RemoteObjectId, own_properties: bool, accessor_properties_only: bool, generate_preview: bool) -> dict:
        '''
        Returns properties of a given object. Object group of the result is inherited from the target
        object.
        
        :param object_id: Identifier of the object to return properties for.
        :param own_properties: If true, returns properties belonging only to the element itself, not to its prototype
        chain.
        :param accessor_properties_only: If true, returns accessor properties (with getter/setter) only; internal properties are not
        returned either.
        :param generate_preview: Whether preview should be generated for the results.
        :returns: a dict with the following keys:
            * result: Object properties.
            * internalProperties: Internal object properties (only of the element itself).
            * privateProperties: Object private properties.
            * exceptionDetails: Exception details.
        '''

        cmd_dict = {
            'method': 'Runtime.getProperties',
            'params': {
                'objectId': object_id,
                'ownProperties': own_properties,
                'accessorPropertiesOnly': accessor_properties_only,
                'generatePreview': generate_preview,
            }
        }
        response = yield cmd_dict
        return {
                'result': [PropertyDescriptor.from_response(i) for i in response['result']],
                'internalProperties': [InternalPropertyDescriptor.from_response(i) for i in response['internalProperties']],
                'privateProperties': [PrivatePropertyDescriptor.from_response(i) for i in response['privateProperties']],
                'exceptionDetails': ExceptionDetails.from_response(response['exceptionDetails']),
            }

    @staticmethod
    def global_lexical_scope_names(execution_context_id: ExecutionContextId) -> typing.List:
        '''
        Returns all let, const and class variables from global scope.
        
        :param execution_context_id: Specifies in which execution context to lookup global scope variables.
        :returns: 
        '''

        cmd_dict = {
            'method': 'Runtime.globalLexicalScopeNames',
            'params': {
                'executionContextId': execution_context_id,
            }
        }
        response = yield cmd_dict
        return [str(i) for i in response['names']]

    @staticmethod
    def query_objects(prototype_object_id: RemoteObjectId, object_group: str) -> RemoteObject:
        '''
        
        
        :param prototype_object_id: Identifier of the prototype to return objects for.
        :param object_group: Symbolic group name that can be used to release the results.
        :returns: Array with objects.
        '''

        cmd_dict = {
            'method': 'Runtime.queryObjects',
            'params': {
                'prototypeObjectId': prototype_object_id,
                'objectGroup': object_group,
            }
        }
        response = yield cmd_dict
        return RemoteObject.from_response(response['objects'])

    @staticmethod
    def release_object(object_id: RemoteObjectId) -> None:
        '''
        Releases remote object with given id.
        
        :param object_id: Identifier of the object to release.
        '''

        cmd_dict = {
            'method': 'Runtime.releaseObject',
            'params': {
                'objectId': object_id,
            }
        }
        response = yield cmd_dict

    @staticmethod
    def release_object_group(object_group: str) -> None:
        '''
        Releases all remote objects that belong to a given group.
        
        :param object_group: Symbolic object group name.
        '''

        cmd_dict = {
            'method': 'Runtime.releaseObjectGroup',
            'params': {
                'objectGroup': object_group,
            }
        }
        response = yield cmd_dict

    @staticmethod
    def run_if_waiting_for_debugger() -> None:
        '''
        Tells inspected instance to run if it was waiting for debugger to attach.
        '''

        cmd_dict = {
            'method': 'Runtime.runIfWaitingForDebugger',
        }
        response = yield cmd_dict

    @staticmethod
    def run_script(script_id: ScriptId, execution_context_id: ExecutionContextId, object_group: str, silent: bool, include_command_line_api: bool, return_by_value: bool, generate_preview: bool, await_promise: bool) -> dict:
        '''
        Runs script with given id in a given context.
        
        :param script_id: Id of the script to run.
        :param execution_context_id: Specifies in which execution context to perform script run. If the parameter is omitted the
        evaluation will be performed in the context of the inspected page.
        :param object_group: Symbolic group name that can be used to release multiple objects.
        :param silent: In silent mode exceptions thrown during evaluation are not reported and do not pause
        execution. Overrides `setPauseOnException` state.
        :param include_command_line_api: Determines whether Command Line API should be available during the evaluation.
        :param return_by_value: Whether the result is expected to be a JSON object which should be sent by value.
        :param generate_preview: Whether preview should be generated for the result.
        :param await_promise: Whether execution should `await` for resulting value and return once awaited promise is
        resolved.
        :returns: a dict with the following keys:
            * result: Run result.
            * exceptionDetails: Exception details.
        '''

        cmd_dict = {
            'method': 'Runtime.runScript',
            'params': {
                'scriptId': script_id,
                'executionContextId': execution_context_id,
                'objectGroup': object_group,
                'silent': silent,
                'includeCommandLineAPI': include_command_line_api,
                'returnByValue': return_by_value,
                'generatePreview': generate_preview,
                'awaitPromise': await_promise,
            }
        }
        response = yield cmd_dict
        return {
                'result': RemoteObject.from_response(response['result']),
                'exceptionDetails': ExceptionDetails.from_response(response['exceptionDetails']),
            }

    @staticmethod
    def set_async_call_stack_depth(max_depth: int) -> None:
        '''
        Enables or disables async call stacks tracking.
        
        :param max_depth: Maximum depth of async call stacks. Setting to `0` will effectively disable collecting async
        call stacks (default).
        '''

        cmd_dict = {
            'method': 'Runtime.setAsyncCallStackDepth',
            'params': {
                'maxDepth': max_depth,
            }
        }
        response = yield cmd_dict

    @staticmethod
    def set_custom_object_formatter_enabled(enabled: bool) -> None:
        '''
        
        
        :param enabled: 
        '''

        cmd_dict = {
            'method': 'Runtime.setCustomObjectFormatterEnabled',
            'params': {
                'enabled': enabled,
            }
        }
        response = yield cmd_dict

    @staticmethod
    def set_max_call_stack_size_to_capture(size: int) -> None:
        '''
        
        
        :param size: 
        '''

        cmd_dict = {
            'method': 'Runtime.setMaxCallStackSizeToCapture',
            'params': {
                'size': size,
            }
        }
        response = yield cmd_dict

    @staticmethod
    def terminate_execution() -> None:
        '''
        Terminate current or next JavaScript execution.
        Will cancel the termination when the outer-most script execution ends.
        '''

        cmd_dict = {
            'method': 'Runtime.terminateExecution',
        }
        response = yield cmd_dict

    @staticmethod
    def add_binding(name: str, execution_context_id: ExecutionContextId) -> None:
        '''
        If executionContextId is empty, adds binding with the given name on the
        global objects of all inspected contexts, including those created later,
        bindings survive reloads.
        If executionContextId is specified, adds binding only on global object of
        given execution context.
        Binding function takes exactly one argument, this argument should be string,
        in case of any other input, function throws an exception.
        Each binding function call produces Runtime.bindingCalled notification.
        
        :param name: 
        :param execution_context_id: 
        '''

        cmd_dict = {
            'method': 'Runtime.addBinding',
            'params': {
                'name': name,
                'executionContextId': execution_context_id,
            }
        }
        response = yield cmd_dict

    @staticmethod
    def remove_binding(name: str) -> None:
        '''
        This method does not remove binding function from global object but
        unsubscribes current runtime agent from Runtime.bindingCalled notifications.
        
        :param name: 
        '''

        cmd_dict = {
            'method': 'Runtime.removeBinding',
            'params': {
                'name': name,
            }
        }
        response = yield cmd_dict

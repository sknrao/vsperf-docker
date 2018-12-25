# Copyright (c) 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_utils import excutils

class ProcessExecutionError(RuntimeError):
    def __init__(self, message, returncode):
        super(ProcessExecutionError, self).__init__(message)
        self.returncode = returncode


class ErrorClass(object):

    def __init__(self, *args, **kwargs):
        if 'test' not in kwargs:
            raise RuntimeError

    def __getattr__(self, item):
        raise AttributeError


class VsperfCException(Exception):
    """Base VSPERF-C Exception.

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    Based on NeutronException class.
    """
    message = "An unknown exception occurred."

    def __init__(self, **kwargs):
        try:
            super(VsperfCException, self).__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:  # pylint: disable=broad-except
            with excutils.save_and_reraise_exception() as ctxt:
                if not self.use_fatal_exceptions():
                    ctxt.reraise = False
                    # at least get the core message out if something happened
                    super(VsperfCException, self).__init__(self.message)

    def __str__(self):
        return self.msg

    def use_fatal_exceptions(self):
        """Is the instance using fatal exceptions.

        :returns: Always returns False.
        """
        return False


class ResourceCommandError(VsperfCException):
    message = 'Command: "%(command)s" Failed, stderr: "%(stderr)s"'


class ContextUpdateCollectdForNodeError(VsperfCException):
    message = 'Cannot find node %(attr_name)s'


class FunctionNotImplemented(VsperfCException):
    message = ('The function "%(function_name)s" is not implemented in '
               '"%(class_name)" class.')


class InvalidType(VsperfCException):
    message = 'Type "%(type_to_convert)s" is not valid'


class InfluxDBConfigurationMissing(VsperfCException):
    message = ('InfluxDB configuration is not available. Add "influxdb" as '
               'a dispatcher and the configuration section')


class YardstickBannedModuleImported(VsperfCException):
    message = 'Module "%(module)s" cannnot be imported. Reason: "%(reason)s"'


class IXIAUnsupportedProtocol(VsperfCException):
    message = 'Protocol "%(protocol)" is not supported in IXIA'


class PayloadMissingAttributes(VsperfCException):
    message = ('Error instantiating a Payload class, missing attributes: '
               '%(missing_attributes)s')


class HeatTemplateError(VsperfCException):
    message = ('Error in Heat during the creation of the OpenStack stack '
               '"%(stack_name)s"')


class IPv6RangeError(VsperfCException):
    message = 'Start IP "%(start_ip)s" is greater than end IP "%(end_ip)s"'


class TrafficProfileNotImplemented(VsperfCException):
    message = 'No implementation for traffic profile %(profile_class)s.'


class TrafficProfileRate(VsperfCException):
    message = 'Traffic profile rate must be "<number>[fps|%]"'


class DPDKSetupDriverError(VsperfCException):
    message = '"igb_uio" driver is not loaded'


class OVSUnsupportedVersion(VsperfCException):
    message = ('Unsupported OVS version "%(ovs_version)s". Please check the '
               'config. OVS to DPDK version map: %(ovs_to_dpdk_map)s.')


class OVSHugepagesInfoError(VsperfCException):
    message = 'MemInfo cannnot be retrieved.'


class OVSHugepagesNotConfigured(VsperfCException):
    message = 'HugePages are not configured in this system.'


class OVSHugepagesZeroFree(VsperfCException):
    message = ('There are no HugePages free in this system. Total HugePages '
               'configured: %(total_hugepages)s')


class OVSDeployError(VsperfCException):
    message = 'OVS deploy tool failed with error: %(stderr)s.'


class OVSSetupError(VsperfCException):
    message = 'OVS setup error. Command: %(command)s. Error: %(error)s.'


class LibvirtCreateError(VsperfCException):
    message = 'Error creating the virtual machine. Error: %(error)s.'


class LibvirtQemuImageBaseImageNotPresent(VsperfCException):
    message = ('Error creating the qemu image for %(vm_image)s. Base image: '
               '%(base_image)s. Base image not present in execution host or '
               'remote host.')


class LibvirtQemuImageCreateError(VsperfCException):
    message = ('Error creating the qemu image for %(vm_image)s. Base image: '
               '%(base_image)s. Error: %(error)s.')


class SSHError(VsperfCException):
    message = '%(error_msg)s'


class SSHTimeout(SSHError):
    pass


class IncorrectConfig(VsperfCException):
    message = '%(error_msg)s'


class IncorrectSetup(VsperfCException):
    message = '%(error_msg)s'


class IncorrectNodeSetup(IncorrectSetup):
    pass


class ScenarioConfigContextNameNotFound(VsperfCException):
    message = 'Context for host name "%(host_name)s" not found'


class StackCreationInterrupt(VsperfCException):
    message = 'Stack create interrupted.'


class TaskRenderArgumentError(VsperfCException):
    message = 'Error reading the task input arguments'


class TaskReadError(VsperfCException):
    message = 'Failed to read task %(task_file)s'


class TaskRenderError(VsperfCException):
    message = 'Failed to render template:\n%(input_task)s'


class RunnerIterationIPCSetupActionNeeded(VsperfCException):
    message = ('IterationIPC needs the "setup" action to retrieve the VNF '
               'handling processes PIDs to receive the messages sent')


class RunnerIterationIPCNoCtxs(VsperfCException):
    message = 'Benchmark "setup" action did not return any VNF process PID'


class TimerTimeout(VsperfCException):
    message = 'Timer timeout expired, %(timeout)s seconds'


class WaitTimeout(VsperfCException):
    message = 'Wait timeout while waiting for condition'


class PktgenActionError(VsperfCException):
    message = 'Error in "%(action)s" action'


class ScenarioCreateNetworkError(VsperfCException):
    message = 'Create Neutron Network Scenario failed'


class ScenarioCreateSubnetError(VsperfCException):
    message = 'Create Neutron Subnet Scenario failed'


class ScenarioDeleteRouterError(VsperfCException):
    message = 'Delete Neutron Router Scenario failed'


class MissingPodInfoError(VsperfCException):
    message = 'Missing pod args, please check'


class UnsupportedPodFormatError(VsperfCException):
    message = 'Failed to load pod info, unsupported format'


class ScenarioCreateRouterError(VsperfCException):
    message = 'Create Neutron Router Scenario failed'


class ScenarioRemoveRouterIntError(VsperfCException):
    message = 'Remove Neutron Router Interface Scenario failed'


class ScenarioCreateFloatingIPError(VsperfCException):
    message = 'Create Neutron Floating IP Scenario failed'


class ScenarioDeleteFloatingIPError(VsperfCException):
    message = 'Delete Neutron Floating IP Scenario failed'


class ScenarioCreateSecurityGroupError(VsperfCException):
    message = 'Create Neutron Security Group Scenario failed'


class ScenarioDeleteNetworkError(VsperfCException):
    message = 'Delete Neutron Network Scenario failed'


class ScenarioCreateServerError(VsperfCException):
    message = 'Nova Create Server Scenario failed'


class ScenarioDeleteServerError(VsperfCException):
    message = 'Delete Server Scenario failed'


class ScenarioCreateKeypairError(VsperfCException):
    message = 'Nova Create Keypair Scenario failed'


class ScenarioDeleteKeypairError(VsperfCException):
    message = 'Nova Delete Keypair Scenario failed'


class ScenarioAttachVolumeError(VsperfCException):
    message = 'Nova Attach Volume Scenario failed'


class ScenarioGetServerError(VsperfCException):
    message = 'Nova Get Server Scenario failed'


class ScenarioGetFlavorError(VsperfCException):
    message = 'Nova Get Falvor Scenario failed'


class ScenarioCreateVolumeError(VsperfCException):
    message = 'Cinder Create Volume Scenario failed'


class ScenarioDeleteVolumeError(VsperfCException):
    message = 'Cinder Delete Volume Scenario failed'


class ScenarioDetachVolumeError(VsperfCException):
    message = 'Cinder Detach Volume Scenario failed'


class ApiServerError(VsperfCException):
    message = 'An unkown exception happened to Api Server!'


class UploadOpenrcError(ApiServerError):
    message = 'Upload openrc ERROR!'


class UpdateOpenrcError(ApiServerError):
    message = 'Update openrc ERROR!'


class ScenarioCreateImageError(VsperfCException):
    message = 'Glance Create Image Scenario failed'


class ScenarioDeleteImageError(VsperfCException):
    message = 'Glance Delete Image Scenario failed'



class SLAValidationError(VsperfCException):
    message = '%(case_name)s SLA validation failed. Error: %(error_msg)s'



class InvalidMacAddress(VsperfCException):
    message = 'Mac address "%(mac_address)s" is invalid'


class ValueCheckError(VsperfCException):
    message = 'Constraint "%(value1)s %(operator)s %(value2)s" does not hold'


class RestApiError(RuntimeError):
    def __init__(self, message):
        self._message = message
        super(RestApiError, self).__init__(message)

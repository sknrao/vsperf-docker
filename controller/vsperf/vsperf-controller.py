# Copyright 2018-19 Spirent Communications.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
VSPER docker-controller.

"""

import io
import time
import grpc

from concurrent import futures

from .proto import vsperf_pb2 as vsperf_pb2
from .proto import vsperf_pb2_grpc as vsperf_pb2_grpc
from .utils import ssh as ssh

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


# pylint: disable=too-few-public-methods,no-self-use
class PseudoFile(io.RawIOBase):
    """
    Handle ssh command output.
    """
    def write(self, chunk):
        """
        Write to file
        """
        if "error" in chunk:
            return
        with open("./output.txt", "a") as fref:
            fref.write(chunk)


class VsperfController(vsperf_pb2_grpc.ControllerServicer):
    """
    Main Controller Class
    """
    def __init__(self):
        """
        Initialization
        """
        # print("Init Function")
        self.client = None
        self.dut = None
        self.user = None
        self.pwd = None
        self.vsperf_conf = None
        self.tgen_client = None
        self.tgen = None
        self.tgen_user = None
        self.tgen_pwd = None
        self.tgen_conf = None
        self.scenario = None
        self.conffile = "vsperf.conf"
        # Default TGen is T-Rex
        self.tgen_conffile = "trex_cfg.yml"

    def setup(self):
        """
        Performs Setup of the client.
        """
        # Just connect to VM.
        self.client = ssh.SSH(host=self.dut, user=self.user,
                              password=self.pwd)
        self.client.wait()

    def install_vsperf(self):
        """
        Perform actual installation
        """
        download_cmd = "git clone https://gerrit.opnfv.org/gerrit/vswitchperf"
        self.client.run(download_cmd)
        install_cmd = "cd vswitchperf/systems ; "
        install_cmd += "./build_base_machine.sh"
        self.client.run(install_cmd)

    def upload_config(self):
        """
        Perform file upload.
        """
        # self.client._put_file_shell(self.conffile, '~/vsperf.conf')
        self.client.put_file(self.conffile, '~/vsperf.conf')

    def run_test(self):
        """
        Run test
        """
        # cmd = "scl enable python33 bash ; "
        cmd = "source ~/vsperfenv/bin/activate ; cd vswitchperf ; "
        cmd += "./vsperf "
        if self.vsperf_conf:
            cmd += "--conf-file ~/vsperf.conf "
            # cmd += self.conffile
        cmd += self.scenario
        with PseudoFile() as pref:
            self.client.run(cmd, stdout=pref, timeout=0)

    def VsperfInstall(self, request, context):
        """
        Handle VSPERF install command from client
        """
        # print("Installing VSPERF")
        self.install_vsperf()
        return vsperf_pb2.StatusReply(message="Successfully Installed")

    def HostConnect(self, request, context):
        """
        Handle host connectivity command from client
        """
        self.dut = request.ip
        self.user = request.uname
        self.pwd = request.pwd
        self.setup()
        return vsperf_pb2.StatusReply(message="Successfully Connected")

    def save_chunks_to_file(self, chunks, filename):
        """
        Write the output to file
        """
        with open(filename, 'wb') as fref:
            for chunk in chunks:
                fref.write(chunk.Content)

    def UploadConfigFile(self, request, context):
        """
        Handle upload config-file command from client
        """
        filename = self.conffile
        self.save_chunks_to_file(request, filename)
        self.upload_config()
        return vsperf_pb2.UploadStatus(Message="Successfully Uploaded",
                                       Code=1)

    def StartTest(self, request, context):
        """
        Handle start-test command from client
        """
        self.vsperf_conf = request.conffile
        self.scenario = request.testtype
        self.run_test()
        return vsperf_pb2.StatusReply(message="Test Successfully running...")

###### Traffic Generator Related functions ####
    def TGenHostConnect(self, request, context):
        """
        Connect to TGen-Node
        """
        self.tgen = request.ip
        self.tgen_user = request.uname
        self.tgen_pwd = request.pwd
        self.TgenSetup()
        return vsperf_pb2.StatusReply(message="Successfully Connected")

    def TgenSetup(self):
        """
        Setup the T-Gen Client
        """
        # Just connect to VM.
        self.tgen_client = ssh.SSH(host=self.tgen, user=self.tgen_user,
                                   password=self.tgen_pwd)
        self.tgen_client.wait()

    def TGenInstall(self, request, context):
        """
        Install Traffic generator on the node.
        """

    def TGenUploadConfigFile(self, request, context):
        """
        Handle upload config-file command from client
        """
        filename = self.tgen_conffile
        self.save_chunks_to_file(request, filename)
        self.upload_config()
        return vsperf_pb2.UploadStatus(Message="Successfully Uploaded",
                                       Code=1)
    def upload_tgen_config(self):
        """
        Perform file upload.
        """
        self.tgen_client.put_file(self.trex_conffile, '/root/trex_cfg.yml')

    def install_tgen(self):
        """
        Perform actual installation
        """
        download_cmd ="git clone https://github.com/cisco-system-traffic-\
            generator/trex-core.git"
        self.tgen_client.run(download_cmd)
        install_cmd = "mv /root/trex-core /root/trex_latest"
        self.tgen_client.run(install_cmd)

    def StartTGen(self, request, context):
        """
        Handle start-test command from client
        """
        self.trex_conf = request.conffile
        self.trex_params = request.params
        run_cmd = "/root/trex_latest/scripts/t-rex-64"
        run_cmd += self.trex_params
        self.tgen_client.run(run_cmd)
        return vsperf_pb2.StatusReply(message="T-Rex Successfully running...")

def serve():
    """
    Start servicing the client
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vsperf_pb2_grpc.add_ControllerServicer_to_server(
        VsperfController(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except (SystemExit, KeyboardInterrupt, MemoryError, RuntimeError):
        server.stop(0)

if __name__ == "__main__":
    serve()

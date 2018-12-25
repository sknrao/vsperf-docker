import vsperf_pb2_grpc as vsperf_pb2_grpc
from concurrent import futures
import time
#import math
import grpc
import vsperf_pb2
import os
import sys
sys.path.insert(0, os.getcwd())
from utils import ssh as ssh

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class VsperfController(vsperf_pb2_grpc.ControllerServicer):
    def __init__(self):
        print("Init Function")
        self.client = None
        self.dut = None
        self.user = None
        self.pwd = None
        self.vsperf_conf = None
        self.scenario = None

    def setup(self):
        # copy vsperf conf to VM
        self.client = ssh.SSH.from_node(self.dut, defaults={
            "user": self.user, "password": self.pwd
        })
        self.client.wait()

    def install_vsperf(self):
        print("Do actual installation")
        download_cmd = "git clone https://gerrit.opnfv.org/gerrit/vswitchperf"
        self.client.run(download_cmd)
        install_cmd = "cd vswitchperf/systems ; "
        install_cmd += "./build_base_machine.sh"
        self.client.run(install_cmd)

    def upload_config(self):
        self.client._put_file_shell(self.vsperf_conf, '~/vsperf.conf')

    def run_test(self):
        # execute vsperf
        cmd = "source ~/vsperfenv/bin/activate ; cd vswitchperf ; "
        cmd += "./vsperf "
        if self.vsperf_conf:
            cmd += "--conf-file ~/vsperf.conf "
        cmd += self.scenario
        self.client.run(cmd)

    def VsperfInstall(self, request, context):
        print("Installing VSPERF")
        return vsperf_pb2.StatusReply(message="Successfully Installed")
        self.dut = request.ip
        self.user = request.uname
        self.pwd = request.pwd
        self.setup()
        self.vsperf_install()

    def save_chunks_to_file(self, chunks, filename):
        with open(filename, 'wb') as f:
            for chunk in chunks:
                f.write(chunk.Content)

    def UploadConfigFile(self, request, context):
        print("Uploading Configuration file")
        filename = 'vsperf.conf'
        self.save_chunks_to_file(request, filename)
        return vsperf_pb2.UploadStatus(Message="Success",
                                       Code=1)

        # Same file file and assign the path to self.vsperf_conf

    def StartTest(self, request, context):
        print("Starting test " + request.testtype + " and using config file " +
              request.conffile)
        return vsperf_pb2.StatusReply(message="Test Successfully running...")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vsperf_pb2_grpc.add_ControllerServicer_to_server(
        VsperfController(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except:
        server.stop(0)

if __name__ == "__main__":
    serve()

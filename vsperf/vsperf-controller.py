import proto.vsperf_pb2_grpc as vsperf_pb2_grpc
from concurrent import futures
from utils import ssh as ssh
import time
import grpc
import proto.vsperf_pb2 as vsperf_pb2
# import os
# import sys
# sys.path.insert(0, os.getcwd())

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
        self.conffile = "vsperf.conf"

    def setup(self):
        # copy vsperf conf to VM
        self.client = ssh.SSH(host=self.dut, user=self.user,
                              password=self.pwd)
        self.client.wait()

    def install_vsperf(self):
        print("Do actual installation")
        download_cmd = "git clone https://gerrit.opnfv.org/gerrit/vswitchperf"
        self.client.run(download_cmd)
        install_cmd = "cd vswitchperf/systems ; "
        install_cmd += "./build_base_machine.sh"
        self.client.run(install_cmd)

    def upload_config(self):
        self.client._put_file_shell(self.conffile, '~/vsperf.conf')

    def run_test(self):
        # execute vsperf
        cmd = "scl enable python33 bash ; "
        cmd += "source ~/vsperfenv/bin/activate ; cd vswitchperf ; "
        cmd += "./vsperf "
        if self.vsperf_conf:
            cmd += "--conf-file ~/vsperf.conf "
        cmd += self.scenario
        self.client.run(cmd)

    def VsperfInstall(self, request, context):
        print("Installing VSPERF")
        self.install_vsperf()
        return vsperf_pb2.StatusReply(message="Successfully Installed")

    def HostConnect(self, request, context):
        self.dut = request.ip
        self.user = request.uname
        self.pwd = request.pwd
        self.setup()
        return vsperf_pb2.StatusReply(message="Successfully Connected")


    def save_chunks_to_file(self, chunks, filename):
        with open(filename, 'wb') as f:
            for chunk in chunks:
                f.write(chunk.Content)

    def UploadConfigFile(self, request, context):
        print("Uploading Configuration file")
        filename = self.conffile
        self.save_chunks_to_file(request, filename)
        self.upload_config()
        return vsperf_pb2.UploadStatus(Message="Successfully Uploaded",
                                       Code=1)

        # Same file file and assign the path to self.vsperf_conf

    def StartTest(self, request, context):
        print("Starting test " + request.testtype + " and using config file " +
              request.conffile)
        self.run_test()
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

import vsperf_pb2_grpc as vsperf_pb2_grpc
from concurrent import futures
import time
#import math
import grpc
import vsperf_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class VsperfController(vsperf_pb2_grpc.ControllerServicer):
    def __init__(self):
        print("Init Function")

    def VsperfInstall(self, request, context):
        print("Installing VSPERF")
        print(request.ip)
        print(request.uname)
        print(request.pwd)
        return vsperf_pb2.StatusReply(message="Successfully Installed")

    def UploadConfigfile(self, request, context):
        print("Uploading Configuration file")


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

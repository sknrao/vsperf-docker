import vsperf_pb2
import vsperf_pb2_grpc
import grpc

def vsperf_install(stub):
    print("Build Message")
    hostinfo = vsperf_pb2.HostInfo(ip='127.0.0.1', uname='root', pwd='pwd')
    install_reply = stub.VsperfInstall(hostinfo)
    print(install_reply.message)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = vsperf_pb2_grpc.ControllerStub(channel)
        print("-------------- Install -------------")
        vsperf_install(stub)

if __name__ == '__main__':
    run()

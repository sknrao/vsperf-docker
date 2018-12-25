import vsperf_pb2
import vsperf_pb2_grpc
import grpc

CHUNK_SIZE = 1024 * 1024  # 1MB


def get_file_chunks(filename):
    with open(filename, 'rb') as f:
        while True:
            piece = f.read(CHUNK_SIZE);
            if len(piece) == 0:
                return
            yield vsperf_pb2.ConfFile(Content=piece)


def upload_config(stub):
    filename = '/home/sridhar/vsperf-trex.conf'
    chunks = get_file_chunks(filename)
    upload_status = stub.UploadConfigFile(chunks)
    print(upload_status.Message)

def start_test(stub):
    print("Later")
    test_control = vsperf_pb2.ControlVsperf(testtype='PVP',
                                            conffile='vsperf.conf')
    control_reply = stub.StartTest(test_control)
    print(control_reply.message)

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
        print("-------------- Upload File -------------")
        upload_config(stub)
        print("-------------- Run Test -------------")
        start_test(stub)

if __name__ == '__main__':
    run()

import configparser
import sys
import proto.vsperf_pb2 as vsperf_pb2
import proto.vsperf_pb2_grpc as vsperf_pb2_grpc
import grpc

CHUNK_SIZE = 1024 * 1024  # 1MB


class VsperfClient(object):
    """
    This class reprsents the VSPERF-client.
    It talks to vsperf-docker to perform installation, configuration and
    test-execution
    """

    def __init__(self):
        self.cfp = 'vsperfclient.conf'
        self.config = configparser.RawConfigParser()
        self.config.read(self.cfp)

    def get_channel_info(self):
        return (self.config.get('Server', 'ip'),
                self.config.get('Server', 'port'))

    def upload_config(self, stub):
        filename = '/home/sridhar/vsperf-trex.conf'
        chunks = self.get_file_chunks(filename)
        upload_status = stub.UploadConfigFile(chunks)
        print(upload_status.Message)

    def start_test(self, stub):
        print("Later")
        test_control = vsperf_pb2.ControlVsperf(testtype =
                                                self.config.get('Testcase',
                                                                'test'),
                                                conffile =
                                                self.config.get('Testcase',
                                                                'conffile'))
        control_reply = stub.StartTest(test_control)
        print(control_reply.message)

    def vsperf_install(self, stub):
        print("Build Message")
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = stub.VsperfInstall(hostinfo)
        print(install_reply.message)

    def get_file_chunks(self, filename):
        with open(filename, 'rb') as f:
            while True:
                piece = f.read(CHUNK_SIZE)
                if len(piece) == 0:
                    return
                yield vsperf_pb2.ConfFile(Content=piece)


# from https://stackoverflow.com/questions/3041986/\
# apt-command-line-interface-like-yes-no-input
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def run():
    client = VsperfClient()
    ip, port = client.get_channel_info()
    print(ip + ':' + port)
    with grpc.insecure_channel(ip + ':' + port) as channel:
        stub = vsperf_pb2_grpc.ControllerStub(channel)
        if query_yes_no("Do you want to install VSPERF on the cost?"):
            client.vsperf_install(stub)
        if query_yes_no("Do you want to upload the config file?"):
            client.upload_config(stub)
        if query_yes_no("Do you want to run the test?"):
            client.start_test(stub)

if __name__ == '__main__':
    run()

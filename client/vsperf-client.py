import configparser
import sys
import proto.vsperf_pb2 as vsperf_pb2
import proto.vsperf_pb2_grpc as vsperf_pb2_grpc
import grpc
# import os

CHUNK_SIZE = 1024 * 1024  # 1MB


header = "\
 _  _  ___  ____  ____  ____  ____     ___  __    ____  ____  _  _  ____\n\
( \/ )/ __)(  _ \( ___)(  _ \( ___)   / __)(  )  (_  _)( ___)( \( )(_  _)\n\
 \  / \__ \ )___/ )__)  )   / )__)   ( (__  )(__  _)(_  )__)  )  (   )(\n\
  \/  (___/(__)  (____)(_)\_)(__)     \___)(____)(____)(____)(_)\_) (__)\n\
\n"

colors = {
        'blue': '\033[94m',
        'pink': '\033[95m',
        'green': '\033[92m',
        }


def colorize(string, color):
    if color not in colors:
        return string
    return colors[color] + string + '\033[0m'


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

    def create_stub(self, channel):
        self.stub = vsperf_pb2_grpc.ControllerStub(channel)

    def upload_config(self):
        filename = self.config.get('ConfFile', 'path')
        chunks = self.get_file_chunks(filename)
        upload_status = self.stub.UploadConfigFile(chunks)
        print(upload_status.Message)

    def upload_tgen_config(self):
        filename = self.config.get('ConfFile', 'tgenpath')
        chunks = self.get_file_chunks(filename)
        upload_status = self.stub.TGenUploadConfigFile(chunks)
        print(upload_status.Message)

    def start_test(self):
        test_control = vsperf_pb2.ControlTGen(params =
                                              self.config.get('TGen',
                                                              'params'),
                                              conffile =
                                              self.config.get('TGen',
                                                              'conffile'))
        control_reply = self.stub.StartTest(test_control)
        print(control_reply.message)

    def start_tgen(self):
        tgen_control = vsperf_pb2.ControlVsperf(testtype =
                                                self.config.get('Testcase',
                                                                'test'),
                                                conffile =
                                                self.config.get('Testcase',
                                                                'conffile'))
        control_reply = self.stub.StartTest(test_control)
        print(control_reply.message)

    def vsperf_install(self):
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = self.stub.VsperfInstall(hostinfo)
        print(install_reply.message)

    def collectd_install(self):
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = self.stub.CollectdInstall(hostinfo)
        print(install_reply.message)

    def tgen_install(self):
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        install_reply = self.stub.TGenInstall(tgeninfo)
        print(install_reply.message)

    def host_connect(self):
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        connect_reply = self.stub.HostConnect(hostinfo)
        print(connect_reply.message)

    def tgen_connect(self):
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        connect_reply = self.stub.TGenHostConnect(tgeninfo)
        print(connect_reply.message)

    def get_file_chunks(self, filename):
        with open(filename, 'rb') as f:
            while True:
                piece = f.read(CHUNK_SIZE)
                if len(piece) == 0:
                    return
                yield vsperf_pb2.ConfFile(Content=piece)


def run():
    client = VsperfClient()
    menuItems = [
        {"Connect to DUT Host": client.host_connect},
        {"Install VSPERF": client.vsperf_install},
        {"Connect to TGen Host": client.tgen_connect},
        {"Install TGen ": client.tgen_install},
        {"Install Collectd": client.collectd_install},
        {"Upload TGen Configuration File": client.upload_tgen_config},
        {"Start TGen ": client.start_tgen},
        {"Upload Test Configuration File": client.upload_config},
        {"Start Test": client.start_test},
        {"Exit": sys.exit}
    ]
    ip, port = client.get_channel_info()
    with grpc.insecure_channel(ip + ':' + port) as channel:
        client.create_stub(channel)
        while True:
            # os.system('clear')
            print(colorize(header, 'blue'))
            print(colorize('version 0.1\n', 'pink'))
            for item in menuItems:
                print(colorize("[" +
                               str(menuItems.index(item)) + "]", 'green') +
                      item.keys()[0])
            choice = raw_input(">> ")
            try:
                if int(choice) < 0:
                    raise ValueError
                menuItems[int(choice)].values()[0]()
            except (ValueError, IndexError):
                pass

if __name__ == '__main__':
    run()

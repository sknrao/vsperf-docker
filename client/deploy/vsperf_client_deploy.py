# pylint: disable=R0904
"""Deploy : vsperf_deploy_client"""


import configparser
import sys
from pathlib import Path


import grpc
from proto import vsperf_pb2
from proto import vsperf_pb2_grpc

CHUNK_SIZE = 1024 * 1024  # 1MB


HEADER = r"""
 _  _  ___  ____  ____  ____  ____     ___  __    ____  ____  _  _  ____
( \/ )/ __)(  _ \( ___)(  _ \( ___)   / __)(  )  (_  _)( ___)( \( )(_  _)
 \  / \__ \ )___/ )__)  )   / )__)   ( (__  )(__  _)(_  )__)  )  (   )(
  \/  (___/(__)  (____)(_)\_)(__)     \___)(____)(____)(____)(_)\_) (__)
"""

COLORS = {
    'blue': '\033[94m',
    'pink': '\033[95m',
    'green': '\033[92m',
}


def colorize(string, color):
    """Colorized HEADER"""
    if color not in COLORS:
        return string
    return COLORS[color] + string + '\033[0m'


class VsperfClient():
    """
    This class reprsents the VSPERF-client.
    It talks to vsperf-docker to perform installation, configuration and
    test-execution
    """

    def __init__(self):
        """read vsperfclient.conf"""
        self.cfp = 'vsperfclient.conf'
        self.config = configparser.RawConfigParser()
        self.config.read(self.cfp)
        self.stub = None

    def get_channel_info(self):
        """get the channel data"""
        return (self.config.get('Server', 'ip'),
                self.config.get('Server', 'port'))

    def create_stub(self, channel):
        """create stub to talk to controller"""
        self.stub = vsperf_pb2_grpc.ControllerStub(channel)

    def host_connect(self):
        """provice dut-host credential to controller"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        connect_reply = self.stub.HostConnect(hostinfo)
        print(connect_reply.message)

    def tgen_connect(self):
        """provide tgen-host credential to controller"""
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        connect_reply = self.stub.TGenHostConnect(tgeninfo)
        print(connect_reply.message)

    def exit_section(self):
        """exit"""
    @classmethod
    def section_execute(cls, menuitems, client):
        """it will use to enter into sub-option"""
        ip_add, port = client.get_channel_info()
        channel = grpc.insecure_channel(ip_add + ':' + port)

        while True:
            client.create_stub(channel)
            while True:
                # os.system('clear')
                print(colorize(HEADER, 'blue'))
                print(colorize('version 0.1\n', 'pink'))
                for item in menuitems:
                    print(colorize("[" +
                                   str(menuitems.index(item)) + "]", 'green') +
                          list(item.keys())[0])
                choice = input(">> ")
                try:
                    if int(choice) < 0:
                        raise ValueError
                    if (int(choice) >= 0) and (int(choice) < (len(menuitems) - 1)):
                        list(menuitems[int(choice)].values())[0]()
                    else:
                        break
                except (ValueError, IndexError):
                    pass
            break

    def upload_tgen_config(self):
        """t-rex config file as a chunk to controller"""
        user_preference = str(input("Are you wanted to use default location specified " \
        	                        "in vsperfclient.conf?[Y/N] : "))
        while True:
            if 'y' in user_preference.lower().strip():
                filename = self.config.get('ConfFile', 'tgenpath')
                break
            elif 'n' in user_preference.lower().strip():
                filename = str(input("Provide correct location for your t-rex configuration " \
                                     "file where trex_cfg.yaml exist\n" \
                                     "e.g: /home/user_name/client/deploy/trex_cfg.yaml \n" \
                                     "Provide location: \n"))
                user_file = Path("{}".format(filename.strip()))
                if user_file.is_file():
                    break
                else:
                    print("**************File Does Not Exist*****************\n")
                    continue
            else:
                print("Invalid Input")
                user_preference = str(input("Are you wanted to use default location specified" \
                                     " in vsperfclient.conf?[Y/N] : "))
                continue

        filename = filename.strip()
        chunks = self.get_file_chunks(filename)
        upload_status = self.stub.TGenUploadConfigFile(chunks)
        print(upload_status.Message)

    def vsperf_install(self):
        """vsperf install on dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = self.stub.VsperfInstall(hostinfo)
        print(install_reply.message)

    def collectd_install(self):
        """collectd install on dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        install_reply = self.stub.CollectdInstall(hostinfo)
        print(install_reply.message)

    def tgen_install(self):
        """install t-rex on Tgen host"""
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        install_reply = self.stub.TGenInstall(tgeninfo)
        print(install_reply.message)
    @classmethod
    def get_file_chunks(cls, filename):
        """convert file into chunk to stream between client and controller"""
        with open(filename, 'rb') as f_1:
            while True:
                piece = f_1.read(CHUNK_SIZE)
                if not piece:
                    return
                yield vsperf_pb2.ConfFile(Content=piece)

    def dut_hugepage_config(self):
        """setup hugepages on dut-host"""
        configparam = vsperf_pb2.HugepConf(hpmax=self.config.get('HugepageConfig', 'HpMax'), \
                                           hprequested=self.config.get('HugepageConfig',\
                                            'HpRequested'))
        config_status_reply = self.stub.DutHugepageConfig(configparam)
        print(config_status_reply.message)

    def upload_collectd_config(self):
        """collectd config file chunks forwarded to controller"""
        user_preference = str(input("Are you wanted to use default location specified " \
        	                        "in vsperfclient.conf?[Y/N] : "))
        while True:
            if 'y' in user_preference.lower().strip():
                filename = self.config.get('ConfFile', 'collectdpath')
                break
            elif 'n' in user_preference.lower().strip():
                filename = str(input("Provide correct location for your collectd configuration " \
                	                 "file where collectd.conf exist\n" \
                                     "e.g: /home/user_name/client/deploy/collectd.conf \n" \
                                     "Provide location: \n"))
                user_file = Path("{}".format(filename.strip()))
                if user_file.is_file():
                    break
                else:
                    print("**************File Does Not Exist*****************\n")
                    continue
            else:
                print("Invalid Input")
                user_preference = str(input("Are you wanted to use default location specified" \
                                     " in vsperfclient.conf?[Y/N] : "))
                continue
        filename = filename.strip()
        chunks = self.get_file_chunks(filename)
        upload_status = self.stub.CollectdUploadConfig(chunks)
        print(upload_status.Message)

    def dut_check_dependecies(self):
        """check_dependecies on dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        check_reply = self.stub.CheckDependecies(hostinfo)
        print(check_reply.message)

    @classmethod
    def establish_connection(cls):
        """
        This Function use to establish connection for vsperf
        """
        client = VsperfClient()
        print("Establlish connection for vsperf")
        menuitems_connection = [
            {"Connect to DUT Host": client.host_connect},
            {"Connect to TGen Host": client.tgen_connect},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_connection, client)
    @classmethod
    def vsperf_setup(cls):
        """setup sub-options"""
        client = VsperfClient()
        print("Prerequisites Installation for VSPERF")
        menuitems_setup = [
            {"Install VSPERF": client.vsperf_install},
            {"Install TGen ": client.tgen_install},
            {"Install Collectd": client.collectd_install},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client)
    @classmethod
    def upload_config_files(cls):
        """all the upload sub-options"""
        client = VsperfClient()

        menuitems_setup = [
            {"Upload TGen Configuration File": client.upload_tgen_config},
            {"Upload Collectd Configuration File": client.upload_collectd_config},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client)
    @classmethod
    def manage_sysparam_config(cls):
        """manage system parameter on dut host before run test"""
        client = VsperfClient()
        menuitems_setup = [
            {"DUT-Host HugePage Configuration": client.dut_hugepage_config},
            {"Check VSPERF Dependecies on DUT-Host": client.dut_check_dependecies},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client)

def run():
    """It will run the actul primary options"""
    client = VsperfClient()
    menuitems = [
        {"Establish Connections": client.establish_connection},
        {"VSPERF Prerequisites Installation": client.vsperf_setup},
        {"Upload Configuration Files": client.upload_config_files},
        {"Manage System Configuration": client.manage_sysparam_config},
        {"Exit": sys.exit}
    ]
    ip_add, port = client.get_channel_info()
    channel = grpc.insecure_channel(ip_add + ':' + port)
    while True:
        client.create_stub(channel)
        while True:
            # os.system('clear')
            print(colorize(HEADER, 'blue'))
            print(colorize('version 0.1\n', 'pink'))
            for item in menuitems:
                print(colorize("[" +
                               str(menuitems.index(item)) + "]", 'green') +
                      list(item.keys())[0])
            choice = input(">> ")
            try:
                if int(choice) < 0:
                    raise ValueError
                list(menuitems[int(choice)].values())[0]()
            except (ValueError, IndexError):
                pass


if __name__ == '__main__':
    run()

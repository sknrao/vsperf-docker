# pylint: disable=R0904
"""Deploy : vsperf_test_client"""


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

    def upload_config(self):
        """transfer config file as a chunk to controller"""
        user_preference = str(input("Are you wanted to use default location specified " \
                                    "in vsperfclient.conf?[Y/N] : "))
        while True:
            if 'y' in user_preference.lower().strip():
                filename = self.config.get('ConfFile', 'path')
                break
            elif 'n' in user_preference.lower().strip():
                filename = str(input("Provide correct location for your test configuration " \
                                     "file where vsperf.conf exist\n" \
                                     "***************** Make Sure You Use Choose Correct" \
                                     " Test File for Upload*******************\n" \
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
        upload_param = self.get_file_chunks(filename)
        upload_status = self.stub.UploadConfigFile(upload_param)
        print(upload_status.Message)

    def start_test(self):
        """start test parameter, test config file and test name"""
        test_control = vsperf_pb2.ControlVsperf(testtype=self.config.get('Testcase', 'test'), \
        	                                    conffile=self.config.get('Testcase', 'conffile'))
        control_reply = self.stub.StartTest(test_control)
        print(control_reply.message)

    def start_tgen(self):
        """start t-rex traffic generetor on tgen-host"""
        tgen_control = vsperf_pb2.ControlTGen(params=self.config.get('TGen', 'params'), \
        	                                  conffile=self.config.get('TGen', 'conffile'))
        control_reply = self.stub.StartTGen(tgen_control)
        print(control_reply.message)

    @classmethod
    def get_file_chunks(cls, filename):
        """convert file into chunk to stream between client and controller"""
        with open(filename, 'rb') as f_1:
            while True:
                file_path = filename
                file_path_list = file_path.split("/")
                test_filename = file_path_list[(len(file_path_list)-1)]
                piece = f_1.read(CHUNK_SIZE)
                if not piece:
                    return None
                return vsperf_pb2.ConfFile(Content=piece, Filename=test_filename)

    def test_status(self):
        """check the test_status"""
        test_check = vsperf_pb2.StatusQuery(
            testtype=self.config.get('Testcase', 'test'))
        check_result_reply = self.stub.TestStatus(test_check)
        print(check_result_reply.message)

    def vsperf_terminate(self):
        """after running test terminate vsperf on dut host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        termination_reply = self.stub.TerminateVsperf(hostinfo)
        print(termination_reply.message)

    def start_beats(self):
        """start beats on dut-host before running test"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.StartBeats(hostinfo)
        print(status_reply.message)

    def remove_vsperf(self):
        """remove vsperf from dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveVsperf(hostinfo)
        print(status_reply.message)

    def remove_result_folder(self):
        """remove resutl folder from dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveResultFolder(hostinfo)
        print(status_reply.message)

    def remove_config_files(self):
        """remove all config files"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveUploadedConfig(hostinfo)
        print(status_reply.message)

    def remove_collectd(self):
        """remove collectd from dut-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveCollectd(hostinfo)
        print(status_reply.message)

    def remove_everything(self):
        """remove everything from dut host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.RemoveEverything(hostinfo)
        print(status_reply.message)

    def sanity_nic_check(self):
        """nic is available on tgen host check"""
        tgeninfo = vsperf_pb2.HostInfo(ip=self.config.get('TGen', 'ip'),
                                       uname=self.config.get('TGen', 'uname'),
                                       pwd=self.config.get('TGen', 'pwd'))
        status_reply = self.stub.SanityNICCheck(tgeninfo)
        print(status_reply.message)

    def sanity_collectd_check(self):
        """check collecd properly running"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityCollectdCheck(hostinfo)
        print(status_reply.message)

    def cpu_allocation_check(self):
        """check cpu allocation"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityCPUAllocationCheck(hostinfo)
        print(status_reply.message)

    def sanity_vnf_path(self):
        """vnf path available on dut host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityVNFpath(hostinfo)
        print(status_reply.message)

    def sanity_vsperf_check(self):
        """check vsperf correctly installed"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityVSPERFCheck(hostinfo)
        print(status_reply.message)

    def sanity_dut_tgen_conn_check(self):
        """check the connection between dut-host and tgen-host"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.SanityTgenConnDUTCheck(hostinfo)
        print(status_reply.message)

    def dut_test_availability(self):
        """dut-host is free for test check"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.DUTvsperfTestAvailability(hostinfo)
        print(status_reply.message)

    def get_test_conf_from_dut(self):
        """get the vsperf test config file from dut host for user to check"""
        hostinfo = vsperf_pb2.HostInfo(ip=self.config.get('Host', 'ip'),
                                       uname=self.config.get('Host', 'uname'),
                                       pwd=self.config.get('Host', 'pwd'))
        status_reply = self.stub.GetVSPERFConffromDUT(hostinfo)
        print(status_reply.message)

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
    def test_status_check(cls):
        """after running test , test status related sub-options"""
        client = VsperfClient()
        menuitems_setup = [
            {"Test status": client.test_status},
            {"Get Test Configuration file from DUT-host": client.get_test_conf_from_dut},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client)

    @classmethod
    def sanity_check_options(cls):
        """all sanity check sub-options"""
        client = VsperfClient()
        menuitems_setup = [
            {"Check installed VSPERF": client.sanity_vsperf_check},
            {"Check Test Config's VNF path is available on DUT-Host": client.sanity_vnf_path},
            {"Check NIC PCIs is available on Traffic Generetor": client.sanity_nic_check},
            {"Check CPU allocation on DUT-Host": client.cpu_allocation_check},
            {"Check installed Collectd": client.sanity_collectd_check},
            {"Check Connection between DUT-Host and Traffic Generator Host":
             client.sanity_dut_tgen_conn_check},
            {"Return to Previous Menu": client.exit_section}
        ]
        client.section_execute(menuitems_setup, client)

    @classmethod
    def run_test(cls):
        """run test sub-options"""
        print("**Before user Run Tests we highly recommend you to perform Sanity Checks.......")
        client = VsperfClient()
        menuitems_setup = [
            {"Start TGen ": client.start_tgen},
            {"Start Beats": client.start_beats},
            {"Start Test": client.start_test},
            {"Return to Previous Menu": client.exit_section}

        ]
        client.section_execute(menuitems_setup, client)

    @classmethod
    def clean_up(cls):
        """clean-up sub-options"""
        print(
            "*******************************************************************\n\n\
             IF you are performing Test on IntelPOD 12 - Node 4, Be careful during removal\n\n\
             *******************************************************************")
        client = VsperfClient()
        menuitems_setup = [
            {"Remove VSPERF": client.remove_vsperf},
            {"Terminate VSPERF": client.vsperf_terminate},
            {"Remove Results from DUT-Host": client.remove_result_folder},
            {"Remove Uploaded Configuration Files": client.remove_config_files},
            {"Remove Collectd": client.remove_collectd},
            {"Remove Everything": client.remove_everything},
            {"Return to Previous Menu": client.exit_section}

        ]
        client.section_execute(menuitems_setup, client)


def run():
    """It will run the actul primary options"""
    client = VsperfClient()
    menuitems = [
        {"Establish Connections": client.establish_connection},
        {"Upload Test Configuration File": client.upload_config},
        {"Perform Sanity Checks before Run Tests": client.sanity_check_options},
        {"Check DUT-Host is available for Test": client.dut_test_availability},
        {"Run Test": client.run_test},
        {"Test Status": client.test_status_check},
        {"Clean-Up": client.clean_up},
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

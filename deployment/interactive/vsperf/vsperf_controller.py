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

# pylint: disable=R0904
# pylint: disable=R0902
# twenty-two is reasonable in this script
# pylint: disable=W0221
"""
VSPER docker-controller.
"""

import io
import time
from concurrent import futures
import grpc

from proto import vsperf_pb2
from proto import vsperf_pb2_grpc
from utils import ssh

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
        # pylint: disable=too-many-instance-attributes
        # twenty-two is reasonable in this case.
        self.client = None
        self.dut = None
        self.user = None
        self.pwd = None
        self.vsperf_conf = None
        self.tgen_client = None
        self.tgen = None
        self.tgen_user = None
        self.tgenpwd = None
        self.tgen_conf = None
        self.scenario = None
        self.hpmax = None
        self.hprequested = None
        self.logdir = None
        self.testcase = None
        self.tgen_ip_address = None
        self.testtype = None
        self.trex_conf = None
        self.trex_params = None
        self.conffile = "vsperf.conf"
        # Default TGen is T-Rex
        self.trex_conffile = "trex_cfg.yml"
        self.collectd_conffile = "collectd.conf"

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
        install_cmd += "echo '{}' | sudo -S ./build_base_machine.sh ".format(
            self.pwd)
        #install_cmd += "./build_base_machine.sh"
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
        # Sometimes hugepage store in /mnt/huge in order to free up the
        # hugepage removing this stored hugepage is necessory
        rmv_cmd = "cd /mnt/huge && echo {} | sudo -S rm -rf *".format(self.pwd)
        self.client.run(rmv_cmd, pty=True)
        cmd = "source ~/vsperfenv/bin/activate ; "
        #cmd = "scl enable python33 bash ; "
        cmd += "cd vswitchperf_ieee_demo && "
        cmd += "./vsperf "
        if self.vsperf_conf:
            cmd += "--conf-file ~/vsperf.conf "
            # cmd += self.conffile
        cmd += self.scenario
        with PseudoFile() as pref:
            self.client.run(cmd, stdout=pref, pty=True)

    def TestStatus(self, request, context):
        """
        Chechk for the test status after performing test
        """
        testtype_list = request.testtype.split(",")
        test_success = []
        test_failed = []
        testtype_list_len = len(testtype_list)
        for test in testtype_list:
            #latest_result_cmd = "find /tmp -mindepth 1 -type d -cmin -5 -printf '%f'"
            test_result_dir = str((self.client.\
            	              execute("find /tmp -mindepth 1 -type d -cmin -5 -printf '%f'")[1]).\
            	              split('find')[0])
            #test_date_cmd = "date +%F"
            test_date = str(self.client.execute("date +%F")[1]).replace("\n", "")
            if test_date in test_result_dir:
                testcase_check_cmd = "cd /tmp && cd `ls -t | grep results | head -{} | tail -1`".\
                                      format(testtype_list_len)
                testcase_check_cmd += " && find . -maxdepth 1 -name '*{}*'".\
                                        format(test)
                testcase_check_output = str(self.client.execute(testcase_check_cmd)[1]).\
                                        split('\n', 2)
                check = 0
                for i in testcase_check_output:
                    if (".csv" in i) or (".md" in i) or (".rst" in i):
                        check += 1
                if check == 3:
                    test_success.append(test)
                else:
                    test_failed.append(test)
                testtype_list_len -= 1
        if len(testtype_list) == len(test_success):
            return vsperf_pb2.StatusReply(message="All Test Successfully Completed on DUT-Host\
                                          \nResults... [OK]")
        if not test_success:
            return vsperf_pb2.StatusReply(
                message="All Test Failed on DUT-Host \nResults... [Failed]")
        return vsperf_pb2.StatusReply(message="Only {} Test failed    Results ... [Failed]\n\
        	    All other Test Successfully Completed on DUT-Host     Results... [OK] ".\
        	    format(test_failed))

    def VsperfInstall(self, request, context):
        """
        Handle VSPERF install command from client
        """
        # print("Installing VSPERF")
        vsperf_check_cmd = "source ~/vsperfenv/bin/activate ; cd vswitchperf* && ./vsperf --help"
        vsperf_check_cmd_result = str(self.client.execute(vsperf_check_cmd)[1])
        vsperf_verify_list = [
            'usage',
            'positional arguments',
            'optional arguments',
            'test selection options',
            'test behavior options']
        for idx, i in enumerate(vsperf_verify_list, start=1):
            if str(i) in vsperf_check_cmd_result:
                if idx < 5:
                    continue
                elif idx == 5:
                    return vsperf_pb2.StatusReply(
                        message="VSPERF is Already Installed on DUT-Host")
        self.install_vsperf()
        return vsperf_pb2.StatusReply(message="VSPERF Successfully Installed DUT-Host")
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
        # This is chechking if vsperf.conf already exist first remove that and
        # then upload the new file.
        check_test_config_cmd = "find ~/ -maxdepth 1 -name vsperf.conf"
        check_test_result = str(self.client.execute(check_test_config_cmd)[1])
        if "vsperf.conf" in check_test_result:
            self.client.run("rm -f vsperf.conf")
        self.upload_config()
        return vsperf_pb2.UploadStatus(Message="Successfully Uploaded",
                                       Code=1)

    def StartTest(self, request, context):
        """
        Handle start-test command from client
        """
        self.vsperf_conf = request.conffile
        self.testtype = request.testtype
        testtype_list = self.testtype.split(",")
        for test in testtype_list:
            self.scenario = test
            self.run_test()
        return vsperf_pb2.StatusReply(message="Test Successfully running...")

###### Traffic Generator Related functions ####
    def TGenHostConnect(self, request, context):
        """
        Connect to TGen-Node
        """
        self.tgen = request.ip
        self.tgen_user = request.uname
        self.tgenpwd = request.pwd
        self.tgen_setup()
        return vsperf_pb2.StatusReply(message="Successfully Connected")

    def tgen_setup(self):
        """
        Setup the T-Gen Client
        """
        # Just connect to VM.
        self.tgen_client = ssh.SSH(host=self.tgen, user=self.tgen_user,
                                   password=self.tgenpwd)
        self.tgen_client.wait()

    def TGenInstall(self, request, context):
        """
        Install Traffic generator on the node.
        """
        kill_cmd = "pkill -f ./t-rex"
        self.tgen_client.send_command(kill_cmd)
        tgen_start_cmd = "cd trex_2.37/scripts && ./t-rex-64 -f cap2/dns.yaml -d 100 -m 1 --nc"
        tgen_start_cmd_result = int(
            self.tgen_client.execute(tgen_start_cmd)[0])
        if tgen_start_cmd_result == 0:
            return vsperf_pb2.StatusReply(
                message="Traffic Generetor has T-rex Installed")
        download_cmd = "git clone https://github.com/cisco-system-traffic-generator/trex-core"
        self.tgen_client.run(download_cmd)
        install_cmd = "cd trex-core/linux_dpdk ; ./b configure ; ./b build"
        self.tgen_client.run(install_cmd)
        # before you setup your trex_cfg.yml make sure to do sanity check
        # NIC PICs and extablished route between your DUT and Test Device.
        return vsperf_pb2.StatusReply(message="Traffic Generetor has now T-rex Installed")

    def TGenUploadConfigFile(self, request, context):
        """
        Handle upload config-file command from client
        """
        filename = self.trex_conffile
        self.save_chunks_to_file(request, filename)
        check_trex_config_cmd = "echo {} | sudo -S find /etc -maxdepth 1 -name trex_cfg.yaml".\
                                 format(self.tgenpwd)
        check_test_result = str(
            self.tgen_client.execute(check_trex_config_cmd)[1])
        if "trex_cfg.yaml" in check_test_result:
            self.tgen_client.run("rm -f /etc/trex_cfg.yaml")
        self.upload_tgen_config()
        self.tgen_client.run(
            "echo {} | sudo -S mv ~/trex_cfg.yaml /etc/".format(self.tgenpwd),
            pty=True)
        return vsperf_pb2.UploadStatus(Message="Successfully Uploaded",
                                       Code=1)

    def upload_tgen_config(self):
        """
        Perform file upload.
        """
        self.tgen_client.put_file(self.trex_conffile, '/root/trex_cfg.yaml')

    def install_tgen(self):
        """
        Perform actual installation
        """
        download_cmd = "git clone https://github.com/cisco-system-traffic-\
            generator/trex-core.git"
        self.tgen_client.run(download_cmd)
        install_cmd = "mv /root/trex-core /root/trex_latest"
        self.tgen_client.run(install_cmd)

# Tool-Chain related Functions####3

    def install_collectd(self):
        """
        installation of the collectd
        """
        check_collectd_config_cmd = "find /opt -maxdepth 1 -name 'collectd'"
        check_test_result = str(
            self.client.execute(check_collectd_config_cmd)[1])
        if "collectd" in check_test_result:
            pass
        else:
            download_cmd = "git clone https://github.com/collectd/collectd.git"
            self.client.run(download_cmd)
            build_cmd = "cd collectd ; "
            build_cmd += "./build.sh"
            self.client.run(build_cmd)
            config_cmd = "cd collectd ; ./configure --enable-syslog "
            config_cmd += "--enable-logfile --enable-hugepages --enable-debug ; "
            self.client.run(config_cmd)
            install_cmd = "cd collectd ; make ; "
            install_cmd += "echo '{}' | sudo -S make install".format(self.pwd)
            self.client.run(install_cmd, pty=True)

    def CollectdInstall(self, request, context):
        """
        Install Collectd on DUT
        """
        self.install_collectd()
        return vsperf_pb2.StatusReply(
            message="Collectd Successfully Installed on DUT-Host")

    def upload_collectd_config(self):
        """
        Perform file upload.
        """
        self.client.put_file(self.collectd_conffile, '~/collectd.conf')
        move_cmd = "echo '{}' | sudo -S mv ~/collectd.conf /opt/collectd/etc".format(
            self.pwd)
        self.client.run(move_cmd, pty=True)

    def CollectdUploadConfig(self, request, context):
        """
        Upload collectd config-file on DUT
        """
        filename = self.collectd_conffile
        self.save_chunks_to_file(request, filename)
        self.upload_collectd_config()
        return vsperf_pb2.UploadStatus(
            Message="Successfully Collectd Configuration Uploaded", Code=1)

    def StartBeats(self, request, context):
        """
        Start fileBeats on DUT
        """
        run_cmd = "echo '{}' | sudo -S service filebeat start".format(self.pwd)
        #run_cmd = "sudo service filebeat start"
        self.client.run(run_cmd, pty=True)
        return vsperf_pb2.StatusReply(message="Beats are started on DUT-Host")

###System Configuration related functions###

    def DutHugepageConfig(self, request, context):
        """
        Configure the DUT system hugepage parameter from client
        """
        self.hpmax = int(request.hpmax)
        self.hprequested = int(request.hprequested)
        hugepage_cmd = "echo '{}' | sudo -S mkdir -p /mnt/huge ; ".format(
            self.pwd)
        hugepage_cmd += "echo '{}' | sudo -S mount -t hugetlbfs nodev /mnt/huge".format(
            self.pwd)
        self.client.run(hugepage_cmd, pty=True)
        hp_nr_cmd = "cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages"
        hp_free_cmd = "cat /sys/devices/system/node/node0/hugepages/hugepages-2048kB/free_hugepages"
        hp_nr = int(self.client.execute(hp_nr_cmd)[1])
        hp_free = int(self.client.execute(hp_free_cmd)[1])
        if hp_free <= self.hprequested:
            hp_nr_new = hp_nr + (self.hprequested - hp_free)
            if hp_nr_new > self.hpmax:
                hp_nr_new = self.hpmax

        nr_hugepage_cmd = "echo '{}' | sudo -S bash -c \"echo 'vm.nr_hugepages={}' >>".\
                           format(self.pwd, hp_nr_new)
        nr_hugepage_cmd += " /etc/sysctl.conf\""
        self.client.run(nr_hugepage_cmd, pty=True)

        dict_cmd = "cat /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
        dict_check = int(self.client.execute(dict_cmd)[0])
        if dict_check == 0:
            node1_hugepage_cmd = "echo '{}' | sudo -s bash -c \"echo 0 >".format(self.pwd)
            node1_hugepage_cmd += " /sys/devices/system/node/node1/"
            node1_hugepage_cmd += "hugepages/hugepages-2048kB/nr_hugepages\""
        return vsperf_pb2.StatusReply(
            message="DUT-Host system configured with {} No of Hugepages".format(hp_nr_new))

    def CheckDependecies(self, request, context):
        """
        Check and Install required packages on DUT
        """
        packages = ['python34-tkinter', 'sysstat', 'bc']
        for pkg in packages:
            # pkg_check_cmd = "dpkg -s {}".format(pkg) for ubuntu
            pkg_check_cmd = "rpm -q {}".format(pkg)
            pkg_cmd_response = self.client.execute(pkg_check_cmd)[0]
            if pkg_cmd_response == 1:
                install_pkg_cmd = "echo '{}' | sudo -S yum install -y {}".format(
                    self.pwd, pkg)
                #install_pkg_cmd = "echo '{}' | sudo -S apt-get install -y {}".format(self.pwd,pkg)
                self.client.run(install_pkg_cmd, pty=True)

        return vsperf_pb2.StatusReply(message="Python34-tkinter, sysstat and bc Packages\
                                    are now Installed")

    def DUTvsperfTestAvailability(self, request, context):
        """
        Before running test we have to make sure there is no other test running
        """
        vsperf_ava_cmd = "ps -ef | grep -v grep | grep ./vsperf | awk '{print $2}'"
        vsperf_ava_result = len((self.client.execute(vsperf_ava_cmd)[1]).split("\n"))
        if vsperf_ava_result == 1:
            return vsperf_pb2.StatusReply(message="DUT-Host is available for performing \
            	                                   VSPERF Test\nYou can perform Test!")
        return vsperf_pb2.StatusReply(message="DUT-Host is busy right now, Wait for some time\n\
        	Always Check availability before Running Test!")


###Clean-UP process related functions####


    def vsperf_remove(self):
        """
        Actual removal of the VSPERF
        """
        vsperf_rm_cmd = "echo '{}' | sudo -S rm -r ~/vswitchperf".format(
            self.pwd)
        self.client.run(vsperf_rm_cmd)
        vsperfenv_rm_cmd = "echo '{}' | sudo -S rm -r -f ~/vsperfenv".format(
            self.pwd)
        self.client.run(vsperfenv_rm_cmd)

    def remove_uploaded_config(self):
        """
        Remove all the uploaded configuration files
        """
        vconfig_rm_cmd = "rm ~/vsperf.conf"
        self.client.run(vconfig_rm_cmd)
        tconfig_rm_cmd = "rm /etc/trex_cfg.yml"
        self.tgen_client.run(tconfig_rm_cmd)
        cdconfig_rm_cmd = "echo '{}' | sudo -S rm /opt/collectd/etc/collectd.conf".format(
            self.pwd)
        self.client.run(cdconfig_rm_cmd)

    def result_folder_remove(self):
        """
        Remove result folder on DUT
        """
        remove_cmd = "rm -r /tmp/*results*"
        self.client.run(remove_cmd)

    def collectd_remove(self):
        """
        Remove collectd from DUT
        """
        collectd_dwn_rm_cmd = "echo '{}' | sudo -S rm -r -f ~/collectd".format(
            self.pwd)
        self.client.run(collectd_dwn_rm_cmd)
        collectd_rm_cmd = "echo '{}' | sudo -S rm -r -f /opt/collectd".format(
            self.pwd)
        self.client.run(collectd_rm_cmd)

    def RemoveVsperf(self, request, context):
        """
        Handle VSPERF removal command from client
        """
        self.vsperf_remove()
        return vsperf_pb2.StatusReply(message="Successfully VSPERF Removed")

    def TerminateVsperf(self, request, context):
        """
        Terminate the VSPERF and kill processes
        """
        stress_kill_cmd = "echo '{}' | sudo -S pkill stress &> /dev/null".format(
            self.pwd)
        python3_kill_cmd = "echo '{}' | sudo -S pkill python3 &> /dev/null".format(
            self.pwd)
        qemu_kill_cmd = "echo '{}' | sudo -S killall -9 qemu-system-x86_64 &> /dev/null".format(
            self.pwd)
        self.client.run(stress_kill_cmd)
        self.client.run(python3_kill_cmd)
        self.client.run(qemu_kill_cmd)

        # sometimes qemu resists to terminate, so wait a bit and kill it again
        qemu_check_cmd = "pgrep qemu-system-x86_64"
        qemu_cmd_response = self.client.execute(qemu_check_cmd)[1]

        if qemu_cmd_response != '':
            time.sleep(5)
            self.client.run(qemu_kill_cmd)
            time.sleep(5)

        ovs_kill_cmd = "echo '{}' | sudo pkill ovs-vswitchd &> /dev/null".format(
            self.pwd)
        ovsdb_kill_cmd = "echo '{}' | sudo pkill ovsdb-server &> /dev/null".format(
            self.pwd)
        vppctl_kill_cmd = "echo '{}' | sudo pkill vppctl &> /dev/null".format(
            self.pwd)
        vpp_kill_cmd = "echo '{}' | sudo pkill vpp &> /dev/null".format(
            self.pwd)
        vpp_cmd = "echo '{}' | sudo pkill -9 vpp &> /dev/null".format(self.pwd)

        self.client.run(ovs_kill_cmd)
        time.sleep(1)
        self.client.run(ovsdb_kill_cmd)
        time.sleep(1)
        self.client.run(vppctl_kill_cmd)
        time.sleep(1)
        self.client.run(vpp_kill_cmd)
        time.sleep(1)
        self.client.run(vpp_cmd)
        time.sleep(1)

        return vsperf_pb2.StatusReply(
            message="All the VSPERF related process terminated successfully")

    def RemoveResultFolder(self, request, context):
        """
        Handle result folder removal command from client
        """
        self.result_folder_remove()
        return vsperf_pb2.StatusReply(
            message="Successfully VSPERF Results Removed")

    def RemoveUploadedConfig(self, request, context):
        """
        Handle all configuration file removal command from client
        """
        self.remove_uploaded_config()
        return vsperf_pb2.StatusReply(
            message="Successfully All Uploaded Config Files Removed")

    def RemoveCollectd(self, request, context):
        """
        Handle collectd removal command from client
        """
        self.collectd_remove()
        return vsperf_pb2.StatusReply(
            message="Successfully Collectd Removed From DUT-Host")

    def RemoveEverything(self, request, context):
        """
        Handle of removing everything from DUT command from client
        """
        self.vsperf_remove()
        self.result_folder_remove()
        self.remove_uploaded_config()
        self.collectd_remove()
        return vsperf_pb2.StatusReply(
            message="Successfully Everything Removed From DUT-Host")

    def StartTGen(self, request, context):
        """
        Handle start-Tgen command from client
        """
        self.trex_conf = request.conffile
        self.trex_params = request.params
        run_cmd = "cd trex_2.37/scripts ; "
        run_cmd += "./t-rex-64 "
        run_cmd += self.trex_params
        self.tgen_client.send_command(run_cmd)
        return vsperf_pb2.StatusReply(message="T-Rex Successfully running...")

    def SanityNICCheck(self, request, context):
        """
        Check either NIC PCI ids are Correctly placed or not
        """
        trex_conf_path = open('/usr/src/app/vsperf/trex_cfg.yaml')
        trex_conf_read = trex_conf_path.readlines()
        for i in trex_conf_read:
            if 'interfaces' in i:
                nic_pid_ids_list = [i.split("\"")[1], i.split("\"")[3]]
                trex_nic_pic_id_cmd = "lspci | egrep -i --color 'network|ethernet'"
                trex_nic_pic_id = str(self.tgen_client.execute(trex_nic_pic_id_cmd)[1]).split('\n')
                acheck = 0
                for k in trex_nic_pic_id:
                    for j in nic_pid_ids_list:
                        if j in k:
                            acheck += 1
                        else:
                            pass
                if acheck == 2:
                    return vsperf_pb2.StatusReply(message="Both the NIC PCI Ids are Correctly \
                    	configured on TGen-Host..............")
        return vsperf_pb2.StatusReply(message="You configured NIC PCI Ids Wrong in \
                TGen-Host............................[OK] \n")

    def SanityCollectdCheck(self, request, context):
        """
        Check and verify collectd is able to run and start properly
        """
        check_collectd_cmd = "find /opt -maxdepth 1 -name 'collectd'"
        check_test_result = str(self.client.execute(check_collectd_cmd)[1])
        if "collectd" in check_test_result:
            check_collectd_run_cmd = "echo {} | sudo -S service collectd start".format(self.pwd)
            self.client.run(check_collectd_run_cmd, pty=True)
            check_collectd_status_cmd = "ps aux | grep collectd"
            check_collectd_status = str(self.client.execute(check_collectd_status_cmd)[1])
            if "/sbin/collectd" in check_collectd_status:
                return vsperf_pb2.StatusReply(message="Collectd is working Fine")
            return vsperf_pb2.StatusReply(message="Collectd Fail to Start, \
            	                                   Install correctly before running Test")
        return vsperf_pb2.StatusReply(message="Collectd is not installed yet.")

    def SanityVNFpath(self, request, context):
        """
        Check if VNF image available on the mention path in Test Config File
        """
        # fetch the VNF path we placed in vsperf.conf file
        vsperf_conf_path = open('/usr/src/app/vsperf/vsperf.conf')
        vsperf_conf_read = vsperf_conf_path.readlines()
        for i in vsperf_conf_read:
            if 'GUEST_IMAGE' in i:
                vnf_image_path = i.split("'")[1]
                vnf_path_check_cmd = "find {}".format(vnf_image_path)
                vfn_path_check_result = str(
                    self.client.execute(vnf_path_check_cmd)[1])
                if vnf_image_path in vfn_path_check_result:
                    return vsperf_pb2.StatusReply(message="Test Configratuion file has Correct \
                                VNF path information on DUT-Host.....[OK]\n ")
        return vsperf_pb2.StatusReply(
            message="Test Configuration file has wrongly placed VNF path information \nVNF is \
            not available on DUT-Host................................[Failed]\n ")

    def SanityVSPERFCheck(self, request, context):
        """
        We have to make sure that VSPERF install correctly
        """
        vsperf_check_command = "source ~/vsperfenv/bin/activate ; cd vswitchperf* && "
        vsperf_check_command += "./vsperf --help"
        vsperf_check_cmd_result = str(self.client.execute(vsperf_check_command)[1])
        vsperf_verify_list = [
            'usage',
            'positional arguments',
            'optional arguments',
            'test selection options',
            'test behavior options']
        for idx, i in enumerate(vsperf_verify_list, start=1):
            if str(i) in vsperf_check_cmd_result:
                if idx < 5:
                    continue
                elif idx == 5:
                    return vsperf_pb2.StatusReply(
                        message="VSPERF Installed Correctly and Working fine\
                                 .........................[OK]")
            return vsperf_pb2.StatusReply(message="VSPERF Does Not Installed Correctly , \
                                          INSTALL IT AGAIN..............[Critical]")
        return vsperf_pb2.StatusReply(message="VSPERF Does Not Installed Correctly , \
                                      INSTALL IT AGAIN..............[Critical]")

    def SanityVSPERFOptionsCheck(self, request, context):
        """
        This sanity will check which type of Options Avialable with installed VSPERF
        """
        options_list = [
            '--version',
            '--list-trafficgens',
            '--list-collectors',
            '--list-vswitches',
            '--list-fwdapps',
            '--list-vnfs',
            '--list-loadgens',
            '--list',
        ]
        vsperf_option_str = ""
        for i in options_list:
            vsperf_option_cmd = "source ~/vsperfenv/bin/activate ; cd vswitchperf* && ./vsperf {}".\
                                format(i)
            vsperf_option_str = vsperf_option_str + str(i) + ": \n"
            vsperf_option_cmd_result = str(
                self.client.execute(vsperf_option_cmd)[1])
            vsperf_option_str = vsperf_option_str + \
                str(vsperf_option_cmd_result) + "\n"
        return vsperf_pb2.StatusReply(message="{} \nBased on the available option and \
        	Test you can buid your VSPERF test configuration file......[OK]".format(vsperf_option_str))

    def SanityTgenConnDUTCheck(self, request, context):
        """
        We should confirm the DUT connectivity with the Tgen and Traffic Generator is working or not
        """
        self.tgen_ip_address = request.ip
        tgen_connectivity_check_cmd = "ping {} -c 1".format(
            self.tgen_ip_address)
        tgen_connectivity_check_result = int(
            self.client.execute(tgen_connectivity_check_cmd)[0])
        if tgen_connectivity_check_result == 0:
            return vsperf_pb2.StatusReply(
                message="DUT-Host is successfully reachable to Traffic Generator......")
        return vsperf_pb2.StatusReply(message="DUT-Host is unsuccessful to reach the \
        	                          Traffic Generator \nMake sure to establish connection \
        	                          between DUT-Host and TGen-Host before running Test\
                                       ............... ")

    def SanityTgenCheck(self, request, context):
        """
        It will check Trex properly running or not
        """
        tgen_start_cmd_check = "cd trex_2.37/scripts && "
        tgen_start_cmd_check += "./t-rex-64 -f cap2/dns.yaml -d 100 -m 1 --nc"
        tgen_start_cmd_result = int(self.tgen_client.execute(tgen_start_cmd_check)[0])
        print(tgen_start_cmd_result)
        if tgen_start_cmd_result == 0:
            return vsperf_pb2.StatusReply(
                message="TGen-Host is successfully running T-rex")
        return vsperf_pb2.StatusReply(\
                message="TGen-Host is unable to start t-rex \nMake sure you installed \
                t-rex correctly and uploaded proper Tgen configuration file")

    def GetVSPERFConffromDUT(self, request, context):
        """
        This will extract the vsperf test configuration from DUT-Host
        """
        read_cmd = "cat ~/vsperf.conf"
        read_cmd_output = str(self.client.execute(read_cmd)[1])
        return vsperf_pb2.StatusReply(message="{}".format(read_cmd_output))


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

import logging
from watchdog.events import FileSystemEventHandler
from os.path import basename
import subprocess
import yaml
from urllib import request, parse
from urllib.error import HTTPError


class NSWatcher(FileSystemEventHandler):

    def __init__(self, config_path="ns-watcher.conf"):
        with open(config_path, 'r') as config_file:
            watcher_conf = yaml.load(config_file)
            self.pa_home = watcher_conf['pa_home']
            self.scheduler_url = watcher_conf['scheduler_url']
            self.credential_file_path = watcher_conf['credential_file_path']
            self.watch_folder = watcher_conf['watch_folder']
            self.rest_user = watcher_conf['rest_user']
            self.rest_password = watcher_conf['rest_password']
            self.url_login = f"{watcher_conf['scheduler_url']}/rest/scheduler/login"
            self.url_rm_ns = f"{watcher_conf['scheduler_url']}/rest/rm/nodesource/remove"

    def build_cli_cmd(self):
        insecure_mode = ""
        if "https" in self.scheduler_url:
            insecure_mode = "-k"
        return f"{self.pa_home}/bin/proactive-client {insecure_mode} -u {self.scheduler_url}/rest" \
               f" -c {self.credential_file_path}"

    def build_infra_cmd(self, infra):
        cmd = ""
        infra_type = infra['type']
        if "AzureVMScaleSetInfrastructure" in infra_type:
            cmd = self.create_azure_vm_ss_infra(infra)
        elif "DefaultInfrastructureManager" in infra_type:
            cmd = self.create_default_infra(infra)
        else:
            logging.info(f"creating {ns_type} not implemented yet")
        return cmd

    def build_policy_cmd(self, policy):
        cmd = ""
        policy_type = policy['type']
        if "StaticPolicy" in policy_type:
            cmd = self.create_static_policy(policy)
        else:
            logging.info(f"creating {policy_type} not implemented yet")
        return cmd

    def on_created(self, event):
        if self.is_valid_file(event):
            ns_name = self.get_ns_name(event)
            ns_to_create = yaml.load(open(event.src_path, 'r'))
            infra = self._sanitize(ns_to_create['infrastructure'])
            policy = self._sanitize(ns_to_create['policy'])
            logging.info(f"Analyzing file {event.src_path}")
            cmd_starter = self.build_cli_cmd()
            infra_cmd = self.build_infra_cmd(infra)
            policy_cmd = self.build_policy_cmd(policy)
            cmd = f"{cmd_starter} -createns {ns_name}" \
                  f" --infrastructure {infra_cmd}" \
                  f" -policy {policy_cmd}"
            logging.info(cmd)
            subprocess.check_call(cmd, shell=True)

    def on_deleted(self, event):
        ns_name = self.get_ns_name(event)
        auth_payload = {
            'username': self.rest_user,
            'password': self.rest_password
        }
        data = parse.urlencode(auth_payload).encode()
        req = request.Request(f"{self.url_login}", data=data)
        session_id = request.urlopen(req).read()
        headers = {
            'sessionid': session_id,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = parse.urlencode({'name': ns_name}).encode()
        req = request.Request(f"{self.url_rm_ns}", headers=headers, data=data)
        try:
            request.urlopen(req).read()
        except HTTPError as err:
            logging.error(f"Removing of {ns_name} failed: {err}")
        logging.info(f"Removed {ns_name}")

    @staticmethod
    def create_default_infra(infra):
        cmd = f"org.ow2.proactive.resourcemanager.nodesource.infrastructure.{infra['type']}"
        logging.info(cmd)
        return cmd

    @staticmethod
    def create_azure_vm_ss_infra(infra):
        cmd = f"org.ow2.proactive.resourcemanager.nodesource.infrastructure.{infra['type']}" \
              f" {infra['azureCredentialFile']}" \
              f" '{infra['customResourceGroupName']}'" \
              f" '{infra['maxVms']}'" \
              f" '{infra['maxNodesPerVM']}'" \
              f" '{infra['machineType']}'" \
              f" '{infra['linuxImage']}'" \
              f" '{infra['sshPublicKey']}'" \
              f" '{infra['alwaysFulfillVM']}'" \
              f" '{infra['targetNetwork']}'" \
              f" '{infra['publicIp']}'" \
              f" '{infra['backendPortNumber1']}'" \
              f" '{infra['backendPortNumber2']}'" \
              f" '{infra['azureRegion']}'" \
              f" '{infra['rmurl']}'" \
              f" '{infra['rmCredentials']}'" \
              f" '{infra['externalStorageAccount']}'" \
              f" '{infra['userCustomStartupScriptUrl']}'" \
              f" '{infra['internalCustomStartupScriptUrl']}'"
        logging.info(cmd)
        return cmd

    @staticmethod
    def create_static_policy(policy):
        return f"org.ow2.proactive.resourcemanager.nodesource.policy.{policy['type']}" \
               f" {policy['userAccessType']} {policy['providerAccessType']}"

    @staticmethod
    def _sanitize(obj):
        for name, value in obj.items():
            if value is None:
                logging.info(f"[Sanitizing parameters] `None` value detected for {name}")
                obj[name] = ""
        return obj

    @staticmethod
    def is_valid_file(event):
        return not event.is_directory and (".yml" in event.src_path or ".yaml" in event.src_path)

    @staticmethod
    def get_ns_name(event):
        """Cleaning the yml file extension
        Careful ! We assume the name is NS-compatible for the RM
        """
        ns_name = basename(event.src_path)
        if ".yml" in ns_name:
            ns_name = ns_name[0:ns_name.find(".yml")]
        if ".yaml" in ns_name:
            ns_name = ns_name[0:ns_name.find(".yaml")]
        return ns_name

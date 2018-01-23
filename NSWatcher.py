import logging
from watchdog.events import FileSystemEventHandler
from os.path import basename
import subprocess
import yaml
from urllib import request, parse


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

    def create_default_infra(self, name, ns_config):
        infra = self._sanitize(ns_config['infrastructure'])
        policy = ns_config['policy']
        insecure_mode = ""
        if "https" in self.scheduler_url:
            insecure_mode = "-k"
        cmd = f"{self.pa_home}/bin/proactive-client {insecure_mode} -u {self.scheduler_url}/rest" \
              f" -c {self.credential_file_path}" \
              f" -createns {name} --infrastructure" \
              f" org.ow2.proactive.resourcemanager.nodesource.infrastructure.{infra['type']}" \
              f" -policy org.ow2.proactive.resourcemanager.nodesource.policy.{policy['type']}" \
              f" {policy['userAccessType']}" \
              f" {policy['providerAccessType']}"
        logging.info(cmd)
        subprocess.check_call(cmd, shell=True)

    def create_azure_vm_ss_infra(self, name, ns_config):
        infra = self._sanitize(ns_config['infrastructure'])
        policy = ns_config['policy']
        insecure_mode = ""
        if "https" in self.scheduler_url:
            insecure_mode = "-k"
        cmd = f"{self.pa_home}/bin/proactive-client {insecure_mode} -u {self.scheduler_url}/rest" \
              f" -c {self.credential_file_path}" \
              f" -createns {name} --infrastructure" \
              f" org.ow2.proactive.resourcemanager.nodesource.infrastructure.{infra['type']}" \
              f" {infra['azureCredentialFile']}" \
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
              f" '{infra['internalCustomStartupScriptUrl']}'" \
              f" -policy org.ow2.proactive.resourcemanager.nodesource.policy.{policy['type']}" \
              f" {policy['userAccessType']}" \
              f" {policy['providerAccessType']}"
        logging.info(cmd)
        subprocess.check_call(cmd, shell=True)

    def on_created(self, event):
        if self.is_valid_file(event):
            ns_name = self.get_ns_name(event)
            ns_to_create = yaml.load(open(event.src_path, 'r'))
            logging.info(f"Analyzing file {event.src_path}")
            self.create_ns(ns_name, ns_to_create)

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
        request.urlopen(req).read()
        logging.info(f"Removed {ns_name}")


    def create_ns(self, ns_name, ns_to_create):
        ns_type = ns_to_create['infrastructure']['type']
        if "AzureVMScaleSetInfrastructure" in ns_type:
            self.create_azure_vm_ss_infra(ns_name, ns_to_create)
        elif "DefaultInfrastructureManager" in ns_type:
            self.create_default_infra(ns_name, ns_to_create)
        else:
            logging.info(f"creating {ns_type} not implemented yet")

    @staticmethod
    def _sanitize(infra):
        for name, value in infra.items():
            if value is None:
                logging.info(f"[Sanitizing parameters] None value detected for {name}")
                infra[name] = ""
        return infra

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

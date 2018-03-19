import logging
from watchdog.events import FileSystemEventHandler
from os.path import basename
from importlib import import_module
import subprocess
import yaml
from urllib import request, parse
from urllib.error import HTTPError
from pathlib import Path


class NSWatcher(FileSystemEventHandler):

    def __init__(self, config_path=f"{Path.home()}/.ns-watcher.conf", debug=False, logger=None):
        with open(config_path, 'r') as config_file:
            watcher_conf = yaml.load(config_file)
            self.logger = logger or logging.getLogger(__name__)
            self.pa_home = watcher_conf['pa_home']
            self.scheduler_url = watcher_conf['scheduler_url']
            self.credential_file_path = watcher_conf['credential_file_path']
            self.watch_folder = watcher_conf['watch_folder']
            self.rest_user = watcher_conf['rest_user']
            self.rest_password = watcher_conf['rest_password']
            self.url_login = f"{watcher_conf['scheduler_url']}/rest/scheduler/login"
            self.url_rm_ns = f"{watcher_conf['scheduler_url']}/rest/rm/nodesource/remove"
            self.verbose = debug

    def build_cli_cmd(self):
        insecure_mode = ""
        if "https" in self.scheduler_url:
            insecure_mode = "-k"
        return f"{self.pa_home}/bin/proactive-client {insecure_mode} -u {self.scheduler_url}/rest" \
               f" -c {self.credential_file_path}"

    def build_infra_cmd(self, infra):
        cmd = ""
        infra_type = infra['type']
        try:
            module_path = f"nswatcher.infrastructures.{infra_type}"
            self.logger.debug(f"module to load: {module_path}")
            infra_module = import_module(module_path)
            cmd = infra_module.build_infra_cmd(infra)
        except ImportError:
            self.logger.error(f"failed to import module {infra_type}")
        return cmd

    def build_policy_cmd(self, policy):
        cmd = ""
        policy_type = policy['type']
        try:
            module_path = f"nswatcher.policies.{policy_type}"
            self.logger.debug(f"module to load: {module_path}")
            policy_module = import_module(module_path)
            cmd = policy_module.build_policy_cmd(policy)
        except ImportError:
            self.logger.error(f"failed to import module {policy_type}")
        return cmd

    def on_created(self, event):
        if self.is_valid_file(event):
            ns_name = self.get_ns_name(event)
            ns_to_create = yaml.load(open(event.src_path, 'r'))
            infra = self._sanitize(ns_to_create['infrastructure'])
            policy = self._sanitize(ns_to_create['policy'])
            self.logger.debug(f"Analyzing file {event.src_path}")
            cmd_starter = self.build_cli_cmd()
            infra_cmd = self.build_infra_cmd(infra)
            policy_cmd = self.build_policy_cmd(policy)
            cmd = f"{cmd_starter} -createns {ns_name}" \
                  f" --infrastructure {infra_cmd}" \
                  f" -policy {policy_cmd}"
            self.logger.debug(cmd)
            stdout = subprocess.DEVNULL
            if self.verbose:
                stdout = subprocess.PIPE
            try:
                subprocess.check_call(cmd, stdout=stdout, shell=True)
                self.logger.info(f"Created nodesource {ns_name} ({infra['type']}, {infra['type']})")
            except subprocess.CalledProcessError as err:
                self.logger.error("Command failed with error %s" % err)

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
        self.logger.info(f"Removed {ns_name}")

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

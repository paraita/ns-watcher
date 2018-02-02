# ns-watcher

This project allows to add nodesources to a ProActive Resource Manager by adding well-formed yml files into a specified folder.
It's purpose is to ease frequent adds and removals of node sources and is **NOT** ready for a production use.

## Requirements

For this, the project assumes the following:

* we have credentials for the RM
* we have a login/password for the REST API
* the proactive-client script is reachable
* the scheduler REST API is reachable

There's a requirements.txt file for the dependencies.

## Configuration

This project needs a `ns-watcher.conf` in the project directory. See the `ns-watcher.template.conf` file.
At the moment, only the StaticPolicy is supported.

Supported infrastructures:
- [ ] AzureInfrastructure
- [ ] LocalInfrastructure
- [ ] AWSEC2Infrastructure
- [ ] CLIInfrastructure
- [ ] AutoUpdateInfrastructure
- [ ] OpenstackInfrastructure
- [x] DefaultInfrastructureManager
- [ ] SSHInfrastructure
- [ ] VMWareInfrastructure
- [x] AzureVMScaleSetInfrastructure
- [ ] GenericBatchJobInfrastructure
- [ ] NativeSchedulerInfrastructure
- [ ] SSHInfrastructureV2
- [ ] LSFInfrastructure
- [ ] PBSInfrastructure


## Usage

Just run the main.py script from within this project.
An NS declaration file should have the following format:

```yaml
infrastructure:
  type: "DefaultInfrastructureManager"
policy:
  type: "StaticPolicy"
  userAccessType: "ALL"
  providerAccessType: "ME"
```

Adding such a file to the watch-folder will create the node source in the RM.
Removing that file will also remove the node souce from the RM.

# ns-watcher

This project allows to add nodesources to a ProActive Resource Manager by adding well-formed yml files into a specified folder.
For this, the project assumes the following:

* we have credentials for the RM
* we have a login/password for the REST API
* the proactive-client script is reachable
* the scheduler REST API is reachable

This project needs a `ns-watcher.conf` in the project directory. See the `ns-watcher.template.conf` file.

an NS declaration file should have the following format:

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

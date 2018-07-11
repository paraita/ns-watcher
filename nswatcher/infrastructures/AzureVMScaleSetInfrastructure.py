def build_infra_cmd(infra):
    cmd = f"org.ow2.proactive.resourcemanager.nodesource.infrastructure.AzureVMScaleSetInfrastructure" \
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
          f" '{infra['internalCustomStartupScriptUrl']}'"
    return cmd

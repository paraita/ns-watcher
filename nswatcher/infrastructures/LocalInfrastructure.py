def build_infra_cmd(infra):
    cmd = f"org.ow2.proactive.resourcemanager.nodesource.infrastructure.LocalInfrastructure" \
          f" {infra['credentials']}" \
          f" '{infra['maxNodes']}'" \
          f" '{infra['nodeTimeout']}'" \
          f" '{infra['paProperties']}'"
    return cmd

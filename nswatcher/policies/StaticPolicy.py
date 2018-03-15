def build_policy_cmd(policy):
    return f"org.ow2.proactive.resourcemanager.nodesource.policy.StaticPolicy" \
           f" {policy['userAccessType']} {policy['providerAccessType']}"

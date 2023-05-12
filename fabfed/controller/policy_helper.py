from typing import Dict, List

from fabfed.util.constants import Constants
from fabfed.exceptions import StitchPortNotFound
from collections import namedtuple

MEMBER_OF = 'member-of'
STITCH_PORT = 'stitch-port'
GROUP = 'group'
PRODUCER_FOR = 'producer-for'
CONSUMER_FOR = 'consumer-for'


class ProviderPolicy:
    def __init__(self, *, type, stitch_ports, groups):
        self.type = type
        self.stitch_ports = stitch_ports

        for group in groups:
            if CONSUMER_FOR not in group:
                group[CONSUMER_FOR] = []
            if PRODUCER_FOR not in group:
                group[PRODUCER_FOR] = []

        from collections import OrderedDict

        self.groups = [OrderedDict(sorted(g.items())) for g in groups]

    def __str__(self) -> str:
        lst = ["stitch_ports=" + str(self.stitch_ports), "groups=" + str(self.groups)]
        return str(lst)

    def __repr__(self) -> str:
        return self.__str__()


StitchInfo = namedtuple("StitchInfo", "stitch_port producer consumer")

def parse_policy(policy) -> Dict[str, ProviderPolicy]:
    for k, v in policy.items():
        stitch_ports = v[STITCH_PORT] if STITCH_PORT in v else []

        for stitch_port in stitch_ports:
            if 'preference' not in stitch_port:
                stitch_port['preference'] = 0

        groups = v[GROUP] if GROUP in v else []

        for g in groups:
            g['provider'] = k

        policy[k] = ProviderPolicy(type=k, stitch_ports=stitch_ports, groups=groups)

    return policy


def load_policy(*, policy_file=None, content=None) -> Dict[str, ProviderPolicy]:
    import os
    import yaml

    if content:
        policy = yaml.safe_load(content)
        return parse_policy(policy)

    if not policy_file:
        policy_file = os.path.join(os.path.dirname(__file__), 'policy.yaml')

    with open(policy_file, 'r') as fp:
        policy = yaml.load(fp, Loader=yaml.FullLoader)
    return parse_policy(policy)


def find_stitch_port_for_group(policy: Dict[str, ProviderPolicy], group: str, providers: List[str]) -> List[StitchInfo]:
    provider1 = providers[0]
    provider2 = providers[1]
    stitch_infos = []

    for g in policy[provider1].groups:
        temp = provider2 + "/" + group

        if temp in g[CONSUMER_FOR]:  # provider1's group is a consumer, find provider2's groups that are producers
            for producer_group in policy[provider2].groups:
                if provider1 + "/" + group in producer_group[PRODUCER_FOR]:
                    for stitch_port in policy[provider2].stitch_ports:
                        if group in stitch_port[MEMBER_OF]:
                            stitch_info = StitchInfo(stitch_port=stitch_port,
                                                     producer=producer_group['provider'],
                                                     consumer=g['provider'])
                            stitch_infos.append(stitch_info)

        if temp in g[PRODUCER_FOR]:   # provider2's group is a producer find provider2's groups that are consumers
            for consumer_group in policy[provider2].groups:
                if provider1 + "/" + group in consumer_group[CONSUMER_FOR]:
                    for stitch_port in policy[provider1].stitch_ports:
                        if group in stitch_port[MEMBER_OF]:
                            stitch_info = StitchInfo(stitch_port=stitch_port,
                                                     producer=g['provider'],
                                                     consumer=consumer_group['provider'])
                            stitch_infos.append(stitch_info)

    return stitch_infos


def find_stitch_port(*, policy: Dict[str, ProviderPolicy], providers: List[str], site=None) -> StitchInfo or None:
    from fabfed.util.utils import get_logger

    logger = get_logger()
    stitch_infos = []

    for g in policy[providers[0]].groups:
        temp_stitch_infos = find_stitch_port_for_group(policy, g['name'], providers)
        stitch_infos.extend(temp_stitch_infos)

    stitch_infos.sort(key=lambda si: si.stitch_port['preference'], reverse=True)

    if site:
        for stitch_info in stitch_infos:
            if site == stitch_info.stitch_port['site']:
                return stitch_info

        logger.warning(f"did not find a stitch port for site={site} and providers={providers}")

    stitch_info = stitch_infos[0] if stitch_infos else None

    if not stitch_info:
        raise StitchPortNotFound(f"did not find a stitch port for providers={providers}")

    logger.info(f"returning stitch port for providers={providers}:{stitch_info}")
    return stitch_info


def find_site(network, resources):
    site = network.attributes.get(Constants.RES_SITE)

    if not site:
        for dep in network.dependencies:
            if dep.resource.is_node:
                site = dep.resource.attributes.get(Constants.RES_SITE)

                if site:
                    break

    if not site:
        for node in [resource for resource in resources if resource.is_node]:
            if [dep for dep in node.dependencies if dep.resource == network]:
                site = node.attributes.get(Constants.RES_SITE)

                if site:
                    break
    return site


def handle_stitch_info(config, policy, resources):
    has_stitch_with = False

    for network in [resource for resource in resources if resource.is_network]:
        if Constants.NETWORK_STITCH_WITH in network.attributes:
            has_stitch_with = True
            dependency_info = network.attributes[Constants.NETWORK_STITCH_WITH]
            dependencies = network.dependencies
            network_dependency = None

            for ed in dependencies:
                if ed.key == Constants.NETWORK_STITCH_WITH and ed.resource.label == dependency_info.resource.label:
                    network_dependency = ed
                    break

            assert network_dependency is not None, "should never happen"
            assert network_dependency.is_external, "only network stitching across providers is supported"
            other_network = network_dependency.resource
            assert other_network.is_network, "only network stitching is supported"

            site = find_site(network, resources)
            stitch_info = find_stitch_port(policy=policy,
                                           providers=[network.provider.type, other_network.provider.type],
                                           site=site)
            network.attributes.pop(Constants.NETWORK_STITCH_WITH)

            if network.provider.type != stitch_info.consumer:
                from fabfed.util.config_models import DependencyInfo

                other_network.attributes[Constants.RES_STITCH_INTERFACE] = DependencyInfo(resource=network,
                                                                                          attribute='')

            network.attributes[Constants.RES_STITCH_INFO] = stitch_info
            other_network.attributes[Constants.RES_STITCH_INFO] = stitch_info

    if has_stitch_with:
        for resource in resources:
            resource.dependencies.clear()

        from fabfed.util.resource_dependency_helper import ResourceDependencyEvaluator, order_resources

        dependency_evaluator = ResourceDependencyEvaluator(resources, config.get_provider_config())
        dependency_map = dependency_evaluator.evaluate()
        resources = order_resources(dependency_map)

    return resources
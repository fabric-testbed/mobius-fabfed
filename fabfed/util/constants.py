class Constants:
    IPv4 = "ipv4"
    IPv6 = "ipv6"
    FAB_EXTENSION = '.fab'
    CREDENTIAL_FILE = 'credential_file'
    PROFILE = 'profile'

    LABEL = 'label'
    RESOURCES = "resources"
    RESOURCE = "resource"
    RES_TYPE = "type"
    RES_SITE = "site"
    RES_COUNT = "count"
    RES_IMAGE = "image"
    RES_NIC_MODEL = "nic_model"
    RES_NETWORK = "network"
    RES_NAME_PREFIX = "name_prefix"

    RES_TYPE_NODE = "node"
    RES_TYPE_NETWORK = "network"
    RES_TYPE_SERVICE = "service"
    RES_SUPPORTED_TYPES = [RES_TYPE_NODE, RES_TYPE_NETWORK, RES_TYPE_SERVICE]
    CONFIG_SUPPORTED_TYPES = ["network", "layer3", "peering"]

    RES_TYPE_VM = "VM"
    RES_TYPE_BM = "Baremetal"
    RES_FLAVOR = "flavor"
    RES_FLAVOR_CORES = "cores"
    RES_FLAVOR_RAM = "ram"
    RES_FLAVOR_DISK = "disk"
    RES_FLAVOR_NAME = "name"
    RES_NET_POOL_START = "pool_start"
    RES_NET_POOL_END = "pool_end"
    RES_NET_GATEWAY = "gateway"
    RES_NET_STITCH_PROVS = "stitch_providers"
    RES_NET_CALLBACK = "callback"
    RES_SUBNET = 'subnet'
    RES_LAYER3 = 'layer3'
    RES_LAYER3_DHCP_START = 'dhcp_start'
    RES_LAYER3_DHCP_END = 'dhcp_end'

    LOGGING = "logging"
    PROPERTY_CONF_LOG_FILE = 'log-file'
    PROPERTY_CONF_LOG_LEVEL = 'log-level'
    PROPERTY_CONF_LOG_RETAIN = 'log-retain'
    PROPERTY_CONF_LOG_SIZE = 'log-size'
    PROPERTY_CONF_LOGGER = "logger"

    EXTERNAL_DEPENDENCIES = "external_dependencies"
    RESOLVED_EXTERNAL_DEPENDENCIES = "resolved_external_dependencies"

    INTERNAL_DEPENDENCIES = "internal_dependencies"
    RESOLVED_INTERNAL_DEPENDENCIES = "resolved_internal_dependencies"

    PROVIDER_CLASSES = {
        "fabric": "fabfed.provider.fabric.fabric_provider.FabricProvider",
        "chi": "fabfed.provider.chi.chi_provider.ChiProvider",
        "sense": "fabfed.provider.sense.sense_provider.SenseProvider",
        "janus": "fabfed.provider.janus.janus_provider.JanusProvider",
        "dummy": "fabfed.provider.dummy.dummy_provider.DummyProvider"
    }

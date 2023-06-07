from fabfed.model import Node
from fabfed.util.utils import get_logger
from . import sense_utils
from .sense_exceptions import SenseException
from . import sense_constants as SenseConstants

logger = get_logger()


class SenseNode(Node):
    def __init__(self, *, label, name: str, network: str, spec: dict):
        super().__init__(label=label, name=name, image="", site="", flavor="")
        assert network
        self.network = network
        self._spec = spec
        self.spec_name = spec['name']
        self.node_details: dict = {}
        self.dataplane_ipv4 = None
        self.dataplane_ipv6 = None

    def create(self):
        si_uuid = sense_utils.find_instance_by_alias(alias=self.network)
        assert si_uuid
        status = sense_utils.instance_get_status(si_uuid=si_uuid)
        assert status == 'CREATE - READY'
        flavor = "unknown"
        
        if "gcp-node" in self.name:
            template_file = 'gcp-template.json'
            flavor = "gcp-node"
        elif "aws-node" in self.name:
            template_file = 'aws-template.json'
            flavor = "aws-node"
        else:
            raise SenseException(f"Was not able to get node template file {self.name}")
        
        details = sense_utils.manifest_create(alias=self.network, template_file=template_file)

        for node_details in details.get("Nodes", []):
            if node_details[SenseConstants.SENSE_AWS_NODE_NAME] == self.spec_name:
                self.node_details = node_details
                break

        # TODO: resolve the difference between spec_name and nodename 
        self.node_details = node_details if not self.node_details and flavor == "gcp-node" else {}
        
        if not self.node_details:
            raise SenseException(f"Was not able to get node details {self.name}:spec_name={self.spec_name}")

        if flavor == "aws-node":
            self.dataplane_ipv4 = self.node_details[SenseConstants.SENSE_AWS_PRIVATE_IP]
            self.mgmt_ip = self.node_details[SenseConstants.SENSE_AWS_PUBLIC_IP]
            self.image = self.node_details[SenseConstants.SENSE_AWS_IMAGE]
            self.image = self.image[self.image.find("+") + 1:]
            self.keyfile = self.node_details[SenseConstants.SENSE_AWS_KEYPAIR]
        elif flavor == "gcp-node":
            self.dataplane_ipv4 = self.node_details[SenseConstants.SENSE_GCP_PRIVATE_IP]
            self.mgmt_ip = self.node_details[SenseConstants.SENSE_GCP_PUBLIC_IP]
            # self.image = self.node_details[SenseConstants.SENSE_GCP_IMAGE]
            # self.image = self.image[self.image.find("+") + 1:]
            # self.keyfile = self.node_details[SenseConstants.SENSE_GCP_KEYPAIR]
        else:
            raise SenseException(f"Unable to init node details {self.name}:{flavor}")

    def delete(self):
        si_uuid = sense_utils.find_instance_by_alias(alias=self.network)
        assert si_uuid is None

    def get_reservation_state(self) -> str:
        pass

    def get_reservation_id(self) -> str:
        pass

    def add_route(self, subnet, gateway):
        pass

    def get_dataplane_address(self, network=None, interface=None, af=None):
        pass

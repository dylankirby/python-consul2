class DiscoveryChain(object):
    def __init__(self, agent):
        warnings.warn(
            "1.6.0+: The discovery "
            "chain API is available "
            "in Consul versions 1.6.0 "
            "and newer.",
            DeprecationWarning,
        )
        self.agent = agent

    """
        This is a low-level API primarily targeted at developers
        building external Connect proxy integrations. Future
        high-level proxy integration APIs may obviate the need
        for this API over time.
        # todo DiscoveryChain
        """

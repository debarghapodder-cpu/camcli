class CampaignBaseModule:
    def __init__(self):
        pass

    def get_cli_commands(self, subparsers):
        """Each module will override this to add its own CLI sub-commands."""
        pass

    def get_agent_tools(self):
        """Each module will override this to return a list of LangChain tools."""
        return []

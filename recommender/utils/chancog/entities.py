import datetime

# TODO: When we port this functionality over to a relational database we need to
#       add a constraint to ensure snippet_id is sequential integers (or we just
#       establish order with the timestamp).
class Snippet:
    def __init__(self, conversation_id, snippet_id, text, snippet_type):
        self.conversation_id = conversation_id
        self.snippet_id = snippet_id
        self.text = text
        self.snippet_type = snippet_type
        self.timestamp = datetime.datetime.now()

class SnippetTable:
    def __init__(self):
        self.entries = []

    def add_entry(self, conversation_id, text, snippet_type):
        snippet_id = self.generate_snippet_id(conversation_id)
        entry = Snippet(conversation_id, snippet_id, text, snippet_type)
        self.entries.append(entry)
        return entry

    def generate_snippet_id(self, conversation_id):
        """
        Generate a unique snippet ID based on the conversation ID and the current number of entries in that conversation.
        """
        same_conversation_entries = [e for e in self.entries if e.conversation_id == conversation_id]
        return f"{conversation_id}_Snippet_{len(same_conversation_entries) + 1}"

    def get_conversation_history(self, conversation_id):
        return [e for e in self.entries if e.conversation_id == conversation_id]

# The intent of the StringMapperEntry and StringMapperTable is to provide a framework to store
# LLM calls using snippets rather than the full texts of the calls. This approach is (a) notional
# and (b) not yet used in any of the main dev code.
class StringMapperEntry:
    def __init__(self, mapper_id, conversation_id, input_snippets, output_snippets, mapper_name, additional_metadata=None):
        self.mapper_id = mapper_id
        self.conversation_id = conversation_id
        self.input_snippets = input_snippets  # List of snippet IDs
        self.output_snippets = output_snippets  # List of snippet IDs
        self.mapper_name = mapper_name
        self.timestamp = datetime.datetime.now()
        self.additional_metadata = additional_metadata

class StringMapperTable:
    def __init__(self):
        self.entries = []

    def generate_mapper_id(self, conversation_id):
        """
        Generate a sequential integer for mapper_id based on the conversation ID.
        """
        same_conversation_entries = [e for e in self.entries if e.conversation_id == conversation_id]
        return len(same_conversation_entries) + 1

    def add_mapper_entry(self, conversation_id, input_snippets, output_snippets, mapper_name, additional_metadata=None):
        mapper_id = self.generate_mapper_id(conversation_id)
        entry = StringMapperEntry(mapper_id, conversation_id, input_snippets, output_snippets, mapper_name, additional_metadata)
        self.entries.append(entry)
        return entry

    def get_mapper_entries_by_conversation(self, conversation_id):
        """
        Retrieve all mapper entries associated with a specific conversation ID.
        """
        return [e for e in self.entries if e.conversation_id == conversation_id]

    def get_mapper_entries_by_name(self, mapper_name):
        """
        Retrieve all mapper entries of a specific mapper name.
        """
        return [e for e in self.entries if e.mapper_name == mapper_name]
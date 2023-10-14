# TODO: consider supporting automatically generated, random IDs
class CallbackWrapper:
    def __init__(self, id, process_input_callback=None, db_callback=None):
        """
        Initialize the CallbackWrapper with a unique identifier, an optional processing callback, and a database callback.
        
        Args:
            id (str): A unique identifier for the conversation or interaction.
            process_input_callback (callable, optional): A callback function for processing the input.
            db_callback (callable, optional): A callback function for storing data in a database.
                                              Defaults to None.
        """
        self.id = id
        self.db_callback = db_callback
        self.process_input_callback = process_input_callback
        self.local_storage = []

    def process_input(self, input_data):
        """
        Process the input data using the callback. If there's no process_input_callback, this is an endpoint.

        Args:
            input_data (dict): The input data to be processed.

        Returns:
            dict or None: Processed data if process_input_callback is not None, otherwise None.
        """
        # Always store the input data
        self.store_data(input_data)

        # If there's a process_input_callback, use it
        if self.process_input_callback:
            processed_data = self.process_input_callback(input_data)
            return processed_data
        else:
            return None

    def store_data(self, data):
        """
        Store the data either using the db_callback or in local storage, tagged with the current ID.
        
        Args:
            data (dict): The data to be stored.
        """

        if self.db_callback:
            self.db_callback(self.id, data)
        else:
            self.local_storage.append(data)

    def get_history(self):
        """
        Retrieve all records associated with the current ID.

        Returns:
            list[dict]: List of records associated with the ID.
        """
        if self.db_callback:
            # If self.db_callback is called with no data, it must return the history.
            return self.db_callback(self.id)
        else:
            return self.local_storage


class OutputManager:
    """
    Manage outputs received from the InputManager.

    The OutputManager processes JSONs that contain LLM responses. The conversation 
    flow starts with the OutputManager.

    Attributes:
        process_input_callback (callable): A required callback function for processing the input.
        db_callback (callable, optional): A callback function for storing data in a database. 
                                          Defaults to None.
        local_storage (list): A local storage for data if no database callback is provided.
    """

    def __init__(self, process_input_callback, db_callback=None):
        """
        Initialize the OutputManager with the required processing callback and an optional database callback.

        Args:
            process_input_callback (callable): A callback function for processing the input.
            db_callback (callable, optional): A callback function for storing data in a database.
                                              Defaults to None.
        """
        self.db_callback = db_callback
        self.process_input_callback = process_input_callback
        self.local_storage = []

    def initialize_conversation(self, framing, salutation):
        """
        Initialize a conversation with framing and salutation.

        Args:
            framing (str): A framing string (for the LLM; not seen by the user).
            salutation (str): A salutation string (this is seen by the user).
        
        Returns:
            dict: The initial view information for the ViewAssembler.
        """
        initial_data = {
            "type": "initial",
            "framing": framing,
            "salutation": salutation
        }
        self.store_input(initial_data)
        
        view_info = {
            "text": salutation
        }
        return view_info

    def process_input(self, json_input):
        """
        Process the input data, which involves storing it in the database and
        calling self.process_input_callback to build the view information.

        Args:
            json_input (dict): The input JSON

        Returns:
            dict: Updated view information for the ViewAssembler.
        """
        input_data = {
            "type": "input",
            "data": json_input
        }
        self.store_input(input_data)

        # Use the process_input_callback to get the view_info
        view_info = self.process_input_callback(json_input)
        return view_info

    def store_input(self, data):
        """
        Store the structured input data

        This method uses the provided db_callback to store the input data if
        available. A local store is also always maintained.

        Args:
            data (dict): The data to store
        """
        if self.db_callback:
            self.db_callback(data)
        self.local_storage.append(data)
    
    @classmethod
    def init_with_view_info(cls, framing, salutation,
                            db_callback=None, process_input_callback=None):
        """
        Initialize the OutputManager and retrieve the initial view information in a single call.

        Args:
            framing (str): A framing string (for the LLM; not seen by the user).
            salutation (str): A salutation string (this is seen by the user).
            db_callback (callable, optional): A callback function for storing data in a database.
                                              Defaults to None.
            process_input_callback (callable): A callback function for processing the input.

        Returns:
            tuple: An instance of OutputManager and the initial view information.
        """
        manager = cls(db_callback=db_callback, process_input_callback=process_input_callback)
        view_info = manager.initialize_conversation(framing, salutation)
        return manager, view_info

class ViewManager:
    """
    Manage views for displaying conversation in a terminal.

    The ViewManager receives inputs from the OutputManager and uses a callback 
    to determine the specifics of how to display the information.

    Attributes:
        display_callback (callable): A callback function that defines how data is displayed in the terminal.
        db_callback (callable, optional): A callback function for storing view data in a database. Defaults to None.
        local_storage (list): A local storage for view data if no database callback is provided.
    """

    def __init__(self, display_callback, db_callback=None):
        self.display_callback = display_callback
        self.db_callback = db_callback
        self.local_storage = []

    def process_input(self, view_info):
        """
        Process the view_info which involves storing it and then displaying it using the callback.

        Args:
            view_info (dict): Information for view. Must contain "text". Can optionally contain "data".
        """
        # Store the view information
        self.store_input(view_info)
        
        # Use the display callback to actually render the view
        self.display_callback(view_info)

    def store_input(self, view_info):
        """
        Store the view information either in a database if available. A local copy is also always maintained.

        Args:
            view_info (dict): The view information to store.
        """
        if self.db_callback:
            self.db_callback(view_info)
        else:
            self.local_storage.append(view_info)

class InputManager:
    """
    Manage inputs for initiating or continuing a conversation.

    The InputManager processes user inputs (e.g., from terminal, web, SMS) and then 
    passes the structured data to the OutputManager for further processing.

    Attributes:
        process_user_input_callback (callable): A callback function that defines how raw user input is processed.
        db_callback (callable, optional): A callback function for storing user input in a database. Defaults to None.
        local_storage (list): A local storage for user input if no database callback is provided.
    """

    def __init__(self, process_user_input_callback, db_callback=None):
        self.process_user_input_callback = process_user_input_callback
        self.db_callback = db_callback
        self.local_storage = []

    def process_input(self, user_input):
        """
        Process the raw user input, which is usually a new chat message (but
        could be, say, a movie rating).

        Args:
            user_input (dict): The user input

        Returns:
            dict: Structured data after processing; passed to the OutputManager
        """
        # Store the raw input
        self.store_input(user_input)
        
        # Use the process_user_input_callback to get the structured data
        structured_data = self.process_user_input_callback(user_input)
        return structured_data

    def store_input(self, user_input):
        """
        Store the user input either in a database or locally. A local store is also always maintained.

        Args:
            user_input (str): The raw input to store.
        """
        if self.db_callback:
            self.db_callback({"type": "user_input", "data": user_input})
        self.local_storage.append({"type": "user_input", "data": user_input})

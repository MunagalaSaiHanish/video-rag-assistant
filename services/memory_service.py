# conversation memory manager


class MemoryManager:

    def __init__(self):

        self.messages = []

    # add message

    def add_message(
        self,
        role,
        content
    ):

        self.messages.append(
            {
                "role": role,
                "content": content
            }
        )

    # get conversation

    # get recent conversation

def get_messages(
    self,
    window_size=10
):

    return self.messages[-window_size:]

    # clear conversation

def clear(self):

    self.messages = []
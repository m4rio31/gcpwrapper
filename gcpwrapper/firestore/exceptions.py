class IllegalArgumentException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidFilterException(IllegalArgumentException):
    "Rised when no document is related to the filter"
    def __init__(self, filters: dict):
        super().__init__(f'No documents found with filter {filters}')
        
        
class InvalidKeyException(Exception):
    "Raised when an invalid key is passed"
    def __init__(self, key: str):
        super().__init__(f'Key {key} is not in the document')
        
        
class NoDocFoundException(Exception):
    "Raised when no document is related to the document ID"
    def __init__(self, collection: str, doc_id: str):
        super().__init__(f'Doc {doc_id} not found in collection {collection}')
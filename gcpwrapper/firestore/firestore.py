# Built-in
import logging
from typing import Any, List, Optional

# Requirements
from google.cloud import exceptions
from google.cloud import firestore

# Local
from gcpwrapper.firestore import exceptions


class Wrapper:
    def __init__(self,
                 attach_logger: Optional[logging.Logger]=None):
        self._client = firestore.Client()
        self._logger = attach_logger
        
    def delete(self, collection: str, doc_id: str):
        self._client.collection(collection).document(doc_id).delete()
    
    def exists(self, collection: str, doc_id: str) -> bool:
        doc = self._client.collection(collection).document(doc_id).get()
        return doc.exists
    
    def get_doc(self, collection: str, doc_id: str) -> dict:
        return self._get_doc(collection, doc_id) 
    
    def get_elem_in_doc(self,
                        collection: str,
                        doc_id: str,
                        get: str) -> Any:
        doc = self._get_doc(collection, doc_id)
        if get not in doc.keys():
            if self._logger:
                self._logger.error(f'Invalid key in document: {get}')
            raise exceptions.InvalidKeyException(get)
        return doc[get]
    
    def query(self,
              collection: str,
              must_exists: bool=False,
              **kwargs) -> List[str]:
        docs = self._client.collection(collection)
        for key, value in kwargs.items():
            docs = docs.where(key, '==', value)
        if next(docs.stream(), -1) == -1:
            if self._logger:
                self._logger.warning(f'No documents found for filter {kwargs}')
            if must_exists:
                raise exceptions.InvalidFilterException(kwargs)
            docs_list = []
        else:
            docs_list = list(docs.stream())
        return docs_list
    
    def upsert(self,
               collection_name: str,
               doc_id: str,
               message: dict) -> dict:
        doc = self.__client.collection(collection_name).document(doc_id)
        try:
            response = doc.create(message)
            if self._logger:
                self._logger.debug(f'Doc {doc_id} created')
        except exceptions.Conflict:
            response = doc.set(message, merge=True)
            if self._logger:
                self._logger.debug(f'Doc {doc_id} updated')
        return response
    
    def _get_doc(self, collection: str, doc_id: str) -> dict:
        doc = self._client.collection(collection).document(doc_id).get()
        if not doc.exists:
            if self._logger:
                self._logger.error(f'Document {doc_id} not found')
            raise exceptions.NoDocFoundException(collection, doc_id)
        return doc.to_dict()
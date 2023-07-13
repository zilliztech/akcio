from abc import ABC, abstractmethod
from typing import List

from towhee.runtime.runtime_pipeline import RuntimePipeline


class BaseMemory(ABC):
    '''Base module to manage memory.'''

    @abstractmethod
    def add_history(self, project: str, session_id: str, messages: List[dict]):
        '''Insert messages to the project table with a field of session_id.'''
        pass

    @abstractmethod
    def get_history(self, project: str, session_id: str) -> List[tuple]:
        '''Get chat history from the project table for each session.'''
        pass

    @abstractmethod
    def drop(self, project):
        '''Clear all memory saved in the table "project"'''
        pass

    @abstractmethod
    def check(self, project) -> bool:
        '''Check if the project table exists in database.'''
        pass


class BasePipelines(ABC):
    '''Base module to create Towhee pipelines'''
            
    @property
    def search_pipeline(self) -> RuntimePipeline:
        '''Define search pipeline'''
        pass

    @property
    def insert_pipeline(self) -> RuntimePipeline:
        '''Define insert pipeline'''
        pass
    
    @abstractmethod
    def create(self, project: str):
        '''Create project table(s) in database(s)'''
        pass

    @abstractmethod
    def check(self, project) -> bool:
        '''Check if project table(s) exist.'''
        pass
    
    @abstractmethod
    def drop(self, project):
        '''Drop project table(s).'''
        pass

    @abstractmethod 
    def count_entities(self, project) -> int:
        '''Count doc chunks in project.'''
        pass
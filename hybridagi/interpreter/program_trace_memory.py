"""The program trace memory. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

from collections import deque
from typing import Iterable
from pydantic.v1 import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

class ProgramTraceMemory(BaseModel):
    objective: str = ""
    program_trace: Iterable = deque()
    chunk_size: int = 100
    memory_template: str = \
"""The Objective is from the perspective of the User
Objective: {objective}
{program_trace}"""

    def clear(self):
        """Method to clear the program trace"""
        self.program_trace = deque()

    def get_trace(self, max_tokens: int) -> str:
        """Load the memory variables"""
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size = self.chunk_size,
            chunk_overlap = 0
        )
        program_trace = "\n".join(self.program_trace)
        texts = text_splitter.split_text(program_trace)
        result = ""
        if len(texts) == 0:
            memory = self.memory_template.format(
                objective = self.objective,
                program_trace = ""
            )
            return memory
        elif len(texts) == 1:
            memory = self.memory_template.format(
                objective = self.objective,
                program_trace = texts[0]
            )
            return memory
        else:
            result = self.memory_template.format(
                objective = self.objective,
                program_trace = ""
            )
            for i in range(0, len(texts)):
                program_trace = "\n".join(texts[len(texts)-i:])

                memory = self.memory_template.format(
                    objective = self.objective,
                    program_trace = program_trace
                )

                encoding = tiktoken.get_encoding("cl100k_base")
                num_tokens = len(encoding.encode(memory))
                if num_tokens < max_tokens:
                    result = memory
                else:
                    break
            return result

    def update_trace(self, prompt):
        """Method to update the program trace"""
        self.program_trace.append(prompt)

    def update_objective(self, objective):
        """Method to update the objective"""
        self.objective = objective

    def revert(self, n: int):
        """Method to revert N steps of the trace"""
        for i in range(n):
            self.program_trace.pop()

#!/usr/bin/env python3
""" Circuit Maker 2 save generation and manipulation package

This module contains utilities to generate and manipulate save strings
for the Roblox game Circuit Maker 2 by ismellbeef1.
"""

__author__ = "SKM GEEK"
__contact__ = "qestudios17@gmail.com"
__copyright__ = "Copyright 2024, SKM GEEK"
__date__ = "2024/07/05"
__deprecated__ = False
__email__ = "qestudios17@gmail.com"
__license__ = "MIT"
__maintainer__ = "SKM GEEK"
__status__ = "Production"
__version__ = "0.3.10"

from uuid import uuid4, UUID
import re

nan = float("nan")

class Block:
    def __init__(self, blockId: int, pos: tuple[float,float,float], state: bool = False, properties: list[float] = []):
        assert 0 <= blockId <= 19, "blockId must be between 0 and 19"
        self.blockId = blockId
        self.pos = pos
        self.state = state
        self.properties = properties
        self.uuid = uuid4()

    def move(self,x = nan,y = nan,z = nan):
        """Move the block"""
        self.pos = (self.pos[0] if x == nan else x,self.pos[1] if y == nan else y,self.pos[2] if z == nan else z)

    def __str__(self) -> str:
        props = [str(p) for p in self.properties]
        pos = [str(int(x)) if x.is_integer() else str(x) for x in self.pos]
        return f"{self.blockId},{self.state},{','.join(pos)}{',' + '+'.join(props) if len(self.properties) > 0 else ''}"


class Save:
    """A class to represent a save, which can be modified."""

    def __init__(self):
        self.blocks: dict[UUID,Block] = {}
        self.connections: dict[tuple[UUID,UUID],tuple[Block,Block]] = {}

    def addBlock(self, blockId: int, pos: tuple[float, float, float],state: bool = False,properties: list[float] = [], snapToGrid: bool = True,) -> Block:
        """Add a block to the save."""
        newBlock = Block(blockId, (int((pos[0])), int((pos[1])), int(pos[2])) if snapToGrid else pos, state, properties)
        self.blocks[newBlock.uuid] = newBlock
        return newBlock

    def addConnection(self, source: Block, target: Block) -> tuple[Block,Block]:
        """Add a connection to the save."""
        new_connection = (source,target)
        self.connections[(source.uuid,target.uuid)] = new_connection
        return new_connection

    def exportSave(self) -> str:
        """Export the save to a Circuit Maker 2 save string."""
        indexes: dict[UUID,int] = {}
        count = 1
        blockstrings: list[str] = []
        connectionstrings: list[str] = []

        for uuid,block in self.blocks.items():
            indexes[uuid] = count
            blockstrings.append(str(block))
            count += 1

        for connect in self.connections:
            connectionstrings.append(f"{indexes[connect[0]]},{indexes[connect[1]]}")
        
        return f"{';'.join(blockstrings)}?{';'.join(connectionstrings)}??"

    def deleteBlock(self, blockRef: Block):
        """Delete a block from the save."""
        assert blockRef.uuid in self.blocks, "block does not exist in save"
        for c in self.connections.keys():
            if c[0] == blockRef.uuid:
                del self.connections[(blockRef.uuid,c[1])]
            elif c[1] == blockRef.uuid:
                del self.connections[(c[0],blockRef.uuid)]
        del self.blocks[blockRef.uuid]

    def deleteConnection(self, source: Block,target: Block):
        """Delete a connection from the save."""
        del self.connections[(source.uuid,target.uuid)]

def validateSave(string: str) -> bool:
    """Check whether a string is a valid savestring or not."""
    # fmt: off
    regex = (
        r"(?<![\d\w,;?+])" # Blocks
        r"(?>"
          r"(?<b>"
            r"\d+,"
            r"[01]?"
            r"(?>,(?<d>-?\d*\.?\d*)){3}"
            r"(?>(\+|,)(?&d)(?!,))*"
            r";?"
          r")+"
        r"(?<!;)\?"
        r")"

        r"(?>" # Connections
          r"(?<i>[1-9][0-9]*),"
          r"(?&i)"
          r";?"
        r")*"
        r"(?<!;)\?"

        r"(?>" # Buildings
          r"[A-Za-z]+,"
          r"(?>(?&d),){3}"
          r"(?>(?&d),){9}"
          r"(?>[01](?&i),?)*"
          r"(?<!,)"
          r";?"
        r")*"
        r"(?<!;)\?"

        r"(" # Sign data
          r"([0-9a-fA-F]{2})"
        r")*"
        r"(?![\d\w,;?+])$"
    )
    # fmt: on
    return re.match(regex, string) != None


def importSave(string: str, snapToGrid: bool = True) -> Save:
    """Import a Circuit Maker 2 save string as a save."""
    assert validateSave(string), "invalid save string"

    newSave = Save()

    blockstring,connectionstring,buildings,sign = string.split("?")
    blocks: list[Block] = []

    for block in blockstring.split(";"):
        block_id,state,x,y,z,properties = block.split(",")
        props = [float(p) for p in properties.split("+")]
        newblock = newSave.addBlock(int(block_id), (float(x),float(y),float(z)), state == "1",props, snapToGrid)
        blocks.append(newblock)

    for connection in connectionstring.split(";"):
        source,target = connection.split(",")
        newSave.addConnection(blocks[int(source)],blocks[int(target)])

    return newSave

"""Module for working with cmd commands"""
# pylint: disable=missing-function-docstring
import re
from typing import List
from .models import SegmentStatus, Segment, JobStatus


class Commands:
    """Set of commands available for parsing"""
    ls = 'ls'
    pwd = 'pwd'
    cat = 'cat'
    tasks = '/share/apps/bin/tasks'


class CommandParser:
    """Set of command parsers"""
    @staticmethod
    def cat(data: str) -> str:
        return data[:-1]

    @staticmethod
    def ls(data: str) -> List[str]:  # pylint: disable=invalid-name
        return data.split('\n')[:-1]

    @staticmethod
    def pwd(data: str) -> str:
        return data[:-1]

    @staticmethod
    def tasks(data: str) -> List[Segment]:
        _help: List[str] = []
        res: List[List[str]] = []
        for line in data.split('\n')[:-1]:
            if line == '':
                res.append(_help)
                _help = []
            else:
                _help.append(line[:-1])
        segments = []
        for i in res:
            # title = re.sub(r' *=+ *', '', i[0])
            name = i[1].split(' ')[4].lower()
            status = SegmentStatus(*map(int, re.findall(r'\d+', i[2])))
            cores_per_node = int(re.findall(r'\d+', i[3])[0])//status.total
            jobs = []
            if i[5] != 'No tasks':
                for j in i[7:]:
                    raw = list(
                        map(lambda x: x[0] + x[1],
                            re.findall(r'(\S+ \S+)|(\S+)', j)))
                    raw[0] = int(raw[0])
                    raw[4] = int(raw[4])
                    raw[5] = int(raw[5])
                    if raw[3] == 'C':
                        raw.insert(-1, None)
                    jobs.append(JobStatus(*raw))
            segments.append(Segment(name, status, cores_per_node, jobs))
        return segments

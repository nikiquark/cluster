"""Module for working with the Irkutsk supercomputer(Matrosov)"""
from typing import List, Tuple
from subprocess import run, PIPE
import os
from random import randint

from cluster.cluster import Cluster

from .commands import Commands, CommandParser
from .models import Segment


class Matrosov(Cluster):
    """Class for working with the Irkutsk supercomputer(Matrosov)"""
    ssh: bool
    segments: List[Segment]

    def __init__(self, ssh=True, ssh_name: str = 'matrosov') -> None:
        self.ssh = ssh
        self.ssh_name = ssh_name
        self.update()

    def __repr__(self) -> str:
        return "Matrosov Cluster"

    def execute(self, command: str,
                source_share: bool = False) -> Tuple[str, str]:
        """Run unix command on cluster

        Args:
            command (str):
                unix command

            source_share (bool, optional):
                Execute source /share/etc/bashrc before running the command.

                Necessary for some commands (e.g. tasks, qsub, qfree).

                Defaults to False.

        Returns:
            tuple[str, str]: stdout, stderr
        """
        command += " | /bin/sed -r 's/\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g'"  # noqa: E501, W605 # pylint: disable=line-too-long, anomalous-backslash-in-string
        if source_share:
            command = 'source /share/etc/bashrc && ' + command
        if self.ssh:
            command = f"ssh {self.ssh_name} \"{command}\""
        result = run(command, stdout=PIPE, stderr=PIPE,
                     encoding='utf-8', shell=True,
                     universal_newlines=True, check=True)

        return result.stdout, result.stderr

    def run(self, _command: str) -> any:
        """Run execute then parse it with CommandParser

        Args:
            _command (str): unix command available in CommandParser

        Returns:
            any: result of the parser's work
        """
        command = _command.split(' ')[0]
        res = self.execute(_command)[0]
        parser = getattr(CommandParser, command)
        return parser(res)

    def update(self) -> None:
        """
        Runs 'tasks' on the cluster and updates self.segments list
        """
        self.segments = []
        out, _ = self.execute(Commands.tasks)
        segments = CommandParser.tasks(out)
        for segment in segments:
            segment.cluster = self
            self.segments.append(segment)
            setattr(self, segment.name, segment)

    def create_file(self, dirname: str, filename: str, data: str) -> None:
        """
            Creates a text file on the cluster

        Args:
            dirname (str): folder name
            filename (str): file name
            data (str): string to insert into the file
        """
        if self.ssh:
            filename_ = f"{randint(1000000, 10000000)}{filename}"
        else:
            filename_ = f"{dirname}/{filename}"
        with open(filename_, 'w', encoding='utf-8') as output:
            output.write(data)

        if self.ssh:
            run(f'scp {filename_} {self.ssh_name}:{dirname}/{filename}',
                shell=True, stdout=PIPE, check=True)
            os.remove(filename_)
            self.execute(f'/usr/bin/dos2unix {dirname}/{filename}')

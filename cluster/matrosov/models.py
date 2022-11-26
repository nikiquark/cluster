"""Supporting classes for working with a cluster"""
# flake8: noqa: E501
from dataclasses import dataclass
from typing import List, Optional
from cluster.cluster import Cluster


@dataclass
class JobStatus:
    """Dataclass for PBS tasks"""
    job_id: int
    username: str
    jobname: str
    status: str
    nodes: int
    cores: int
    queuetime: str
    starttime: Optional[str] = None
    runtime: Optional[str] = None
    timeleft: Optional[str] = None
    resources: Optional[str] = None


@dataclass
class SegmentStatus:
    """Dataclass for information about segment load"""
    total: int
    free: int
    busy: int
    down: int


@dataclass
class Segment:
    """Class for working with a cluster segment (e.g. intel or amd on Matrosov)"""
    name: str
    nodes_info: SegmentStatus
    cores_per_node: int
    jobs: List[JobStatus]
    cluster: Optional[Cluster] = None

    def __repr__(self) -> str:
        return f"{self.name} - {self.nodes_info.free}/{self.nodes_info.total}"

    def create_job(self, dirname: str, name: str, nodes: int,
                   lcode_argv: str, lcode_dir: str):
        """Create PBS config in the given folder"""
        template = f"""
#!/bin/bash
#PBS -N {name}
#PBS -l nodes={nodes}:{self.name}:ppn={self.cores_per_node},pvmem=40000mb,walltime=10:00:00
cd $PBS_O_WORKDIR
/share/apps/bin/mpiexec -perhost {self.cores_per_node} {lcode_dir}/lcode.{self.name} {lcode_argv}
"""
        if self.cluster is not None:
            self.cluster.create_file(dirname, 'submit.pbs', template)

    def submit_job(self, dirname):
        """Run PBS task"""
        self.cluster.execute(
            f'cd {dirname} && qsub.{self.name} submit.pbs', source_share=True)

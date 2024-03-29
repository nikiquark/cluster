from time import sleep
from typing import Dict, List
from colorama import Fore
import peewee
from cluster import Matrosov
from cluster.matrosov.models import Segment
from cluster.matrosov import Commands
from models import Point, Status, CF, Config


m = Matrosov()
workdir = '/home/yarygova_v/nikita/grid/'
templatedir = workdir + 'template/'


def print_failure(data):
    print(f'{Fore.RED}✖{Fore.RESET}', data)


def print_success(data):
    print(f'{Fore.GREEN}✔{Fore.RESET}', data)


def name(left: float, right: float) -> str:
    return f"{round(left*100)}-{round(right*100)}"


def unname(name: str) -> List[float]:
    return [int(i)/100 for i in name.split('-')]


def load_cfg() -> Dict[str, int]:
    return {i.key: i.value for i in Config.select()}


def add_job(point: Point, segment: str) -> None:
    l, r = point.l, point.r
    l_, r_ = 1 + l/100, 1 + r/100
    jobname = name(l, r)
    jobdir = workdir + f'{jobname}/'
    seg: Segment = getattr(m, segment)

    # make dir for job
    m.execute(f'mkdir {jobdir}')

    # copy files for job
    m.execute(f'cp {templatedir}beamfile.bin {jobdir}beamfile.bin')
    m.execute(f'cp {templatedir}beamfile.bit {jobdir}beamfile.bit')
    m.execute(f'cp {templatedir}lcode.cfg {jobdir}lcode.cfg')

    # make plasma-zshape
    plasma_zshape = f'plasma-zshape = """\n\
12828.539611796372 1.0 L 1.0550\n\
13897.58457944607 1.0550 L 1.0550\n\
2672.6124191242443 0 L 0\n\
26726.12419124244 {l_:.5f} L {r_:.5f}\n\
"""'
    m.create_file(jobdir, 'plasma-zshape-profile.txt', plasma_zshape)

    # make pbs for job
    seg.create_job(jobdir, jobname, cfg[CF.nodes_per_calc],
                   './lcode.cfg ./plasma-zshape-profile.txt',
                   '~/lcode2d/lcode')

    # run job
    seg.submit_job(jobdir)
    print_success(segment + ' submit job: ' + jobname)

    point.status = Status.CALCULATING
    point.save()


def check_success(jobname):
    jobdir = workdir + f'{jobname}/'
    #files = m.run(Commands.ls)
    files, _ = m.execute(f'ls {jobdir}'); files = files.split('\n')
    if 'success' not in files:
        print_failure(f"Problem with job: {jobname}")
        m.execute(f'mv {workdir}{jobdir} {workdir}fail/{jobdir}')
        #m.submit_job(jobdir)
        # l, r = unname(jobname)
        # cur_point = Point.select().where(Point.l == l).where(Point.r == r).get()
        # cur_point.status = Status.PENDING
        # cur_point.save()
        return True
    return False

if __name__ == '__main__':
    while True:
        cfg = load_cfg()
        if cfg[CF.QUIT]:
            break

        # update cluster
        m.update()
        active_amd = [i.jobname for i in m.amd.jobs if i.status == 'R']
        active_intel = [i.jobname for i in m.intel.jobs if i.status == 'R']
        # query_amd = [i.jobname for i in m.amd.jobs if i.status == 'Q']
        # query_intel = [i.jobname for i in m.intel.jobs if i.status == 'Q']
        # check success jobs
        active_jobs = [i.jobname for i in m.amd.jobs +
                    m.intel.jobs if i.status != 'C']
        calculating_jobs = [name(i.l, i.r) for i in Point.select().where(
            Point.status == Status.CALCULATING)]
        finished = set(calculating_jobs) - set(active_jobs)
        for i in finished:
            # TODO: run PAE calculating
            if check_success(i):
                continue
            l, r = unname(i)
            p = Point.select().where(Point.l == l).where(Point.r == r).get()
            p.status = Status.SUCCESS
            p.save()

        # add new jobs
        pending_jobs = Point.select().where(Point.status == Status.PENDING)
        free_amd = m.amd.nodes_info.free
        free_intel = m.intel.nodes_info.free

        n_intel = (free_intel - cfg[CF.free_intel]) // cfg[CF.nodes_per_calc]
        n_amd = (free_amd - cfg[CF.free_amd]) // cfg[CF.nodes_per_calc]
        n_intel = min(n_intel, cfg[CF.max_intel] - len(active_intel))
        n_amd = min(n_amd, cfg[CF.max_amd] - len(active_amd))

        for _ in range(n_intel):
            # add job to intel
            try:
                aspt = Point.get(Point.status == Status.PENDING)
                add_job(aspt, 'intel')
            except peewee.DoesNotExist:
                break
        for _ in range(n_amd):
            # add job to amd
            try:
                aspt = Point.get(Point.status == Status.PENDING)
                add_job(aspt, 'amd')
            except peewee.DoesNotExist:
                break

        # Query job (angry mode)
        query_amd = [i.jobname for i in m.amd.jobs if i.status == 'Q']
        query_intel = [i.jobname for i in m.intel.jobs if i.status == 'Q']
        n_amd = cfg[CF.query_amd] - len(query_amd)
        n_intel = cfg[CF.query_intel] - len(query_intel)
        for i in range(n_amd):
            try:
                aspt = Point.get(Point.status == Status.PENDING)
                add_job(aspt, 'amd')
            except peewee.DoesNotExist:
                pass
        for i in range(n_intel):
            try:
                aspt = Point.get(Point.status == Status.PENDING)
                add_job(aspt, 'intel')
            except peewee.DoesNotExist:
                pass

        print('.', end='', flush=True)
        sleep(cfg[CF.delay])

import threading
import typing

TaskResult = typing.Type['TaskResult']
Task = typing.Callable[[], TaskResult]
WorkerPool = typing.List[typing.Optional[threading.Thread]]


def execute_tasks_async(tasks: typing.List[Task]):
    num_tasks = len(tasks)
    results = num_tasks * [None]

    def spawn_workers(num_cores: int):
        pool: WorkerPool = num_cores * [None]
        done_workers = []

        for task_index in range(num_tasks):
            while not done_workers:
                done_workers = find_done_workers(pool)
            worker_index = done_workers.pop()
            pool[worker_index] = threading.Thread(target=work, args=(task_index,))
            pool[worker_index].start()

        for worker in pool:
            if worker is not None:
                worker.join()

    def find_done_workers(pool: WorkerPool) -> typing.List[int]:
        def is_done(worker: typing.Optional[threading.Thread]):
            if worker is None:
                return True
            return not worker.is_alive()

        return [index for index, worker in enumerate(pool) if is_done(worker)]

    def work(index: int):
        task = tasks[index]
        results[index] = task()

    def run():
        conductor = threading.Thread(target=spawn_workers(8))
        conductor.start()
        conductor.join()
        return results

    return run()

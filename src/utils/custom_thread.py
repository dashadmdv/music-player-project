from threading import Thread, BoundedSemaphore

thread_limiter = BoundedSemaphore(1)


class CustomThread(Thread):
    def __init__(self, target, args):
        super().__init__()
        self.function = target
        self.args = args
        self.value = None

    def run(self):
        thread_limiter.acquire()
        try:
            self.value = self.function(self.args)
        finally:
            thread_limiter.release()

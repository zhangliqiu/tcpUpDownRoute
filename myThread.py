from threading import Thread
class MyThread(Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


if __name__ == '__main__':
    t1 = MyThread(cal_sum, args=(1, 5))
    t2 = MyThread(cal_sum, args=(6, 10))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    res1 = t1.get_result()
    res2 = t2.get_result()

    print(res1 + res2)

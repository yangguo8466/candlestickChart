'''
Created on 2016-5-3

@author: Raomengnan
'''
import time
from threading import Thread, activeCount, Condition,Lock;

class ThreadPool:
    def __init__(self,max_p):
        self._start = True
        self._runningTasks = []
        self._waitingTasks = []

        self._MAX_RUN = max_p
        self._checkThread = Thread(target=self.taskDispatch)
        self._checkThread.start()

        self._lock = Condition(Lock())


    def addTask(self,target, args):
        # print("add task",args)
        if self._lock.acquire(20):#互斥锁
            '''先将锁添加到等待队列中,剩下的事情由调度线程去完成'''
            task = Task(target,args)
            self._waitingTasks.append(task)

            # print("task wait",args)
            self._lock.release()

    #不断地检测线程池中是否有退出的线程
    def taskDispatch(self):
        while self._start:
            '''remove the task in runningTasks'''
            if self._runningTasks.__len__() > 0:
                for task in self._runningTasks:
                    if not task._thread.is_alive():
                        print("task remove stop",task._args)
                        self._runningTasks.remove(task)
                    # else: # python can not real stop a thread
                    #      if task.getTimeUsed() > self.MAX_TIME_BLOCK:
                    #          print("task remove timeout",task._args)
                    #          task._thread.stop()
                    #          self.runningTasks.remove(task)
            if activeCount() <= self._MAX_RUN:
                if self._waitingTasks.__len__() > 0:
                    task = self._waitingTasks.pop()
                    task.start()
                    self._runningTasks.append(task)

    def stop(self):
        self._start = False


class Task:
    def __init__(self,_target,_args):
        self._beginTime = time.time()
        self._args = _args
        self._thread = Thread(target=_target,args=_args)
        
    def getTimeUsed(self):
        return time.time() - self._beginTime

    def start(self):
        self._thread.start()





# if __name__ == '__main__':
#     def test(i):
#         print(i)
#         time.sleep(10)
#
#     pool = ThreadPool(10)
#     arg = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#     for i in arg:
#         args = [i]
#         pool.addTask(test,args)
#         # pool.checkThread.join()


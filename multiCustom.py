#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# -------------------------------------------
#
# @Name: multiCustom
#
# @Describe: a simple model of 'producer(1) - customer(N)'
#
#
# @CreateDate:    2013-07-20
#
# @Author:  weigaofeng@baidu.com
# @Modifier:
#
# -------------------------------------------
# CODE BEGINS
#
#
import os
import Queue
import json
from m_conf import m_conf
import threading
import time
from producer import PRODUCER
from customer import CUSTOMER



class MANAGER:
    ''' manager of producer and customers'''
    def __init__(self,logger):
        self.workers = {}
        self.producer = PRODUCER
        self.statistic = {}
        self.task_queue = Queue.Queue()
        self.logger = logger
        self.statistic = {}

    def feedTask(self):
        tasks = self.producer.genTasks()
        if tasks:
            for task_ in tasks:
                self.task_queue.put(task_)
            self.logger.debug('feed %s tasks', len(tasks))
        else:
            self.logger.debug('feed %s tasks', 0)

    def fetchTask(self):
        if self.task_queue.qsize() > 0:
            task = self.task_queue.get()
            self.task_queue.task_done()
            return task
        else:
            return None

    def getWorkerCnt(self):
        return len(self.workers)

    def isWorkersIdle(self):
        for worker_ in self.workers.values():
            if not worker_.isIdle():
                return False
        return True

    def start(self):
        self.logger.debug("master start work...")

        # start workers
        for i in range(0,m_conf['worker_num']):
            new_worker = WORKER('worker_%02d'%i)
            new_worker.setDaemon(self)
            new_worker.run()
            self.workers[new_worker.getName()] = new_worker

        # loop
        while True:
            # feed tasks
            if self.task_queue.qsize() < self.getWorkerCnt() * 2:
                self.feedTask()

            # how long to sleep
            if self.task_queue.qsize() == 0 and self.isWorkersIdle():
                manager_sleep = m_conf['manager_sleep']
                self.logger.debug("no new tasks, sleep for a while `%s seconds`............", manager_sleep)
                time.sleep(manager_sleep)
            else:
                time.sleep(m_conf['manager_interval'])

            # statistic out
            for worker_ in self.workers.values():
                self.statistic[worker_.getName()] = worker_.statistic
            statistic_info = self._prettyStatistic()
            self.logger.debug("Work status: %s" % statistic_info)

   def _prettyStatistic(self):
        suc_all = 0
        fail_all = 0
        for key, val in self.statistic.items():
            suc_all += val['suc']
            fail_all += val['fail']

        msg = "current workers %d, successed tasks %d, failed tasks %d, %s left. statistic info: \n%s" % (
                len(self.workers), suc_all, fail_all, self.task_queue.qsize(), json.dumps(self.statistic)
                )
        return msg


class WORKER(threading.Thread):
    def __init__(self, manager, name, logger):
        threading.Thread.__init__(self, name = name)
        self.manager = manager
        self.customer = CUSTOMER
        self.bIdle = True
        self.logger = logger
        self.statistic = {
            'suc':0,
            'fail':0,
        }

    def isIdle(self):
        return self.bIdle

    def _doWork(self, task):
        return self.customer.finishTask(task)

    def run(self):
        self.logger.debug("%s start work" % (self.getName()))

        while True:
            self.bIdle = False

            task = self.manager.fetchTask()
            if not task:
                self.bIdle = True
                worker_sleep = m_conf['worker_sleep']
                self.logger.debug("not enough task for me, sleep for a while `%s seconds`............", worker_sleep)
                time.sleep(worker_sleep)
                continue

            rlt, msg = self._doWork(task)
            if rlt:
                self.statistic['suc'] += 1
                self.logger.info("task successed")
            else:
                self.statistic['fail'] += 1
                self.logger.info("task failed, errmsg = %s" % msg)

            self.bIdle = True

    def terminal(self):
        pass




#
#
# ----------- DEBUG OR MAIN -----------------
#
if  __name__ == '__main__':
    pass
#
# 
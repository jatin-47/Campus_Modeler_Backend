class region_Lockdown():
    """
    Lockdown functions for regions. Inherited by region
    """

    def __init__(self):
        self.Shutdown = 0
        self.roles_restricted = []
        self.Shutdown_duration = 0

        self.LockdownLog = []  # populate this

        self.PeriodLocks = []  # Keeping them seperate so they can be sorted
        self.ThresholdLocks = []

        self.OngoingLocks = []

        self.prevPositive = 0  # Storing the number of people tested positive on the previous day for delta_pt lock

    def impose_lockdown(self,duration,roles_restricted):
        self.Shutdown = 1
        self.Shutdown_duration = duration
        self.roles_restricted = roles_restricted

    def lift_lockdown(self):
        self.Shutdown = 0
        self.Shutdown_duration = 0
        self.roles_restricted = []

    # def lock_sector(self, SectorIndex, master):
    #     master.SectorLockStatus[SectorIndex] = 1
    #
    # def unlock_sector(self, SectorIndex, master):
    #     master.SectorLockStatus[SectorIndex] = 0
    #
    # def get_total_positive_cases(self, master):
    #     totalPositive = 0
    #     for name in master.RegionNames:
    #         totalPositive += master.Regions[name].NumTestedPositive.value
    #
    #     return totalPositive
    #
    # def __print_total_positive__(self, master):
    #     for name in master.RegionNames:
    #         logging.info('Region {} has {} positive cases'.format(name, master.Regions[name].NumTestedPositive.value))
    #
    # def __check_ongoing_locks__(self, master, runpm):
    #     """
    #     Iterates over the ongoing locks and lifts locks when the time is up.
    #     The tuples in self.OngoingLocks are like -> (Day lock ends, sector locked)
    #     """
    #     tempOngoingLocks = self.OngoingLocks.copy()
    #     for lock in tempOngoingLocks:
    #         if self.Today == lock[0]:
    #
    #             if lock[1] == -1:  # Region Lock
    #                 self.lift_lockdown()
    #                 self.OngoingLocks.remove(lock)
    #                 self.ComplianceRate = runpm.ComplianceRate
    #                 logging.info('Region {} unlocked on day {}'.format(self.Name, self.Today))
    #
    #             else:  # Sector Lock
    #                 if self.HandlesSectorLock:  ##Declared in Region class
    #                     self.unlock_sector(lock[1], master)
    #                     self.OngoingLocks.remove(lock)
    #                     logging.info('Sector {} unlocked by region {} on day {}'.format(lock[1], self.Name, self.Today))
    #
    # def __apply_lock__(self, lock, master):  # add check if sector is already locked, remove
    #     """
    #     Locks (or extends lockdown of) a region or sector
    #     Args:
    #         lock (tuple): Tuple from Parameters -> ()
    #     """
    #     if lock[3] == -1:  # Region Lock
    #         if self.Locked.value == 0:  # Region not locked yet. Lock it
    #             self.impose_lockdown()
    #             self.OngoingLocks.append([min(self.Today + lock[1], self.SIMULATION_DAYS), lock[3]])
    #             self.LockdownLog.append([self.Today, min(self.Today + lock[1], self.SIMULATION_DAYS)])
    #             logging.info('Region {} locked till day {} on day {}'.format(self.Name, min(self.Today + lock[1],
    #                                                                                         self.SIMULATION_DAYS),
    #                                                                          self.Today))
    #
    #         else:  # Region currently locked. Extend Lockdown
    #             for i, prev_lock in enumerate(self.OngoingLocks):
    #                 if prev_lock[1] == -1:  # find the previous region lock
    #                     self.OngoingLocks[i][0] = min(self.Today + lock[1],
    #                                                   self.SIMULATION_DAYS)  # set the end date of prev lock as the end date of new lock
    #                     self.LockdownLog.append([self.Today, min(self.Today + lock[1], self.SIMULATION_DAYS)])
    #                     logging.info('Region {} lockdown extended till day {} on day {}'.format(self.Name,
    #                                                                                             min(self.Today + lock[
    #                                                                                                 1],
    #                                                                                                 self.SIMULATION_DAYS),
    #                                                                                             self.Today))
    #                     break
    #
    #     else:  # Sector Lock
    #         if self.HandlesSectorLock:  # Only first region would handle Sector Locks
    #             self.__print_total_positive__(master)
    #             SectorIndex = lock[3]
    #             if master.SectorLockStatus[SectorIndex] == 0:  # Sector not locked yet. Lock it
    #                 self.lock_sector(SectorIndex, master)
    #                 self.OngoingLocks.append([min(self.Today + lock[1], self.SIMULATION_DAYS), lock[3]])
    #                 logging.info('Sector {} locked by region {} till day {} on day {}'.format(lock[3], self.Name,
    #                                                                                           min(self.Today + lock[1],
    #                                                                                               self.SIMULATION_DAYS),
    #                                                                                           self.Today))
    #
    #             else:  # Sector currently locked. Extend Lockdown
    #                 for i, prev_lock in enumerate(self.OngoingLocks):
    #                     if prev_lock[1] == lock[3]:  # find the previous lock for that sector
    #                         self.OngoingLocks[i][0] = min(self.Today + lock[1],
    #                                                       self.SIMULATION_DAYS)  # set the end date of prev lock as the end date of new lock
    #                         logging.info(
    #                             'Sector {} lockdown extended by region {} till day {} on day {}'.format(lock[3],
    #                                                                                                     self.Name,
    #                                                                                                     min(self.Today +
    #                                                                                                         lock[1],
    #                                                                                                         self.SIMULATION_DAYS),
    #                                                                                                     self.Today))
    #                         break
    #
    # def check_lockdown_status(self, master, runpm):
    #     self.__check_ongoing_locks__(master, runpm)
    #
    #     tempLocks = self.LockdownPhases.copy()
    #
    #     for lock in tempLocks:
    #         if lock[2] == 'p':
    #             if self.Today == lock[0]:
    #                 self.__apply_lock__(lock, master)
    #                 self.LockdownPhases.remove(lock)
    #                 if len(lock) == 5:
    #                     print('Compulsary region lock of region {} on day {} with old cr = {}, new cr = {}'.format(
    #                         self.Name, self.Today, self.ComplianceRate, lock[4]))
    #                     self.ComplianceRate = lock[4]
    #
    #         elif lock[2] == 't':
    #             if lock[3] == -1:  # if it's a region lock check only positive cases in that region
    #                 if len(self.TestedP['Positive']) >= lock[0]:
    #                     self.__apply_lock__(lock, master)
    #                     self.LockdownPhases.remove(lock)
    #
    #             else:  # if it's a sector lock check city-wide positives
    #                 totalPositive = self.get_total_positive_cases(master)
    #                 if totalPositive >= lock[0]:
    #                     self.__apply_lock__(lock, master)
    #                     self.LockdownPhases.remove(lock)
    #
    #         elif lock[2] == 'delta_pt':
    #             if lock[3] == -1:  # Region-wide lock
    #                 if len(self.TestedP['Positive']) - self.prevPositive > lock[0]:
    #                     if self.Locked.value == 0:  # Only Lock if the region is not already locked (rolling lock, not extending lock)
    #                         self.__apply_lock__(lock, master)
    #                         # self.LockdownPhases.remove(lock)
    #                         print(
    #                             'Region {} had {}	positive tested yesterday and {} today, so locking it for {} days on day {} old cr = {}, new cr = {}'.format(
    #                                 self.Name, self.prevPositive, len(self.TestedP['Positive']), lock[1], self.Today,
    #                                 self.ComplianceRate, lock[4]))
    #                         self.ComplianceRate = lock[4]
    #
    #         self.prevPositive = len(self.TestedP['Positive'])
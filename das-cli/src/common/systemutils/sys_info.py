import os
import time
import shutil
import psutil

class SystemInfoExtractor:

    def __init__(self):
        pass

    IGNORED_MOUNTPOINTS_PREFIX = (
        "/boot",
        "/proc",
        "/sys",
        "/dev",
        "/run",
        "/snap",
        "/var/lib/docker",
        "/var/lib/containers",
        "/var/lib/kubelet",
    )

    def get_cpu_info(self):
        cpuUsagePercent = psutil.cpu_percent()
        cpuTotalCores = psutil.cpu_count()

        return {
            "cpuUsage" : cpuUsagePercent,
            "cpuTotalCores" : cpuTotalCores
        }

    def get_memory_info(self):
        memoryInfo = psutil.virtual_memory()

        return {
            "totalMemory" : round(memoryInfo.total / 1024 ** 2),
            "usedMemory": round(memoryInfo.used / 1024 ** 2),
        }

    def get_disks_info(self):

        partitionInfo = psutil.disk_partitions()

        formatted_partitions = []

        for partition in partitionInfo:

            if not partition.mountpoint.startswith(self.IGNORED_MOUNTPOINTS_PREFIX):
                partition_device = partition.device
                partition_mntpoint = partition.mountpoint

                generalDiskInfo = shutil.disk_usage(partition.mountpoint)
                diskTotalMB = round(generalDiskInfo.total / 1024 ** 2)
                diskUsedMB = round(generalDiskInfo.used / 1024 ** 2)

                formatted_partitions.append(
                    {
                        "disk_device": partition_device,
                        "disk_mntpoint": partition_mntpoint,
                        "disk_total_space": diskTotalMB,
                        "disk_used_space": diskUsedMB,
                    }
                )

        return formatted_partitions


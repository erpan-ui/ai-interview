from concurrent.futures import ThreadPoolExecutor


class ThreadPoolService:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def get_executor(self):
        """获取线程池实例"""
        return self.executor

    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=False)


# 全局单例实例
thread_pool_service = ThreadPoolService()

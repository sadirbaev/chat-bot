
def post_worker_init(worker):

    import chatserver
    chatserver.start_consumer_thread()
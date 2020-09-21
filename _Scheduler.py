import Live

def schedule(evt):
    """ Schedules an event to be triggered at the next interval. """
    _scheduled_events.append(evt)


def start_scheduler():
    """ Starts the scheduler/timer. """
    _scheduler.start()


def stop_scheduler():
    """ Stops the scheduler/timer. """
    _scheduler.stop()


def add_client(client):
    """ Adds the client to the list of clients.  The client must implement an on_tick
    method. """
    if client not in _clients:
        _clients.append(client)


def remove_client(client):
    """ Removes a previously added client. """
    if client in _clients:
        _clients.remove(client)


def _tick():
    for c in _clients:
        c.on_tick()

    for e in reversed(_scheduled_events):
        e()
        _scheduled_events.remove(e)


_clients = []
_scheduled_events = []
_scheduler = Live.Base.Timer(callback=_tick, interval=1, repeat=True)
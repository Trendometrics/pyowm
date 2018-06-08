from pyowm.utils import timeformatutils
from pyowm.alertingapi30.enums import AlertChannelsEnum


class Trigger:
    """
    Object representing a the check if a set of weather conditions are met on a given geographical area: each condition
    is a rule on the value of a given weather parameter (eg. humidity, temperature, etc). Whenever a condition from a
    `Trigger` is met, the OWM API crates an alert and binds it to the the `Trigger`.
    A `Trigger` is the local proxy for the corresponding entry on the OWM API, therefore it can get ouf of sync as
    time goes by and conditions are met: it's up to you to "refresh" the local trigger by using a
    `pyowm.utils.alertingapi30.AlertManager` instance.
    :param start: time object representing the time when the trigger begins to be checked
    :type start: int, ``datetime.datetime`` or ISO8601-formatted string
    :param end: time object representing the time when the trigger ends to be checked
    :type end: int, ``datetime.datetime`` or ISO8601-formatted string
    :param alerts: the `Alert` objects representing the alerts that have been fired for this `Trigger` so far. Defaults
    to `None`
    :type alerts: list of `pyowm.utils.alertingapi30.Alert` instances
    :param conditions: the `Condition` objects representing the set of checks to be done on weather variables
    :type conditions: list of `pyowm.utils.alertingapi30.Condition` instances
    :param area: the geographic are over which conditions are checked: it can be composed by multiple geoJSON types
    :type area: list of geoJSON types (str)
    :param alert_channels: the alert channels through which alerts originating from this `Trigger` can be consumed.
    Defaults to OWM API polling
    :type alert_channels: list of `pyowm.utils.alertingapi30.AlertChannel` instances
    :param id: optional unique ID for this `Trigger` instance
    :type id: str
    :returns:  a *Trigger* instance
    :raises: *ValueError* when start or end epochs are `None` or when end precedes start or when conditions or area
    are empty collections

    """
    def __init__(self, start, end, conditions, area, alerts=None, alert_channels=None, id=None):
        assert start is not None
        assert end is not None
        unix_start = timeformatutils.to_UNIXtime(start)
        unix_end = timeformatutils.to_UNIXtime(end)
        if unix_start >= unix_end:
            raise ValueError("Error: the start epoch must precede the end epoch")
        self.start = unix_start
        self.end = unix_end
        assert conditions is not None
        if len(conditions) == 0:
            raise ValueError('A trigger must contain at least one condition: you provided none')
        assert area is not None
        if len(area) == 0:
            raise ValueError('The area for a trigger must contain at least one geoJSON type: you provided none')
        if alerts is None or len(alerts) == 0:
            self.alerts = list()
        else:
            self.alerts = alerts
        if alert_channels is None or len(alert_channels) == 0:
            self.alert_channels = [AlertChannelsEnum.OWM_API_POLLING]
        else:
            self.alert_channels = alert_channels
        self.id = id

    def get_alerts(self):
        """
        Returns all of the alerts for this `Trigger`
        :return: a list of `Alert` objects
        """
        return self.alerts

    def get_alert(self, alert_id):
        """
        Returns the `Alert` of this `Trigger` having the specified ID
        :param alert_id: str, the ID of the alert
        :return: `Alert` instance
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None

    def get_alerts_since(self, timestamp):
        """
        Returns all the `Alert` objects of this `Trigger` that were fired since the specified timestamp.
        :param timestamp: time object representing the point in time since when alerts have to be fetched
        :type timestamp: int, ``datetime.datetime`` or ISO8601-formatted string
        :return: list of `Alert` instances
        """
        unix_timestamp = timeformatutils.to_UNIXtime(timestamp)
        result = []
        for alert in self.alerts:
            if alert.last_update >= unix_timestamp:
                result.append(alert)
        return result

    def get_alerts_on(self, weather_param):
        """
        Returns all the `Alert` objects of this `Trigger` that refer to the specified weather parameter (eg. 'temp',
        'pressure', etc.). The allowed weather params are the ones enumerated by class
        `pyowm.alertingapi30.enums.WeatherParametersEnum`
        :param weather_param: str, values in `pyowm.alertingapi30.enums.WeatherParametersEnum`
        :return: list of `Alert` instances
        """
        result = []
        for alert in self.alerts:
            for met_condition in alert.met_conditions:
                if met_condition['condition'].weather_param == weather_param:
                    result.append(alert)
                    break
        return result

    def __repr__(self):
        return "<%s.%s - id=%s, start=%s, end=%s, alerts=%s>" % (
                    __name__,
                    self.__class__.__name__,
                    self.id if self.id is not None else 'None',
                    timeformatutils.to_ISO8601(self.start),
                    timeformatutils.to_ISO8601(self.end),
                    str(len(self.alerts)))
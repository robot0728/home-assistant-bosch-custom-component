"""Bosch statistic helper for Recording/Energy sensor."""
from __future__ import annotations
import logging
from homeassistant.components.recorder.models import (
    StatisticData,
    StatisticMetaData,
)
from sqlalchemy.exc import IntegrityError

try:
    from homeassistant.components.recorder.db_schema import StatisticsMeta
except ImportError:
    from homeassistant.components.recorder.models import StatisticsMeta
from homeassistant.components.recorder.util import session_scope
from homeassistant.components.recorder.statistics import async_add_external_statistics

_LOGGER = logging.getLogger(__name__)


class StatisticHelper:
    """Statistic helper class."""

    def __init__(self, new_stats_api: bool = False):
        """Initialize statistic helper."""
        self._short_id = None
        self._new_stats_api = new_stats_api

    async def move_old_entity_data_to_new(self, event_time=None) -> None:
        """Rename old entity_id in statistic table. Not working currently."""
        old_entity_id = self.entity_id
        _LOGGER.debug("Moving entity id statistic data to new format.")
        try:
            with session_scope(hass=self.hass) as session:
                session.query(StatisticsMeta).filter(
                    (StatisticsMeta.statistic_id == old_entity_id)
                    & (StatisticsMeta.source == "recorder")
                ).update(
                    {
                        StatisticsMeta.statistic_id: self.statistic_id,
                        StatisticsMeta.source: self._domain_name.lower(),
                        StatisticsMeta.name: self._name,
                    }
                )
        except IntegrityError as err:
            _LOGGER.error("Can't move entity id. It already exists. %s", err)

    @property
    def statistic_metadata(self) -> StatisticMetaData:
        """Statistic Metadata recorder model class."""
        return StatisticMetaData(
            has_mean=False,
            has_sum=True,
            name=self._name,
            source=self._domain_name.lower(),
            statistic_id=self.statistic_id,
            unit_of_measurement=self._unit_of_measurement,
        )

    def add_external_stats(self, stats: list[StatisticData]) -> None:
        """Add external statistics."""
        self._state = "external"
        if not stats:
            return
        async_add_external_statistics(self.hass, self.statistic_metadata, stats)

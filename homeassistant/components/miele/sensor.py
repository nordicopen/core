"""Sensor platform for Miele integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import STATE_STATUS_TAGS, MieleAppliance, StateStatus
from .coordinator import MieleConfigEntry, MieleDataUpdateCoordinator
from .entity import MieleEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MieleSensorDescription(SensorEntityDescription):
    """Class describing Miele sensor entities."""

    data_tag: str
    convert: Callable[[Any], Any] | None = None
    zone: int | None = None


@dataclass
class MieleSensorDefinition:
    """Class for defining sensor entities."""

    types: tuple[MieleAppliance, ...]
    description: MieleSensorDescription


SENSOR_TYPES: Final[tuple[MieleSensorDefinition, ...]] = (
    MieleSensorDefinition(
        types=(
            MieleAppliance.WASHING_MACHINE,
            MieleAppliance.WASHING_MACHINE_SEMI_PROFESSIONAL,
            MieleAppliance.TUMBLE_DRYER,
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.DISHWASHER,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.HOB_HIGHLIGHT,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.COFFEE_SYSTEM,
            MieleAppliance.HOOD,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.ROBOT_VACUUM_CLEANER,
            MieleAppliance.WASHER_DRYER,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.HOB_INDUCTION,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
            MieleAppliance.HOB_INDUCT_EXTR,
        ),
        description=MieleSensorDescription(
            key="state_status",
            translation_key="status",
            data_tag="state_status",
            convert=lambda x: STATE_STATUS_TAGS.get(x, x),
        ),
    ),
    MieleSensorDefinition(
        types=(
            MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL,
            MieleAppliance.OVEN,
            MieleAppliance.OVEN_MICROWAVE,
            MieleAppliance.DISH_WARMER,
            MieleAppliance.STEAM_OVEN,
            MieleAppliance.MICROWAVE,
            MieleAppliance.FRIDGE,
            MieleAppliance.FREEZER,
            MieleAppliance.FRIDGE_FREEZER,
            MieleAppliance.STEAM_OVEN_COMBI,
            MieleAppliance.WINE_CABINET,
            MieleAppliance.WINE_CONDITIONING_UNIT,
            MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT,
            MieleAppliance.STEAM_OVEN_MICRO,
            MieleAppliance.DIALOG_OVEN,
            MieleAppliance.WINE_CABINET_FREEZER,
            MieleAppliance.STEAM_OVEN_MK2,
        ),
        description=MieleSensorDescription(
            key="state_temperature_1",
            data_tag="state_temperature_1",
            zone=1,
            device_class=SensorDeviceClass.TEMPERATURE,
            translation_key="temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            convert=lambda x: x / 100.0,
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MieleConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = config_entry.runtime_data.coordinator

    entities = [
        MieleSensor(coordinator, device_id, definition.description)
        for device_id in coordinator.data.devices
        for definition in SENSOR_TYPES
        if coordinator.data.devices[device_id].device_type in definition.types
    ]

    async_add_entities(entities)


APPLIANCE_ICONS = {
    MieleAppliance.WASHING_MACHINE: "mdi:washing-machine",
    MieleAppliance.TUMBLE_DRYER: "mdi:tumble-dryer",
    MieleAppliance.TUMBLE_DRYER_SEMI_PROFESSIONAL: "mdi:tumble-dryer",
    MieleAppliance.DISHWASHER: "mdi:dishwasher",
    MieleAppliance.OVEN: "mdi:chef-hat",
    MieleAppliance.OVEN_MICROWAVE: "mdi:chef-hat",
    MieleAppliance.HOB_HIGHLIGHT: "mdi:pot-steam-outline",
    MieleAppliance.STEAM_OVEN: "mdi:chef-hat",
    MieleAppliance.MICROWAVE: "mdi:microwave",
    MieleAppliance.COFFEE_SYSTEM: "mdi:coffee-maker",
    MieleAppliance.HOOD: "mdi:turbine",
    MieleAppliance.FRIDGE: "mdi:fridge-industrial-outline",
    MieleAppliance.FREEZER: "mdi:fridge-industrial-outline",
    MieleAppliance.FRIDGE_FREEZER: "mdi:fridge-outline",
    MieleAppliance.ROBOT_VACUUM_CLEANER: "mdi:robot-vacuum",
    MieleAppliance.WASHER_DRYER: "mdi:washing-machine",
    MieleAppliance.DISH_WARMER: "mdi:heat-wave",
    MieleAppliance.HOB_INDUCTION: "mdi:pot-steam-outline",
    MieleAppliance.STEAM_OVEN_COMBI: "mdi:chef-hat",
    MieleAppliance.WINE_CABINET: "mdi:glass-wine",
    MieleAppliance.WINE_CONDITIONING_UNIT: "mdi:glass-wine",
    MieleAppliance.WINE_STORAGE_CONDITIONING_UNIT: "mdi:glass-wine",
    MieleAppliance.STEAM_OVEN_MICRO: "mdi:chef-hat",
    MieleAppliance.DIALOG_OVEN: "mdi:chef-hat",
    MieleAppliance.WINE_CABINET_FREEZER: "mdi:glass-wine",
    MieleAppliance.HOB_INDUCT_EXTR: "mdi:pot-steam-outline",
}


class MieleSensor(MieleEntity, SensorEntity):
    """Representation of a Sensor."""

    entity_description: MieleSensorDescription

    def __init__(
        self,
        coordinator: MieleDataUpdateCoordinator,
        device_id: str,
        description: MieleSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device_id, description)
        if description.key == "state_status":
            self._attr_icon = APPLIANCE_ICONS.get(
                MieleAppliance(coordinator.data.devices[self._device_id].device_type),
                "mdi:state-machine",
            )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = getattr(
            self.coordinator.data.devices[self._device_id],
            self.entity_description.data_tag,
            None,
        )
        if self.entity_description.convert is not None:
            value = self.entity_description.convert(value)
        return value

    @property
    def available(self) -> bool:
        """Return the availability of the entity."""

        if self.entity_description.key == "state_status":
            return True
        if not self.coordinator.last_update_success:
            return False
        return (
            self.coordinator.data.devices[self._device_id].state_status
            != StateStatus.NOT_CONNECTED
        )


# class MieleSensor(MieleEntity, SensorEntity):
#     """Representation of a Sensor."""

#     entity_description: MieleSensorDescription

#     def __init__(
#         self,
#         coordinator: DataUpdateCoordinator,
#         device_id,
#         description: MieleSensorDescription,
#     ) -> None:
#         """Initialize the sensor."""
#         super().__init__(coordinator, device_id, description)
#         _LOGGER.debug("init sensor %s", device_id)
#         if self.entity_description.convert_icon is not None:
#             self._attr_icon = self.entity_description.convert_icon(
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.type_key_raw
#                 ],
#             )
#         self._available_states = []
#         if self.entity_description.available_states is not None:
#             self._available_states = self.entity_description.available_states(
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.type_key_raw
#                 ],
#             )
#         self._last_elapsed_time_reported = None
#         self._last_started_time_reported = None
#         self._last_abs_time = {}

#     @property
#     def native_value(self) -> StateType:
#         """Return the state of the sensor."""
#         if self.entity_description.key in [
#             "stateRemainingTime",
#             "stateStartTime",
#         ]:
#             return self._get_minutes()

#         if self.entity_description.key in [
#             "stateElapsedTime",
#         ]:
#             mins = self._get_minutes()
#             # Keep value when program ends
#             if (
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.status_key_raw
#                 ]
#                 == STATE_STATUS_PROGRAM_ENDED
#             ):
#                 return self._last_elapsed_time_reported
#             # Force 0 when appliance is off
#             if (
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.status_key_raw
#                 ]
#                 == STATE_STATUS_OFF
#             ):
#                 return 0
#             self._last_elapsed_time_reported = mins
#             return mins

#         if self.entity_description.key in [
#             "stateRemainingTimeAbs",
#             "stateStartTimeAbs",
#         ]:
#             return self._get_absolute_time()

#         if self.entity_description.key in [
#             "stateElapsedTimeAbs",
#         ]:
#             started_time = self._get_absolute_time(sub=True)
#             # Don't update sensor if state == program_ended
#             if (
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.status_key_raw
#                 ]
#                 == STATE_STATUS_PROGRAM_ENDED
#             ):
#                 return self._last_started_time_reported
#             # Force no state when appliance is off
#             if (
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.status_key_raw
#                 ]
#                 == STATE_STATUS_OFF
#             ):
#                 return None
#             self._last_started_time_reported = started_time
#             return started_time

#         # Log raw and localized values for programID etc
#         # Active if logger.level is DEBUG or INFO
#         if _LOGGER.getEffectiveLevel() <= logging.INFO:
#             if self.entity_description.key in {
#                 "stateProgramPhase",
#                 "stateProgramId",
#                 "stateProgramType",
#             }:
#                 while len(self.hass.data[DOMAIN]["id_log"]) >= 500:
#                     self.hass.data[DOMAIN]["id_log"].pop()

#                 self.hass.data[DOMAIN]["id_log"].append(
#                     {
#                         "appliance": self.coordinator.data[self._device_id][
#                             self.entity_description.type_key
#                         ],
#                         "key": self.entity_description.key,
#                         "raw": self.coordinator.data[self._device_id][
#                             self.entity_description.data_tag
#                         ],
#                         "localized": self.coordinator.data[self._device_id][
#                             self.entity_description.data_tag_loc
#                         ],
#                     }
#                 )

#         # Show 0 consumption when the appliance is not running,
#         # to correctly reset utility meter cycle. Ignore this when
#         # appliance is not connected (it may disconnect while a program
#         # is running causing problems in energy stats).
#         state = self.coordinator.data[self._device_id][
#             self.entity_description.status_key_raw
#         ]
#         if self.entity_description.key in [
#             "stateCurrentEnergyConsumption",
#             "stateCurrentWaterConsumption",
#         ] and state in [
#             STATE_STATUS_ON,
#             STATE_STATUS_OFF,
#             STATE_STATUS_PROGRAMMED,
#             STATE_STATUS_WAITING_TO_START,
#             STATE_STATUS_IDLE,
#             STATE_STATUS_SERVICE,
#         ]:
#             return 0

#         if (
#             self.coordinator.data[self._device_id].get(self.entity_description.data_tag)
#             is None
#         ):
#             return None
#         if self.coordinator.data[self._device_id].get(
#             self.entity_description.data_tag, -32768
#         ) in (
#             -32766,
#             -32768,
#         ):
#             return None
#         if (
#             self.entity_description.key in ["stateProgramId", "stateProgramPhase"]
#             and self.coordinator.data[self._device_id][self.entity_description.data_tag]
#             <= 0
#         ):
#             return None

#         if self.entity_description.convert is None:
#             return self.coordinator.data[self._device_id][
#                 self.entity_description.data_tag
#             ]

#         # If configuration.yaml contains an overridden mapping, use that value if available
#         custom_mapped_value = self._get_custom_mapped_value(
#             self.coordinator.data[self._device_id][self.entity_description.data_tag]
#         )
#         if (
#             custom_mapped_value is not None
#             and custom_mapped_value in self._available_states
#         ):
#             return custom_mapped_value

#         # Otherwise use converter specified in entity description
#         return self.entity_description.convert(
#             self.coordinator.data[self._device_id][self.entity_description.data_tag],
#             self.coordinator.data[self._device_id][
#                 self.entity_description.type_key_raw
#             ],
#         )

#     def _get_minutes(self):
#         mins = (
#             self.coordinator.data[self._device_id][self.entity_description.data_tag]
#             * 60
#             + self.coordinator.data[self._device_id][self.entity_description.data_tag1]
#         )
#         if (
#             self.entity_description.data_tag2 is not None
#             and self.entity_description.data_tag2 is not None
#         ):
#             mins = mins + (
#                 self.coordinator.data[self._device_id][
#                     self.entity_description.data_tag2
#                 ]
#                 * 60
#                 + self.coordinator.data[self._device_id][
#                     self.entity_description.data_tag3
#                 ]
#             )
#         return mins

#     def _get_absolute_time(self, sub=False):
#         now = dt_util.now().replace(second=0, microsecond=0)
#         mins = self._get_minutes()
#         if mins == 0:
#             return None
#         if sub:
#             val = now - timedelta(minutes=mins)
#         else:
#             val = now + timedelta(minutes=mins)
#         formatted = val.strftime("%H:%M")
#         _LOGGER.debug(
#             "Key:  %s | Dev: %s | Mins: %s | Now: %s | State: %s",
#             self.entity_description.key,
#             self._device_id,
#             mins,
#             now,
#             formatted,
#         )
#         # check for previous value and return it if differning of +/-1 min
#         if self.entity_description.key in self._last_abs_time:
#             previous_value = self._last_abs_time[self.entity_description.key]
#             prev_minute = previous_value - timedelta(seconds=120)
#             next_minute = previous_value + timedelta(seconds=120)
#             if prev_minute <= val <= next_minute:
#                 return previous_value.strftime("%H:%M")
#         self._last_abs_time[self.entity_description.key] = val
#         return formatted

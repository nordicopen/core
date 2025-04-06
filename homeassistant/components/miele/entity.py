"""Entity base class for the Miele integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import MieleDataUpdateCoordinator


class MieleEntity(CoordinatorEntity[MieleDataUpdateCoordinator]):
    """Base class for Miele entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MieleDataUpdateCoordinator,
        device_id: str,
        description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self.entity_description = description
        self._attr_unique_id = f"{self.entity_description.key}-{self._device_id}"

        appliance_type = self.coordinator.data.devices[
            self._device_id
        ].device_type_localized
        if appliance_type == "":
            appliance_type = self.coordinator.data.devices[self._device_id].tech_type

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            serial_number=self._device_id,
            name=appliance_type,
            manufacturer=MANUFACTURER,
            model=self.coordinator.data.devices[self._device_id].tech_type,
            hw_version=self.coordinator.data.devices[self._device_id].xkm_tech_type,
            sw_version=self.coordinator.data.devices[
                self._device_id
            ].xkm_release_version,
        )

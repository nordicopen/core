"""Platform for Miele select entity."""

from __future__ import annotations

from base64 import b64decode
from collections.abc import Callable
from dataclasses import dataclass
import logging
import re
from typing import Final

from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import MieleAppliance
from .coordinator import MieleConfigEntry, MieleDataUpdateCoordinator
from .entity import MieleDevice, MieleEntity

PARALLEL_UPDATES = 1

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MieleImageDescription(ImageEntityDescription):
    """Class describing Miele image entities."""

    value_fn: Callable[[MieleDevice], StateType]


@dataclass
class MieleImageDefinition:
    """Class for defining image entities."""

    types: tuple[MieleAppliance, ...]
    description: MieleImageDescription


CAMERA_TYPES: Final[tuple[MieleImageDefinition, ...]] = (
    MieleImageDefinition(
        types=(
            MieleAppliance.OVEN,
            MieleAppliance.FREEZER,
        ),
        description=MieleImageDescription(
            key="oven_camera_image",
            value_fn=lambda value: 1,
            translation_key="oven_camera_image",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MieleConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the image platform."""
    coordinator = config_entry.runtime_data.coordinator
    added_devices: set[str] = set()

    def _async_add_new_devices() -> None:
        nonlocal added_devices
        new_devices_set, current_devices = coordinator.async_add_devices(added_devices)
        added_devices = current_devices

        async_add_entities(
            MieleImage(coordinator, device_id, definition.description)
            for device_id, device in coordinator.data.devices.items()
            for definition in CAMERA_TYPES
            if device_id in new_devices_set and device.device_type in definition.types
        )

    config_entry.async_on_unload(coordinator.async_add_listener(_async_add_new_devices))
    _async_add_new_devices()


class MieleImage(MieleEntity, ImageEntity):
    """Representation of a camera image entity."""

    entity_description: MieleImageDescription
    _attr_content_type = "image/gif"

    def __init__(
        self,
        coordinator: MieleDataUpdateCoordinator,
        device_id: str,
        description: MieleImageDescription,
    ) -> None:
        """Initialize the image entity."""
        super().__init__(coordinator, device_id, description)
        ImageEntity.__init__(self, coordinator.hass)
        self.entity_description = description
        self._attr_image_last_updated = dt_util.utcnow()

    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""

    #     self._attr_image_last_updated = dt_util.utcnow()
    #     super()._handle_coordinator_update()

    async def async_image(self) -> bytes | None:
        """Return bytes of image."""

        # image_path = Path(__file__).parent / "pizza_slice.gif"
        # return await self.hass.async_add_executor_job(image_path.read_bytes)

        match = re.search("data:(.+?);base64,", self.image_string)
        prefix = ""
        if match:
            prefix = match.group()
            self._attr_content_type = match.group(1)
            return b64decode(self.image_string.removeprefix(prefix))
        return None

    image_string: str = (
        "data:image/gif;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQ"
        "ICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBl"
        "Lm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIV"
        "IpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnW"
        "b2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqL"
        "tYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbp"
        "oDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQ"
        "s9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1p"
        "GRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V"
        "/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWqua"
        "ZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekok"
        "RY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS"
        "3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y"
        "+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFx"
        "Ikd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN"
        "29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX"
        "4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
    )

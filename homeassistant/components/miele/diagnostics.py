"""Diagnostics support for Miele."""

from __future__ import annotations

from typing import Any, cast

from aiohttp import ClientError

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceEntry

from .coordinator import MieleConfigEntry

TO_REDACT = {"access_token", "refresh_token", "serialNumber"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: MieleConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    miele_data = {}
    miele_data["devices"] = {
        device_id: device_data.raw
        for device_id, device_data in config_entry.runtime_data.data.devices.items()
    }
    miele_data["actions"] = {
        device_id: action_data.raw
        for device_id, action_data in config_entry.runtime_data.data.actions.items()
    }

    return {
        "config_entry_data": async_redact_data(dict(config_entry.data), TO_REDACT),
        "miele_data": async_redact_data(miele_data, TO_REDACT),
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: MieleConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    info = {}
    info["manufacturer"] = device.manufacturer
    info["model"] = device.model

    coordinator = config_entry.runtime_data

    miele_data = {}

    miele_data["devices"] = {
        device_id: device_data.raw
        for device_id, device_data in config_entry.runtime_data.data.devices.items()
    }
    miele_data["actions"] = {
        device_id: action_data.raw
        for device_id, action_data in config_entry.runtime_data.data.actions.items()
    }
    try:
        miele_data["programs"] = await coordinator.api.get_programs(
            cast(str, device.serial_number)
        )
    except ClientError as err:
        raise HomeAssistantError(
            "Unable to fetch programs list from Miele API"
        ) from err

    return {
        "info": async_redact_data(info, TO_REDACT),
        "data": async_redact_data(config_entry.data, TO_REDACT),
        "miele_data": async_redact_data(miele_data, TO_REDACT),
    }

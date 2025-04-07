"""The Miele integration."""

from __future__ import annotations

import asyncio

from aiohttp import ClientError, ClientResponseError

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow

from .api import AsyncConfigEntryAuth
from .const import DOMAIN
from .coordinator import MieleConfigEntry, MieleDataUpdateCoordinator, MieleRuntimeData

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: MieleConfigEntry) -> bool:
    """Set up Miele from a config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    auth = AsyncConfigEntryAuth(aiohttp_client.async_get_clientsession(hass), session)
    try:
        await auth.async_get_access_token()
    except ClientResponseError as err:
        if 400 <= err.status < 500:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="config_entry_auth_failed",
            ) from err
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="config_entry_not_ready",
        ) from err
    except ClientError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="config_entry_not_ready",
        ) from err

    # Setup MieleAPI and coordinator for data fetch
    coordinator = MieleDataUpdateCoordinator(hass, entry, auth)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = MieleRuntimeData(coordinator, None)

    entry.runtime_data.event_listener = asyncio.create_task(
        entry.runtime_data.coordinator.api.listen_events(
            data_callback=entry.runtime_data.coordinator.callback_update_data,
            actions_callback=entry.runtime_data.coordinator.callback_update_actions,
        )
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: MieleConfigEntry) -> bool:
    """Unload a config entry."""

    entry.runtime_data.event_listener.cancel()  # type: ignore[union-attr]
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

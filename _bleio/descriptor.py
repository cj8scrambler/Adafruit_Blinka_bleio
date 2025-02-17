# SPDX-FileCopyrightText: Copyright (c) 2020 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`_bleio.descriptor`
=======================================================================

_bleio implementation for Adafruit_Blinka_bleio

* Author(s): Dan Halbert for Adafruit Industries
"""
from __future__ import annotations
from typing import Union

from bleak.backends.descriptor import BleakGATTDescriptor

from _bleio.attribute import Attribute
from _bleio.common import adapter, Characteristic
from _bleio.uuid_ import UUID

Buf = Union[bytes, bytearray, memoryview]


# pylint: disable=too-many-instance-attributes
class Descriptor:
    """Stores information about a BLE descriptor.

    Descriptors are attached to BLE characteristics and provide contextual
    information about the characteristic."""

    def __init__(
        self,
        *,
        uuid: UUID,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        max_length: int = 20,
        fixed_length: bool = False,
        initial_value: Buf = b"",
    ):

        """There is no regular constructor for a Descriptor. A new local Descriptor can be created
        and attached to a Characteristic by calling `add_to_characteristic()`.
        Remote Descriptor objects are created by `_bleio.Connection.discover_remote_services`
        as part of remote Characteristics in the remote Services that are discovered.
        """
        self._uuid = uuid
        self._read_perm = read_perm
        self._write_perm = write_perm
        self._max_length = max_length
        self._fixed_length = fixed_length
        self._initial_value = initial_value
        self._characteristic = None
        self._bleak_gatt_descriptor = None

    @classmethod
    def add_to_characteristic(
        cls,
        characteristic: Characteristic,
        uuid: UUID,
        *,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        max_length: int = 20,
        fixed_length: bool = False,
        initial_value: Buf = b"",
    ):

        """Create a new Descriptor object, and add it to this Service.

        :param Characteristic characteristic:
           The characteristic that will hold this descriptor
        :param UUID uuid: The uuid of the descriptor
        :param int read_perm: Specifies whether the descriptor can be read by a client,
           and if so, which security mode is required.
           Must be one of the integer values
           `_bleio.Attribute.NO_ACCESS`, `_bleio.Attribute.OPEN`,
           `_bleio.Attribute.ENCRYPT_NO_MITM`, `_bleio.Attribute.ENCRYPT_WITH_MITM`,
           `_bleio.Attribute.LESC_ENCRYPT_WITH_MITM`,
           `_bleio.Attribute.SIGNED_NO_MITM`, or `_bleio.Attribute.SIGNED_WITH_MITM`.
        :param int write_perm: Specifies whether the descriptor can be written by a client,
           and if so, which security mode is required.
           Values allowed are the same as ``read_perm``.
        :param int max_length: Maximum length in bytes of the descriptor value.
           The maximum allowed is 512, or possibly 510 if ``fixed_length`` is False.
           The default, 20, is the maximum
           number of data bytes that fit in a single BLE 4.x ATT packet.
        :param bool fixed_length: True if the descriptor value is of fixed length.
        :param buf initial_value: The initial value for this descriptor.

        :return: the new Descriptor.
        """
        desc = Descriptor(
            uuid=uuid,
            read_perm=read_perm,
            write_perm=write_perm,
            max_length=max_length,
            fixed_length=fixed_length,
            initial_value=initial_value,
        )
        desc._characteristic = characteristic  # pylint: disable=protected-access
        return desc

    @classmethod
    def _from_bleak(
        cls, characteristic: Characteristic, bleak_descriptor: BleakGATTDescriptor
    ):
        desc = Descriptor.add_to_characteristic(
            characteristic=characteristic,
            uuid=UUID(bleak_descriptor.uuid),
            read_perm=Attribute.OPEN,
            write_perm=Attribute.OPEN,
        )

        # pylint: disable=protected-access
        desc._bleak_gatt_descriptor = bleak_descriptor
        # pylint: enable=protected-access
        return desc

    @property
    def uuid(self) -> UUID:
        """The descriptor uuid. (read-only)"""
        return self._uuid

    @property
    def characteristic(self) -> Characteristic:
        """The Characteristic this Descriptor is a part of."""
        return self._characteristic

    @property
    def value(self) -> bytes:
        """The value of this descriptor."""
        return adapter.await_bleak(
            # pylint: disable=protected-access
            self.characteristic.service.connection._bleak_client.read_gatt_descriptor(
                self.uuid.string
            )
        )

    @value.setter
    def value(self, val) -> None:
        adapter.await_bleak(
            # pylint: disable=protected-access
            self.characteristic.service.connection._bleak_client.write_gatt_descriptor(
                self.uuid.string, val
            )
        )

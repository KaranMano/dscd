from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUCCESS: _ClassVar[Status]
    FAIL: _ClassVar[Status]

class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ELECTRONICS: _ClassVar[Category]
    FASHION: _ClassVar[Category]
    OTHERS: _ClassVar[Category]
    ANY: _ClassVar[Category]
SUCCESS: Status
FAIL: Status
ELECTRONICS: Category
FASHION: Category
OTHERS: Category
ANY: Category

class StatusResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    def __init__(self, status: _Optional[_Union[Status, str]] = ...) -> None: ...

class ItemInfo(_message.Message):
    __slots__ = ("name", "category", "quantity", "description", "pricePerUnit")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICEPERUNIT_FIELD_NUMBER: _ClassVar[int]
    name: str
    category: Category
    quantity: int
    description: str
    pricePerUnit: int
    def __init__(self, name: _Optional[str] = ..., category: _Optional[_Union[Category, str]] = ..., quantity: _Optional[int] = ..., description: _Optional[str] = ..., pricePerUnit: _Optional[int] = ...) -> None: ...

class ItemList(_message.Message):
    __slots__ = ("itemIDs", "itemInfos", "sellerAddresses", "ratings")
    ITEMIDS_FIELD_NUMBER: _ClassVar[int]
    ITEMINFOS_FIELD_NUMBER: _ClassVar[int]
    SELLERADDRESSES_FIELD_NUMBER: _ClassVar[int]
    RATINGS_FIELD_NUMBER: _ClassVar[int]
    itemIDs: _containers.RepeatedScalarFieldContainer[int]
    itemInfos: _containers.RepeatedCompositeFieldContainer[ItemInfo]
    sellerAddresses: _containers.RepeatedScalarFieldContainer[str]
    ratings: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, itemIDs: _Optional[_Iterable[int]] = ..., itemInfos: _Optional[_Iterable[_Union[ItemInfo, _Mapping]]] = ..., sellerAddresses: _Optional[_Iterable[str]] = ..., ratings: _Optional[_Iterable[float]] = ...) -> None: ...

class SellerInfo(_message.Message):
    __slots__ = ("address", "uuid")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    address: str
    uuid: str
    def __init__(self, address: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class RegistrationRequest(_message.Message):
    __slots__ = ("sellerInfo",)
    SELLERINFO_FIELD_NUMBER: _ClassVar[int]
    sellerInfo: SellerInfo
    def __init__(self, sellerInfo: _Optional[_Union[SellerInfo, _Mapping]] = ...) -> None: ...

class SellRequest(_message.Message):
    __slots__ = ("itemInfo", "sellerInfo")
    ITEMINFO_FIELD_NUMBER: _ClassVar[int]
    SELLERINFO_FIELD_NUMBER: _ClassVar[int]
    itemInfo: ItemInfo
    sellerInfo: SellerInfo
    def __init__(self, itemInfo: _Optional[_Union[ItemInfo, _Mapping]] = ..., sellerInfo: _Optional[_Union[SellerInfo, _Mapping]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("itemID", "pricePerUnit", "quantity", "sellerInfo")
    ITEMID_FIELD_NUMBER: _ClassVar[int]
    PRICEPERUNIT_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SELLERINFO_FIELD_NUMBER: _ClassVar[int]
    itemID: int
    pricePerUnit: int
    quantity: int
    sellerInfo: SellerInfo
    def __init__(self, itemID: _Optional[int] = ..., pricePerUnit: _Optional[int] = ..., quantity: _Optional[int] = ..., sellerInfo: _Optional[_Union[SellerInfo, _Mapping]] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("itemID", "sellerInfo")
    ITEMID_FIELD_NUMBER: _ClassVar[int]
    SELLERINFO_FIELD_NUMBER: _ClassVar[int]
    itemID: int
    sellerInfo: SellerInfo
    def __init__(self, itemID: _Optional[int] = ..., sellerInfo: _Optional[_Union[SellerInfo, _Mapping]] = ...) -> None: ...

class DisplayRequest(_message.Message):
    __slots__ = ("sellerInfo",)
    SELLERINFO_FIELD_NUMBER: _ClassVar[int]
    sellerInfo: SellerInfo
    def __init__(self, sellerInfo: _Optional[_Union[SellerInfo, _Mapping]] = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ("itemName", "itemCategory")
    ITEMNAME_FIELD_NUMBER: _ClassVar[int]
    ITEMCATEGORY_FIELD_NUMBER: _ClassVar[int]
    itemName: str
    itemCategory: Category
    def __init__(self, itemName: _Optional[str] = ..., itemCategory: _Optional[_Union[Category, str]] = ...) -> None: ...

class BuyRequest(_message.Message):
    __slots__ = ("itemID", "quantity", "address")
    ITEMID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    itemID: int
    quantity: int
    address: str
    def __init__(self, itemID: _Optional[int] = ..., quantity: _Optional[int] = ..., address: _Optional[str] = ...) -> None: ...

class WishListRequest(_message.Message):
    __slots__ = ("itemID", "address")
    ITEMID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    itemID: int
    address: str
    def __init__(self, itemID: _Optional[int] = ..., address: _Optional[str] = ...) -> None: ...

class RateRequest(_message.Message):
    __slots__ = ("itemID", "rating", "address")
    ITEMID_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    itemID: int
    rating: float
    address: str
    def __init__(self, itemID: _Optional[int] = ..., rating: _Optional[float] = ..., address: _Optional[str] = ...) -> None: ...

class UpdateNotification(_message.Message):
    __slots__ = ("itemID", "itemInfo", "rating", "sellerAddress")
    ITEMID_FIELD_NUMBER: _ClassVar[int]
    ITEMINFO_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    SELLERADDRESS_FIELD_NUMBER: _ClassVar[int]
    itemID: int
    itemInfo: ItemInfo
    rating: float
    sellerAddress: str
    def __init__(self, itemID: _Optional[int] = ..., itemInfo: _Optional[_Union[ItemInfo, _Mapping]] = ..., rating: _Optional[float] = ..., sellerAddress: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

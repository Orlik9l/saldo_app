from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
from datetime import datetime

__all__ = ['Asset', 'BankProperties', 'LiabilityProperties', 'Account', 'JournalEntry', 'Transaction']

@dataclass
class Asset:
    """Asset information (currency)"""
    key: str
    code: str
    name: str
    type: str
    symbol: str
    icon: str

@dataclass
class BankProperties:
    """Bank account properties"""
    provider: str
    externalAccountId: Optional[str]
    institutionId: Optional[str]
    institutionName: str
    institutionLogo: Optional[str]
    mask: str
    creditLimit: float
    name: Optional[str]
    externalItemId: Optional[str]
    currencyIsoCode: Optional[str]
    lastTransactionTimestamp: Optional[int]
    initialBalanceTransactionId: Optional[str]
    syncEnabled: Optional[bool]

@dataclass
class LiabilityProperties:
    """Liability account properties"""
    phone: str
    email: str

@dataclass
class Account:
    """Account information"""
    id: int
    name: str
    icon: Optional[str]
    color: Optional[str]
    type: str
    reportPart: str
    systemType: str
    status: str
    bankProperties: Optional[BankProperties]
    liabilityProperties: Optional[LiabilityProperties]
    primaryAccount: bool
    excludeFromTotal: bool
    parentId: Optional[int]
    preset: bool
    createdTimestamp: int
    updatedTimestamp: int

@dataclass
class JournalEntry:
    """Journal entry for a transaction"""
    accountId: str
    accountName: str
    amount: float
    type: str

@dataclass
class Transaction:
    """
    Transaction record from Saldo API
    
    Attributes:
        transactionDate: Transaction date (timestamp)
        title: Transaction title/description
        journalList: List of journal entries
        id: Transaction ID
        sourceDescription: Original description from source
        actionStatus: Current status of the transaction
        createdTimestamp: When the transaction was created
        updatedTimestamp: When the transaction was last updated
    """
    transactionDate: int
    title: str
    journalList: List[Dict]  # Keep as Dict to handle varying structures
    id: str
    sourceDescription: Optional[str] = None
    actionStatus: Optional[str] = None
    createdTimestamp: Optional[int] = None
    updatedTimestamp: Optional[int] = None

    @property
    def date(self) -> str:
        """Get the transaction date as a string timestamp"""
        return str(self.transactionDate)

    @property
    def description(self) -> str:
        """Get the transaction description"""
        return self.title or self.sourceDescription or 'No Description'

    def get_amount(self) -> float:
        """Get the transaction amount"""
        if not self.journalList:
            return 0
        # Get the first non-zero amount
        for entry in self.journalList:
            amount = entry.get('amount', 0)
            if amount != 0:
                return amount
        return 0

    def get_account_name(self) -> str:
        """Get the account name"""
        if not self.journalList:
            return "Unknown Account"
        first_entry = self.journalList[0]
        return first_entry.get('accountName', 'Unknown Account')

    def get_currency(self) -> str:
        """Get the transaction currency code"""
        master_entry = next(j for j in self.journalList if j.get('accountId') == "master")
        return master_entry.get('asset', {}).get('code', 'Unknown') 
from time import sleep
from tronpy import Tron
from os import system, name
from decimal import Decimal
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound


class TRONAddress:
    # Initialize the TRON client for the Shasta test network.
    __client = Tron(network="shasta")

    def __init__(self, passphrase: str):
        """
        Initialize a TRONAddress instance with the given passphrase.

        Parameters:
        passphrase (str): The passphrase used to generate the address and private key.

        Attributes:
        address (str): The base58check-encoded TRON address derived from the passphrase.
        private_key (str): The private key corresponding to the address.
        balance (Decimal): The current balance of the address in TRX.
        """
        self.key_dict = self.__client.get_address_from_passphrase(passphrase)
        self.address = self.key_dict["base58check_address"]
        self.private_key = self.key_dict["private_key"]
        self.balance = self.update_balance()

    def update_balance(self) -> Decimal:
        """
        Update the balance of the address by querying the TRON network.

        Returns:
        Decimal: The balance of the address in TRX.
        """
        try:
            return self.__client.get_account_balance(self.address)
        except AddressNotFound:
            # Return zero if the address is not found on the network.
            return Decimal(0)

    def send_trx(self, recipient_address: str, amount: Decimal) -> str:
        """
        Send TRX from the current address to a specified recipient address.

        Parameters:
        recipient_address (str): The address of the recipient.
        amount (Decimal): The amount of TRX to send.

        Returns:
        str: The transaction ID of the sent transaction.
        """
        txn = (
            self.__client.trx.transfer(
                from_=self.address,
                to=recipient_address,
                amount=int((amount - 2) * 1_000_000)  # Convert TRX to Sun (1 TRX = 1,000,000 Sun)
            ).build().sign(PrivateKey(bytes.fromhex(self.private_key)))
        )
        # Broadcast the transaction and wait for it to be confirmed.
        return txn.broadcast().wait()["id"]


if __name__ == "__main__":
    try:
        while True:
            # Clear the console screen based on the operating system.
            system("cls") if name == "nt" else system("clear")

            # Create instances for Bob and Alice with their respective passphrases.
            bob = TRONAddress("Wow?NcFqumNrd6uJ+N^v")
            alice = TRONAddress("xV9Pk2zVy1XEQ*G@0hg:")

            # Display Bob's and Alice's addresses and balances.
            print(f"Bob: {bob.address} | {bob.balance} TRX\n")
            print(f"Alice: {alice.address} | {alice.balance} TRX")

            # Notify if both addresses have zero balance.
            if bob.balance + alice.balance == 0:
                print("\nYou can get test coins here: https://shasta.tronex.io/")

            # Prompt user to press Enter to initiate a transaction.
            input("\nPress Enter to continue...\n")

            # Perform a transaction if Bob has more balance than Alice.
            if bob.balance > alice.balance:
                print(f"Transaction ID: {bob.send_trx(alice.address, bob.balance)}")

            # Perform a transaction if Alice has more balance than Bob.
            if alice.balance > bob.balance:
                print(f"Transaction ID: {alice.send_trx(bob.address, alice.balance)}")

            # Wait for 5 seconds before the next iteration.
            sleep(5)
    except KeyboardInterrupt:
        # Exit cleanly on keyboard interrupt and clear the console.
        exit(system("cls") if name == "nt" else system("clear"))

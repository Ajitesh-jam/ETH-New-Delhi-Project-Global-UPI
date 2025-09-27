// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;


contract PaymentSender {
    event PaymentSent(address indexed from, address indexed to, uint256 amount);

    function send(address payable recipient, uint256 amount) external payable {
        require(recipient != address(0), "recipient=0");
        require(amount > 0, "amount=0");
        require(msg.value >= amount, "insufficient msg.value");

        (bool ok, ) = recipient.call{value: amount}("");
        require(ok, "transfer failed");

        uint256 refund = msg.value - amount;
        if (refund > 0) {
            (bool rok, ) = payable(msg.sender).call{value: refund}("");
            require(rok, "refund failed");
        }

        emit PaymentSent(msg.sender, recipient, amount);
    }

    receive() external payable {}
}

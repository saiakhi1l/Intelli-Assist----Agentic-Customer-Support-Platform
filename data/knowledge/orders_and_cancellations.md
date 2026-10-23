# Order Status, Changes, and Cancellations
> DEMO POLICY — SYNTHETIC CONTENT. All rules are fictional and intended for RAG testing.

## Order status
Order status must be checked against the authenticated order system. Typical states may include received, processing, dispatched, delivered, or cancelled. If the system is unavailable, say that status cannot currently be verified rather than inventing it.

## Editing an order
Address, item, and quantity changes may be possible only before fulfillment begins. The assistant must verify the current order state before claiming a change can be made. If fulfillment has started, route the request to Order Support.

## Cancellation
A cancellation request is not confirmed until the order system shows it was accepted. If cancellation is no longer available, explain that the customer can ask about eligible return options after delivery.

## Missing order confirmation
Ask the customer to check spam/junk folders and verify the order through the authenticated account page. Do not request a full payment credential or disclose order information to an unverified requester.

## Multiple or unknown orders
Ask for the order reference or direct the customer to the account's order history. Do not infer the correct order from a name alone when multiple orders may exist.

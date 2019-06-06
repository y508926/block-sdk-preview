# Input and Output blocks

## Input blocks

### Timestamp handling

An input block is a block that receives data from an external (to the model) source, and makes it available to other blocks within the model.  An input block will typically have block *outputs* only, though it is permitted to have  block inputs. All model evaluations involving sending data between blocks must happen at a specified point in time. Input blocks may take a timestamp from an external source (typically indicating exactly when the input occurred), or may treat the data has having occurred in the near future.  As described in the Analytics Builder documentation, the runtime has a global configuration setting `timedelay_secs` which is the delay that the runtime will wait for before processing events. (This allows it to receive events out of order, and it will execute based on timestamp order - provided events are received within this `timedelay_secs` period).

Typically, an input block will listen for events using an `on all <EventType>` listener, started in the `$init` action. On matching an event,the block will extract a timestamp from the event, and create a timer for that value, for the appropriate Partition value (see [Partitions](070-Partitions.md)). On the timer being triggered, the value from the event is sent as an output. Typically, the event received will be passed as the payload of the timer. If an event is received with a timestamp that is too old, then the `createTimerWith` will throw (this would be in effect requesting a timer trigger in the past, and that is not permitted, as it would result in having to re-evaluate a past model evaluation, and could invalidate previous outputs).  If the event is too old, this should be reported to the runtime using the `BlockBase.droppedEvent` action, providing the event and the source timestamp of that event.

If a block cannot obtain a timestamp, or is configured to ignore the timestamps, it should use an absolute timer.  This must be in the future (the timer's value must be `> BlockBase.getModelTime()`).

### Declaring input streams

An input block also needs to declare what event types and fields that identify a series of events (i.e. what fields it is filtering on) it is consuming. This is done by calling `BlockBase.listensForInput`, providing the event type name (fully qualified - i.e. including package name), a set of field names and values it is filtering on, and which partition value it is listening for. This is required so that the runtime can determine whether an input block is receiving output from a different model, in which case the models need to be executed in the correct order.

The `fields` provided to `listensForInput` do not have to reflect exact fields of an event type. For example, when listening to Cumulocity Measurements, a `fragment` and `series` are specified, but these do not correspond to fields of an event type (instead, the values are keys in the measurements dictionary and sub-dictionary).

The `BlockBase.listensForInput` should be called during a call to `$validate` - the runtime needs to validate that any inputs or outputs for a model are legal in the context of other models running.

### Routing inputs to workers and partitions

As models execute in potentially multiple worker threads, each event type should be forwarded to worker contexts appropriately.

For the Cumulocity event types `Alarm`, `Event`, `Measurement` and `Operation`, a monitor included in AnalyticsBuilder, **ForwardCumulocityMeasurements.mon** is responsible for forwarding these to the appropriate worker context. This also identifies source Managed Objects with a property named `pas_broadcastDevice` and will treat these as broadcast devices - the product Cumulocity input blocks will identify managed objects with this property and use the `Partition_Broadcast` partition value for these sources.

For other event types, the `RequestForwarding.byKey` or `RequestForwarding.unpartitioned` actions can be called from the `$preSpawnInit` action to request forwarding of a given type. (Multiple requests for the same type are permitted, but should be consistent on which field the type is partitioned by, or if it is unpartitioned).

## Output blocks

An output block is a block that sends data to an external target. An output block will typically have block *inputs* only (the value to send), but it may have block outputs as well.

Output blocks should construct the event to send, typically using block inputs and parameters.  The event should be `route`d and `send` to the appropriate channel. The event is `route`d so that other models can pick up the same event and process it.

When sending events, these may be sent to an external system that will or will not echo the same event back to the correlator. For example, sending an HTTP request to a remote web service would result in a response, but the correlator would not be sent the request.  However, invoking a web service hosted by the correlator itself or sending to a system such as Cumulocity or a message bus which echoes events back to the correlator would result in the correlator receiving the event again. In these cases, output blocks should make a distinction between the event routed and the one sent (which will be echoed back to the correlator). For Cumulocity Measurements, this is achieved by adding a property identifying the model name to the event sent to Cumulocity, but not the event routed internally. The input block ignores events with this property set - it should have already processed them (and they are likely to be treated as 'late').

An output block also needs to declare what event types and fields it is sending. This is done by calling `BlockBase.sendsOutput`, with the same parameters as an input block would use.

[< Prev: The Value type](090-ValueType.md) | [Contents](000-contents.md) | [Next: Asynchronous validations >](110-AsynchronousValidations.md) 

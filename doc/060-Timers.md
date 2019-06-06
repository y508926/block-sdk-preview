# Timers

Timers should be managed by the Analytics Builder framework.  This allows the runtime to handle:

* Models executing in simulation mode, which run at some offset from real time.
* Multiple timers firing at the same time from different blocks executing a single model 'activation'.

Blocks should not use the `currentTime` variable.

To create a timer, use the `BlockBase` methods `createTimer` and `createTimerWith`.  The `createTimer` takes a relative offset time and a `payload`, the second allows passing `TimerParams` object to give more control.  When the timer fires, it will call a method named `$timerTriggered` on the block.  This can take parameters including:

* `Activation $activation`
* Block `$State` `$blockState`
* `$payload` (of any EPL type - `string`, `float`, event types, `any`, etc)
* `TimerHandle $timerHandle`
* `ConfigPropertyValue $configPropertyValues`

From this `$timerTriggered` it is thus possible to pass call the `$setOutput` actions with the provided `$activation` value.

The `$payload` is the value provided to `createTimer` or added to the `TimerParams`.

## Timer handles

The `createTimerWith` action returns a `TimerHandle` object (and this can also be a parameter to the `$timerTriggered` action).  This allows the timer to be cancelled by calling `$base.cancelTimer(timerHandle)`.  The `TimerHandle` can be stored in the `$State` object if required.

## Timer Parameters

`TimerParams` allows the user to create a timer which is:

* absolute: fires at an absolute point in time (taking into account any offset due to running in simulation mode)
* relative: as per the `createTimer` method
* recurring: a recurring timer will trigger at the interval specified.

`TimerParams` allows adding a payload via the `withPayload` action, and a partition can be specified. (see later topic)

[< Prev: Blocks with state](050-State.md) | [Contents](000-contents.md) | [Next: Partition Values >](070-Partitions.md) 

# Partition Values

All model evaluation must occur in the context of a partition; for a model processing events from multiple devices in a group, this corresponds to each device within the group. For models processing events from a single device, then the model will have a single partition.

A timer may be created from within a `$process` call or a `$timerTriggered` call as part of model evaluation.  In these cases, by default the partition for the timer will be inherited from the executing context. For example, see the **TimeDelay.mon** sample, which just uses the simple `$base.createTimer` method - the partition is implicitly the same as triggered the block's execution.

A timer may also be created from the `$init` action, or a listener set up in the `$init` action.  In this case, there is no partition associated with the execution of the `$init` action, so a partition value should be provided in a `TimerParams` object.

Partition values can be used in timers or when a block declares [input or output](100-InputAndOutput.md). The value can be one of the following:

| Name | Timers | Declaring of input or output | Description |
|------|--------|---------------|-------------|
| `Partition_Default` | N | Y | denotes a default partition.  This is used if the model is not using independent execution for different partitions.  In the Cumulocity input blocks, this is used if they are configured with a normal device. |
| `Partition_Broadcast` | Y | N | the timer will execute for every partition that the model is active for. |
| `Partition_Wildcard` |  N | Y | a block input or output applies to multiple partition values. (e.g. used for input/ outputs configured with device groups). |
| any other type | Y |  Y | an identifier for a distinct partition - e.g. in Cumulocity input blocks configured with a device group, the individual member device id (a string value) is used for the per-device partition.|

[< Prev: Timers](060-Timers.md) | [Contents](000-contents.md) | [Next: Dynamic types >](080-DynamicTypes.md) 

# Blocks with state

While a block can contain fields on the event type that makes the event definition, these fields should not be used to store state that changes as the model executes.  For this 'runtime state', use a separate event type, named `<block>_$State` and this can be supplied as a parameter to the `$process` method of the block.

Separating the state to a different object allows the framework to provide a different `$State` object for each partition that a model may execute, without blocks needing to manage which separate partitions. A model may use multiple partitions if it is being used to process different devices within a device group in Cumulocity. In this case, the framework will maintain a separate `$State` object for each partition, and provide it to blocks when they receive input.

Keeping the runtime state of a block separate from the block implementation also facilitates potential future features of Analytics Builder:

* storing the state so it is not lost if the correlator is stopped.
* moving processing from one correlator to another or from one context to another.
* upgrading from old blocks to newer implementations of the blocks.

The State may contain any fields, but these fields should be serializable. This excludes the EPL types:

* `action<..>`
* `chunk`
* `listener`
* `any` values of the above, or any value that refers to a value of the above types.

This is not currently enforced.

Refer to the **Windowing.mon** sample for an example of a block that uses a parameter value and validates it.

[< Prev: Parameters, block startup and error handling](040-Parameters.md) | [Contents](000-contents.md) | [Next: Timers >](060-Timers.md) 

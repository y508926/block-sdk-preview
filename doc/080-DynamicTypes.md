# Dynamic types

Blocks may use a static type for inputs and outputs; one of:

* string
* boolean
* float

Blocks may also support different types for inputs and outputs. The exact type for outputs should be provided by the block, possibly as a result of parameters or what inputs it has connected to it.  Blocks can support different input types and inspect these. What types of inputs are provided to a block are available from `BlockBase.getInputTypeName` when the `$validate` method is called, and the `$validate` should throw an exception if the input types connected are incorrect.

## Providing output types

Blocks can declare what type an output is in the following ways:

* parameter type of the `$setOutput` action
* a `string constant $OUTPUT_TYPE_<outputId>`
* an action `$outputType_<outputId>() returns string`

At most one of the string constant and action may be present on a block.

The string constant form, or the return value of the `$outputType` action can be one of:

* `boolean`, `string`, `float`
* `pulse`  (to distinguish between boolean and pulse outputs).
* `input(<inputId>)` - the same type as the named input.
* `sameAsAll(<inputId1>, <inputId2>, ...)` - the same type as the named input. If any of the named input types are different, then this is treated as a validation error.
* `pulseOrBoolean(<inputId1>, <inputId2>, ...)` - if all of the named inputs are boolean, then the output type is boolean. If any of the inputs are a pulse type, then the outpyt is a pulse type.

The `$setOutput` parameter type should be compatible with what types the block will generate - for `pulseOrBoolean`, a boolean is sufficient; in other cases, a `Value` or `any` type should be used.

[< Prev: Partition Values](070-Partitions.md) | [Contents](000-contents.md) | [Next: The Value type >](090-ValueType.md) 

# Parameters, block startup and error handling

Blocks may specify a number of parameters that can be provided to customize the behaviour of the block.  Block parameters are shown in the model editor, and are provided to the block when the model starts.

Block parameters can be one of the following types:

* `string`
* `float`
* enumerations of any of the above types (i.e. multiple valid values)
* `boolean`
* `sequence<NameValue>` where NameValue has `string name` and `any value` fields.
* `optional<>` of any of the above types.

Block parameters are represented by a separate event definition, named after the block with a `_$Parameters` suffix, with a field for each parameter, and this is provided as a field of the block named `$parameter`:

```Java
package apamax.sampleblock;
using apama.analyticsbuilder.BlockBase;
using apama.analyticsbuilder.Activation;

event Offset_$Parameters {
    float offset;
}

event Offset {
    Offset_$Parameters $parameters;
...
}
```

When a model is started, values for the block parameters will be filled in (if a block parameter is an `optional<>` then it may be left as an empty optional).  If a model has multiple instances of the same block, each block will have separate Parameters.

## Validating parameters

The block may wish to perform some checking of the block's parameters; not all values or combinations of values are necessary valid. The block can do this by implementing a `$validate` action on either the `$Parameters` type or the block itself.  The `$validate` method should check the values of the `$Parameters` and throw an exception if the parameters are invalid.  (A `$validate` method on the block may also check things such as which inputs are connected, or what type they are).

Blocks do not have to check that all required parameters are present or of the correct  type - if a parameter is of a concrete type and not optional, it must be present and of the correct type - the framework will report an error before calling `$validate` for the block.

When throwing an exception, it is recommended to provide the message of the exception as a message property, which is stored in a separate JSON file, which maps message Ids to the text of the message.  The message Id should be `block_msg_<type of the block>_<identifier>`. When using a message property, it is possible to provide values to be substituted into the message - use `{{0}}` (and higher numbers) in the message text.  Use the L10N.getLocalizedException For example,to provide a message indicating a value is out of range which includes the value provided, then provide a $validate method:

```Java
action $validate() {
    if offset < 0.0 or not offset.isFinite() {
        throw L10N.getLocalizedException("block_msg_apamax.sampleblock.Offset_outOfRange", [<any> offset]);
    }
}
```

And provide a message in a JSON file as so:

```JSON
{
    "block_msg_apamax.sampleblock.Offset_outOfRange": "Value {{0}} is out of range (must be zero or a positive finite number)"
}
```

While the block SDK currently only supports English messages, this mechanism will be used in future releases to provide support to translate error messages to other languages.

The block should not typically modify the block parameters.  If the block wishes to generate derived values of the parameters, then add this as fields on the block (without `$` prefixes).

Refer to the **TimeDelay.mon** sample for an example of a block that uses a parameter value and validates it.

## Initialisation actions

After the model has validated all blocks (calling `$validate` methods where present, and checking that the supplied parameters match the required parameters for all blocks, and other checks), then model is ready for execution. After validation but before the first values are processed in the model, the model will call any `$preSpawnInit` and `$init` actions on blocks.  The `$preSpawnInit` action will only be called once, while `$init` may be called on each worker thread.  These methods should never throw an exception - if any checks are required that may fail, they should occur in the `$validate` method.

The `$validate`, `$preSpawnInit` and `$init` methods do not have any required parameters, but they may optionally take:

* `dictionary<string,any> $modelScopeProperties` - contains the model name, mode and mode properties.  (See the `ABConstants` type for reference`)
* `ConfigurationProperty $configPropertyValues` - accessor for global configuration properties.

These should be treated as read-only.

[< Prev: How to build a block into an extension](030-BuildingExtensions.md) | [Contents](000-contents.md) | [Next: Blocks with state >](050-State.md) 

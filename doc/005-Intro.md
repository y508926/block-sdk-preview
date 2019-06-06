# Introduction

This Software Development Kit (SDK) describes how to write blocks for the Apama Analytics Builder. Analytics Builder allows users to create 'models' by combining a number of blocks, providing parameter values for the blocks and wiring the blocks together. Blocks can implement connectivity to receive data from external sources, send data to external sinks, or to perform processing or calculations based on values flowing through the model.

Analytic Models run in the Apama correlator, and are managed by the Analytics Builder framework.  The framework is responsible for checking that the model wiring is valid, the lifetime of the model, and invoking blocks when values flow through a model. Blocks can be tested using the 'pysys' test framework that is included in Apama installations. In order to develop, test and package blocks, you will need a full installation of Apama.

Blocks are implemented in Apama's Event Processing Language (EPL).  This guide assumes a working knowledge of EPL. Refer to the [Apama documentation on developing EPL applications](http://www.apamacommunity.com/documents/10.3.1.1/apama_10.3.1.1_webhelp/apama-webhelp/#page/apama-webhelp%2Fco-DevApaAppInEpl_how_this_book_is_organized.html%23) and [EPL ApamaDoc reference](http://www.apamacommunity.com/documents/10.3.1.1/apama_10.3.1.1_webhelp/ApamaDoc/index.html).

Blocks can range from very simple stateless functions to more complex logic. Blocks can include:

* Parameters - these are values provided when a model is activated. Blocks can validate that the parameters are legal.  Parameters can be optional, of numeric, boolean, string, enumeration or list types.
* State - the framework holds the state and provides it to the block when needed.  The framework can provide different state for different partitions of a model. (For example, within Cumulocity, a model can apply to a device group, and the model will have separate state for each device within the group).
* Inputs and outputs - these allow the block to connect with wires to other blocks within the model.
* Send and receive events - these allow the block to interact with external data sources or sinks, or to other models or even EPL applications.
* Documentation - a block can include in-line 'ApamaDoc' documenting the behaviour of the block, parameters, inputs and outputs. This is visible in the model editor part of the Analytics Builder.

A very minimal block implementation would be:

```Java
package apamax.sampleblock;
using apama.analyticsbuilder.BlockBase;

event Offset {
    BlockBase $base;
    action $process(Activation $activation, float $input_value) {
        $setOutput_output($activation, $input_value + 100.0 );
    }
    action<Activation, float> $setOutput_output;
}
```

This block simply adds 100 to every input value.  Note that the block has a `BlockBase` field named `$base` - this is required for every block.  The `$process` action has parameters for the inputs, and the output is sent by calling the `$setOutput_output` action field. The framework takes care of creating an instance of the block when it is required for a model, configuring the `$base` and `$setOutput_output` fields and calling the `$process` action when the block receives input.

[< Prev: Contents](000-contents.md) | [Contents](000-contents.md) | [Next: Basic blocks >](010-BasicBlocks.md) 

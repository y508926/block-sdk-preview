# How to build a block into an extension

Once a block is written in EPL, it can be packaged into an 'extension'.  Extensions are zip files that can be used to add blocks to the Analytics Builder runtime. Analytics Builder is deployed within Cumulocity, and extensions are stored in the inventory. This SDK provides a command line utility called `analyticsbuilder` which is available in the `bin` directory. This can be used to build an extension or upload an extension to a Cumulocity installation.

The `analyticsbuilder` script is run from the command line, and a two-word command is provided, followed by any arguments required by the command. Commands available are:

* `build extension --output`

Builds an extension, generating a local .zip file. e.g.

```bash
analyticsbuilder build extension --input samples/blocks --output sample-blocks.zip
```

* `build extension --cumulocity_url`

Upload an extension to a Cumulocity instance

```bash
analyticsbuilder build extension --input samples/blocks --cumulocity_url https://demo.cumulocity.com/ --username user --password pass
```

* `build metadata`

Build JSON metadata only

```bash
analyticsbuilder build metadata --input samples/blocks  --output samples.json
```

Note: if you wish to use the samples provided in the `samples` directory as the starting point for your own blocks, it is strongly recommended that you:

* Make a copy of the contents of the samples directory.
* Change the package name (and if appropriate, the block names) of the blocks.

This avoids any confusion as to the functionality and ownership of the blocks. The samples are not productised blocks, and are subject to removal or changes in future releases without notice.

[< Prev: Naming and documenting blocks](020-NamingAndDoc.md) | [Contents](000-contents.md) | [Next: Parameters, block startup and error handling >](040-Parameters.md) 

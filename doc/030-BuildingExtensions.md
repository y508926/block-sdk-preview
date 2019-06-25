# Building a block into an extension

Once a block is written in EPL, it can be packaged into an "extension". Extensions are **.zip** files that can be used to add blocks to the Analytics Builder runtime. Analytics Builder is deployed within Cumulocity IoT, and extensions are stored in the inventory. This SDK provides a command line utility called `analytics_builder` which is available in the **bin** directory. This can be used to build an extension or upload an extension to a Cumulocity IoT installation.

Most of the `analytics_builder` commands use a `--input` argument which specifies the path to a directory. All **.mon** files found under that directory will be included, and a **messages-EN.json** file will be used for the runtime messages. (TODO: review once we have an implementation.)

The `analytics_builder` script is run from the command line. A two-word command is provided, followed by any arguments required by the command. Commands available are:

* `build extension --output <path to zip file>`

  Build an extension, generating a local **.zip** file. For example:

  ```bash
  analytics_builder build extension --input samples/blocks --output sample-blocks.zip
  ```

* `build extension --cumulocity_url <url> --username <user> --password <password>`

  Upload an extension to a Cumulocity IoT instance. If using an IP address in the URL, you should also specify `--tenantId <tenant id>`. For example: (TODO: review once we have an implementation.) 

  ```bash
  analytics_builder build extension --input samples/blocks --cumulocity_url https://demo.cumulocity.com/ --username user --password pass
  ```

* `build metadata --output <json file>`

  Build JSON metadata only. This can be useful for reviewing what is extracted from the block and visible in the model editor. For example:

  ```bash
  analytics_builder build metadata --input samples/blocks  --output samples.json
  ```

See the `analytics_builder --help` output for full details of the options.

**Note:** If you wish to use the samples provided in the **samples** directory as the starting point for your own blocks, it is strongly recommended that you:

* Make a copy of the contents of the **samples** directory.
* Change the package name (and if appropriate, the block names) of the blocks.

This avoids any confusion as to the functionality and ownership of the blocks. The samples are not productized blocks, and are subject to removal or changes in future releases without notice.

[< Prev: Naming and documenting blocks](020-NamingAndDoc.md) | [Contents](000-contents.md) | [Next: Testing blocks >](035-Testing.md) 

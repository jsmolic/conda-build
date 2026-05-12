**********
Building v1 recipe with conda-build
**********

`conda-build` recently added support for building v1 recipes using the Python bindings for rattler-build.

To get started with building v1 recipes, it is enough to invoke `conda-build` in the feedstock's root directory. `conda-build`
should automatically recognize the recipe format and delegate the build to the ne  wly added v1 recipe API.



Channel configuration
......................

Conda-build passes the channel configuration normally to rattler-build that can be configured using all of the traditional 
supported ways.



Package upload
...............

Packages build from v1 recipes can be uploaded in the same way as those built from v0 recipes.
`conda-build` behaves the same with v1 recipes in a way that it will automatically upload packages to 
the desider anaconda.org channel if this option is enabled in `.condarc` or through the `conda-build` CLI.


Authentication with private channels
.....................................


Limitations
............

Limitations of the current v1 recipe implementation are:

- improvements in the UI: current terminal output uses a modified version of rattler-build's SimpleProgressCallback
to pass the level and messages to conda-build's logging system. 
This can be updated in the future to look nicer and be more consistent with rattler-build itself.
- Support for multi-channels is not complete. If set, `conda-build` will currently simply expand the subchannels 
from a multichannel and pass them to `py-rattler-build` without ensuring that they have the same channel priority.
This will be updated once `rattler-build` gains proper support for multi channels.


Migrating recipes
.................

To migrate the recipe from v0 to v1 format, `conda-recipe-manager` tool can be used.

To convert the recipe, simply invoke:

`conda-recipe-manager convert recipe/meta.yaml > recipe/recipe.yaml`

This will save the new recipe in a `recipe.yaml` file.

There are some differences in some aspects between the two recipe formats and special attentioun should be
paid in some cases when converting the recipes.

More details about those differences can be found in the rattler-build docs: https://rattler-build.prefix.dev/dev/converting_from_conda_build/

# qudi-ffpc-modules

---
A collection of qudi measurement modules originally developed for fiber Fabry-Pérot cavities measurements.



## Installation
For installation instructions please refer to the
[iqo-modules installation guide](https://github.com/Ulm-IQO/qudi-iqo-modules/blob/main/docs/installation_guide.md).
Although it is a different sets of modules, the approach is the same (specific installation instructions will be available soon...)

## More information
The best starting point for further researching the qudi documentation is the [readme file](https://github.com/Ulm-IQO/qudi-core) of the qudi-core repo.


> __WARNING:__
> 
> Do __NOT__ put any `__init__.py` files into qudi namespace packages. Doing so will prevent any 
> addon packages to install additional modules into the respective package or any sub-packages.
> 
> You can however create your own non-namespace packages (including `__init__.py`). Just make sure 
> you do not want to install any addons later on in this package or any sub-packages thereof.

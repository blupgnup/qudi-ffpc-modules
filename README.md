# qudi-ffpc-modules

---
A collection of qudi measurement modules originally developed for fiber Fabry-Pérot cavities measurements.



## Installation
*Installation has been tested using python 3.9.13*

Create a virtual environment and install qudi-core via pip

    pip install qudi-core

Clone this repo and move into main folder. Then install repo using pip:

    pip install -e .

Install qudi Ipython kernel with the following command:

    qudi-install-kernel

*If not installed by pip during qudi-core installation (missing requirement ?) install qtconsole*

    pip install qtconsole

Update the config file using *default.cfg* file as a base example and run qudi

    qudi


## More information
The best starting point for further researching the qudi documentation is the [readme file](https://github.com/Ulm-IQO/qudi-core) of the qudi-core repo.


> __WARNING:__
> 
> Do __NOT__ put any `__init__.py` files into qudi namespace packages. Doing so will prevent any 
> addon packages to install additional modules into the respective package or any sub-packages.
> 
> You can however create your own non-namespace packages (including `__init__.py`). Just make sure 
> you do not want to install any addons later on in this package or any sub-packages thereof.

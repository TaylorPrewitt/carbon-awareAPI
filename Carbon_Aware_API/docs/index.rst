.. carbonaware-API documentation master file, created by
   sphinx-quickstart on Fri Oct 22 13:21:59 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CarbonAware-API's documentation!
===========================================

Brief Description
-----------------
This is the documentation page for the `Carbon Aware API`_ project. The goal of this project is to reduce the amount of carbon emissions outputted to the environment as a result of utilizing cloud resources - Primarily GPUs for tasks such as training Machine & Deep Learning models. The API exists as a wrapper on top of the `WattTime API`_. This API will take in the different WattTime endpoints for Carbon Intensity (CI) data and associate them to AZ regions.

.. _Carbon Aware API: https://github.com/TaylorPrewitt/carbon-awareAPI
.. _WattTime API: https://www.watttime.org/

Why CarbonAware API?
--------------------
Azure (AZ) customers have requested their Azure Carbon emissions footprint be available. In response, Microsoft Azure released the "`Azure Sustainability Calculator`_" that uses yearly average emissions data to enable customers to make more informed decisions about their environmental impact. There is an opportunity to make emissions efficiency a key competitve advantage, as well as signifcantly reducing Azure emissions, through targeted Software Development.

.. _Azure Sustainability Calculator: https://azure.microsoft.com/en-us/blog/microsoft-sustainability-calculator-helps-enterprises-analyze-the-carbon-emissions-of-their-it-infrastructure/


.. toctree::
   :maxdepth: 2
   :caption: Content:

   usage.md
   data.md

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

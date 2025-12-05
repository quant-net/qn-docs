Hardware Abstraction Layer
##########################

Hardware Abstraction Layer (HAL)
--------------------------------

The Hardware Abstraction Layer (HAL) provides :doc:`Agent </agent>`
:doc:`Command Interpreters </interpreters>` with access to hardware
drivers for managing real-time hardware operations.

When an RPC command request is received, agent command interpreters
often need to interact with real-time hardware devices to perform tasks
such as local device and link calibration or entanglement generation.

HAL reads the real-time hardware configuration from a configuration file
and dynamically initializes a driver within its object instance. This
instance is then passed to the command interpreter during its
initialization.

Device Configuration
--------------------

Device configurations are specified under the ``[devices]`` section in
the configuration file and require the following parameters:

* ``enabled`` : ``bool`` - Enables or disables the device
* ``type`` : Specifies the device type, which must be one of the
  following classes: ``LightSrc``, ``Filter``, ``LightMeasurement``,
  ``SignalMeasurement``, ``AnalogController``, ``DigitalController``,
  ``ExpFramework``
* ``driver`` : Name of the driver class to be initialized
* Additional items are passed as dictionary parameters to the driver
  constructor when initialized

Example Device Configuration::

    [devices]
    [[exp_framework]]
    enabled = true    
    type = Exp_Framework
    driver = ArtiqClient
    host = ::1
    port = 3251

    [[lightsource]]
    enabled = true
    type = Light_Source
    driver = overlay
    device = /dev/ttyACM0
    baud_rate = 9600
    bsm_ip = 10.0.0.7
    bsm_port = 55180    

    [[epc]]
    enabled = true
    type = Filter
    driver = DummyEPC    

    [[polarimeter]]
    enabled = true
    type = Light_Measurement    
    driver = Thorlabs
    device = /dev/usbtmc0

    [[egp]]
    enabled = true
    type = EGP
    driver = SimEGPDriver
    protocol = EGProtocol

    [[messaging]]
    enabled = true
    type = Messaging
    driver = PassthroughDriver

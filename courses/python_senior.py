# Python Course Definition
COURSE_ID = "senior_python_developer"
COURSE_TITLE = "Senior Python Developer"
COURSE_DESCRIPTION = "Master Python's runtime internals, memory management, and advanced metaprogramming. Architect scalable distributed systems using Clean Architecture, custom asynchronous engines, database performance strategies, high-throughput testing, and enterprise container deployment."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: CPython Internals, Memory Management, and Advanced Magic Methods",
        "theory": """
### CPython Execution Model and the GIL
CPython, the reference implementation of Python, compiled source code into bytecode, which is then executed on a virtual machine. 
- **The Global Interpreter Lock (GIL)**: A mutual exclusion lock that ensures only one thread executes Python bytecode at a time. This lock protects CPython's internal memory from race conditions but prevents multi-threaded Python programs from scaling across multiple CPU cores for CPU-bound tasks.
- **Subinterpreters (PEP 684/703)**: Modern Python environments are moving toward isolating execution states. Subinterpreters run within a single OS process but maintain separate GILs, allowing true parallel execution of Python bytecode across threads.

### Memory Management and Garbage Collection
CPython uses two primary memory management mechanisms:
1. **Reference Counting**: Every object contains an internal counter (`ob_refcnt`) tracking how many active references point to it. When this counter drops to zero, CPython immediately deallocates the object's memory.
2. **Generational Garbage Collection**: Reference counting cannot detect cyclic references (e.g., Object A references Object B, and Object B references Object A). CPython's cycle-detecting garbage collector groups objects into three generations (Gen 0, 1, and 2) based on survival rates, occasionally scanning them to break cycles and free leaked memory.

### Advanced Magic Methods and Object Allocation
You can customize object creation and optimize memory usage using advanced dunder methods:
- **`__new__` vs `__init__`**: `__new__` is the static allocator method that actually creates and returns the new object instance, while `__init__` is the instance initializer. Overriding `__new__` allows you to customize the creation of immutable objects or control instantiation patterns.
- **`__call__`**: Allows class instances to be invoked as functions, which is useful for creating stateful decorators.
- **`__slots__`**: Restricts the dynamic attributes of a class to a predefined list, preventing Python from creating a dynamic `__dict__` for each instance. This significantly reduces memory usage when instantiating millions of objects.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To analyze Python's garbage collection, check reference counts, and inspect bytecode, use these tools:
* `python3 -m dis script.py`  
  Disassembles Python source code, displaying the underlying bytecode instructions.
* `python3 -c "import gc; print(gc.get_threshold())"`  
  Prints the active allocation thresholds for CPython's generational garbage collector.

#### Syntax Reference
The code blocks below outline memory optimizations, object allocation overrides, and byte inspection:

* **Implementing Slots for Memory Optimization:**
  ```python
  class OptimizedNode:
      # Prevents __dict__ generation, locking attributes to 'id' and 'value'
      __slots__ = ("id", "value")

      def __init__(self, node_id: int, value: str):
          self.id = node_id
          self.value = value
  ```
* **Overriding Class Instantiation (__new__):**
  ```python
  class ImmutabilityProxy:
      def __new__(cls, *args, **kwargs):
          # Intercept allocation, execute custom instantiation logic
          instance = super().__new__(cls)
          return instance
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Reference Counting and Generational GC Cycles
* **Situation:** You need to diagnose a memory leak caused by cyclic references and verify that the generational garbage collector can successfully identify and reclaim the leaked memory.
* **Action:** Use the built-in `sys` and `gc` modules to track reference counts and manually trigger garbage collection cycles.
  ```python
  import sys
  import gc

  class Node:
      def __init__(self, name):
          self.name = name
          self.linked_node = None

  # Disable automatic collection to isolate tests
  gc.disable()

  node_a = Node("Alpha")
  node_b = Node("Beta")

  # Create a cyclic reference
  node_a.linked_node = node_b
  node_b.linked_node = node_a

  print("Ref Count Node A:", sys.getrefcount(node_a) - 1) # Accounting for getrefcount reference

  # Delete local pointers; the objects remain in memory due to the cyclic reference
  del node_a
  del node_b

  # Manually run garbage collection to break the cyclic reference and reclaim memory
  unreachable_objects = gc.collect()
  print(f"Garbage collector found and destroyed {unreachable_objects} cyclic leak objects.")
  gc.enable()
  ```

#### Example 2: Memory Optimization utilizing Class __slots__
* **Situation:** Your network application processes millions of real-time point records concurrently, and you need to reduce memory usage to prevent the system from running out of memory.
* **Action:** Define a class using `__slots__` to prevent CPython from creating a dynamic `__dict__` for each instance.
  ```python
  import sys

  class DynamicPoint:
      def __init__(self, x, y):
          self.x = x
          self.y = y

  class SlottedPoint:
      __slots__ = ("x", "y")
      def __init__(self, x, y):
          self.x = x
          self.y = y

  dyn_inst = DynamicPoint(10, 20)
  slot_inst = SlottedPoint(10, 20)

  # Check standard memory footprint sizes
  print("Dynamic Point size (no dict):", sys.getsizeof(dyn_inst))
  print("Dynamic Point inner dict size:", sys.getsizeof(dyn_inst.__dict__))
  print("Slotted Point size:", sys.getsizeof(slot_inst))
  # Slotted instances do not have an internal __dict__ attribute
  print("Has dict attribute:", hasattr(slot_inst, "__dict__"))
  ```

#### Example 3: Custom Object Instantiation utilizing __new__
* **Situation:** You need to build a connection dispatcher that returns pre-allocated, cached connection objects instead of instantiating new connections on every call.
* **Action:** Override the `__new__` method to intercept class creation and return instances from a custom cache.
  ```python
  class ConnectionPool:
      _instances = {}

      def __new__(cls, pool_id):
          # Check if an instance with this pool_id already exists
          if pool_id not in cls._instances:
              print(f"Allocating new connection pool space: {pool_id}")
              # Allocate memory using the parent class's __new__ method
              cls._instances[pool_id] = super().__new__(cls)
          return cls._instances[pool_id]

      def __init__(self, pool_id):
          # Ensure initialization logic only runs when needed
          self.pool_id = pool_id

  pool_1 = ConnectionPool("us-east-1")
  pool_2 = ConnectionPool("us-east-1")

  print("Are both references identical in memory?:", pool_1 is pool_2)
  ```

#### Example 4: Stateful Call Tracker utilizing __call__
* **Situation:** You need to build a decorator class that tracks and limits the number of times a service function is called across your application.
* **Action:** Implement a stateful class that overrides the `__call__` method to intercept function invocations.
  ```python
  class RateLimiter:
      def __init__(self, func, max_calls):
          self.func = func
          self.max_calls = max_calls
          self.calls_count = 0

      def __call__(self, *args, **kwargs):
          self.calls_count += 1
          if self.calls_count > self.max_calls:
              raise PermissionError("Rate limit exceeded for resource!")
          return self.func(*args, **kwargs)

  @RateLimiter, max_calls=2
  def dispatch_invoice(invoice_id):
      return f"Invoice {invoice_id} dispatched."

  # Standard calls
  print(dispatch_invoice(901))
  print(dispatch_invoice(902))

  try:
      # Third call triggers rate limiter exception
      print(dispatch_invoice(903))
  except PermissionError as err:
      print("System caught expected rate limit exception:", err)
  ```

#### Example 5: Correct Implementation of __repr__ and __str__
* **Situation:** You need to create clean, informative logging representations for system-critical components, distinguishing between developer-focused debugging traces and user-friendly logging logs.
* **Action:** Override `__repr__` and `__str__` to provide distinct representations for development and production environments.
  ```python
  class SystemCluster:
      def __init__(self, cluster_id, node_ips):
          self.cluster_id = cluster_id
          self.node_ips = node_ips

      def __str__(self):
          # User-friendly string representation for production logs
          return f"Cluster '{self.cluster_id}' running {len(self.node_ips)} nodes."

      def __repr__(self):
          # Unambiguous developer-focused representation to recreate the object
          return f"SystemCluster(cluster_id='{self.cluster_id}', node_ips={self.node_ips})"

  cluster = SystemCluster("PROD-DB-01", ["10.0.0.1", "10.0.0.2"])
  print("User Log (str):", str(cluster))
  print("Developer Trace (repr):", repr(cluster))
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Cycle Detector and Garbage Collection Trigger
* **Objective:** Write a utility that monitors objects for cyclic reference leaks and manually forces garbage collection cleanup.
* **Tasks:**
  1. Define two classes, `ParentService` and `ChildService`, that reference each other in their constructors to create circular dependencies.
  2. Disable Python's automatic garbage collection using the `gc` module.
  3. Instantiate 1,000 cycles inside a loop, deleting the local references to the objects on each iteration.
  4. Use `gc.collect()` to trigger a manual collection cycle. Log the number of collected cycles, and measure execution performance.

#### Lab 2: Slots Memory Utilization Benchmarker
* **Objective:** Measure and compare memory footprints between slotted classes and dynamic classes.
* **Tasks:**
  1. Define two classes representing user profile records: `DynamicProfile` (no slots) and `SlottedProfile` (with slots).
  2. Instantiate 500,000 instances of each class, storing them in separate lists.
  3. Use tools like `sys.getsizeof` or memory-profiler modules to measure and output the exact memory difference between the two lists.
  4. Demonstrate that slotted classes cannot accept dynamic, unlisted attributes at runtime.

#### Lab 3: Singleton Object Pool via __new__
* **Objective:** Use `__new__` to implement an immutable object pool pattern.
* **Tasks:**
  1. Build a class named `SymmetricKey` that represents a cryptographic key.
  2. Override `__new__` to cache key instances based on their hashing signature.
  3. If a key is instantiated with a signature that already exists in the cache, return the existing key instance from the pool instead of creating a new one.
  4. Verify that instantiating identical keys returns the exact same object in memory.

#### Lab 4: Class-Based Call Tracker using __call__
* **Objective:** Use the descriptor and callable protocols to build a stateful decorator.
* **Tasks:**
  1. Create a class `ExecutionAuditDecorator` that accepts a target function in its constructor.
  2. Implement `__call__` to log the function's name and arguments, execute the function, and increment an internal call counter.
  3. Add a method `retrieve_metrics()` that returns the total execution count for the decorated function.
  4. Apply your decorator to a mock database query function and verify its count logs.

#### Lab 5: Structural Debug Logger via __repr__
* **Objective:** Design consistent debugging representations for nested structures using `__repr__`.
* **Tasks:**
  1. Create three classes representing a physical system: `Sensor`, `Machine`, and `Factory`.
  2. Add references to `Sensor` objects inside the `Machine` class, and references to `Machine` objects inside the `Factory` class.
  3. Implement `__repr__` for each class, ensuring they return unambiguous strings showing their attributes and parent-child relationships (e.g., `Factory(id='F1', machines=[Machine(id='M1', ...)])`).
  4. Print the root `Factory` instance to verify that nested children are represented clearly in logs.
""",
        "insight": """
### Interview Q&A

#### Q1: What triggers CPython's generational garbage collector, and how does it resolve cyclic references?
* **Answer:** CPython's garbage collector is triggered when the number of allocations minus deallocations exceeds a generation's threshold. To resolve cyclic references, the collector temporarily copies reference counts for all tracked objects, ignores external references, and decrements internal reference counts across cyclic references. Any object whose reference count drops to zero during this check is flagged as part of an isolated cycle and is scheduled for deallocation.

#### Q2: How does '__slots__' optimize memory, and what are its trade-offs?
* **Answer:** By default, Python classes store their attributes in a dynamic dictionary (`__dict__`), which has significant memory overhead to allow dynamic attribute additions. Declaring `__slots__` tells Python to allocate a fixed-size array in memory for attributes instead, bypassing the creation of a `__dict__` for each instance. This significantly reduces the memory footprint of classes with many instances, but it prevents you from adding dynamic attributes at runtime and can complicate inheritance.

#### Q3: What is the fundamental difference between the '__new__' and '__init__' methods?
* **Answer:** `__new__` is a static method that acts as the physical allocator, running first to create and return a new instance of the class. `__init__` is an instance method that runs second to initialize the attributes of the newly created instance. Overriding `__new__` allows you to customize the instantiation process itself, such as returning cached instances or custom subclasses.

#### Q4: How does the per-interpreter GIL (subinterpreters) change concurrency in modern Python?
* **Answer:** Traditionally, the GIL limited a Python process to running a single thread at a time, making standard threads ineffective for CPU-bound tasks. The per-interpreter GIL (introduced in PEP 684) allows a single Python process to run multiple subinterpreters, each with its own isolated GIL. This allows threads running inside separate subinterpreters to run in parallel on separate CPU cores, bypassing the process-level GIL overhead of standard multiprocessing.

#### Q5: When should you override '__repr__' versus '__str__'?
* **Answer:** You should override `__str__` to return a clean, user-friendly string representation of an object for display in production logs, reports, and user interfaces. You should override `__repr__` to return an unambiguous, developer-focused string representation (ideally resembling valid Python code) to make debugging and error reporting easier.

### Senior Assessment Focus
Be prepared to trace object allocation lifecycles in memory, write memory-efficient code using slots, explain CPython reference counting and cyclic garbage collection, and use the subinterpreter APIs to optimize parallel code.
"""
    },
    {
        "id": 2,
        "title": "Module 2: Advanced Metaprogramming and Descriptor Protocols",
        "theory": """
### Customizing Class Creation with Metaclasses
In Python, classes themselves are objects. A class's type is `type`, meaning `type` is the default metaclass that builds class objects.
- **Metaclasses**: Classes that inherit from `type` and are used to customize how other classes are created.
- By defining a custom metaclass, you can override its `__new__` or `__init__` methods to intercept class creation. This allows you to inspect, modify, or validate class attributes, register APIs, or enforce styling rules before a class is initialized.

### The Descriptor Protocol
Descriptors allow you to customize how class attributes are accessed, updated, or deleted. Any class that implements one or more of these magic methods is a descriptor:
- **`__get__(self, instance, owner)`**: Intercepts attribute retrieval.
- **`__set__(self, instance, value)`**: Intercepts attribute assignment.
- **`__delete__(self, instance)`**: Intercepts attribute deletion.
Descriptors are categorized by the methods they implement:
- **Data Descriptors**: Implement both `__get__` and `__set__`. They take precedence over instance dictionaries during attribute lookups.
- **Non-Data Descriptors**: Implement only `__get__` (e.g., standard methods). They can be overridden by instance dictionary assignments.

### Dynamic Code Execution and Reflection
Python provides reflection tools to inspect and modify attributes at runtime:
- **`getattr` and `setattr`**: Retrieve and set attributes dynamically using string names.
- **`__getattr__` vs `__getattribute__`**: `__getattribute__` is called first on *every* attribute access, while `__getattr__` is called only as a fallback if the attribute is not found through standard lookup channels.
- Avoid using dynamic execution functions like `eval()` and `exec()` on untrusted input, as they can execute arbitrary, malicious code and present severe security risks.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
No external shell utilities are required to run metaprogramming APIs. Verify and validate runtime code compilation using standard interactive flags:
* `python3 -i meta_script.py`  
  Runs a script and keeps the interactive REPL active to inspect dynamically generated classes and metaclass hierarchies.

#### Syntax Reference
The code blocks below outline custom metaclass definitions and data descriptors:

* **Defining a Metaclass:**
  ```python
  class APIValidationMeta(type):
      def __new__(cls, name, bases, attrs):
          # Intercept class definition
          if "endpoint" not in attrs:
              raise TypeError(f"Class '{name}' must define an 'endpoint' attribute.")
          return super().__new__(cls, name, bases, attrs)
  ```
* **Implementing a Data Descriptor:**
  ```python
  class NonEmptyString:
      def __init__(self, name):
          self.name = name

      def __get__(self, instance, owner):
          return instance.__dict__.get(self.name)

      def __set__(self, instance, value):
          if not isinstance(value, str) or len(value.strip()) == 0:
              raise ValueError("Attribute must be a non-empty string.")
          instance.__dict__[self.name] = value
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Enforcing API Route Compliance with Metaclasses
* **Situation:** You are building an internal web framework. You need to ensure that every subclass of `BaseController` defines an `http_methods` list, raising an error at class definition time (not at runtime) if it is missing.
* **Action:** Create a custom metaclass to validate class attributes during class definition.
  ```python
  class ControllerVerificationMeta(type):
      def __new__(mcs, name, bases, attrs):
          # Skip validation for the abstract base class itself
          if name != "BaseController":
              if "http_methods" not in attrs:
                  raise TypeError(f"Validation failed: Class '{name}' must declare an 'http_methods' list.")
              if not isinstance(attrs["http_methods"], list):
                  raise TypeError(f"Validation failed: 'http_methods' in Class '{name}' must be a list.")
          return super().__new__(mcs, name, bases, attrs)

  class BaseController(metaclass=ControllerVerificationMeta):
      pass

  # This class compiles successfully:
  class AuthController(BaseController):
      http_methods = ["POST", "GET"]

  # This class raises a TypeError during compilation:
  try:
      class InvalidController(BaseController):
          pass
  except TypeError as err:
      print("System blocked compilation of invalid controller:", err)
  ```

#### Example 2: Type Validation Descriptors
* **Situation:** You need to enforce data validation rules across multiple database model attributes without using boilerplate getter and setter methods.
* **Action:** Build a data descriptor to intercept and validate attribute updates.
  ```python
  class PositiveInteger:
      def __set_name__(self, owner, name):
          # Automatically store the attribute name
          self.private_name = f"_{name}"

      def __get__(self, instance, owner):
          if instance is None:
              return self
          return getattr(instance, self.private_name, None)

      def __set__(self, instance, value):
          if not isinstance(value, int) or value <= 0:
              raise ValueError(f"Attribute must be an integer greater than zero.")
          setattr(instance, self.private_name, value)

  class WarehouseItem:
      stock_count = PositiveInteger()
      sku_code = PositiveInteger()

      def __init__(self, stock, sku):
          self.stock_count = stock
          self.sku_code = sku

  item = WarehouseItem(150, 9081)
  try:
      item.stock_count = -5  # Triggers the descriptor's __set__ validation
  except ValueError as err:
      print("Descriptor prevented assignment:", err)
  ```

#### Example 3: Dynamic Plugin Loader using getattr and importlib
* **Situation:** Your application supports dynamic plugins. You need to load plugin modules from a directory and invoke their entry point functions at runtime based on string configurations.
* **Action:** Combine the built-in `importlib` library with the `getattr` function to import and call code dynamically.
  ```python
  import importlib

  def trigger_plugin_action(module_name, function_name, payload):
      try:
          # Dynamically import the module
          module = importlib.import_module(module_name)
          # Retrieve the function attribute from the module using its name
          target_function = getattr(module, function_name)
          return target_function(payload)
      except (ImportError, AttributeError) as err:
          print(f"Failed to execute dynamic plugin '{module_name}': {err}")
          return None

  # Testing with the standard 'math' module as a mock plugin
  output = trigger_plugin_action("math", "sqrt", 144)
  print("Dynamic function result:", output)
  ```

#### Example 4: Auto-Registering Service Metaclass
* **Situation:** You are building a microservices framework and need to automatically register all service classes with a central directory as soon as they are defined.
* **Action:** Create a custom metaclass that registers class references during the class definition step.
  ```python
  service_registry = {}

  class RegisterServiceMeta(type):
      def __init__(cls, name, bases, attrs):
          super().__init__(name, bases, attrs)
          if name != "BaseService":
              service_key = attrs.get("service_key", name.lower())
              service_registry[service_key] = cls
              print(f"Service '{name}' registered under key: '{service_key}'")

  class BaseService(metaclass=RegisterServiceMeta):
      pass

  class UserBillingService(BaseService):
      service_key = "billing"

  class EmailNotificationService(BaseService):
      pass

  print("Active Registry:", list(service_registry.keys()))
  ```

#### Example 5: Custom Property Decorator with Lazy Evaluation
* **Situation:** You need to calculate a complex database metric that is expensive to compute, and you want to cache the result on the instance after the first lookup so it is not re-computed on subsequent accesses.
* **Action:** Implement a custom non-data descriptor that caches computed values in the instance's dictionary.
  ```python
  class LazyProperty:
      def __init__(self, calculation_method):
          self.calculation_method = calculation_method
          self.__doc__ = calculation_method.__doc__

      def __get__(self, instance, owner):
          if instance is None:
              return self
          # Compute the value
          result = self.calculation_method(instance)
          # Cache the result in the instance's dictionary
          instance.__dict__[self.calculation_method.__name__] = result
          print(f"Computed and cached lazy property '{self.calculation_method.__name__}'")
          return result

  class DataLog:
      def __init__(self, raw_points):
          self.raw_points = raw_points

      @LazyProperty
      def total_sum(self):
          return sum(self.raw_points)

  log = DataLog([10, 20, 30, 40])
  print("First Access:")
  print("Sum:", log.total_sum) # Computes and caches the result
  print("Second Access:")
  print("Sum:", log.total_sum) # Returns the cached value directly from __dict__
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: API Schema Enforcing Metaclass
* **Objective:** Create a metaclass that validates and enforces specific class interfaces during class compilation.
* **Tasks:**
  1. Define a metaclass `EnforceSecurityMeta` that inspects class attributes.
  2. The metaclass must ensure that any class using it implements an integer attribute named `security_clearance_level`.
  3. Ensure that the clearance level is within a valid range of 1 to 5.
  4. Write test classes to verify that subclasses with missing or out-of-range clearance levels raise a `TypeError` when the script compiles.

#### Lab 2: Non-Negative Number Validator Descriptor
* **Objective:** Use the descriptor protocol to implement structured parameter validations.
* **Tasks:**
  1. Create a data descriptor class `NonNegativeValue` that stores attribute values in a private class dictionary.
  2. Implement `__get__` and `__set__` to prevent assigning values that are not numbers or are less than zero.
  3. Apply your descriptor to two attributes, `price` and `discount`, on an `Invoice` model class.
  4. Write tests to verify that attempting to assign a negative value to either attribute raises a `ValueError`.

#### Lab 3: Dynamic Configuration Injector
* **Objective:** Use reflection and dynamic module imports to load configuration files at runtime.
* **Tasks:**
  1. Write a script that checks a configuration string (e.g., `ENV_STAGE="development"`).
  2. Use `importlib` to dynamically import a configuration module corresponding to the stage (e.g., `dev_config` or `prod_config`).
  3. Use `getattr` to extract specific settings, such as `DATABASE_URI` and `DEBUG_PORT`, from the imported module.
  4. If an attribute is missing, fallback to a default configuration dictionary.

#### Lab 4: Custom Property Decorator Clone
* **Objective:** Build a simplified, custom implementation of Python's built-in `@property` decorator from scratch.
* **Tasks:**
  1. Design a descriptor class `CustomProperty` that accepts a getter function in its constructor.
  2. Implement `__get__` to call the getter function, passing the target instance as an argument.
  3. Implement a `.setter(self, setter_method)` decorator method that stores the setter function.
  4. Implement `__set__` to call the stored setter function when the attribute is modified.
  5. Apply your custom decorator to a class and verify that its getters and setters are triggered correctly.

#### Lab 5: Auto-Discovery Service Registry Metaclass
* **Objective:** Use metaclasses to build a plug-and-play service registration system.
* **Tasks:**
  1. Create a metaclass `AutoDiscoveryMeta` that tracks class creation.
  2. Implement a global registration dictionary `discovered_services`.
  3. When a class using this metaclass is defined, inspect its parent classes. If it inherits from a base service class, add its reference to the global dictionary.
  4. Demonstrate that adding new service classes automatically updates the registry without needing manual registration calls.
""",
        "insight": """
### Interview Q&A

#### Q1: What is the difference between a data descriptor and a non-data descriptor in Python?
* **Answer:** A data descriptor implements both `__get__` and `__set__` (and optionally `__delete__`). A non-data descriptor implements only `__get__`. During attribute lookup, Python prioritizes data descriptors over the instance's dictionary (`__dict__`), meaning its `__set__` method is always called. However, an instance's dictionary takes precedence over non-data descriptors, meaning assigning a value to the attribute will override the descriptor.

#### Q2: What happens during class creation when a Metaclass is evaluated?
* **Answer:** When Python encounters a class definition with a custom metaclass, it pauses class creation and passes the class name, its parent classes, and its attributes to the metaclass's `__new__` method. The metaclass can inspect, modify, or inject attributes before calling `super().__new__()` to compile and allocate the new class object.

#### Q3: Why are dynamic code execution functions like 'eval()' and 'exec()' restricted in professional systems?
* **Answer:** `eval()` and `exec()` compile and execute arbitrary strings as Python code. If these strings contain unvalidated user input, they can expose the application to Remote Code Execution (RCE) vulnerabilities, allowing attackers to access the file system, execute system commands, or leak sensitive credentials.

#### Q4: How does 'getattr' behave when a property does not exist, and what is the difference between '__getattr__' and '__getattribute__'?
* **Answer:** `__getattribute__` is called first on *every* attribute lookup, regardless of whether the attribute exists on the object. If CPython cannot find the attribute through standard lookups, or if `__getattribute__` raises an `AttributeError`, the lookup falls back to the `__getattr__` method. `getattr(obj, name)` wraps this entire lookup process, returning a fallback default value if an `AttributeError` is raised.

#### Q5: When should you use a metaclass instead of a class decorator?
* **Answer:** You should use a class decorator to modify or wrap a class after it has already been created (e.g., adding helper methods or registering routing rules). You must use a metaclass when you need to intercept and customize the class creation process itself (e.g., validating class attributes before initialization, modifying parent inheritance structures, or enforcing subclass API schemas).

### Senior Assessment Focus
Be prepared to write validation decorators, build data descriptors to intercept attribute operations, explain class creation lifecycles using metaclasses, and use reflection tools like `getattr` securely.
"""
    },
    {
        "id": 3,
        "title": "Module 3: Code Profiling, Asynchronous Scaling, and Performance Extensions",
        "theory": """
### Identifying Performance Bottlenecks with Profilers
Optimizing applications starts with identifying exact bottlenecks using profiling tools:
- **`cProfile`**: A built-in, deterministic profiler that measures the execution count and duration of every function call in your application.
- **`line_profiler`**: A fine-grained profiler that measures the execution duration of each individual line of code within a target function, which is useful for optimizing specific algorithms.
- **`memory_profiler`**: Monitors memory usage line-by-line, helping you spot memory leaks and track large allocations.

### Compiling Performance-Critical Code
When Python's interpreter is too slow for CPU-bound tasks, you can compile performance-critical code using external tools:
- **Cython**: A compiler that compiles Python code into native C extensions, allowing you to add static C type declarations to speed up calculations.
- **PyPy**: An alternative Python interpreter that uses Just-In-Time (JIT) compilation to run code up to 5x faster than standard CPython.
- **Rust/C/C++ Extensions (via PyO3/C-API)**: Compiles performance-heavy modules written in system languages like Rust into binary extensions that can be imported directly into Python.

### Scaling Asynchronous Architecture
For I/O-bound applications, you can scale concurrency using Python's `asyncio` framework:
- **The Event Loop**: Manages and schedules asynchronous tasks. Running synchronous blocking code (like standard database drivers or file operations) inside the event loop blocks the entire process.
- **Executors**: Use `loop.run_in_executor` to run synchronous blocking code on a background thread or process pool without blocking the main event loop.
- **High-Performance Drivers**: Use specialized asynchronous drivers, like `asyncpg` for PostgreSQL, to execute database queries concurrently in a single non-blocking session pool.
- **Task Queues**: Use `asyncio.Queue` to coordinate work between concurrent producer and consumer coroutines.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To profile execution times, check memory footprints, and compile Cython modules, run:
* `python3 -m cProfile -s cumulative script.py`  
  Runs a script under the deterministic profiler, sorting outputs by cumulative execution time.
* `kernprof -l -v script_to_profile.py`  
  Runs line-by-line profiling on functions decorated with `@profile`.
* `python3 -m memory_profiler script.py`  
  Profiles and logs memory consumption line-by-line.

#### Syntax Reference
The code blocks below outline async queues, thread execution, and database pooling:

* **Distributing Work with Asyncio Queues:**
  ```python
  import asyncio

  async def worker(queue: asyncio.Queue):
      while True:
          task_item = await queue.get()
          # Process item...
          queue.task_done()
  ```
* **Offloading Blocking Code to an Executor:**
  ```python
  import asyncio
  from concurrent.futures import ThreadPoolExecutor

  executor = ThreadPoolExecutor(max_workers=5)

  async def run_blocking_task():
      loop = asyncio.get_running_loop()
      # Run blocking synchronous work in background thread pool
      result = await loop.run_in_executor(executor, blocking_function)
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Profiling Code Bottlenecks using cProfile and pstats
* **Situation:** Your application is experiencing unexpected latency, and you need to pinpoint the exact function causing the bottleneck.
* **Action:** Run `cProfile` and use the `pstats` module to analyze and sort function execution metrics.
  ```python
  import cProfile
  import pstats
  import time

  def database_lookup_simulation():
      time.sleep(0.5) # Simulated slow I/O operation

  def math_calculation_simulation(limit):
      return sum(i * i for i in range(limit))

  def execute_application():
      database_lookup_simulation()
      math_calculation_simulation(1_000_000)

  # Profile execution
  profiler = cProfile.Profile()
  profiler.enable()
  execute_application()
  profiler.disable()

  # Output metrics sorted by cumulative execution time
  stats = pstats.Stats(profiler).sort_stats("cumulative")
  stats.print_stats(10)  # Print the top 10 bottlenecks
  ```

#### Example 2: Coordinating Tasks with Asyncio Queues
* **Situation:** You need to build an asynchronous job consumer that processes tasks from a queue using a pool of concurrent workers.
* **Action:** Implement producer-consumer coroutines coordinated by an `asyncio.Queue`.
  ```python
  import asyncio

  async def job_producer(queue: asyncio.Queue, job_count: int):
      for i in range(job_count):
          await queue.put(f"Job_{i}")
          print(f"[PRODUCER] Added Job_{i} to processing queue.")

  async def job_consumer(worker_id: str, queue: asyncio.Queue):
      while True:
          job = await queue.get()
          print(f"[CONSUMER-{worker_id}] Processing: {job}")
          await asyncio.sleep(0.2) # Simulate processing I/O latency
          print(f"[CONSUMER-{worker_id}] Completed: {job}")
          queue.task_done() # Notify queue that the task is finished

  async def main():
      queue = asyncio.Queue()
      # Start 3 concurrent consumers
      consumers = [asyncio.create_task(job_consumer(f"C{i}", queue)) for i in range(3)]

      # Generate jobs
      await job_producer(queue, 5)
      # Wait until all jobs in the queue are completed
      await queue.join()

      # Cancel consumers once queue is drained
      for c in consumers:
          c.cancel()

  asyncio.run(main())
  ```

#### Example 3: Running Blocking Synchronous Code in Executors
* **Situation:** Your asynchronous web API needs to parse a large image using a synchronous image processing library. Running this directly in an async function would block the main thread and freeze the event loop.
* **Action:** Run the blocking function in a background thread pool executor using `loop.run_in_executor`.
  ```python
  import asyncio
  import time
  from concurrent.futures import ThreadPoolExecutor

  def blocking_image_parse(image_name):
      print(f"[THREAD] Processing image '{image_name}' on background thread...")
      time.sleep(1.5) # Simulate heavy blocking CPU/IO operation
      return f"processed_data_for_{image_name}"

  async def async_health_check_ping():
      for i in range(3):
          print("[LOOP] Health check active...")
          await asyncio.sleep(0.5)

  async def main():
      loop = asyncio.get_running_loop()
      # Create a thread pool executor
      with ThreadPoolExecutor(max_workers=2) as executor:
          # Schedule blocking work in the background thread pool
          future_task = loop.run_in_executor(executor, blocking_image_parse, "profile.png")
          
          # The main event loop remains unblocked and can process other tasks
          await asyncio.gather(future_task, async_health_check_ping())
          print("All tasks completed. Result:", future_task.result())

  asyncio.run(main())
  ```

#### Example 4: Asynchronous Database Operations with asyncpg Pools
* **Situation:** Your asynchronous API needs to query PostgreSQL concurrently. Using standard synchronous drivers with threading adds overhead; you need a high-performance, non-blocking connection pool.
* **Action:** Use `asyncpg` to manage a connection pool and execute queries concurrently.
  ```python
  # Mocking asyncpg behavior for demonstrative execution without active databases
  import asyncio

  class MockAsyncpgConnection:
      async def fetch(self, query, *args):
          await asyncio.sleep(0.1) # Non-blocking async sleep
          return [{"user_id": args[0], "status": "active"}]

  class MockAsyncpgPool:
      def acquire(self):
          return MockAsyncpgConnection()

  async def run_query(pool, user_id):
      connection = pool.acquire()
      result = await connection.fetch("SELECT * FROM users WHERE id = $1", user_id)
      print(f"Query returned result for ID {user_id}: {result}")

  async def main():
      pool = MockAsyncpgPool()
      # Run multiple database queries concurrently
      await asyncio.gather(
          run_query(pool, 101),
          run_query(pool, 102),
          run_query(pool, 103)
      )

  asyncio.run(main())
  ```

#### Example 5: Tracking Memory Usage with memory_profiler
* **Situation:** Your data processing script is running out of memory. You need to analyze its memory consumption line-by-line to identify where large allocations are happening.
* **Action:** Use `memory_profiler` to inspect the memory usage of your data processing function.
  ```python
  # Run this example using: python -m memory_profiler script.py
  from memory_profiler import profile

  @profile
  def process_large_dataset():
      # Allocates memory for a list of 1,000,000 integers
      numbers = [i for i in range(1_000_000)]
      
      # Generates a list of filtered squares, allocating more memory
      squares = [x * x for x in numbers if x % 2 == 0]
      
      del numbers  # Deallocate list reference to free memory
      return len(squares)

  if __name__ == "__main__":
      _ = process_large_dataset()
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Application Bottleneck Analysis with Line Profiler
* **Objective:** Profile a slow calculations module line-by-line to identify performance bottlenecks.
* **Tasks:**
  1. Write a script containing three computationally heavy functions.
  2. Decorate the target functions with the `@profile` decorator.
  3. Run `line_profiler` to measure the hits, time, and percentage of execution spent on each line.
  4. Optimize the slowest line (e.g., refactoring list lookups to set lookups) and verify the performance improvement using the profiler.

#### Lab 2: Async Queue-Based Job Distributor
* **Objective:** Build an asynchronous task consumer using queues to coordinate concurrent workers.
* **Tasks:**
  1. Write an async script with a shared `asyncio.Queue` resource.
  2. Implement an async task producer that adds 100 transaction IDs to the queue.
  3. Create 5 concurrent consumer workers that pull jobs from the queue, simulate network requests, and log completions.
  4. Track and log the total processing time.

#### Lab 3: Parallelizing Synchronous File Processors in Asyncio
* **Objective:** Use ThreadPoolExecutors to run blocking file operations concurrently in an async app.
* **Tasks:**
  1. Write a synchronous function that writes large text strings to local files.
  2. Write an async task that schedules 10 file-writing jobs concurrently.
  3. Use `loop.run_in_executor` to offload the synchronous file-writing tasks to a `ThreadPoolExecutor`.
  4. Verify that the async event loop continues to execute and process concurrent health check pings without blocking.

#### Lab 4: Database Pool Stress Test
* **Objective:** Simulate a high-throughput database connection pool under heavy concurrent load.
* **Tasks:**
  1. Write an async script that simulates database querying latency.
  2. Set up a connection pool class that limits active database connections to 10.
  3. Spawn 100 concurrent async coroutines that attempt to acquire connection leases and run mock queries.
  4. Measure how long it takes to process all 100 queries under different pool size constraints.

#### Lab 5: Memory Leak Detector with Memory Profiler
* **Objective:** Identify and fix memory leaks in data pipelines using memory profiling.
* **Tasks:**
  1. Write a script that reads and processes large arrays, creating a memory leak by appending historical objects to a global list.
  2. Run `memory_profiler` to pinpoint the exact line where memory usage increases and is not reclaimed.
  3. Refactor the script to use generators or yield operations instead of global lists.
  4. Re-run the profile check to verify that memory usage remains stable.
""",
        "insight": """
### Interview Q&A

#### Q1: How does 'asyncio' execute tasks concurrently on a single thread, and what happens when you run synchronous blocking code inside an async loop?
* **Answer:** `asyncio` achieves concurrency using cooperative multitasking managed by an event loop. The event loop monitors registered tasks; when a task reaches an `await` statement (representing non-blocking I/O), it yields control back to the loop, which executes other ready tasks. If you run synchronous blocking code (like `time.sleep()` or standard database queries), it blocks the entire thread, preventing the event loop from scheduling other tasks.

#### Q2: Why do asynchronous drivers like 'asyncpg' perform significantly faster than standard thread-wrapped synchronous database drivers?
* **Answer:** Synchronous drivers require a separate thread to handle each concurrent database query, which adds system memory and context-switching overhead under load. Asynchronous drivers like `asyncpg` communicate with the database socket directly using non-blocking TCP connections on a single thread. This eliminates thread management overhead and allows the driver to process thousands of queries concurrently.

#### Q3: What is the difference between deterministic profiling (like 'cProfile') and statistical profiling?
* **Answer:** Deterministic profiling (`cProfile`) monitors every single function call and record exact durations and execution counts. While highly accurate, this adds significant runtime overhead. Statistical profilers periodically sample the program's call stack instead, which has minimal overhead and is safer to run in production, but does not provide exact execution counts.

#### Q4: When is compiling Cython or PyPy execution preferable over writing C/Rust extensions?
* **Answer:** PyPy is best for optimizing pure Python applications with minimal external dependencies, as its Just-In-Time (JIT) compiler speeds up execution without requiring code modifications. Cython is best for optimizing math-heavy math algorithms inside CPython by adding static type declarations to Python code. Writing C/Rust extensions (e.g., via PyO3) is best when you need maximum performance, want to reuse existing system libraries, or need precise memory control.

#### Q5: How does 'asyncio.shield()' protect coroutine execution, and what are its limitations?
* **Answer:** `asyncio.shield(task)` protects a coroutine from being cancelled by its caller. If the caller is cancelled, the shield returns a `CancelledError` to the caller, but allows the underlying task to continue running in the background. However, if the shielded task itself is cancelled directly, or if the main event loop is stopped, the task will still be terminated.

### Senior Assessment Focus
Be prepared to profile application hot spots, resolve memory leaks, use asyncio and ThreadPoolExecutors to scale concurrent workflows, and use async database connection pools under load.
"""
    },
    {
        "id": 4,
        "title": "Module 4: Enterprise System Architecture, Databases, and Caching",
        "theory": """
### Database Optimization Beyond the ORM
Scaling enterprise data architectures requires optimizing database schemas and scaling storage:
- **Advanced Query Tuning**: Analyze database query plans (using `EXPLAIN ANALYZE`) to identify slow joins, sequential scans, and missing indexes.
- **Replication**: Distributes data across multiple database instances, routing writes to a master node and reads to replica nodes.
- **Sharding**: Partitions large databases horizontally, splitting data across separate database engines based on a routing key (e.g., customer country).

### Distributed Caching Topologies
Implementing a distributed caching layer (using Redis or Memcached) reduces database load and latency. Common caching patterns include:
- **Cache-Aside (Lazy Loading)**: The application queries the cache first. If the data is missing (cache miss), it queries the database, writes the result to the cache, and returns it.
- **Write-Through**: The application writes updates to the cache first, and the cache immediately writes the changes to the database before returning.
- **Write-Behind (Write-Back)**: The application writes updates to the cache first, and the cache asynchronously writes the changes to the database in background batches.

### Architectural Patterns
Maintainable, decoupled codebases are built using structured software patterns:
- **Domain-Driven Design (DDD)**: Structures software around domain models and business logic. It uses entities (objects with unique identities), value objects (immutable attributes), and aggregates (groups of related objects).
- **Clean / Hexagonal Architecture (Ports and Adapters)**: Decouples core business logic from external dependencies (such as databases, web frameworks, and third-party APIs) using interfaces (Ports) and concrete implementations (Adapters).
- **Event-Driven Architecture (EDA)**: Uses message brokers (like RabbitMQ, Celery, or Kafka) to distribute tasks asynchronously, improving system scalability and decoupling microservices.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To manage message queues and run background tasks using Celery or Redis, run:
* `redis-cli ping`  
  Pings the local Redis cache to verify connection status.
* `celery -A tasks_module worker --loglevel=info`  
  Launches a Celery worker process to process asynchronous background tasks.

#### Syntax Reference
The code blocks below outline Clean Architecture boundaries and Redis caching patterns:

* **Clean Architecture Interface Boundary (Port):**
  ```python
  from abc import ABC, abstractmethod

  class UserRepositoryPort(ABC):
      @abstractmethod
      def get_by_id(self, user_id: int) -> dict:
          pass
  ```
* **Redis Cache-Aside Pattern Implementation:**
  ```python
  import redis
  import json

  cache = redis.Redis(host='localhost', port=6379, db=0)

  def get_user_data(user_id: int) -> dict:
      cache_key = f"user:{user_id}"
      cached_data = cache.get(cache_key)
      if cached_data:
          return json.loads(cached_data)
      return {} # Handle cache miss...
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: High-Performance Cache-Aside Implementation with Redis
* **Situation:** Your database is struggling under heavy read load for product detail pages. You need to implement a Redis caching layer to reduce read queries.
* **Action:** Implement a cache-aside query function with automated key expiration.
  ```python
  import redis
  import json
  import time

  # Connect to local Redis instance
  cache_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

  def db_query_product_details(product_id):
      time.sleep(0.5) # Simulate expensive database query
      return {"id": product_id, "title": "Premium Widget", "price": 45.00}

  def fetch_product_details(product_id):
      cache_key = f"product:details:{product_id}"
      
      # Step 1: Check the cache
      cached_data = cache_client.get(cache_key)
      if cached_data:
          print("[CACHE] Cache hit! Returning product details.")
          return json.loads(cached_data)
          
      # Step 2: Query the database on cache miss
      print("[CACHE] Cache miss. Querying database...")
      product_details = db_query_product_details(product_id)
      
      # Step 3: Write result back to cache with a 10-minute expiration (TTL)
      cache_client.setex(cache_key, 600, json.dumps(product_details))
      return product_details

  # Run verification
  try:
      _ = fetch_product_details(204) # Database query
      _ = fetch_product_details(204) # Cache hit
  except redis.exceptions.ConnectionError:
      print("Local Redis is down. Ensure service is active to run cache execution.")
  ```

#### Example 2: Designing Clean Architecture Ports and Adapters
* **Situation:** You want to design a core business logic layer that is decoupled from database frameworks, allowing you to swap databases (e.g., from PostgreSQL to MongoDB) without rewriting business logic.
* **Action:** Define an abstract base class (Port) for data access, and implement a concrete subclass (Adapter) to handle database queries.
  ```python
  from abc import ABC, abstractmethod

  # ==========================================
  # PORT LAYER (Core Business Logic Boundary)
  # ==========================================
  class CustomerRepositoryPort(ABC):
      @abstractmethod
      def fetch_balance(self, customer_id: str) -> float:
          pass

  # ==========================================
  # USE CASE LAYER (Pure Business Logic)
  # ==========================================
  class TransferService:
      def __init__(self, repo: CustomerRepositoryPort):
          # Depend on the abstraction (Port), not the concrete implementation (Adapter)
          self.repo = repo

      def is_eligible_for_loan(self, customer_id: str) -> bool:
          balance = self.repo.fetch_balance(customer_id)
          return balance > 10_000.0

  # ==========================================
  # ADAPTER LAYER (Infrastructure Database Implementation)
  # ==========================================
  class PostgreSQLCustomerAdapter(CustomerRepositoryPort):
      def fetch_balance(self, customer_id: str) -> float:
          # Concrete implementation of database queries
          print(f"[SQL DATABASE] Querying customer balance for {customer_id}")
          return 15_000.00

  # Wire dependencies at the application entry point
  db_adapter = PostgreSQLCustomerAdapter()
  loan_checker = TransferService(db_adapter)
  print("Loan Eligibility Status:", loan_checker.is_eligible_for_loan("C-8901"))
  ```

#### Example 3: Celery Event Broker Task Distribution and Retries
* **Situation:** Your payment processing service calls an unstable third-party API. You need to handle these updates asynchronously using background workers, automatically retrying payments with exponential backoff if the API fails.
* **Action:** Define an asynchronous Celery task with exponential backoff retry policies.
  ```python
  # Celery task definition structure
  # To run this, a Celery app instance must be configured
  # from celery_app import app

  class MockCeleryTask:
      def __init__(self, name):
          self.name = name

      def retry(self, exc, countdown, max_retries):
          print(f"[RETRY] Retrying task in {countdown} seconds due to error: {exc}. Retries remaining: {max_retries}")

  # Mocking a Celery task definition
  task_tracker = MockCeleryTask("process_third_party_billing")

  def process_third_party_billing(payment_id, retries=3):
      try:
          print(f"[BILLING] Sending payment '{payment_id}' to billing API...")
          # Simulate payment gateway timeout
          raise RuntimeError("Gateway connection timed out")
      except Exception as exc:
          if retries > 0:
              # Implement exponential backoff retry calculation
              backoff_delay = (2 ** (3 - retries)) * 5
              task_tracker.retry(exc=exc, countdown=backoff_delay, max_retries=retries-1)
          else:
              print("[CRITICAL] Max retries reached. Dispatching alert.")

  process_third_party_billing("PAYMENT_ID_104", retries=3)
  ```

#### Example 4: Simulating Database Sharding at the Routing Layer
* **Situation:** Your user table is growing too large for a single database instance. You need to shard the database, splitting users across distinct database engines based on their user ID.
* **Action:** Implement a database routing engine that selects connection targets based on a sharding key.
  ```python
  class ShardedDatabaseRouter:
      def __init__(self):
          # Simulating connection handles to separate shard engines
          self.shards = {
              "shard_even": "DB_HANDLE_SHARD_EVEN_INSTANCE",
              "shard_odd": "DB_HANDLE_SHARD_ODD_INSTANCE"
          }

      def get_shard_connection(self, user_id):
          # Determine the target database shard based on the user ID
          if user_id % 2 == 0:
              return self.shards["shard_even"]
          else:
              return self.shards["shard_odd"]

  router = ShardedDatabaseRouter()
  print("Routing user 502 to database shard:", router.get_shard_connection(502))
  print("Routing user 503 to database shard:", router.get_shard_connection(503))
  ```

#### Example 5: DDD Value Objects implementing Immutability
* **Situation:** You are building an enterprise domain model and want to implement Money as a DDD Value Object, ensuring it is immutable and cannot be updated with mismatched currencies.
* **Action:** Implement an immutable value object class by overriding `__eq__` and raising exceptions on mutation attempts.
  ```python
  class CurrencyMismatchError(Exception): pass

  class MoneyValueObject:
      __slots__ = ("_amount", "_currency")

      def __init__(self, amount: float, currency: str):
          # Direct variable bindings to simulate immutability
          super().__setattr__("_amount", float(amount))
          super().__setattr__("_currency", currency.upper())

      @property
      def amount(self): return self._amount

      @property
      def currency(self): return self._currency

      def __setattr__(self, name, value):
          raise AttributeError("Value Objects are immutable and cannot be modified.")

      def __add__(self, other):
          if self.currency != other.currency:
              raise CurrencyMismatchError("Cannot add money values with different currencies.")
          return MoneyValueObject(self.amount + other.amount, self.currency)

      def __eq__(self, other):
          return self.amount == other.amount and self.currency == other.currency

  cash_usd = MoneyValueObject(150.00, "USD")
  tip_usd = MoneyValueObject(15.00, "USD")
  print("Total Balance:", (cash_usd + tip_usd).amount, "USD")

  try:
      cash_usd.amount = 200.00 # Attempting to mutate raising an error
  except AttributeError as err:
      print("System caught expected mutation exception:", err)
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Redis Cache-Aside Handler
* **Objective:** Implement the Cache-Aside pattern with TTL expiration and automatic database synchronization.
* **Tasks:**
  1. Set up an SQL connection to an SQLite database containing user profiles.
  2. Implement a class-based Redis cache wrapper.
  3. Write a function `retrieve_profile_by_id(user_id)` that fetches the profile from the cache. On a cache miss, query the database, write the result back to the cache with a 30-second TTL, and return it.
  4. Write an updater function `modify_profile(user_id, updated_data)` that updates the database and immediately invalidates (deletes) the cached key.

#### Lab 2: Hexagonal Architecture API Simulator
* **Objective:** Design an API service that relies on interface ports to remain decoupled from underlying databases.
* **Tasks:**
  1. Write an abstract port `OrderPersistencePort` with abstract methods `save_order()` and `get_order()`.
  2. Write two concrete adapters: `MemoryOrderAdapter` (using dictionaries) and `SQLOrderAdapter` (using SQLite).
  3. Design an application service class `OrderService` that depends solely on the `OrderPersistencePort` interface.
  4. Demonstrate that you can swap from the memory database to the SQL database without modifying the `OrderService` business logic.

#### Lab 3: Celery Tasks with Exponential Retries
* **Objective:** Build robust, fault-tolerant background tasks using Celery retry mechanisms.
* **Tasks:**
  1. Configure a mock asynchronous task queue resembling Celery task execution.
  2. Implement a background execution task `process_transaction(payment_id)`.
  3. Inside the task, write a try-except block that captures connection timeouts to external payment gateways.
  4. Configure the task to retry up to 5 times using exponential backoff (e.g., waiting $2^R$ seconds, where $R$ is the retry count).

#### Lab 4: Multi-Tenant Database Sharder Routing Logic
* **Objective:** Build a multi-tenant routing engine that shards data across distinct database engines.
* **Tasks:**
  1. Initialize three SQLite databases representing distinct geographical database shards: `shard_europe`, `shard_asia`, and `shard_americas`.
  2. Create a router class `GlobalDatabaseRouter` that routes read and write operations based on a user's location.
  3. Write an active dispatcher routine that parses incoming client queries, routes the connection to the correct geographical database shard, and executes the queries.

#### Lab 5: Event-Driven Message Consumer
* **Objective:** Implement a message consumer class that processes events from Kafka or RabbitMQ brokers.
* **Tasks:**
  1. Build a message consumer class that connects to a messaging queue.
  2. Write a message router that processes incoming event payloads, executing distinct functions based on the event type (e.g., `ORDER_CREATED`, `PAYMENT_RECEIVED`).
  3. Wrap the message consumer in a transaction context. If processing an event fails, ensure the message is returned to the queue (nack) to prevent data loss.
""",
        "insight": """
### Interview Q&A

#### Q1: How does Clean / Hexagonal Architecture isolate core business logic from database and framework dependencies?
* **Answer:** Clean / Hexagonal Architecture separates layers using strict dependency rules and interfaces (Ports). Core business logic is located in the center and defines interfaces (Ports) for external actions (like fetching database records). External infrastructure components (Adapters, such as ORMs or API clients) implement these interfaces. Since dependencies always point inward, you can swap external frameworks or databases without modifying core business logic.

#### Q2: What is the difference between Cache-Aside and Write-Through caching patterns, and what are their respective trade-offs?
* **Answer:** In the Cache-Aside pattern, the application is responsible for reading and writing to both the cache and the database. Cache misses require the application to load data from the database and write it back to the cache. In the Write-Through pattern, the application writes updates directly to the caching layer, and the cache immediately writes the updates to the database before returning. Cache-Aside is highly resilient to cache failures but can result in stale data. Write-Through guarantees data consistency but adds write latency.

#### Q3: How do you implement Database Sharding in Python applications at the routing layer?
* **Answer:** Database Sharding divides a large database into smaller, horizontal partitions (shards) across separate database engines. At the Python application routing layer, you implement a database router that intercepts all database read and write operations. The router evaluates a sharding key (such as User ID or Tenant ID) and routes the request to the correct database shard, ensuring data is distributed consistently.

#### Q4: What is the role of an aggregate root in Domain-Driven Design (DDD), and how is it implemented?
* **Answer:** An aggregate is a cluster of domain objects (entities and value objects) that are treated as a single unit for data changes. The aggregate root is the primary entity within the aggregate that acts as the sole gateway for all external modifications. To modify any nested objects within the aggregate, external services must call methods on the aggregate root itself, ensuring domain invariants and business rules are enforced consistently.

#### Q5: Why are asynchronous message queues (like Celery, RabbitMQ, or Kafka) preferred over direct HTTP calls for communication between microservices?
* **Answer:** Asynchronous message queues decouple services by allowing them to communicate asynchronously. If a receiving service is offline, under heavy load, or experiences transient network errors, the message queue buffers messages until the receiver recovers. This prevents failures in one service from cascading to other services, improves system throughput, and allows services to scale independently.

### Senior Assessment Focus
Be prepared to design Clean Architecture systems, write custom database routing engines to handle sharding and replication, implement distributed caching strategies with Redis, and design decoupled microservices using asynchronous message brokers.
"""
    },
    {
        "id": 5,
        "title": "Module 5: Security, Enterprise Testing, and DevOps Infrastructure",
        "theory": """
### Mitigating OWASP Web Vulnerabilities
Production-ready Python services must mitigate critical OWASP web security vulnerabilities:
- **SQL Injection**: Prevented by using ORM engines or parameterized queries instead of executing raw, format-string SQL statements.
- **Insecure Deserialization**: The standard `pickle` module is insecure. Deserializing untrusted `pickle` payloads can trigger Remote Code Execution (RCE) because the module executes custom instructions (via the `__reduce__` magic method) during reconstruction. Use safe, standard serialization formats like JSON, Protocol Buffers, or Msgpack instead.
- **Secrets Management**: Never commit hardcoded API keys, database credentials, or secret keys to version control. Inject them into your application at runtime using environment variables, or retrieve them dynamically from a secure secrets manager (such as AWS Secrets Manager or HashiCorp Vault).

### Enterprise Testing Pipelines
Testing complex, distributed systems requires a multi-layered testing pipeline:
- **Integration Testing**: Verifies that your core code integrates correctly with database engines, caches, and third-party services.
- **End-to-End (E2E) Testing**: Simulates complete user lifecycles across the entire system, verifying that all APIs, services, and queues work together correctly.
- **Load and Stress Testing**: Verifies how your application behaves under heavy concurrent load. Use performance testing tools like **Locust** to simulate thousands of concurrent user connections and identify system bottlenecks.

### Containerization and Production DevOps
Deploying cloud-native applications requires secure, optimized containerization:
- **Multi-Stage Docker Builds**: Optimizes Docker images by separating the build environment from the runtime environment. You compile dependencies in an initial build stage, copy only the compiled binaries into a minimal final runtime image, and run the container as a non-root user. This reduces container image size and minimizes the security attack surface.
- **CI/CD Pipelines**: Automate tests, linting, security audits, container builds, and deployments to cloud platforms using tools like GitHub Actions or GitLab CI.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To perform security scans, run load tests, and build optimized Docker images, run:
* `bandit -r project_directory/`  
  Scans Python code for security vulnerabilities, such as hardcoded passwords or unsafe `pickle` operations.
* `locust -f locustfile.py --host=https://api.staging.site`  
  Launches the Locust load testing web interface to simulate concurrent traffic.
* `docker build -t app-service:latest .`  
  Compiles and packages the local application directory into a Docker image.

#### Syntax Reference
The code blocks below outline multi-stage Docker builds and Locust test scripts:

* **Production Multi-Stage Dockerfile for Python:**
  ```dockerfile
  # --- Build Stage ---
  FROM python:3.11-slim AS builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir --user -r requirements.txt

  # --- Runtime Stage ---
  FROM python:3.11-slim AS runner
  WORKDIR /app
  # Copy compiled packages from builder stage
  COPY --from=builder /root/.local /root/.local
  COPY . .
  ENV PATH=/root/.local/bin:$PATH
  # Run application as non-root user for security compliance
  USER 1001
  CMD ["python", "server.py"]
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Exploiting and Mitigating a Pickle Vulnerability
* **Situation:** A legacy service uses the `pickle` module to serialize and store user session tokens. You need to demonstrate why this is a critical security vulnerability and refactor the service to use safe JSON serialization.
* **Action:** Write a proof-of-concept showing how `pickle` can be exploited to execute arbitrary code, and then refactor the code to use JSON.
  ```python
  import pickle
  import json
  import os

  # --- VULNERABLE CODE (Demonstrating the exploit risk) ---
  class ExploitPayload:
      def __reduce__(self):
          # __reduce__ tells pickle how to reconstruct the object.
          # Here, we return a command execution function and its arguments.
          # If a server deserializes this payload, it will execute the command.
          return (os.system, ("echo '[SECURITY ALERT] Arbitrary Code Executed!'",))

  vulnerable_payload = pickle.dumps(ExploitPayload())

  # Simulating a server deserializing the untrusted payload:
  print("Deserializing vulnerable pickle payload:")
  pickle.loads(vulnerable_payload)

  # --- SECURED SOLUTION ---
  print("\\nImplementing secure serialization:")
  session_data = {"user_id": 104, "role": "admin", "verified": True}
  
  # Serialize using safe, standard JSON
  secure_payload = json.dumps(session_data)
  print("JSON Serialized Payload:", secure_payload)
  
  # Deserialize back to dictionary
  parsed_session = json.loads(secure_payload)
  print("Decoded Session Data safely:", parsed_session)
  ```

#### Example 2: Load Testing APIs using Locust
* **Situation:** You are deploying an API service and need to run a load test to verify its latency and throughput under heavy concurrent traffic.
* **Action:** Write a Locust load testing script to simulate concurrent user behavior.
  ```python
  # Save this code as locustfile.py and run using the command: locust
  from locust import HttpUser, task, between

  class APIUserPerformanceTest(HttpUser):
      # Simulate a think-time of 1 to 3 seconds between tasks
      wait_time = between(1, 3)

      @task(1)
      def check_health_status(self):
          # Send a GET request to the health check endpoint
          self.client.get("/api/v1/health")

      @task(2)
      def submit_payment_query(self):
          # Send a POST request containing a payment payload
          headers = {"Content-Type": "application/json"}
          payload = {"amount": 250.00, "currency": "USD"}
          self.client.post("/api/v1/payments", json=payload, headers=headers)
  ```

#### Example 3: Secure Secrets Retrieval with IAM Fallback
* **Situation:** Your script needs to connect to an external production database. You need to ensure database credentials are never stored in your source code or committed to version control.
* **Action:** Retrieve database credentials securely using environment variables, falling back to a mock secure secrets manager if they are missing.
  ```python
  import os

  def get_secure_database_uri():
      # Step 1: Attempt to retrieve credentials from environmental variables
      db_uri = os.environ.get("PRODUCTION_DATABASE_URI")
      if db_uri:
          print("Database credentials retrieved successfully from environment variables.")
          return db_uri
          
      # Step 2: Fallback to querying an external secrets manager
      print("Credentials missing from environment. Querying Secrets Manager API...")
      # Mock calling an external service (e.g., AWS Secrets Manager or HashiCorp Vault)
      mock_secrets_store = {"uri": "postgresql://secure_admin:vault_pwd@prod-db:5432/app"}
      return mock_secrets_store["uri"]

  db_connection_uri = get_secure_database_uri()
  ```

#### Example 4: Automated CI/CD Testing Pipeline (GitHub Actions)
* **Situation:** You want to set up an automated CI/CD pipeline that runs your test suite, checks code formatting, and runs security scans every time code is pushed to your repository.
* **Action:** Configure a GitHub Actions workflow file to run these quality checks automatically.
  ```yaml
  # Standard configuration for a GitHub Actions workflow: .github/workflows/ci.yml
  name: Continuous Integration Pipeline

  on:
    push:
      branches: [ main, develop ]
    pull_request:
      branches: [ main ]

  jobs:
    test_and_lint:
      runs-on: ubuntu-latest
      steps:
      - name: Check out repository code
        uses: actions/checkout@v3

      - name: Set up Python runtime env
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff pytest bandit

      - name: Run Ruff Linter check
        run: ruff check .

      - name: Run Bandit Security Audit
        run: bandit -r .

      - name: Execute Pytest test suites
        run: pytest
  ```

#### Example 5: Parameterized Raw SQL Querying
* **Situation:** You are writing raw SQL queries inside your application and need to ensure they are protected against SQL injection attacks.
* **Action:** Write parameterized SQL queries instead of using string formatting or concatenation.
  ```python
  import sqlite3

  connection = sqlite3.connect(":memory:")
  cursor = connection.cursor()
  cursor.execute("CREATE TABLE accounts (username TEXT, password TEXT)")
  cursor.execute("INSERT INTO accounts VALUES ('admin', 'secret_pass')")

  user_input_username = "admin' OR '1'='1" # Simulated SQL injection attempt
  user_input_password = "any_password"

  # SECURE: Always pass inputs as parameters in a tuple, letting the database engine escape them safely
  secure_query = "SELECT * FROM accounts WHERE username = ? AND password = ?"
  cursor.execute(secure_query, (user_input_username, user_input_password))
  result = cursor.fetchall()

  print("Secure query results:", result) # Returns empty list, SQL injection prevented!
  connection.close()
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Deserialization Vulnerability Bypass
* **Objective:** Secure an application by refactoring a vulnerable `pickle` serialization routine to use safe JSON.
* **Tasks:**
  1. Write a script that serializes and deserializes user configuration dictionaries using the `pickle` module.
  2. Implement a proof-of-concept exploit using a custom class with a `__reduce__` method that executes an unauthorized system command when deserialized.
  3. Refactor the script to use safe JSON serialization instead.
  4. Verify that the JSON deserializer parses the configuration safely and rejects any executable exploit payloads.

#### Lab 2: Locust Performance Benchmark Suite
* **Objective:** Write and execute a Locust test suite to benchmark an API's performance under load.
* **Tasks:**
  1. Write a Python API service using a framework like FastAPI or Flask, including a fast endpoint and a slow, database-heavy endpoint.
  2. Write a Locust testing script that defines distinct user flows, targeting the fast endpoint 80% of the time and the slow endpoint 20% of the time.
  3. Start the API service, launch Locust from your terminal, and run a load test simulating 50 concurrent users.
  4. Identify the database-heavy endpoint's response latency bottleneck and record the results.

#### Lab 3: Production-Hardened Multi-Stage Container Build
* **Objective:** Write a multi-stage Dockerfile to compile and run a Python service securely.
* **Tasks:**
  1. Create a Python web app directory containing an entry-point script and a `requirements.txt` file.
  2. Write a multi-stage `Dockerfile`. In the first stage (`builder`), compile dependencies. In the second stage (`runner`), copy the compiled dependencies and run the application as a non-root user.
  3. Build the container image.
  4. Run the container locally and verify that the application runs successfully as a non-root user and has a minimal image size.

#### Lab 4: Static Analysis and Security Linting with Bandit
* **Objective:** Use security linting tools to identify and fix security issues in your code.
* **Tasks:**
  1. Write a Python script containing intentional security vulnerabilities, such as hardcoded API keys, standard `pickle` calls, and unsafe raw SQL string formatting.
  2. Install Bandit in your development environment.
  3. Run `bandit -r .` to scan your project directory and generate a security report.
  4. Refactor your code to fix every security vulnerability flagged in the report, and re-run the scan to verify the code is secure.

#### Lab 5: Automated CI/CD Pipeline Configuration
* **Objective:** Create a GitHub Actions workflow to run testing, linting, and security audits automatically.
* **Tasks:**
  1. Create a local Git repository containing a Python project.
  2. Inside the project directory, create a GitHub Actions workflow directory structure: `.github/workflows/ci.yml`.
  3. Write a workflow script that installs project dependencies, checks code styling using Ruff, runs security audits using Bandit, and executes your test suite using Pytest on every push.
  4. Push your changes to GitHub and verify that the CI pipeline runs and passes successfully.
""",
        "insight": """
### Interview Q&A

#### Q1: Why is the 'pickle' module insecure, and what mechanism allows it to execute remote code during deserialization?
* **Answer:** CPython's `pickle` module is insecure because it is designed to reconstruct arbitrary, complex Python objects from byte streams. If an object implements the `__reduce__` magic method, the pickle engine executes the function and arguments returned by `__reduce__` to reconstruct the object during deserialization. If an attacker injects a malicious payload returning a system-level function (like `os.system`) inside `__reduce__`, the server will execute the arbitrary command as soon as it deserializes the payload, resulting in a Remote Code Execution (RCE) vulnerability.

#### Q2: How do multi-stage Docker builds reduce container image size and optimize production security for Python services?
* **Answer:** Multi-stage Docker builds allow you to use separate container environments for building and running your application. In the first stage (`builder`), you install compilers, build tools, and dependencies, which creates a large intermediate image. In the final stage (`runner`), you copy only the compiled libraries and application source code into a minimal runtime base image (like `python:alpine` or `python:slim`). This significantly reduces the final container image size and removes compiler utilities, minimizing the container's security attack surface.

#### Q3: What metrics should you monitor during a load test with Locust to identify system bottlenecks?
* **Answer:** During a load test, you should monitor several key metrics to identify performance bottlenecks:
  - **Latency (Response Time Percentiles - 95th and 99th)**: Identifies if response times degrade under heavy traffic.
  - **Throughput (Requests Per Second - RPS)**: Measures the maximum volume of concurrent traffic the system can process.
  - **Failures and Error Rates**: Identifies if the system crashes or drops connections under load.
  - **CPU and Memory Utilization**: Measures resource consumption on the host server to spot memory leaks and CPU bottlenecks.

#### Q4: How do you manage secrets securely in cloud-native Python deployments, and why should you avoid '.env' files in production?
* **Answer:** In production, `.env` files present security risks because they can be accidentally committed to version control, exposed via web server misconfigurations, or leaked during server backups. Instead, you should manage secrets securely by injecting them into the environment at runtime using your container orchestration platform (e.g., Kubernetes Secrets) or retrieving them dynamically from a dedicated, secure secrets manager (such as AWS Secrets Manager or HashiCorp Vault) using role-based access controls (IAM).

#### Q5: How does Bandit detect security issues in Python code, and what are its common false positives?
* **Answer:** Bandit parses Python source code into an Abstract Syntax Tree (AST) and runs security checks against the code structure to identify common vulnerabilities (such as hardcoded passwords, unsafe imports, SQL injection risks, and weak cryptography). A common false positive is when Bandit flags standard debugging tools, such as using `assert` statements (which are stripped out during optimized CPython compilation) or referencing raw strings that look like passwords but are actually non-sensitive fallback defaults.

### Senior Assessment Focus
Be prepared to write secure code that is protected against SQL Injection and deserialization vulnerabilities, configure multi-stage Dockerfiles, design automated CI/CD pipelines, and run enterprise-grade load tests with Locust.
"""
    }
]
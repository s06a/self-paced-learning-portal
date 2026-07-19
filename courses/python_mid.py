# Python Course Definition
COURSE_ID = "mid_level_python_developer"
COURSE_TITLE = "Mid-Level Python Developer"
COURSE_DESCRIPTION = "Transition from writing basic scripts to developing clean, modular, and performance-optimized Python applications. Master Pythonic patterns, object-oriented design, database tuning, concurrency, and professional testing methodologies."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Advanced Core Python and Functional Programming",
        "theory": """
### Advanced Pythonic Syntax & Variable Arguments
Writing clean, maintainable Python code requires a shift toward idiomatic patterns. Master the packing and unpacking operators:
- **`*args`**: Dynamically collects excess positional arguments into a single tuple.
- **`**kwargs`**: Collects key-value arguments into a standard dictionary.
Using these patterns allows for robust wrapper functions and decorators.

### Static Analysis and Type Hinting
While Python remains a dynamically typed language, large-scale systems rely on static type checking to prevent bugs. Python’s `typing` module allows you to annotate functions and classes:
- Annotate variables and return values using `Union`, `Optional`, `List`, `Dict`, and `Callable`.
- Perform pre-runtime verification using static type checkers like `mypy` to detect type mismatches and reference errors before they hit production.

### Functional Paradigms
Python supports functional programming features that simplify data transformations:
- **`lambda` functions**: Small, anonymous single-expression blocks.
- **`map()` and `filter()`**: Lazy-evaluation utilities that generate elements only when iterated.
Using comprehensions (list, dict, and set) alongside lazy generator expressions helps construct fast, memory-efficient data pipelines.

### Custom Context Managers
Context managers manage system resources like files, database connections, and network sockets. You can create custom context managers using:
1. **Class-based approach**: Implement the `__enter__` and `__exit__` magic methods.
2. **Function-based approach**: Use the `@contextmanager` decorator from the built-in `contextlib` library along with `yield`.
The exit mechanism guarantees clean-up operations, even if exceptions are raised during execution.

### Metaprogramming with Custom Decorators
Decorators are callables that accept a function (or class) as an argument, modify or log its behavior, and return an updated callable. They use lexical closures to wrap execution paths. Using `functools.wraps` is critical to preserve the target function's metadata, such as its name, docstrings, and signature.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To perform static analysis or execute and debug your advanced python code, run:
* `mypy script.py`  
  Triggers a static analysis check on type annotations.
* `mypy --strict script.py`  
  Enforces strict typing checks, flag errors for any unannotated signatures.

#### Syntax Reference
The code blocks below outline advanced type annotations, custom context managers, and functional patterns:

* **Type Annotation & Mypy Checking:**
  ```python
  from typing import List, Dict, Optional, Union, Callable

  def process_payload(
      raw_data: List[Dict[str, int]], 
      callback: Callable[[int], None]
  ) -> Optional[Union[int, str]]:
      return None
  ```
* **Custom Class-Based Context Manager:**
  ```python
  class LockAcquirer:
      def __init__(self, resource_id: str):
          self.resource_id = resource_id

      def __enter__(self):
          print(f"Acquiring lock for: {self.resource_id}")
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          print(f"Releasing lock for: {self.resource_id}")
          return False  # False propagates raised exceptions
  ```
* **Custom Context Manager with Contextlib:**
  ```python
  from contextlib import contextmanager

  @contextmanager
  def temporary_session():
      print("Init session")
      try:
          yield "ACTIVE_SESSION"
      finally:
          print("Close session")
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Parameter Pass-Through with *args and **kwargs
* **Situation:** You need to build a modular audit wrapper that logs execution metadata before forwarding arguments to a target function.
* **Action:** Capture arbitrary parameters using `*args` and `**kwargs` and unpack them into the target function call.
  ```python
  def log_audit_trail(action_name, *args, **kwargs):
      print(f"[AUDIT LOG] Action: {action_name}")
      if args:
          print(f"[AUDIT LOG] Positional arguments received: {args}")
      if kwargs:
          print(f"[AUDIT LOG] Keyword arguments received: {kwargs}")
          
      # Simulating execution of underlying function...
      print("[AUDIT LOG] Record persisted to security ledger.")

  log_audit_trail("USER_PW_RESET", 1042, ip_address="192.168.0.55", forced=True)
  ```

#### Example 2: Static Analysis Type Hinting with Optional and Union
* **Situation:** You are writing an API client and want to ensure the response handler is strongly typed, making it clear to developers when a query can return empty or multi-type responses.
* **Action:** Apply type annotations using `Union` and `Optional`, then verify the code with `mypy`.
  ```python
  from typing import Union, Dict, Optional

  def fetch_cache_record(key: str) -> Optional[Union[str, Dict[str, str]]]:
      db_sim = {"session_token_1": "active", "user_profile_1": {"role": "admin"}}
      
      if key not in db_sim:
          return None
      return db_sim[key]

  result = fetch_cache_record("user_profile_1")
  print("Fetched Data:", result)
  ```

#### Example 3: Custom Timer Decorator with `@functools.wraps`
* **Situation:** You need to measure and log the execution time of slow database queries without modifying their internal code.
* **Action:** Implement a custom decorator that uses `time.perf_counter()` and `functools.wraps` to preserve the original function's metadata.
  ```python
  import time
  import functools

  def performance_monitor(func):
      @functools.wraps(func)
      def wrapper(*args, **kwargs):
          start_time = time.perf_counter()
          output = func(*args, **kwargs)
          duration = time.perf_counter() - start_time
          print(f"[METRIC] '{func.__name__}' execution duration: {duration:.5f}s")
          return output
      return wrapper

  @performance_monitor
  def compute_heavy_dataset(limit):
      '''Simulates processing of high-density numerical streams.'''
      return sum(i * i for i in range(limit))

  _ = compute_heavy_dataset(5_000_000)
  print("Preserved docstring:", compute_heavy_dataset.__doc__)
  ```

#### Example 4: Database Connection Simulator Context Manager
* **Situation:** You need to simulate database connection pools and guarantee that connection channels are safely released back to the pool, even if a query crashes.
* **Action:** Design a class-based context manager implementing the `__enter__` and `__exit__` magic methods.
  ```python
  class ManagedDbConnection:
      def __init__(self, pool_name):
          self.pool = pool_name
          self.connection = None

      def __enter__(self):
          self.connection = f"Connection_Handle_{self.pool}"
          print(f"[RESOURCE] Opened: {self.connection}")
          return self.connection

      def __exit__(self, exc_type, exc_val, exc_tb):
          print(f"[RESOURCE] Closed: {self.connection}")
          if exc_type is not None:
              print(f"[RESOURCE] Error flagged during session: {exc_val}")
          # Return False to propagate exceptions, or True to suppress them
          return False 

  try:
      with ManagedDbConnection("Replica_Pool") as db_handle:
          print(f"Executing operations on: {db_handle}")
          # Trigger an error during the database operations
          raise ValueError("Query syntax error near line 10")
  except ValueError:
      print("Exception was caught and handled in the outer application scope.")
  ```

#### Example 5: Functional Stream Processing with map, filter, and lambda
* **Situation:** You need to parse a stream of numerical financial transactions, discard negative values (representing failures), apply a processing fee to the remaining values, and return the final list.
* **Action:** Combine lazy-evaluation functional programming methods like `map()`, `filter()`, and `lambda` to transform the stream.
  ```python
  raw_deposits = [500.0, -10.0, 1250.50, 0.0, -450.0, 320.0]

  # Filter out negative values or zero, then apply a 2.5% processing surcharge
  valid_streams = filter(lambda val: val > 0, raw_deposits)
  processed_invoices = map(lambda val: round(val * 1.025, 2), valid_streams)

  # Materialize output
  print("Finalized Transaction Values:", list(processed_invoices))
  # Output: [512.5, 1281.76, 328.0]
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Flexible Logging Decorator
* **Objective:** Build a customizable decorator that logs both inputs and outputs for any target function.
* **Tasks:**
  1. Write a decorator named `log_call_details` that logs the name of the function, its positional arguments, and its keyword arguments before it runs.
  2. Log the value returned by the function after it runs.
  3. Use `functools.wraps` to ensure the target function retains its name and docstrings.
  4. Apply the decorator to a function that calculates compound interest and test its behavior.

#### Lab 2: Safe JSON API Response Type Hint Validator
* **Objective:** Design a statically typed API parser using Python's modern typing features, and verify it with `mypy`.
* **Tasks:**
  1. Define custom type aliases using standard annotations: `UserID = int`, `PayloadDict = Dict[str, Union[str, int]]`.
  2. Write a function `validate_and_parse(payload: PayloadDict) -> Optional[UserID]` that extracts a user ID from a dictionary.
  3. If the dictionary does not contain a valid ID or if the ID is negative, return `None`. Otherwise, return the parsed ID.
  4. Run `mypy` on your script and resolve any static typing issues it flags.

#### Lab 3: System Resource Custom Context Manager
* **Objective:** Write a custom context manager using the `contextlib` module to handle temporary environment changes.
* **Tasks:**
  1. Import the `@contextmanager` decorator from `contextlib`.
  2. Write a function-based context manager named `temporary_working_directory(new_dir)` that saves the current working directory, switches to `new_dir` using `os.chdir`, and switches back to the original directory in its `finally` block.
  3. Apply your context manager to verify that working paths are restored even if the code inside the `with` block crashes.

#### Lab 4: Config Handler using *args and **kwargs
* **Objective:** Build an extensible settings parser using variable-length unpacking.
* **Tasks:**
  1. Define a class `SystemConfig` with a dictionary of default configuration settings: `{"host": "localhost", "port": 8000, "debug": False}`.
  2. Implement an `update_settings(*args, **kwargs)` method.
  3. If positional arguments are passed, raise a custom exception (`ValueError`).
  4. Update the internal settings dictionary using key-value overrides from `**kwargs`, then return the updated dictionary.

#### Lab 5: Large File Data Stream Processor
* **Objective:** Combine generators and functional programming elements to process large files with minimal memory overhead.
* **Tasks:**
  1. Write a generator function `read_logs_lazy(log_file_path)` that yields lines from a log file one-by-line using a context manager.
  2. Write a data pipeline using `filter` and a `lambda` expression to extract lines containing "ERROR".
  3. Write a second pipeline step using `map` and a `lambda` expression to extract the timestamp (the first field in the line).
  4. Materialize and display only the first 5 parsed timestamps to avoid reading the entire file into memory.
""",
        "insight": """
### Interview Q&A

#### Q1: Why is '@functools.wraps' used when writing custom decorators?
* **Answer:** By default, wrapping a function in a decorator replaces its metadata with that of the inner wrapper function. Applying `@functools.wraps(func)` preserves the original function's name (`__name__`), docstring (`__doc__`), annotations, and call signature, preventing errors in debugging tools and reflection APIs.

#### Q2: When should you use generator functions ('yield') over standard lists?
* **Answer:** You should use generator functions when processing large or infinite datasets, as they evaluate elements lazily (one at a time, on demand) and don't load the entire collection into memory. This reduces the application's memory footprint and improves initial load times.

#### Q3: What does 'Optional[T]' signify compared to 'Union[T, None]'?
* **Answer:** In Python's typing system, they are equivalent. `Optional[T]` is shorthand for `Union[T, None]`, indicating that a variable or return value can either be of type `T` or contain the value `None`.

#### Q4: How does '__exit__' handle exceptions, and how can it prevent them from bubbling up?
* **Answer:** The third and fourth positional arguments of the `__exit__(self, exc_type, exc_val, exc_tb)` method receive details about any exception raised inside the `with` block. If `__exit__` returns `True`, Python suppresses the exception and continues normal execution. If it returns `False`, the exception propagates up the stack.

#### Q5: What is the difference between *args and **kwargs in functional signatures versus call-site invocation?
* **Answer:** In a function signature, `*args` packs positional arguments into a tuple, while `**kwargs` packs keyword arguments into a dictionary. At the call-site, using `*` unpacks an iterable into positional arguments, while `**` unpacks a dictionary into keyword arguments.

### Mid-Level Assessment Focus
Be prepared to explain lexical closures and scope rules, write custom decorators that accept parameters, and construct clean, type-hinted functional structures that can be validated with `mypy`.
"""
    },
    {
        "id": 2,
        "title": "Module 2: Object-Oriented Deep Dive & Standard Library Mastery",
        "theory": """
### Abstract Base Classes
Abstract Base Classes (ABCs) act as formal contracts defining the interface requirements for subclasses.
- **`abc` module**: Used to declare abstract classes using `abc.ABC` and the `@abstractmethod` decorator.
- Any subclass that inherits from an ABC must implement all of its abstract methods. Attempting to instantiate a subclass without defining these methods raises a `TypeError` at runtime.

### Polymorphism, Method Overriding, and the MRO
Polymorphism allows subclasses to define distinct implementations for the same interface.
- **Method Overriding**: Subclasses can override methods defined in their parent classes.
- **Method Resolution Order (MRO)**: Python resolves method lookups in multiple inheritance hierarchies using the **C3 Linearization** algorithm.
- **`super()`**: Resolves method lookups according to the class's MRO, preventing duplicate initialization calls across the inheritance tree.

### Advanced Standard Library Modules
Write faster, more reliable code by leveraging advanced modules from the standard library:
1. **`collections`**:
   - `defaultdict`: Automatically initializes keys with a default type when accessed.
   - `Counter`: A dictionary subclass optimized for counting hashable objects.
   - `deque`: A double-ended queue optimized for fast left/right appends and pops ($O(1)$ complexity).
   - `namedtuple`: Creates lightweight, tuple-like objects with named fields.
2. **`itertools`**: Built-in utilities for memory-efficient looping, such as `chain` (merging iterables), `groupby` (grouping sequential keys), and `permutations` (combinatorics).
3. **`functools`**: Tools for modifying or caching callables, such as `lru_cache` (caching function results) and `partial` (fixing argument values).
4. **`logging`**: A structured system for logging application behavior. It is far more robust than `print()` statements and can be configured with distinct handlers, formatters, and severity levels.
5. **`re`**: A built-in engine for compiling and matching regular expressions to parse text.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To capture and inspect runtime logging statements, configure and run your script using these patterns:
* `python3 script_with_logging.py`  
  Runs a script, outputting logged events to standard output or a configured log file based on severity levels.

#### Syntax Reference
The code blocks below outline abstract base classes, cooperative inheritance, and advanced collections usage:

* **Defining Abstract Base Classes (ABCs):**
  ```python
  from abc import ABC, abstractmethod

  class ServiceConnector(ABC):
      @abstractmethod
      def connect(self) -> bool:
          pass
  ```
* **MRO & Multiple Inheritance Cooperative Chain:**
  ```python
  class BaseNode:
      def __init__(self):
          print("BaseNode initialized")

  class ReadNode(BaseNode):
      def __init__(self):
          super().__init__()
          print("ReadNode initialized")
  ```
* **Advanced Collections Instantiation:**
  ```python
  from collections import defaultdict, Counter, deque, namedtuple

  counts = Counter(["error", "info", "error"])  # counts["error"] == 2
  grouped = defaultdict(list)                  # grouped["new_key"].append(1)
  queue = deque([1, 2, 3], maxlen=10)          # fast double-ended queue
  Record = namedtuple("Record", ["id", "type"]) # Record(1, "audit")
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Abstract Base Classes for Payment Processing
* **Situation:** You need to design an extensible payment system where all payment processors are guaranteed to implement identical checkout interfaces.
* **Action:** Define an abstract base class utilizing the `abc` module and override its abstract methods in subclasses.
  ```python
  from abc import ABC, abstractmethod

  class BaseProcessor(ABC):
      @abstractmethod
      def authenticate(self) -> bool:
          '''Authenticate with third-party gateway.'''
          pass

      @abstractmethod
      def execute_charge(self, amount: float) -> str:
          '''Process the charge and return a unique transaction hash ID.'''
          pass

  class StripeProcessor(BaseProcessor):
      def authenticate(self) -> bool:
          print("Connecting to Stripe API...")
          return True

      def execute_charge(self, amount: float) -> str:
          return f"STRIPE_TXN_SUCCESS_{int(amount)}"

  # Attempting to instantiate BaseProcessor raises an error:
  # processor = BaseProcessor()  # TypeError
  client = StripeProcessor()
  client.authenticate()
  print("Charge status:", client.execute_charge(150.0))
  ```

#### Example 2: Method Resolution Order (MRO) & Cooperative Multiple Inheritance
* **Situation:** You are designing a plugin architecture where component mixins must share initializer logic without breaking the call tree.
* **Action:** Implement cooperative classes using the `super()` method and inspect the class's MRO.
  ```python
  class BaseComponent:
      def __init__(self):
          print("BaseComponent logic run")

  class LoggerMixin(BaseComponent):
      def __init__(self):
          super().__init__()
          print("LoggerMixin logic run")

  class MetricsMixin(BaseComponent):
      def __init__(self):
          super().__init__()
          print("MetricsMixin logic run")

  class CustomWorker(LoggerMixin, MetricsMixin):
      def __init__(self):
          super().__init__()
          print("CustomWorker initialized")

  # Instantiate custom worker and view the MRO
  worker = CustomWorker()
  print("MRO Resolution Chain:", [cls.__name__ for cls in CustomWorker.__mro__])
  ```

#### Example 3: Log Ingestion with Regular Expressions and Counter
* **Situation:** You need to parse a raw text file of network events, locate instances of IP addresses and HTTP error codes (400-500), and count the occurrences of each error.
* **Action:** Combine the standard library modules `re` and `collections.Counter` to parse the strings.
  ```python
  import re
  from collections import Counter

  log_records = [
      "192.168.1.1 - GET /index.html 200",
      "10.0.0.5 - POST /api/login 401",
      "192.168.1.1 - GET /assets/logo.png 200",
      "172.16.0.3 - GET /admin 403",
      "10.0.0.5 - POST /api/login 401"
  ]

  # Compile regex pattern to identify HTTP codes and capturing group
  status_code_pattern = re.compile(r"\\s([45]\\d{2})\\b")
  captured_errors = []

  for record in log_records:
      match = status_code_pattern.search(record)
      if match:
          captured_errors.append(match.group(1))

  # Compute metrics using Counter
  error_metrics = Counter(captured_errors)
  print("Aggregated Error Metrics:", dict(error_metrics))
  # Output: {'401': 2, '403': 1}
  ```

#### Example 4: LRU Caching for Optimization with partial
* **Situation:** You have a performance-critical recursive function that computes Fibonacci-based intervals, and you need to optimize it by caching intermediate results.
* **Action:** Apply the `@functools.lru_cache` decorator and use `functools.partial` to pre-configure default mathematical constants.
  ```python
  import functools

  @functools.lru_cache(maxsize=128)
  def compute_complex_fibonacci(n):
      if n < 2:
          return n
      return compute_complex_fibonacci(n - 1) + compute_complex_fibonacci(n - 2)

  # Use functools.partial to create a pre-configured caller for n=30
  fetch_thirty_interval = functools.partial(compute_complex_fibonacci, 30)

  print("Result:", fetch_thirty_interval())
  print("Cache performance metadata:", compute_complex_fibonacci.cache_info())
  ```

#### Example 5: Grouping Structured Records with Itertools and Namedtuple
* **Situation:** You need to group a collection of user access logs by department to generate security metrics.
* **Action:** Define an immutable `namedtuple` structure, sort the list by the grouping key, and apply the `itertools.groupby` function.
  ```python
  import itertools
  from collections import namedtuple

  UserAccess = namedtuple("UserAccess", ["username", "department"])

  logs = [
      UserAccess("alice", "Engineering"),
      UserAccess("bob", "Sales"),
      UserAccess("charlie", "Engineering"),
      UserAccess("david", "Sales"),
      UserAccess("eve", "Engineering")
  ]

  # Sorting is mandatory before running itertools.groupby
  sorted_logs = sorted(logs, key=lambda log: log.department)

  grouped_results = {}
  for dept, group in itertools.groupby(sorted_logs, key=lambda log: log.department):
      grouped_results[dept] = [user.username for user in group]

  print("Grouped Department Profiles:", grouped_results)
  # Output: {'Engineering': ['alice', 'charlie', 'eve'], 'Sales': ['bob', 'david']}
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Abstract File Parser Architecture
* **Objective:** Design an extensible document parsing library using Abstract Base Classes.
* **Tasks:**
  1. Define an abstract base class named `FileParser` using the `abc` module.
  2. Implement an abstract method `parse(self, filepath)` that returns a dictionary of contents, and another abstract method `validate_schema(self, data)`.
  3. Create concrete subclasses `JSONParser` and `CSVParser` that implement both abstract methods.
  4. Write a parser coordinator function that accepts a list of parser objects and filepaths, executes them polymorphically, and returns the aggregated data.

#### Lab 2: Memoized API Cache Simulator
* **Objective:** Build a cached system utility using `functools` and logging.
* **Tasks:**
  1. Set up a logger using Python's `logging` module that writes to both a file and standard output, formatting logs with severity and timestamps.
  2. Create a function `simulate_external_api_call(endpoint_path)` that logs "Sending request to server..." and sleeps for 2 seconds.
  3. Apply `functools.lru_cache` to cache successful responses.
  4. Run the function multiple times with duplicate inputs to verify that cached results are returned instantly without sending redundant server requests.

#### Lab 3: Email Log Regex Extractor & Aggregator
* **Objective:** Parse structured files using regular expressions and advanced collections.
* **Tasks:**
  1. Generate a multi-line mock text representing raw email inbox routing information.
  2. Write a regular expression with capturing groups to extract the sender's username and domain name (e.g., `username@domain.com`).
  3. Loop through the logs, match the pattern, and store the domains in a `collections.defaultdict(int)` or a `collections.Counter`.
  4. Print the top 3 most common domain names and their occurrences.

#### Lab 4: Cooperative Base Class Initializer (MRO/super)
* **Objective:** Resolve initialization conflicts in multiple inheritance hierarchies.
* **Tasks:**
  1. Define a class `BaseService` that implements an `initialize()` method.
  2. Create two subclasses, `DatabaseService` and `CachingService`, that override `initialize()` and call `super().initialize()`.
  3. Create a class `WebApplication` that inherits from both `DatabaseService` and `CachingService` and calls `super().initialize()`.
  4. Instantiate `WebApplication`, trigger the initialization process, and verify that every class's initialization logic is run exactly once in MRO order.

#### Lab 5: Fixed-Size Queue Monitor
* **Objective:** Use `collections.deque` and `itertools` to track sliding windows of application metrics.
* **Tasks:**
  1. Initialize a `collections.deque` with a `maxlen` of 5.
  2. Write a function that processes incoming values (integers representing CPU metrics), appends them to the deque, and uses `itertools.chain` to join them with a fallback default historical list of length 3.
  3. Generate continuous metric inputs.
  4. Print the active sliding window and calculate its average value on each tick.
""",
        "insight": """
### Interview Q&A

#### Q1: How does Python determine Method Resolution Order (MRO) in multiple inheritance, and what is C3 linearization?
* **Answer:** Python resolves method lookups in multiple inheritance hierarchies using the **C3 Linearization** algorithm. This algorithm constructs a deterministic resolution path that respects two main rules: child classes are searched before their parents, and parents are searched in the order they are listed in the inheritance declaration.

#### Q2: What are Abstract Base Classes (ABCs), and how do they differ from normal parent classes?
* **Answer:** ABCs serve as formal interface contracts. Unlike standard parent classes, ABCs define abstract methods that subclasses *must* implement. Trying to instantiate an ABC or a subclass that has unimplemented abstract methods raises a `TypeError` at runtime.

#### Q3: Why should you avoid compiling regular expression patterns ('re.compile()') inside functions or tight loops?
* **Answer:** Compiling a regular expression pattern requires parsing the expression string and building an internal matching state machine. Doing this inside a tight loop or function is highly inefficient because the pattern is re-compiled on every iteration. You should instead compile patterns once at the module level.

#### Q4: What are the performance advantages of 'collections.deque' over a standard list for queue operations?
* **Answer:** A standard list is a contiguous array, meaning inserting or deleting items at the beginning of the list requires shifting all subsequent elements in memory, resulting in $O(N)$ complexity. A `collections.deque` is implemented as a doubly linked list, which allows inserting and deleting elements at both ends in $O(1)$ constant time.

#### Q5: How does 'functools.lru_cache' manage function arguments and outputs in memory?
* **Answer:** The `@functools.lru_cache` decorator wraps a function with a hash map that stores previous inputs as keys and their corresponding return values as values. If the function is called with the same arguments, the decorator bypasses execution and returns the cached result. When the cache hits its `maxsize` limit, the Least Recently Used (LRU) algorithm evicts the oldest items.

### Mid-Level Assessment Focus
Understand how cooperative inheritance uses `super()`, write robust regular expressions with capturing groups, and use standard collections and iterators to optimize resource-intensive tasks.
"""
    },
    {
        "id": 3,
        "title": "Module 3: Relational Database Performance, Migrations & Transactions",
        "theory": """
### Mitigating the N+1 Query Problem
The **N+1 query problem** is a common ORM performance pitfall. It occurs when your application makes one query to fetch parent records, and then makes $N$ separate queries to fetch related child records for each parent. To prevent this, use eager loading techniques:
- **Django ORM**: Use `select_related` (for one-to-one and foreign key relationships via an SQL JOIN) or `prefetch_related` (for many-to-many and reverse relations via separate batch queries).
- **SQLAlchemy**: Use `joinedload` or `subqueryload` to load relationships eagerly in a single database round-trip.

### Database Indexing Strategies
An index is a database structure that speeds up query performance by allowing the engine to locate rows without performing a full table scan.
- Always index columns used frequently in `WHERE` filters, `JOIN` conditions, and `ORDER BY` operations.
- Avoid indexing columns with low cardinality (few unique values) or tables that receive frequent writes, as indexing increases write latency because the database must update the index on every write.

### Schema Migrations
Migrations evolve your database schema as your application requirements change.
- When writing migrations, ensure changes are backwards-compatible (e.g., instead of adding a new non-nullable column without a default, add it as nullable, populate existing rows with default values, and then apply the non-nullable constraint).
- Always dry-run and inspect the underlying SQL executed by tools like Alembic or Django Migrations before applying changes in production.

### Transaction Management and Isolation
A database transaction is a unit of work that must be processed reliably according to ACID rules.
- Run multi-step database writes within an explicit transaction block to ensure that if any step fails, all preceding changes are rolled back.
- Use row-level locking (e.g., `SELECT ... FOR UPDATE` in SQL or `.with_for_update()` in SQLAlchemy) to lock specific database rows during transactions. This prevents race conditions where concurrent processes try to modify the same record at the same time.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To manage, generate, and check migrations using Alembic (SQLAlchemy) or Django, run:
* `alembic revision --autogenerate -m "Add index"`  
  Generates a new database migration script by comparing code models against active schemas.
* `alembic upgrade head`  
  Applies all pending migrations to the database.
* `python manage.py makemigrations`  
  (Django) Generates new schema migration files.
* `python manage.py migrate`  
  (Django) Appies migration modifications to target database.

#### Syntax Reference
The code blocks below show how to optimize queries and use locking in SQLAlchemy:

* **SQLAlchemy Eager Loading (Joined Load):**
  ```python
  from sqlalchemy.orm import joinedload
  
  # Select orders and eagerly load their customer relationships in one SQL JOIN query
  orders = session.query(Order).options(joinedload(Order.customer)).all()
  ```
* **SQLAlchemy Pessimistic Row Locking:**
  ```python
  # Retrieve a user record and apply a write-lock until the transaction is committed
  record = session.query(Account).filter_by(id=1).with_for_update().first()
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Mitigating the N+1 Query Problem in SQLAlchemy
* **Situation:** You need to retrieve a list of book records and display their publishers. If written naively, the ORM queries the database once to load the list of books, and then queries the database again for every single book to load its publisher.
* **Action:** Optimize the query by using SQLAlchemy's `joinedload` function to fetch both the books and their publishers in a single query.
  ```python
  from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import relationship, sessionmaker, joinedload

  Base = declarative_base()

  class Publisher(Base):
      __tablename__ = 'publishers'
      id = Column(Integer, primary_key=True)
      name = Column(String)

  class Book(Base):
      __tablename__ = 'books'
      id = Column(Integer, primary_key=True)
      title = Column(String)
      publisher_id = Column(Integer, ForeignKey('publishers.id'))
      publisher = relationship("Publisher")

  engine = create_engine('sqlite:///:memory:')
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()

  # OPTIMIZED: joinedload instructs SQLAlchemy to perform an SQL JOIN, fetching everything in 1 query
  optimized_books = session.query(Book).options(joinedload(Book.publisher)).all()
  for book in optimized_books:
      # Accessing publishers now relies on pre-fetched data, preventing N+1 queries
      print(f"Book: {book.title} | Publisher: {book.publisher.name if book.publisher else 'None'}")
  ```

#### Example 2: Managing Database Transactions with Context Managers
* **Situation:** Your script must debit one account and credit another. You need to ensure both operations complete successfully, or roll back both operations if either step fails.
* **Action:** Wrap the operations in a database transaction block using a context manager.
  ```python
  from sqlalchemy import create_engine, Column, Integer, String, Float
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import sessionmaker

  Base = declarative_base()

  class Account(Base):
      __tablename__ = 'accounts'
      id = Column(Integer, primary_key=True)
      balance = Column(Float)

  engine = create_engine('sqlite:///:memory:')
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()

  # Create accounts
  session.add_all([Account(id=1, balance=500.0), Account(id=2, balance=100.0)])
  session.commit()

  # Transaction block
  try:
      # Start of transaction context
      sender = session.query(Account).get(1)
      receiver = session.query(Account).get(2)

      # Debit
      sender.balance -= 200.0
      # Credit
      receiver.balance += 200.0

      # Force error to test rollback
      raise RuntimeError("Network timeout during transfer processing")

      session.commit()
  except Exception as err:
      session.rollback()  # Undo changes
      print(f"Transaction aborted and rolled back due to error: {err}")

  # Verify balances are unchanged
  print("Sender Balance:", session.query(Account).get(1).balance) # remains 500.0
  ```

#### Example 3: Simulating Concurrent Updates with Row Locking
* **Situation:** Multiple background worker scripts process the same payment queue. You need to lock row records to prevent multiple workers from processing the same payment simultaneously.
* **Action:** Apply a pessimistic write-lock using `.with_for_update()` in SQLAlchemy.
  ```python
  # This example simulates a worker locking a transaction row
  # 'with_for_update' translates to SELECT ... FOR UPDATE in SQL engines (PostgreSQL, MySQL)
  try:
      with session.begin():
          # Locking row with id=1 for exclusive write access
          payment_task = session.query(Account).filter_by(id=1).with_for_update().first()
          print(f"Exclusively locked account for: {payment_task.id}. Processing...")
          payment_task.balance += 50.0
          # Row remains locked to other processes until session exits this transaction context
  except Exception as e:
      print("Transaction failed:", e)
  ```

#### Example 4: Writing a Backwards-Compatible Alembic Schema Migration
* **Situation:** You need to add a non-nullable integer column named `classification_code` to a pre-existing table that already contains millions of rows.
* **Action:** Write a multi-step, backwards-compatible migration script.
  ```python
  # Mock of an Alembic upgrade script
  def upgrade():
      # Step 1: Add the column as nullable
      # op.add_column('users', sa.Column('classification_code', sa.Integer(), nullable=True))
      print("Step 1: Added column 'classification_code' as nullable.")

      # Step 2: Populate existing rows with default values
      # op.execute("UPDATE users SET classification_code = 1")
      print("Step 2: Populated existing database records with default code values.")

      # Step 3: Modify the column to be non-nullable
      # op.alter_column('users', 'classification_code', nullable=False)
      print("Step 3: Altered column constraints to non-nullable.")
  ```

#### Example 5: Database Indexing Configuration using SQLAlchemy Models
* **Situation:** You need to define database indexes on high-frequency columns, like emails, to optimize read queries while maintaining standard data models.
* **Action:** Declare indexes on specific columns directly inside your SQLAlchemy models.
  ```python
  from sqlalchemy import Index

  class Customer(Base):
      __tablename__ = 'customers'
      id = Column(Integer, primary_key=True)
      email = Column(String, nullable=False, unique=True, index=True) # Direct index
      status = Column(String, nullable=False)

      # Composite index across multiple columns
      __table_args__ = (
          Index('idx_email_status', 'email', 'status'),
      )
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: SQL Join Optimization Profiler
* **Objective:** Detect and fix the N+1 query problem by profile queries using sqlite3 loggers.
* **Tasks:**
  1. Build a local SQLite database containing a `Department` table and an `Employee` table. Populate the database with 50 employee records across 5 departments.
  2. Write a Python script that iterates through all employees and prints their department's name. Record and display the total number of underlying database queries triggered by this loop.
  3. Refactor the query to use an explicit SQL `JOIN` to load both tables in a single query.
  4. Compare the query count and execution time of both approaches.

#### Lab 2: Transaction Error Rollback Handler
* **Objective:** Implement an automated money transfer system that guarantees transaction rollbacks when errors occur.
* **Tasks:**
  1. Define a database table containing account records with balances.
  2. Write a function `execute_transfer(db_session, sender_id, receiver_id, amount)` that processes transfers.
  3. Wrap the transfer operations in a transaction block. If the sender's balance becomes negative, raise a custom `InsufficientFundsError`.
  4. Ensure that if this error is raised, the entire transaction is rolled back and database states are preserved.

#### Lab 3: Row Lock Simulation
* **Objective:** Prevent double-processing race conditions using database row locks.
* **Tasks:**
  1. Create a table called `order_queue` containing orders and processing states (`PENDING`, `PROCESSING`, `COMPLETED`).
  2. Write a function `process_order_task(worker_id, order_id)` that selects a pending order.
  3. Use row-level locking (`with_for_update()`) to lock the order row.
  4. Change the order's state to `PROCESSING`, wait 2 seconds (simulating work), and then commit the transaction to release the lock.
  5. Run multiple threads invoking this task on the same order, and verify that only one thread can modify the row at a time.

#### Lab 4: Backwards-Compatible Migration Plan
* **Objective:** Write a Python script that simulates a multi-step database schema migration.
* **Tasks:**
  1. Set up an SQLite database containing a `user_profiles` table with `id` and `name` columns.
  2. Write a python script that simulates adding a `verified` boolean column to the table.
  3. First, add the column as nullable.
  4. Second, run a query to update all pre-existing rows to `False`.
  5. Finally, alter the column's constraint to make it non-nullable.

#### Lab 5: Database Query Optimization Profiling Task
* **Objective:** Compare query performance before and after adding a database index.
* **Tasks:**
  1. Create a table named `large_dataset` and populate it with 10,000 mock records containing unique random keys.
  2. Write a script that searches for specific records by their key. Measure and record the query execution times.
  3. Apply an index to the search column.
  4. Run the same queries again, and compare the execution times to measure the performance improvement.
""",
        "insight": """
### Interview Q&A

#### Q1: What is the N+1 query problem, and how do prefetching techniques fix it?
* **Answer:** The N+1 query problem is an ORM performance issue where the application makes one initial query to fetch parent records, and then makes $N$ separate queries to fetch related child data for each parent record. Prefetching techniques fix this by using SQL joins to load parent and child records in a single batch query, reducing database round-trips.

#### Q2: What is the difference between 'select_related' and 'prefetch_related' in Django ORM?
* **Answer:** `select_related` works by creating an SQL `JOIN` query to fetch related data on the same database query. It is designed for single-valued relationships (like foreign keys and one-to-one fields). `prefetch_related` runs a second, separate batch query to fetch related objects and merges them in Python memory, which is designed for many-to-many relationships and reverse foreign keys.

#### Q3: Why is adding a 'NOT NULL' constraint to a pre-existing column in a large database table risky, and how do you do it safely?
* **Answer:** If the table already contains rows, adding a `NOT NULL` constraint without a default value will fail because the database doesn't know what values to write to existing rows. To do this safely, you should add the column as nullable, populate existing rows with default values, and then apply the `NOT NULL` constraint.

#### Q4: What is pessimistic row locking, and when should you use it over optimistic locking?
* **Answer:** Pessimistic row locking (such as `SELECT ... FOR UPDATE`) locks specific database rows until the current transaction is committed, preventing other sessions from modifying or reading them. Use pessimistic locking in high-concurrency systems where conflict is highly likely, such as inventory reservation systems or payment gateways.

#### Q5: How do database indexes improve read query performance, and what is their impact on write operations?
* **Answer:** Database indexes organize data in trees (like B-trees) to allow the query engine to find rows in logarithmic time ($O(\log N)$) instead of performing a slow linear scan of the entire table ($O(N)$). However, indexes add overhead to writes because the database must update the index structure every time data is inserted, updated, or deleted.

### Mid-Level Assessment Focus
Understand how to run query profiling tools, identify and resolve N+1 queries, design backwards-compatible migration steps, and manage concurrent writes using transactions and row-level locks.
"""
    },
    {
        "id": 4,
        "title": "Module 4: Testing, Mocking, and Advanced Developer Tooling",
        "theory": """
### Contemporary Testing Frameworks
Automated testing ensures your code behaves as expected and prevents regressions:
- **`pytest`**: The standard testing framework, known for its clean syntax, robust assertion handling, and powerful dependency injection architecture.
- **Fixtures**: Reusable setup and teardown utilities used to prepare resources, database records, or mock endpoints for test suites.

### Isolate Units of Code using Mocking
Mocking isolates the unit of code you are testing from external services (like third-party APIs, physical file systems, or remote databases):
- **`unittest.mock`**: The built-in module used to mock objects and patch functions.
- **`Mock` and `MagicMock`**: Create fake objects that simulate real dependencies, allowing you to define return values and verify which methods were called and with what arguments.
- **Patching**: Dynamically intercepts imports during test execution to swap real functions with mocks.

### Modern Dependency and Package Managers
While `pip` and standard `requirements.txt` files are common, modern Python development uses advanced dependency management tools like **Poetry** or **Pipenv**:
- These tools manage dependencies using a single `pyproject.toml` file.
- They generate a `.lock` file to lock dependencies to their exact sub-versions, ensuring reproducible environments across all local and production systems.

### Code Style Automation
Consistent style across team codebases is maintained using automated linters and formatters:
- **Formatters (`black`)**: Automatically rewrite your code to match official style guidelines, eliminating debates over formatting details.
- **Linters (`flake8`, `ruff`)**: Perform static analysis to detect syntax errors, potential bugs, unused imports, and non-Pythonic patterns.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To manage dependencies, test execution, linting, and formatting, run these commands:
* `pytest`  
  Discovers and runs all test suites matching `test_*.py` patterns in the project path.
* `pytest -v --tb=short`  
  Runs tests in verbose mode, showing concise error stack traces.
* `poetry init`  
  Starts an interactive wizard to configure a poetry-driven `pyproject.toml` environment.
* `poetry install`  
  Installs all project dependencies from the lockfile into an isolated virtual environment.
* `ruff check .`  
  Lints the entire directory, finding syntax errors and dead code.
* `black --check .`  
  Verifies that all Python files in the directory comply with Black style guidelines.

#### Syntax Reference
The code blocks below outline pytest fixtures and mocking patterns:

* **Pytest Fixture and Assertion:**
  ```python
  import pytest

  @pytest.fixture
  def sample_dataset():
      return {"key_a": 100, "key_b": 200}

  def test_value_addition(sample_dataset):
      assert sample_dataset["key_a"] + sample_dataset["key_b"] == 300
  ```
* **Patching an External Target:**
  ```python
  from unittest.mock import patch

  # Patching a target function during test execution
  with patch("module_name.external_api_call") as mock_api:
      mock_api.return_value = {"status": "SUCCESS"}
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Pytest Test Cases and Fixtures
* **Situation:** You need to test a custom data-processing class that computes transaction metrics, ensuring your tests use clean, isolated test data.
* **Action:** Define a pytest fixture to instantiate the test data and verify behaviors using standard assertions.
  ```python
  import pytest

  class TransactionSummary:
      def __init__(self, raw_amounts):
          self.amounts = raw_amounts

      def get_net_total(self):
          return sum(self.amounts)

  # Pytest fixture provides clean, reusable test data
  @pytest.fixture
  def transaction_data():
      return [150.0, -50.0, 300.0, -25.0]

  # Inject the fixture directly into the test function
  def test_net_total_calculation(transaction_data):
      summary = TransactionSummary(transaction_data)
      assert summary.get_net_total() == 375.0
  ```

#### Example 2: Mocking API Calls with patch and MagicMock
* **Situation:** Your script fetches coordinates from an external mapping API. You need to unit test your script without sending actual network requests to the API.
* **Action:** Patch the API request method using `unittest.mock.patch` and mock its return value.
  ```python
  import requests
  from unittest.mock import patch, MagicMock

  def retrieve_location_data(city_name):
      response = requests.get(f"https://api.mapservice.com/geo?q={city_name}")
      return response.json().get("coordinates")

  # Mock requests.get directly inside the test
  @patch("requests.get")
  def test_retrieve_location_data(mock_get):
      # Create a mock response object
      mock_response = MagicMock()
      mock_response.json.return_value = {"coordinates": "40.7128,-74.0060"}
      mock_get.return_value = mock_response

      result = retrieve_location_data("NewYork")
      
      # Assert the response values and ensure requests.get was called
      assert result == "40.7128,-74.0060"
      mock_get.assert_called_once_with("https://api.mapservice.com/geo?q=NewYork")
  ```

#### Example 3: Mocking Side Effects for Exceptions and Dynamic Returns
* **Situation:** You need to test how your system handles external network timeouts or database disconnect exceptions.
* **Action:** Assign mock side effects to simulate exception triggers inside your test suites.
  ```python
  import pytest
  import requests
  from unittest.mock import patch

  def query_secure_endpoint():
      try:
          response = requests.get("https://api.secure_service.com", timeout=2)
          return response.status_code
      except requests.exceptions.Timeout:
          return "TIMEOUT_FALLBACK"

  @patch("requests.get")
  def test_query_secure_endpoint_timeout(mock_get):
      # Set the side_effect to raise an exception when requests.get is called
      mock_get.side_effect = requests.exceptions.Timeout("Server timed out")

      result = query_secure_endpoint()
      
      assert result == "TIMEOUT_FALLBACK"
  ```

#### Example 4: poetry-driven pyproject.toml Configuration
* **Situation:** You need to specify project dependencies, lock library versions, and structure packaging options for deployment.
* **Action:** Define a `pyproject.toml` file to manage dependencies and build tools.
  ```toml
  # Standard representation of a pyproject.toml file
  [tool.poetry]
  name = "payment_analyzer"
  version = "1.2.0"
  description = "A performance-optimized finance analysis toolkit."
  authors = ["Developer Team <dev@company.com>"]

  [tool.poetry.dependencies]
  python = "^3.11"
  requests = "^2.31.0"
  sqlalchemy = "^2.0.25"

  [tool.poetry.group.dev.dependencies]
  pytest = "^8.0.0"
  ruff = "^0.2.0"
  black = "^24.1.0"

  [build-system]
  requires = ["poetry-core>=1.0.0"]
  build-backend = "poetry.core.masonry.api"
  ```

#### Example 5: Automating Quality Check with Ruff and Black Configuration
* **Situation:** You want to configure automated linting and formatting settings to clean up the code inside your project directory.
* **Action:** Configure linter and formatting rules directly in your project settings.
  ```toml
  # Extending the pyproject.toml configuration file to include Ruff settings
  [tool.ruff]
  line-length = 88
  select = ["E", "F", "I"] # Enforce style errors, syntax bugs, and import order
  ignore = ["E501"]        # Ignore line-length exceptions flagged by Ruff

  [tool.black]
  line-length = 88
  target-version = ['py311']
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Testing a Custom Cache Class with Pytest
* **Objective:** Write unit tests using pytest features and setups.
* **Tasks:**
  1. Build a class `TimeBoundCache` with `set(key, value)` and `get(key)` methods.
  2. Implement an eviction policy that removes keys if they expire.
  3. Write a pytest file `test_cache.py` containing a fixture that instantiates an active cache instance.
  4. Write tests to verify that setting and getting keys works as expected, and that keys are properly evicted when they expire.

#### Lab 2: Mocking an External HTTP Payment Client
* **Objective:** Isolate your code from third-party services during testing by mocking HTTP responses.
* **Tasks:**
  1. Create a class `StripeClient` with a method `charge_customer(user_id, amount)`. This method makes a `POST` request to Stripe's payment API and returns the transaction ID.
  2. Write unit tests for your class.
  3. Use `unittest.mock.patch` to mock the HTTP POST request.
  4. Verify that your system handles successful payments, handles payment failures, and never makes actual HTTP requests to Stripe during testing.

#### Lab 3: Dynamic Side-Effect Mocking for File I/O
* **Objective:** Test error-handling routines by mocking file operations to raise errors.
* **Tasks:**
  1. Write a function `import_dataset_file(filepath)` that reads and parses comma-separated data.
  2. Write unit tests to check how the function handles corrupted files or system failures.
  3. Use `mock.patch("builtins.open")` to mock file opening, and set its `side_effect` to raise a `PermissionError` or `IsADirectoryError`.
  4. Verify that the function handles these errors gracefully and logs them instead of crashing.

#### Lab 4: Designing a Package Environment with Poetry
* **Objective:** Manage virtual environments and lock dependencies using Poetry.
* **Tasks:**
  1. Install Poetry globally on your system.
  2. Initialize a new project directory named `poetry_lab` using `poetry new poetry_lab`.
  3. Add the `requests` library to the project's dependencies and `pytest` to its development dependencies using the CLI.
  4. Inspect the generated `pyproject.toml` and `poetry.lock` files to verify that dependency versions are locked.

#### Lab 5: Integrating Pre-commit Style Rules
* **Objective:** Configure Ruff and Black to enforce consistent code style automatically.
* **Tasks:**
  1. Set up a Python directory containing several poorly styled files.
  2. Add Ruff and Black formatting rules to your project's configuration.
  3. Run `ruff check` on the files and fix any syntax errors or issues it flags.
  4. Run `black` to format the files, and verify that all indentation and spacing issues are resolved.
""",
        "insight": """
### Interview Q&A

#### Q1: What are Pytest fixtures, and how do they differ from setUp and tearDown methods in unittest?
* **Answer:** Pytest fixtures are modular, reusable functions used to prepare and clean up resources for tests. Unlike `unittest`'s class-based `setUp` and `tearDown` methods, which run before and after every test inside the class, Pytest fixtures are injected directly into test functions as arguments, can be scoped to distinct levels (e.g., function, class, module, or session), and use `yield` to manage cleanup.

#### Q2: Why is the 'autospec=True' parameter recommended when using the patch decorator?
* **Answer:** By default, mocks mock any attribute or method called on them, even if those attributes or methods do not exist on the real object. Passing `autospec=True` dynamically inspects the real class or function being mocked, ensuring that if you call a method with incorrect parameters or access an invalid attribute, the mock immediately raises a `TypeError`, catching outdated test assumptions.

#### Q3: What is the purpose of the 'poetry.lock' file, and why should it be committed to version control?
* **Answer:** The `poetry.lock` file stores the exact version of every dependency and sub-dependency installed in your environment. Committing the lockfile to version control ensures that every developer on your team and all production servers install the exact same package versions, preventing "works on my machine" bugs.

#### Q4: How do you mock a class attribute versus mocking an entire external module?
* **Answer:** To mock a class attribute or method, patch it by referencing its path in the import namespace: `@patch("app.module.ClassName.method_name")`. To mock an entire external module, patch the imported reference of that module: `@patch("app.module.external_library")`.

#### Q5: What is the difference between a linter (like Ruff) and a code formatter (like Black)?
* **Answer:** A formatter (like Black) automatically re-styles and rewrites your code's physical layout—such as line spacing, trailing commas, and brackets—to match formatting standards. A linter (like Ruff) analyzes your code's AST (Abstract Syntax Tree) to identify programmatic bugs, unused imports, logic errors, and security issues.

### Mid-Level Assessment Focus
Understand how to inject Pytest fixtures, mock external dependencies using mocks and patches, manage project dependencies with Poetry, and automate code style checks using Ruff and Black.
"""
    },
    {
        "id": 5,
        "title": "Module 5: Concurrency Foundations & Pythonic Design Patterns",
        "theory": """
### Understanding Concurrency in Python
Concurrency allows your application to execute multiple tasks concurrently. The best concurrency model depends on whether your tasks are CPU-bound or I/O-bound:
- **CPU-bound tasks**: Calculations or data-processing operations that keep the CPU busy (e.g., matrix multiplication).
- **I/O-bound tasks**: Operations that spend most of their time waiting for external input/output (e.g., fetching data from an API, reading files, or waiting for database queries).

### Concurrency Models and the GIL
Python's concurrency models are governed by the **Global Interpreter Lock (GIL)**:
- **The GIL**: A mutex that prevents multiple threads from executing Python bytecode at the same time, protecting internal thread-safe objects from state conflicts.
- **Multiprocessing**: Spawns separate operating system processes, each with its own Python interpreter and memory space. Since each process has its own GIL, this model bypasses the GIL entirely, making it ideal for CPU-bound tasks.
- **Threading**: Uses multiple execution paths within a single process. Since all threads share the same GIL, only one thread can run Python bytecode at a time, making threading ideal for I/O-bound tasks.
- **Asynchronous Programming (`asyncio`)**: Uses cooperative multitasking where a single thread runs an event loop. Coroutines cooperatively yield control back to the event loop using `async` and `await`, allowing you to run thousands of concurrent I/O-bound tasks on a single thread.

### Pythonic Design Patterns
Design patterns are reusable solutions to common software design problems. Mid-level developers should know these four patterns:
1. **Factory Pattern**: Decouples object creation from application logic. It uses a creator method or factory class to instantiate distinct subclasses based on input parameters.
2. **Singleton Pattern**: Restricts instantiation of a class to a single object, ensuring a global point of access (such as a shared connection pool). This is best implemented using class attributes or metaclasses.
3. **Strategy Pattern**: Encapsulates interchangeable algorithms within distinct classes, allowing the application to select which algorithm to run at runtime.
4. **Adapter Pattern**: Acts as a bridge between incompatible interfaces, allowing classes with different method signatures to work together seamlessly.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To test and profile concurrent processes, run these commands:
* `python3 async_script.py`  
  Runs cooperative event loops utilizing asyncio calls.
* `python3 -m cProfile script.py`  
  Profiles script execution to identify performance bottlenecks and measure thread/process overhead.

#### Syntax Reference
The code blocks below outline async coroutines, thread-safe states, and design patterns:

* **Asyncio Coroutine Definition:**
  ```python
  import asyncio

  async def fetch_api_data(endpoint: str) -> dict:
      # Yield control back to the event loop during network delay
      await asyncio.sleep(1) 
      return {"endpoint": endpoint, "status": "ok"}
  ```
* **Thread-Safe Locked Context:**
  ```python
  import threading

  shared_state_lock = threading.Lock()

  def safe_increment():
      with shared_state_lock:
          # Thread-safe operations on shared variables
          pass
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: I/O-Bound Performance with asyncio.gather
* **Situation:** You need to query three external inventory endpoints. Running this sequentially (one after the other) is slow because the script wastes time waiting for each network response.
* **Action:** Use an asynchronous event loop and `asyncio.gather` to run the queries concurrently.
  ```python
  import asyncio
  import time

  async def download_mock_catalog(api_id, latency):
      print(f"[ASYNC] Querying catalog client: {api_id}")
      await asyncio.sleep(latency)  # Yields control back to the event loop
      print(f"[ASYNC] Received catalog response from: {api_id}")
      return f"dataset_{api_id}"

  async def main():
      start_time = time.perf_counter()
      # Run three tasks concurrently
      results = await asyncio.gather(
          download_mock_catalog("A", 1.5),
          download_mock_catalog("B", 2.0),
          download_mock_catalog("C", 1.0)
      )
      duration = time.perf_counter() - start_time
      print(f"Retrieved data: {results} in {duration:.2f} seconds.")

  # Run the async main loop
  asyncio.run(main())
  ```

#### Example 2: CPU-Bound Execution with multiprocessing.Pool
* **Situation:** You need to perform heavy calculations (like checking prime numbers) on a list of millions of integers. Since this is CPU-bound, using threading is slow due to the GIL.
* **Action:** Distribute the work across multiple CPU cores using `multiprocessing.Pool`.
  ```python
  import time
  from multiprocessing import Pool

  def calculate_heavy_square(n):
      # Heavy CPU operation
      for _ in range(1_000_000):
          pass
      return n * n

  if __name__ == '__main__':
      dataset = [15, 30, 45, 60, 75, 90]
      
      start_time = time.perf_counter()
      # Spawns worker processes, matching process count to CPU cores
      with Pool() as pool:
          results = pool.map(calculate_heavy_square, dataset)
          
      duration = time.perf_counter() - start_time
      print(f"Results: {results} calculated in {duration:.4f} seconds.")
  ```

#### Example 3: Thread-Safe Shared State using threading.Lock
* **Situation:** Multiple threads are updating a shared database connection counter. Without synchronization, threads can overwrite each other's changes, leading to race conditions and inaccurate counts.
* **Action:** Synchronize access to the shared counter using a `threading.Lock`.
  ```python
  import threading
  import time

  shared_counter = 0
  counter_lock = threading.Lock()

  def increment_shared_resources():
      global shared_counter
      for _ in range(100):
          time.sleep(0.001) # Force thread context switching
          # Acquire the lock before modifying shared state
          with counter_lock:
              current_val = shared_counter
              shared_counter = current_val + 1

  # Create and run concurrent threads
  threads = [threading.Thread(target=increment_shared_resources) for _ in range(5)]
  for t in threads:
      t.start()
  for t in threads:
      t.join()

  print("Final secure counter value:", shared_counter) # Guaranteed to be 500
  ```

#### Example 4: Factory Pattern for Multi-Format Exporters
* **Situation:** Your application needs to support exporting files in different formats (such as PDF, CSV, and Markdown), and you want to decide which format to export to at runtime.
* **Action:** Implement a Factory Pattern to decouple document generation from file format creation.
  ```python
  from abc import ABC, abstractmethod

  # Abstract class defines exporter interface
  class DocumentExporter(ABC):
      @abstractmethod
      def export_data(self, dataset) -> str:
          pass

  class PDFExporter(DocumentExporter):
      def export_data(self, dataset):
          return f"Generated custom vector PDF document with data: {dataset}"

  class CSVExporter(DocumentExporter):
      def export_data(self, dataset):
          return f"Formatted flat CSV text with data: {dataset}"

  # Factory class instantiates subclasses dynamically
  class ExporterFactory:
      _exporters = {"pdf": PDFExporter, "csv": CSVExporter}

      @classmethod
      def get_exporter(cls, file_format: str) -> DocumentExporter:
          exporter_cls = cls._exporters.get(file_format.lower())
          if not exporter_cls:
              raise ValueError(f"Unsupported export format: {file_format}")
          return exporter_cls()

  exporter = ExporterFactory.get_exporter("pdf")
  print(exporter.export_data("User Activity Log"))
  ```

#### Example 5: Strategy Pattern for Interchangeable Discount Calculations
* **Situation:** You are building an e-commerce checkout system with dynamic discounts (like flat rate reductions, percentage-based discounts, and seasonal clearance rates) that must change at runtime based on active campaigns.
* **Action:** Implement the Strategy Pattern to encapsulate and swap different discount algorithms.
  ```python
  from abc import ABC, abstractmethod

  # Strategy interface
  class DiscountStrategy(ABC):
      @abstractmethod
      def apply_discount(self, original_price: float) -> float:
          pass

  class PercentageDiscount(DiscountStrategy):
      def __init__(self, percent):
          self.percent = percent

      def apply_discount(self, original_price):
          return original_price * (1.0 - self.percent)

  class FlatRateDiscount(DiscountStrategy):
      def __init__(self, amount):
          self.amount = amount

      def apply_discount(self, original_price):
          return max(0.0, original_price - self.amount)

  # Context class delegates calculations to strategy objects
  class ShoppingCart:
      def __init__(self, price, discount_strategy: DiscountStrategy):
          self.price = price
          self.strategy = discount_strategy

      def get_total(self):
          return self.strategy.apply_discount(self.price)

  # Instantiating cart with specific discount strategy
  flat_cart = ShoppingCart(100.0, FlatRateDiscount(15.00))
  percentage_cart = ShoppingCart(100.0, PercentageDiscount(0.20))

  print("Flat-rate balance:", flat_cart.get_total())       # 85.0
  print("Percentage-discount balance:", percentage_cart.get_total()) # 80.0
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Async Web Scraper Simulator
* **Objective:** Build an asynchronous scraper using `asyncio` to download data from multiple URLs concurrently.
* **Tasks:**
  1. Write an asynchronous function `fetch_page_simulation(url, delay)` that yields control back to the event loop using `asyncio.sleep()`.
  2. Implement a wrapper routine that accepts a list of URLs and dynamic delays.
  3. Use `asyncio.gather` to execute these simulation tasks concurrently.
  4. Measure and print the total execution time to verify that all downloads ran concurrently.

#### Lab 2: Multiprocess Parallel Image Resizer Simulator
* **Objective:** Perform heavy CPU-bound math calculations across multiple CPU cores using `multiprocessing`.
* **Tasks:**
  1. Write a function `simulate_heavy_resizing(image_id)` that performs intense CPU calculations (such as running nested loops up to 5,000,000 counts).
  2. Instantiate a mock list of 10 image IDs.
  3. Map the function to a `multiprocessing.Pool` instance matching your system's core count.
  4. Compare the performance against a standard sequential `for` loop to measure the performance improvement.

#### Lab 3: Thread-Safe Connection Pool (Singleton)
* **Objective:** Implement a thread-safe Singleton pattern to share a database connection pool across multiple threads.
* **Tasks:**
  1. Create a class `DbConnectionPool` that implements the Singleton pattern using a thread-safe custom `__new__` method or a metaclass lock.
  2. Inside the class, initialize a counter tracking active connections.
  3. Instantiate multiple parallel threads that attempt to query and modify the class instance.
  4. Verify that all threads interact with the exact same instance in memory and that state metrics remain accurate.

#### Lab 4: Logging Interface with the Adapter Pattern
* **Objective:** Create a class using the Adapter Pattern to make a legacy logger compatible with a standard logging interface.
* **Tasks:**
  1. Define a third-party class `LegacyXMLService` that logs events using incompatible signatures (e.g., `write_xml_log(msg, urgency="LOW")`).
  2. Define a target interface class `StandardLogger` with a `log_info(message)` method.
  3. Implement an adapter class `XMLLoggerAdapter` that wraps the legacy service and implements the `StandardLogger` interface.
  4. Verify that client applications can use the adapter class as if it were a standard logger.

#### Lab 5: Encapsulating Dynamic Taxes via the Strategy Pattern
* **Objective:** Use the Strategy Pattern to build a tax calculation system that supports interchangeable international tax rules.
* **Tasks:**
  1. Write an abstract class `TaxStrategy` with an abstract method `compute_tax(amount)`.
  2. Create concrete strategy classes `USTax`, `EUTax`, and `NoTax`.
  3. Implement a class `Invoice` that accepts a transaction amount and a `TaxStrategy`.
  4. Write a script to calculate total amounts for the same transaction using different tax strategies, swapping strategies at runtime.
""",
        "insight": """
### Interview Q&A

#### Q1: What is the GIL (Global Interpreter Lock), and how does it affect threading in CPU-bound tasks?
* **Answer:** The GIL is a mutex in the CPython interpreter that prevents multiple threads from executing Python bytecode at the same time. While this protects internal objects from race conditions, it means CPU-bound multi-threaded programs cannot run in parallel on multi-core systems. For CPU-bound tasks, you should use multiprocessing instead of threading.

#### Q2: When should you use 'asyncio' over standard 'threading' for I/O-bound tasks?
* **Answer:** You should use `asyncio` for high-concurrency systems (like web servers) that handle thousands of long-lived, slow, or concurrent connections. `asyncio` runs on a single thread and has very little resource overhead. For simpler I/O-bound tasks with fewer concurrent processes, or when using third-party libraries that do not support async calls, standard `threading` is often easier to implement.

#### Q3: Why is implementing the Singleton pattern using a class attribute or a metaclass preferable over overriding '__new__'?
* **Answer:** Overriding `__new__` to implement a Singleton still triggers the `__init__` constructor on every instantiation call, which can re-initialize and overwrite the class's state. Implementing the Singleton pattern using a metaclass or class-level lock guarantees that the instance is created and initialized exactly once, preventing state overrides.

#### Q4: What is the difference between an Asynchronous coroutine and a standard Python function?
* **Answer:** A standard function runs from start to finish without pausing and blocks the main thread. An asynchronous coroutine (declared with `async def`) is a specialized object that can suspend its execution using `await`. This allows the event loop to run other concurrent tasks on the same thread while waiting for I/O operations to complete.

#### Q5: How does the Strategy pattern differ from inheritance when implementing variations in object behavior?
* **Answer:** Inheritance relies on a static, compile-time relationship where subclasses extend a parent class's behavior. The Strategy pattern uses composition to encapsulate interchangeable algorithms in separate helper classes. This allows the application to swap behaviors at runtime by passing different strategy objects to the main class, making the system more modular and decoupled.

### Mid-Level Assessment Focus
Understand when to use threading, multiprocessing, or asyncio based on resource bottlenecks, how to write thread-safe code, and how to apply design patterns (like Factory and Strategy) to keep your code modular and reusable.
"""
    }
]
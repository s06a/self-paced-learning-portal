# Python Course Definition
COURSE_ID = "junior_python_developer"
COURSE_TITLE = "Junior Python Developer"
COURSE_DESCRIPTION = "Master Python basic syntax, data structures, control flow, object-oriented concepts, basic database usage, and foundational web API integration."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Core Python Syntax, Control Flow, and Built-in Data Structures",
        "theory": """
### Dynamic Typing and Variable Binding
Python is a dynamically typed, garbage-collected language. In Python, variables are references to objects stored in memory rather than statically declared, labeled storage containers. Typing is resolved and checked at runtime. This means a single variable identifier can reference different object types during its lifecycle without requiring explicit casting.

### Control Flow Mechanics
Conditional statements (`if`, `elif`, `else`) evaluate expressions for boolean truthiness. Loops allow repetitive task execution:
- **`for` loops:** Ideal for iterating over a fixed sequence or iterable (like a list, dictionary, or range).
- **`while` loops:** Ideal for executing a block of code as long as a specified condition remains true.
- **Control Keywords:**
  - `break` exits the nearest enclosing loop immediately.
  - `continue` skips the remainder of the current loop iteration and proceeds to the next cycle.
  - `pass` acts as a syntactical placeholder where code is required but no action is desired.

### Built-in Data Types & Mutability
Python collections are categorized by whether their values can be modified after creation:
1. **Mutable Structures:**
   - **Lists (`list`):** Ordered, dynamically sized arrays. Ideal for sequential access, appending, and sorting.
   - **Dictionaries (`dict`):** Key-value maps utilizing a hash-table implementation. Keys must be immutable and hashable (e.g., strings, numbers, or tuples).
   - **Sets (`set`):** Unordered collections of unique, hashable objects. Highly optimized for membership testing and mathematical set operations (union, intersection).
2. **Immutable Structures:**
   - **Strings (`str`):** Read-only sequences of Unicode characters.
   - **Tuples (`tuple`):** Fixed-size ordered sequences often used to group related data.
   - **Numeric Types (`int`, `float`):** Scalar values representing integers and floating-point real numbers.
   - **Booleans (`bool`):** True/False states.

### List Comprehensions
List comprehensions provide a concise, readable syntax to create new lists from existing iterables. They combine mapping and filtering operations into a single-line expression, often performing better than standard `for` loops due to underlying optimization.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To execute scripts, interact with the interpreter, or test code, use these terminal commands:
* `python3`  
  Launches the interactive Python REPL (Read-Eval-Print Loop).
* `python3 script.py`  
  Runs a local Python file in the interpreter.
* `python3 -c "print('Quick check')"`  
  Executes a single inline Python command from the terminal.

#### Syntax Reference
The basic building blocks of Python control structures and data structures are formatted as follows:

* **Variable Assignment & Basic Types:**
  ```python
  username = "admin"      # String (str)
  max_attempts = 5        # Integer (int)
  ratio = 0.75            # Float (float)
  is_verified = True      # Boolean (bool)
  ```
* **Conditionals:**
  ```python
  if max_attempts > 5:
      print("Limit exceeded")
  elif max_attempts == 5:
      print("Warning threshold reached")
  else:
      print("Safe range")
  ```
* **Loop Structures:**
  ```python
  # Iterate over sequence
  for index in range(5):
      if index == 2:
          continue # skip index 2
      print(index)

  # Conditional execution
  count = 0
  while count < 3:
      print(count)
      count += 1
  ```
* **List Comprehension:**
  ```python
  # syntax: [expression for item in iterable if condition]
  squares = [x * x for x in range(10) if x % 2 == 0]
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Safe Membership Verification and Loop Control
* **Situation:** You need to scan a stream of incoming transaction processing IDs, process legitimate ones, and halt execution if a known blacklisted ID is discovered.
* **Action:** Use a `for` loop combined with `break` and `continue` to filter the items against built-in set and list structures.
  ```python
  blacklist = {"TX_ERR_99", "TX_MAL_04"}
  transactions = ["TX_OK_01", "TX_OK_02", "TX_ERR_99", "TX_OK_03"]

  for tx in transactions:
      if tx in blacklist:
          print(f"Critical error: Blacklisted transaction {tx} detected! Halting stream processing.")
          break
      if tx.startswith("TX_ERR"):
          print(f"Skipping minor error: {tx}")
          continue
      print(f"Processing transaction: {tx}")
  ```

#### Example 2: Dictionary Manipulation and Formatting
* **Situation:** You need to normalize user profile records from a database query, converting legacy attributes to standard formats.
* **Action:** Iterate through user objects, apply mutation operations to active profiles, and construct an updated mapping.
  ```python
  legacy_users = {
      101: {"username": " ALICE_9 ", "is_active": True},
      102: {"username": "bob_smith", "is_active": False},
      103: {"username": "CHARLIE_R  ", "is_active": True}
  }

  normalized_profiles = {}
  for user_id, info in legacy_users.items():
      if info["is_active"]:
          clean_name = info["username"].strip().lower()
          normalized_profiles[user_id] = clean_name

  print(normalized_profiles)
  # Output: {101: 'alice_9', 103: 'charlie_r'}
  ```

#### Example 3: Set Operations for Deduplication
* **Situation:** Your analytics script receives overlapping visitor log sets from two different servers, and you must calculate unique visits across both locations.
* **Action:** Merge two distinct lists into set structures and perform set mathematical operations.
  ```python
  server_a_ips = ["192.168.1.1", "10.0.0.5", "192.168.1.1", "172.16.0.4"]
  server_b_ips = ["10.0.0.5", "172.16.0.4", "172.16.0.8"]

  set_a = set(server_a_ips)
  set_b = set(server_b_ips)

  unique_all = set_a.union(set_b)
  both_visited = set_a.intersection(set_b)

  print("Unique visitors across network:", list(unique_all))
  print("Visitors logged on both systems:", list(both_visited))
  ```

#### Example 4: List Comprehensions with Filtering and Mapping
* **Situation:** You need to extract a clean sublist of high-value, active order IDs from a messy sequence of numerical transaction amounts.
* **Action:** Write a single-line list comprehension containing nested conditional logic to filter out elements.
  ```python
  raw_orders = [120.50, -45.00, 300.00, 15.25, 0.00, 550.00]
  # Filter positive values greater than 100 and apply a 10% discount
  discounted_orders = [round(amt * 0.90, 2) for amt in raw_orders if amt > 100.00]

  print(discounted_orders)
  # Output: [108.45, 270.0, 495.0]
  ```

#### Example 5: Tuple Destructuring and Read-Only Record Iteration
* **Situation:** Your configuration contains fixed network definitions that should not be altered during runtime, which you need to format for a reporting console.
* **Action:** Leverage immutable tuples and iterate using destructuring assignment.
  ```python
  network_nodes = (
      ("Gateway_01", "192.168.1.1", 8080),
      ("Db_Node_01", "10.0.0.24", 5432),
      ("Cache_Node", "10.0.0.25", 6379)
  )

  for hostname, ip_addr, port in network_nodes:
      print(f"Node '{hostname}' is listening on address {ip_addr}:{port}")
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: The Prime Finder and Skip Mechanism
* **Objective:** Build a tool using loops and loop control statements to isolate specific values.
* **Tasks:**
  1. Initialize a loop cycling numbers from 2 up to 20.
  2. Implement an inner checker to verify if a number is prime.
  3. If the number is composite, use `continue` to move to the next cycle.
  4. If the number is prime, print it. If you encounter the prime number 17, terminate the entire operation using `break`.

#### Lab 2: Grade Book Analyzer
* **Objective:** Practice list and dictionary creation and traversal.
* **Tasks:**
  1. Define a dictionary named `grade_book` where keys are student names and values are lists of their test scores.
  2. Write a loop to iterate through the database record entries.
  3. For each student, compute the mathematical average of their list of scores.
  4. If their average is 90 or above, print their name along with "Status: Honors". Otherwise, print their name and "Status: Pass".

#### Lab 3: Unique Tag Aggregator
* **Objective:** Use set operations to perform deduplication tasks.
* **Tasks:**
  1. Define three lists of tags represents user interests (e.g., `["python", "web", "cloud"]`, `["data", "python"]`, `["cloud", "docker", "kubernetes"]`).
  2. Create an empty set named `unique_tags`.
  3. Loop through each list of tags and update `unique_tags` so it contains only unique tags across all entries.
  4. Convert the final output into a sorted list and display it.

#### Lab 4: Inventory Threshold Monitor
* **Objective:** Practice conditionals and list iteration.
* **Tasks:**
  1. Set up a dictionary tracking inventory items and their quantities (e.g., `{"screws": 120, "bolts": 8, "washers": 250, "nuts": 4}`).
  2. Iterate over the item-quantity pairs.
  3. Check if the quantity is below 10 (Restock immediately), between 10 and 50 (Warning: Low), or above 50 (Optimal).
  4. Print the status message for each inventory item.

#### Lab 5: Log String Sanitizer
* **Objective:** Write an advanced list comprehension to process and clean messy string elements.
* **Tasks:**
  1. Define a raw list containing leading/trailing whitespace strings and lowercase keys: `["  auth_success ", " DB_CONN_FAIL", "  rate_limit_exceeded   ", "CACHE_HIT  "]`.
  2. Use a list comprehension to clean each string by removing all leading and trailing whitespace.
  3. Force all string characters to be strictly uppercase.
  4. Exclude any cleaned string containing the word "SUCCESS".
  5. Print the finalized sanitized list.
""",
        "insight": """
### Interview Q&A

#### Q1: What is the main structural difference between a List and a Tuple in Python?
* **Answer:** Lists are mutable, meaning their elements can be modified, appended, or removed in-place, which is ideal for dynamic sequential datasets. Tuples are immutable; once created, their structure and values cannot be changed, making them more memory-efficient and safe for protecting static records from accidental side-effects.

#### Q2: How does the 'is' operator differ from the '==' operator?
* **Answer:** The `==` operator performs an equality evaluation, checking whether the actual *values* of the two operands are equal. The `is` operator performs an identity evaluation, checking whether both operands reference the exact same *object* in system memory (i.e., they share the same physical address in RAM).

#### Q3: How does Python evaluate the 'truthiness' of collections?
* **Answer:** In a boolean context, Python evaluates any empty collection (such as an empty list `[]`, dictionary `{}`, set `set()`, tuple `()`, or string `""`) to `False`. Any collection containing one or more elements evaluates to `True`.

#### Q4: What is the purpose of the 'pass' keyword, and how does it differ from 'continue'?
* **Answer:** `pass` is a null statement used as a syntactical placeholder when a block of code (like a conditional statement or class body) is required by Python's grammar but no logical operation needs to run. `continue` is a control flow statement that skips the rest of the current loop block and immediately starts the next iteration of the loop.

#### Q5: Why must keys in a Python dictionary be immutable/hashable?
* **Answer:** Dictionaries use hash tables to search for keys in constant time ($O(1)$ complexity). To find a key, Python computes a hash value from the key. If the key were mutable, its value could change, altering its hash and making it impossible for the dictionary to find the associated value in memory.

### Junior Assessment Focus
Be ready to trace variable assignments to demonstrate how variables point to objects in memory. You should also be prepared to write clean list comprehensions and explain the consequences of mutability when changing elements inside nested structures.
"""
    },
    {
        "id": 2,
        "title": "Module 2: Functions, Variable Scope, Exceptions, and File I/O",
        "theory": """
### Creating and Using Functions
Functions are the modular building blocks of clean code. They are declared using the `def` keyword. 
- **Parameters:** Functions accept input parameters, which can be standard positional arguments or keyword arguments. 
- **Default Arguments:** You can set default values for arguments, making them optional.
- **Return Values:** Functions pass computed results back to the caller using the `return` statement. If no return statement is defined, the function implicitly returns `None`.

### Variable Scope and the LEGB Rule
Variable access in Python is determined by where variables are declared. Python resolves variable names using the **LEGB** lookup order:
1. **Local (L):** Variables defined inside the active function.
2. **Enclosing (E):** Variables in outer functions of nested function structures.
3. **Global (G):** Variables defined at the top-level of the script or module.
4. **Built-in (B):** Standard keywords and operations (like `len`, `range`, `ValueError`).

### Exception Handling
Exceptions interrupt normal execution when runtime errors occur. To prevent crashes, Python uses `try` blocks:
- **`try`:** Encloses operations that might raise an error.
- **`except`:** Catches and handles specific exceptions (e.g., `ValueError`, `KeyError`). Catching specific exceptions prevents hiding unrelated system errors or typos.
- **`else`:** Runs code only if no exceptions were raised.
- **`finally`:** Runs code under all circumstances (even if a program crash or return statement is triggered), making it useful for cleanup tasks.

### File Input and Output (I/O)
Reading and writing local files is safest when using the `with` statement. The `with` statement acts as a **context manager**, automatically closing the system file descriptor when the block of code finishes, even if exceptions are raised.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To quickly test and inspect function logic, file operations, or standard library execution, use these command tools:
* `python3 -m unittest test_script.py`  
  Runs built-in tests on functions within a specific file.
* `help([object])`  
  (Within Python REPL) Displays documentation for standard functions or objects.

#### Syntax Reference
The code blocks below outline function, scope, exception, and file handling structures:

* **Function Definition with Defaults:**
  ```python
  def generate_greeting(user, role="Guest"):
      return f"Welcome {user} ({role})"
  ```
* **Scope Modification:**
  ```python
  system_counter = 0  # Global variable

  def increment_counter():
      global system_counter
      system_counter += 1
  ```
* **Robust Exception Handling:**
  ```python
  try:
      number = int("invalid_int")
  except ValueError as err:
      print(f"Encountered parsing error: {err}")
  else:
      print("No errors encountered!")
  finally:
      print("Cleanup operation completed.")
  ```
* **Context-Safe File Operations:**
  ```python
  # Writing data
  with open("output.txt", "w", encoding="utf-8") as file:
      file.write("Logged Entry")

  # Reading data
  with open("output.txt", "r", encoding="utf-8") as file:
      content = file.read()
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Computing Regional Pricing with Keyword Defaults
* **Situation:** You need a helper function to calculate the final price of items, applying discounts and variable regional tax rates that default to standard values.
* **Action:** Define a function utilizing optional parameters and keyword-only execution patterns.
  ```python
  BASE_TAX_RATE = 0.08  # Global default

  def calculate_final_price(base_price, discount=0.0, custom_tax=None):
      tax_rate = custom_tax if custom_tax is not None else BASE_TAX_RATE
      discounted_total = base_price - discount
      if discounted_total < 0:
          discounted_total = 0.0
      return round(discounted_total * (1 + tax_rate), 2)

  # Run using mix of positional and keyword arguments
  standard_price = calculate_final_price(100.0)
  discounted_price = calculate_final_price(100.0, discount=15.0, custom_tax=0.12)

  print(f"Standard: {standard_price}, Customized: {discounted_price}")
  ```

#### Example 2: Scope Isolation (Global vs Local Modification)
* **Situation:** You need to track application status states using global variables while securely updating them within utility functions.
* **Action:** Use the `global` keyword to modify global states inside a local scope.
  ```python
  app_status = "INITIALIZING"

  def update_status(new_status):
      global app_status
      old_status = app_status # Local variable storing previous state
      app_status = new_status
      return f"Transitioned from {old_status} to {new_status}"

  print(update_status("RUNNING"))
  print(f"Current Global App Status: {app_status}")
  ```

#### Example 3: Safe Parsing of Configuration Strings
* **Situation:** Your script processes incoming configuration strings that could contain invalid numbers, and you must prevent system failures during casting.
* **Action:** Wrap type conversions in a `try-except-else-finally` block.
  ```python
  def parse_port_number(raw_port):
      try:
          parsed_port = int(raw_port)
      except ValueError as err:
          print(f"Validation Warning: '{raw_port}' is invalid. Defaulting to 80. ({err})")
          return 80
      else:
          print("Port processed successfully with no exceptions.")
          return parsed_port
      finally:
          print("Port validation step execution complete.")

  active_port = parse_port_number("8080")
  fallback_port = parse_port_number("invalid_port_string")
  ```

#### Example 4: Context-Safe Text Logger
* **Situation:** Your application needs to log transaction errors directly to a physical file and ensure system resources are freed afterward.
* **Action:** Use the context manager `with open` to write safely.
  ```python
  log_file_path = "system_events.log"
  error_payloads = ["Database timeout at 12:01", "Unauthorized API hit at 12:02"]

  with open(log_file_path, "w", encoding="utf-8") as writer:
      for index, payload in enumerate(error_payloads, 1):
          writer.write(f"[LOG_ID_{index:03d}] - {payload}\\n")

  # File is guaranteed to be closed at this point.
  print("Event logs written successfully.")
  ```

#### Example 5: Multi-Format CSV/Text File Analyzer
* **Situation:** You need to read and extract keys from a text file that lists values line-by-line, discarding empty lines.
* **Action:** Open and read a file safely line-by-line using a context manager.
  ```python
  # Writing a mock file first
  with open("data_source.txt", "w", encoding="utf-8") as f:
      f.write("user_id,status\\n\\n101,active\\n102,inactive\\n\\n103,active")

  valid_rows = []
  with open("data_source.txt", "r", encoding="utf-8") as file:
      for line in file:
          clean_line = line.strip()
          if clean_line and not clean_line.endswith("status"):
              valid_rows.append(clean_line.split(","))

  print("Processed dataset records:", valid_rows)
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Interactive Celsius to Fahrenheit Converter
* **Objective:** Create a script that takes numerical inputs, applies math conversions, and handles errors.
* **Tasks:**
  1. Write a function `celsius_to_fahrenheit(c_temp)` that returns $(c\_temp \times 9/5) + 32$.
  2. Implement an interactive runtime loop using `input()`.
  3. Parse inputs to float inside a `try-except` block to capture `ValueError` (e.g., if a user enters non-numeric characters) and output a clean error message without crashing.

#### Lab 2: Dynamic Tax Calculator with Default Parameters
* **Objective:** Design reusable calculation interfaces using default parameters.
* **Tasks:**
  1. Write a function `calculate_invoice(subtotal, tax_rate=0.05, shipping_flat=10.0)`.
  2. The function must return $subtotal + (subtotal \times tax\_rate) + shipping\_flat$.
  3. Run three test cases: one passing only the subtotal, one modifying only the tax rate using keyword execution, and one changing all inputs. Print the outputs.

#### Lab 3: Safe File Reader with Fallbacks
* **Objective:** Build a robust directory file parser.
* **Tasks:**
  1. Write a function `read_config_file(file_path)` that opens and returns the contents of a file.
  2. Wrap the execution in a `try-except` block targeting `FileNotFoundError`.
  3. If the target file does not exist, capture the exception, write a default configuration to the file path, and then return the default values.

#### Lab 4: Scope Investigator
* **Objective:** Debug local, enclosing, global, and built-in scope behaviors.
* **Tasks:**
  1. Declare a global variable `system_mode = "Production"`.
  2. Write a nested function where the outer function defines a local variable `mode_flag = "Enclosing"`.
  3. In the inner nested function, attempt to print all variables: `system_mode`, `mode_flag`, and a local variable `internal_var = "Local"`.
  4. Use the `global` and non-local keywords to modify the global `system_mode` value from within the nested function, then output the modified values to verify scoping rules.

#### Lab 5: User Activity Logger
* **Objective:** Build a logging system using file append modes.
* **Tasks:**
  1. Create a script containing a list of dictionary actions (e.g., `{"user": "Alice", "action": "LOGIN"}`).
  2. Use a context manager to open a local file called `user_actions.log` using append mode (`"a"`).
  3. Write each activity record to the file on a new line.
  4. Ensure a fallback `finally` block prints "Logging completed."
""",
        "insight": """
### Interview Q&A

#### Q1: What happens if you define a mutable default argument like 'target_list=[]' in a function signature?
* **Answer:** In Python, default argument values are evaluated once when the function is defined, not every time it is called. If you pass a mutable object like a list as a default argument, all subsequent calls that rely on the default will share and modify the exact same list instance in memory, causing unexpected data leaks.

#### Q2: What is the LEGB rule, and how does Python resolve variable lookups?
* **Answer:** The LEGB rule defines the order of scopes Python searches to resolve variable names. It first searches the **Local** scope inside the current function, then the **Enclosing** scope of outer functions, then the **Global** module scope, and finally the **Built-in** scope for standard names.

#### Q3: Why is using a general 'except:' or 'except Exception:' block discouraged?
* **Answer:** Blanket exception blocks catch every exception, including system interrupts (like `KeyboardInterrupt`) and syntax or logical typos. This can mask underlying bugs and make debugging and maintenance difficult. You should always catch specific exceptions instead.

#### Q4: How does the 'finally' block behave if a return statement is triggered within a 'try' or 'except' block?
* **Answer:** The `finally` block is guaranteed to run before the function returns. Even if a `return` is reached inside the `try` or `except` blocks, the interpreter temporarily pauses the return operation, runs the `finally` block, and then completes the return.

#### Q5: What is the main benefit of using a 'with' statement when opening a file?
* **Answer:** The `with` statement utilizes the context manager protocol to ensure that resources like system file descriptors are automatically closed when execution leaves the block, even if runtime exceptions occur. This prevents resource leaks and file corruption.

### Junior Assessment Focus
Be ready to explain how Python handles scopes, write functions with default and keyword-only parameters, and handle potential failures like file issues or parsing errors without crashing your code.
"""
    },
    {
        "id": 3,
        "title": "Module 3: Object-Oriented Python and Standard Library",
        "theory": """
### Object-Oriented Programming (OOP) Core
Python is natively object-oriented, meaning everything is an object with its own namespace:
- **Classes:** Custom blueprints containing state (attributes) and behavior (methods).
- **The `__init__` Initializer:** The constructor method called automatically when creating a new class instance.
- **The `self` Parameter:** Represents the current instance of the class, allowing access to instance attributes and methods.
- **Inheritance:** Deriving a child class from a parent class to promote reuse and extension.
- **Super Function (`super()`):** A built-in function used to access and run methods from a parent class.

### Standard Library Foundations
Python comes with built-in modules that handle common development tasks:
- **`math`:** Provides standard mathematical calculations (such as ceilings, square roots, and trigonometric operations).
- **`datetime`:** Used for parsing, formatting, and performing arithmetic on calendar dates and times.
- **`json`:** Converts Python objects (like lists and dictionaries) to JSON strings (serialization) and back (deserialization).
- **`random`:** Generates pseudo-random numbers and selections.
- **`os` and `sys`:** Allow interacting with the host operating system, navigating directory paths, and accessing command-line arguments.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
Standard modules require no installation. Learn to import and explore their interfaces using:
* `import os; print(os.getcwd())`  
  Prints the active working directory of your script environment.
* `import sys; print(sys.argv)`  
  Prints list of arguments passed to the script at command invocation.

#### Syntax Reference
The code blocks below outline core OOP constructs and standard library imports:

* **Basic Class with Inheritance:**
  ```python
  class Vehicle:
      def __init__(self, make, model):
          self.make = make
          self.model = model

  class Truck(Vehicle):
      def __init__(self, make, model, capacity):
          super().__init__(make, model)  # parent initialization
          self.capacity = capacity
  ```
* **Import Statements:**
  ```python
  import json                         # Standard import
  from datetime import datetime       # Specific object import
  import random as rand_generator    # Alias import
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Class Construction for CRM User Representation
* **Situation:** You need to model a standard user record in a CRM system, offering methods to change statuses and generate clean system reports.
* **Action:** Build a class with attributes, standard methods, and a custom string representation method.
  ```python
  class CRMUser:
      def __init__(self, name, email):
          self.name = name
          self.email = email
          self.status = "PENDING"

      def activate(self):
          self.status = "ACTIVE"

      def __str__(self):
          return f"User: {self.name} | Email: {self.email} | Status: {self.status}"

  user_record = CRMUser("Bob", "bob@site.com")
  user_record.activate()
  print(user_record) # Evaluates __str__
  ```

#### Example 2: Inherited Account Structure using super()
* **Situation:** You need to build a premium bank account class that inherits attributes from a base account but adds a credit line limit.
* **Action:** Extend a parent class and call its constructor using the `super()` method.
  ```python
  class BankAccount:
      def __init__(self, owner, balance):
          self.owner = owner
          self.balance = balance

  class PremiumAccount(BankAccount):
      def __init__(self, owner, balance, credit_limit=5000):
          super().__init__(owner, balance)
          self.credit_limit = credit_limit

      def query_available_funds(self):
          return self.balance + self.credit_limit

  premium_client = PremiumAccount("Charlie", 1500.0)
  print(f"Total available credit limit funds: ${premium_client.query_available_funds()}")
  ```

#### Example 3: JSON Serialization and Deserialization
* **Situation:** Your script must load credentials and API configurations from a JSON string and output modified configurations back to a file payload format.
* **Action:** Use the standard `json` module's serialization methods.
  ```python
  import json

  # Deserialization (JSON string -> Python dict)
  raw_payload = '{"api_key": "abc123xyz", "max_queries": 100, "debug": true}'
  config = json.loads(raw_payload)
  print(f"Loaded API key: {config['api_key']}")

  # Serialization (Python dict -> JSON formatted string)
  config["max_queries"] = 250
  updated_json_str = json.dumps(config, indent=4)
  print(updated_json_str)
  ```

#### Example 4: Expiration Interval Calculations with Datetime
* **Situation:** Your application issues temporary session authorization tokens that must expire exactly 3 hours and 30 minutes after generation.
* **Action:** Leverage the `datetime` and `timedelta` classes to calculate exact time offsets.
  ```python
  from datetime import datetime, timedelta

  current_time = datetime.now()
  validity_duration = timedelta(hours=3, minutes=30)
  expiration_time = current_time + validity_duration

  print("Token Created At:", current_time.strftime("%Y-%m-%d %H:%M:%S"))
  print("Token Expires At:", expiration_time.strftime("%Y-%m-%d %H:%M:%S"))
  ```

#### Example 5: Operating System File System Queries
* **Situation:** Your script needs to check if a logs directory exists, create it if missing, and print system info such as the current script path.
* **Action:** Use the `os` and `sys` modules to interact with the environment.
  ```python
  import os
  import sys

  logs_dir = "system_logs"
  if not os.path.exists(logs_dir):
      os.makedirs(logs_dir)
      print(f"Directory '{logs_dir}' has been created.")
  else:
      print(f"Directory '{logs_dir}' already exists.")

  print(f"Platform: {sys.platform}")
  print(f"Running script context: {sys.argv[0]}")
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Library Book Tracking Class
* **Objective:** Design a custom class to model real-world objects and manage state.
* **Tasks:**
  1. Define a class named `Book` with attributes `title`, `author`, and `checked_out` (which defaults to `False`).
  2. Implement a method `borrow()` that sets `checked_out` to `True` if it is currently `False`, or displays a message if the book is already checked out.
  3. Implement a method `return_book()` that sets `checked_out` to `False`.
  4. Instantiate two books and simulate borrowing and returning actions.

#### Lab 2: Bank Account Class with Withdrawal Limits
* **Objective:** Protect instance states using methods.
* **Tasks:**
  1. Create a class `BankAccount` containing `owner` and `balance` attributes initialized in the constructor.
  2. Write a `deposit(amount)` method that adds money to the balance.
  3. Write a `withdraw(amount)` method that subtracts money from the balance, provided the account has sufficient funds.
  4. If the withdrawal amount exceeds the balance, print an error message instead of executing the transaction.

#### Lab 3: Configuration File Parser and Merger (JSON)
* **Objective:** Read standard JSON configurations, modify dictionary attributes, and serialize them.
* **Tasks:**
  1. Write a script that checks for a local file named `app_config.json`. If missing, write a default JSON configuration mapping back to disk.
  2. Read the config file and load it into a Python dictionary.
  3. Add a new key called `"last_accessed"` updating it with the current date, then save it back to disk.

#### Lab 4: Code Execution Timer
* **Objective:** Use `datetime` to measure execution performance.
* **Tasks:**
  1. Capture a starting time marker using `datetime.now()`.
  2. Implement a mathematical execution loop (e.g., calculation squares of numbers up to 1,000,000).
  3. Capture an ending time marker, compute the difference, and print the elapsed execution duration.

#### Lab 5: Random Password Generator
* **Objective:** Use the standard `random` and `string` libraries.
* **Tasks:**
  1. Write a script that imports `random` and the `string` module.
  2. Prompt the user for an integer password length.
  3. Combine lists of ASCII letters, digits, and special characters.
  4. Select random characters from this combined pool and compile them into a password string, then print the result.
""",
        "insight": """
### Interview Q&A

#### Q1: What is the role of the 'self' parameter inside Python class methods?
* **Answer:** `self` represents the specific instance of the class that is currently calling the method. It allows each individual object to access and modify its own attributes and methods, keeping its state isolated from other objects created from the same class.

#### Q2: What is the functional difference between the standard constructor '__init__' and the '__str__' method?
* **Answer:** `__init__` is an initializer method that runs automatically when a new instance of a class is created to set up the object's initial attributes. `__str__` is a special method that returns a readable, user-friendly string representation of the object when evaluated by functions like `print()` or `str()`.

#### Q3: How do class variables differ from instance variables?
* **Answer:** Class variables are defined directly inside the class body and are shared among all instances of that class. Instance variables are declared inside methods (usually `__init__`) using `self.variable_name`, making them unique to each individual object.

#### Q4: What is the difference between 'import math' and 'from math import sqrt'?
* **Answer:** `import math` imports the entire math namespace, requiring you to access functions using the dot operator (e.g., `math.sqrt()`). `from math import sqrt` imports only the `sqrt` function directly into the local namespace, allowing you to use it without the `math.` prefix.

#### Q5: Why is the 'sys' module used for command-line arguments instead of 'os'?
* **Answer:** The `sys` module handles system-specific parameters and APIs related directly to the Python interpreter (such as the script argument list `sys.argv` and python paths). The `os` module handles operating system-level tasks, like file systems, processes, and environment variables.

### Junior Assessment Focus
Be ready to show how to build simple class hierarchies, use inheritance, call constructors, and import standard library modules to parse files and calculate dates.
"""
    },
    {
        "id": 4,
        "title": "Module 4: Relational Databases, SQL, and Web API Integration",
        "theory": """
### Relational Databases & SQL Foundations
A relational database organizes data into structured tables with rows and columns. Python applications communicate with databases using standard relational tools:
- **SQL (Structured Query Language):** The domain-specific language used to write queries.
- **CRUD Operations:** The foundational actions of persistent storage:
  - **C**reate (`INSERT`)
  - **R**ead (`SELECT`)
  - **U**pdate (`UPDATE`)
  - **D**elete (`DELETE`)
- **SQL Parameterization:** Passing values to a query using placeholder tokens (e.g., `?` or `%s`). This prevents **SQL Injection** attacks, which are a major security vulnerability where malicious input is executed as SQL commands.

### Object-Relational Mappers (ORMs)
ORMs like Django ORM or SQLAlchemy map database tables to Python classes and database rows to Python objects. This allows developers to query, filter, and save database records using standard Python code instead of writing raw SQL.

### Web Service Integration via HTTP
The Web uses the HTTP protocol to exchange information.
- **REST APIs:** Representational State Transfer APIs use standard HTTP request methods to perform actions:
  - `GET` to retrieve data.
  - `POST` to send new data to a server.
  - `PUT` to update existing data.
  - `DELETE` to remove data.
- **The `requests` Library:** A popular, user-friendly Python package for making HTTP requests.
- **Common Status Codes:**
  - `200 OK` / `201 Created`: The request succeeded.
  - `400 Bad Request`: Client-side input or syntax errors.
  - `404 Not Found`: The requested resource does not exist.
  - `500 Internal Server Error`: Server-side errors.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To make API requests or interact with databases, install packages and establish connections using:
* `pip install requests`  
  Installs the third-party requests library.
* `pip install sqlalchemy`  
  Installs the SQLAlchemy toolkit and ORM.

#### Syntax Reference
The code blocks below outline SQLite cursor patterns and HTTP GET/POST syntax:

* **SQLite Database Connection & Parameterized Query:**
  ```python
  import sqlite3
  conn = sqlite3.connect("app_data.db")
  cursor = conn.cursor()

  # Create Table
  cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)''')

  # Parameterized Insert
  cursor.execute("INSERT INTO users VALUES (?, ?)", (1, "Alice"))
  conn.commit()
  conn.close()
  ```
* **HTTP Requests (GET & POST):**
  ```python
  import requests

  # GET Request
  get_resp = requests.get("https://api.site.com/data", timeout=5)
  data = get_resp.json()

  # POST Request
  payload = {"username": "admin", "role": "editor"}
  post_resp = requests.post("https://api.site.com/users", json=payload, timeout=5)
  status = post_resp.status_code
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: SQLite Local Database CRUD Operations
* **Situation:** You need to initialize a local SQLite database table to store system product quantities and perform CRUD actions.
* **Action:** Use the built-in `sqlite3` driver to create a table and insert records.
  ```python
  import sqlite3

  connection = sqlite3.connect("inventory.db")
  cursor = connection.cursor()

  # Create a table
  cursor.execute('''
      CREATE TABLE IF NOT EXISTS products (
          product_id INTEGER PRIMARY KEY,
          title TEXT,
          stock_count INTEGER
      )
  ''')

  # Insert values using parameter placeholders
  cursor.execute("INSERT OR REPLACE INTO products (product_id, title, stock_count) VALUES (?, ?, ?)", (501, "Screws", 120))
  connection.commit()

  # Read values
  cursor.execute("SELECT * FROM products")
  print("Current Inventory Records:", cursor.fetchall())
  connection.close()
  ```

#### Example 2: Parameterized Select Queries
* **Situation:** You need to securely query database user records filtered by user input, without exposing the system to SQL injection.
* **Action:** Execute a query using parameter placeholders instead of string formatting.
  ```python
  import sqlite3

  connection = sqlite3.connect("inventory.db")
  cursor = connection.cursor()

  target_item = "Screws"

  # SECURE: Always pass variables as parameters in a tuple
  cursor.execute("SELECT * FROM products WHERE title = ?", (target_item,))
  result = cursor.fetchall()
  print("Found matching item:", result)

  # BAD PRACTICE TO AVOID:
  # cursor.execute(f"SELECT * FROM products WHERE title = '{target_item}'")

  connection.close()
  ```

#### Example 3: SQLAlchemy Basic Model Mapping and Filtering
* **Situation:** You need to map database tables to Python objects and query them using SQLAlchemy.
* **Action:** Define an ORM model and run basic queries on an in-memory SQLite database.
  ```python
  from sqlalchemy import create_engine, Column, Integer, String
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import sessionmaker

  Base = declarative_base()

  class Member(Base):
      __tablename__ = 'members'
      id = Column(Integer, primary_key=True)
      username = Column(String)

  # Create in-memory DB and session
  engine = create_engine('sqlite:///:memory:')
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()

  # Save a record
  new_member = Member(id=1, username="charlie_01")
  session.add(new_member)
  session.commit()

  # Query and Filter records
  matched_user = session.query(Member).filter_by(username="charlie_01").first()
  print(f"ORM found user: {matched_user.username} with ID {matched_user.id}")
  ```

#### Example 4: REST API Consumption with HTTP GET and Timeout
* **Situation:** Your script must fetch details from an external API, handle different response states, and ensure requests don't hang indefinitely.
* **Action:** Make a `GET` request using the `requests` library with status checks and timeouts.
  ```python
  import requests

  endpoint = "https://jsonplaceholder.typicode.com/posts/1"

  try:
      response = requests.get(endpoint, timeout=5.0)
      if response.status_code == 200:
          data = response.json()
          print("Request successful!")
          print(f"Title: {data['title']}")
      elif response.status_code == 404:
          print("The requested resource was not found.")
      else:
          print(f"Server returned an error status: {response.status_code}")
  except requests.exceptions.Timeout:
      print("The request timed out before receiving a response.")
  ```

#### Example 5: Submitting JSON Payloads with HTTP POST
* **Situation:** You need to register a new user profile on a remote microservice by submitting a JSON payload.
* **Action:** Make an HTTP `POST` request with the `json` parameter.
  ```python
  import requests

  target_url = "https://jsonplaceholder.typicode.com/posts"
  user_payload = {
      "title": "New Registration",
      "body": "User active, verification pending.",
      "userId": 999
  }

  response = requests.post(target_url, json=user_payload, timeout=5)
  if response.status_code == 201:
      print("Success: Resource created on the remote server.")
      print("Server returned database key ID:", response.json().get("id"))
  else:
      print(f"Failed with status: {response.status_code}")
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: SQLite Contact Directory App (Insert and Retrieval)
* **Objective:** Write a script that saves and retrieves names using an SQLite database.
* **Tasks:**
  1. Create a Python script that connects to a database named `directory.db`.
  2. Create a table named `contacts` with columns `name` and `phone`.
  3. Prompt the user to enter a contact's name and phone number.
  4. Securely insert the data using parameterized SQL.
  5. Query the database table and print all contacts to the console.

#### Lab 2: Database Updater
* **Objective:** Practice updating and deleting SQL database records.
* **Tasks:**
  1. Use the SQLite database created in Lab 1.
  2. Write a function `update_phone_number(name, new_phone)` that uses SQL `UPDATE` to modify a phone number based on a contact's name.
  3. Write a function `delete_contact(name)` that uses SQL `DELETE` to remove a contact.
  4. Call these functions and verify the changes by querying the database.

#### Lab 3: Basic SQLAlchemy Record Inserter
* **Objective:** Write queries and insert database records using SQLAlchemy.
* **Tasks:**
  1. Create a Python script using SQLAlchemy.
  2. Define an ORM class `Product` with columns `id`, `name`, and `price`.
  3. Connect to a local SQLite database named `store.db` and create the schema.
  4. Create and save three products to the database using the ORM.
  5. Use `session.query(Product).filter()` to retrieve and print products with a price greater than 50.

#### Lab 4: Fetching Public Placeholder Posts
* **Objective:** Make HTTP requests to an API and parse the JSON response.
* **Tasks:**
  1. Use the `requests` library to query `https://jsonplaceholder.typicode.com/users`.
  2. Loop through the resulting JSON list of user dictionaries.
  3. Print each user's `name` alongside their nested `company` name.
  4. Handle potential failures by checking if the response has a success status code.

#### Lab 5: Web API Network Error Handler
* **Objective:** Handle connection issues and bad responses gracefully.
* **Tasks:**
  1. Write a script that attempts to send a `GET` request to an invalid URL (e.g., `http://invalid-domain-name-xyz.com`).
  2. Wrap the API request in a `try-except` block targeting `requests.exceptions.RequestException`.
  3. In the event of a connection failure, catch the exception and print a friendly warning message instead of letting the program crash.
""",
        "insight": """
### Interview Q&A

#### Q1: What is SQL Injection, and how do parameter placeholders protect queries?
* **Answer:** SQL Injection is a security vulnerability where an attacker injects malicious SQL commands into user inputs to exploit database engines. Parameter placeholders (such as `?` or `%s`) protect queries by separating executable SQL code from raw data, ensuring the database treats user input strictly as values rather than executable commands.

#### Q2: What is an ORM (Object-Relational Mapper), and what are its trade-offs?
* **Answer:** An ORM maps database tables to classes and table rows to class instances. This allows developers to interact with the database using standard Python code, which prevents SQL injection and abstracts differences between database engines. The trade-offs include a learning curve and potential performance overhead for complex, high-volume queries.

#### Q3: What do the HTTP status codes 200, 400, 404, and 500 represent?
* **Answer:** 
  - `200 OK`: The request was successful.
  - `400 Bad Request`: The server could not process the request due to client-side errors (e.g., malformed input).
  - `404 Not Found`: The requested resource could not be found.
  - `500 Internal Server Error`: The server encountered an unexpected error and could not complete the request.

#### Q4: Why should you always set a 'timeout' when using the 'requests' library?
* **Answer:** By default, the `requests` library does not set timeout limits. If a remote server is down, overloaded, or unresponsive, the request can hang indefinitely, blocking the application and wasting system resources. Setting a `timeout` ensures the request raises a timeout exception if the server does not respond within the specified window.

#### Q5: What is the difference between a database query's 'fetchone()' and 'fetchall()' methods?
* **Answer:** `fetchone()` retrieves the next single row from a query result set, returning a single tuple or `None` if no more rows are available. `fetchall()` retrieves all remaining rows from the result set, returning a list of tuples.

### Junior Assessment Focus
Be ready to write parameterized queries to prevent SQL Injection, query and write records using ORM systems, explain common HTTP status codes, and use the requests library to consume APIs.
"""
    },
    {
        "id": 5,
        "title": "Module 5: Developer Tooling, Packaging, and Best Practices",
        "theory": """
### Virtual Environments
A virtual environment is an isolated directory that contains a specific Python installation and its own set of dependencies. It prevents conflicts between different package versions installed across multiple projects on the same system.

### Package Management and Dependencies
`pip` is the package installer for Python, pulling packages from the Python Package Index (PyPI). To help recreate environments across development and production systems, dependencies and their exact versions are locked into a `requirements.txt` file.

### Version Control with Git
Git is a distributed version control system that tracks code changes and coordinates work among team members.
- **`git init`**: Initializes a new repository.
- **`git clone`**: Downloads an existing repository.
- **`git checkout -b`**: Creates and switches to a new branch.
- **`git add` & `git commit`**: Stages and commits code changes.
- **`git push`**: Uploads local commits to a remote repository.
- **Pull Requests (PRs)**: Let developers review, discuss, and test code changes before merging them into the main branch.

### Python Code Style and PEP 8
PEP 8 is Python's official style guide. Following PEP 8 makes code more readable and consistent across the codebase. Key guidelines include:
- Use 4 spaces per indentation level.
- Limit line length to 79 characters.
- Use `snake_case` for function and variable names, and `PascalCase` for class names.
- Place imports on separate lines at the top of the file.

### Debugging in Python
Debugging involves identifying and fixing logical bugs. While `print()` statements are useful for quick checks, the built-in interactive debugger (`pdb` / `breakpoint()`) is much more powerful. It pauses execution, allowing you to step through code line-by-line and inspect variable values.
""",
        "commands": """
### Command & Syntax Reference

#### Command Reference
To manage environments, track repositories, and style code, use these commands:
* `python3 -m venv my_env`  
  Creates an isolated virtual environment directory named `my_env`.
* `source my_env/bin/activate`  
  (Linux/macOS) Activates the virtual environment.
* `my_env\\Scripts\\activate`  
  (Windows Command Prompt) Activates the virtual environment.
* `pip freeze > requirements.txt`  
  Saves the list of installed package versions to a file.
* `pip install -r requirements.txt`  
  Installs all packages listed in a requirements file.
* `git checkout -b feature-branch`  
  Creates and switches to a branch named `feature-branch`.

#### Syntax Reference
The code blocks below outline code debugging and formatting style standards:

* **Triggering Interactive Debugger:**
  ```python
  def process_data(value):
      # Pause execution and open pdb shell
      breakpoint() 
      result = value * 2
      return result
  ```
* **PEP 8 Compliant Naming Conventions:**
  ```python
  # Class names use PascalCase
  class InvoiceCalculator:
      # Constant values are defined in UPPERCASE
      BASE_MULTIPLIER = 1.15

      # Variable and function names use snake_case
      def calculate_tax(self, user_income):
          return user_income * self.BASE_MULTIPLIER
  ```
""",
        "examples": """
### Real-World Examples

#### Example 1: Creating a Virtual Environment and Requirements File
* **Situation:** You need to set up a clean, isolated environment to develop your Python app with specific library versions.
* **Action:** Create a virtual environment using the command line, install the `requests` library, and output the dependencies to a `requirements.txt` file.
  ```bash
  # Step 1: Create the virtual environment
  python3 -m venv crm_env

  # Step 2: Activate the environment (Linux/macOS command shown)
  source crm_env/bin/activate

  # Step 3: Install requests library
  pip install requests==2.31.0

  # Step 4: Write package list to requirements file
  pip freeze > requirements.txt
  ```

#### Example 2: Git Version Control Workflow
* **Situation:** You need to create a new branch to work on a feature, add your code, and commit your changes to version control.
* **Action:** Initialize a local Git repository, create a branch, stage, and commit the modified file.
  ```bash
  # Initialize directory as a git repository
  git init

  # Create and switch to a new branch
  git checkout -b feature-auth-flow

  # Stage changes made to a Python script
  git add auth_utils.py

  # Commit changes with a clear description
  git commit -m "Add password hashing helper functions"
  ```

#### Example 3: Refactoring Code to meet PEP 8 Standards
* **Situation:** You have a poorly formatted script with bad naming conventions and inconsistent spacing, and you need to clean it up to meet PEP 8 standards.
* **Action:** Refactor the script to use correct naming conventions, spacing, and formatting.
  ```python
  # POOR FORMATTING (AVOID):
  # class my_app:
  #   def CalculateSum(self,a,b):
  #     Result = a+b; return Result;

  # PEP 8 COMPLIANT FORMATTING:
  class MyApp:
      def calculate_sum(self, val_a, val_b):
          result = val_a + val_b
          return result
  ```

#### Example 4: Step-Through Debugging with breakpoint()
* **Situation:** Your script is outputting unexpected values during calculation loops, and you need to inspect variables as the loop runs.
* **Action:** Insert a `breakpoint()` statement to step through execution.
  ```python
  def find_first_even(numbers):
      for num in numbers:
          # Pauses execution and opens the interactive debugger
          # You can type 'p num' to print value or 'c' to continue
          breakpoint()
          if num % 2 == 0:
              return num
      return None

  first_even = find_first_even([1, 3, 5, 6, 7])
  print("Found:", first_even)
  ```

#### Example 5: Multi-Dependency Installation and Recovery
* **Situation:** A colleague sent you a repository with a `requirements.txt` file, and you need to install all of its dependencies in your local environment.
* **Action:** Activate your virtual environment and run the single command to install the required dependencies.
  ```bash
  # Ensure your virtual environment is active
  # Install the dependencies listed in requirements.txt
  pip install -r requirements.txt
  ```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Package Sandbox Creation
* **Objective:** Create a clean virtual environment and install dependencies.
* **Tasks:**
  1. Open a terminal and navigate to your project directory.
  2. Create a virtual environment named `lab_env` using the `venv` module.
  3. Activate the virtual environment.
  4. Install any package from PyPI (such as `requests`).
  5. Save the environment's package snapshot to a `requirements.txt` file and verify its contents.

#### Lab 2: Local Git Project Initialization
* **Objective:** Initialize a repository, stage files, and make commits.
* **Tasks:**
  1. Open a terminal and create a new directory named `git_lab`.
  2. Initialize it as a Git repository using `git init`.
  3. Create a Python script named `hello.py` inside the directory.
  4. Stage the file using `git add` and commit it with the message "Initial project commit".
  5. Create a branch named `experimental-feature` and switch to it using checkout.

#### Lab 3: Refactoring a Non-Compliant Script to PEP 8
* **Objective:** Refactor a poorly styled script to comply with PEP 8 standards.
* **Tasks:**
  1. Copy the following code block into a file:
     ```python
     class myclass:
      def DoThing(self,X,Y):
         z=X+Y
         return z
     ```
  2. Refactor the code to use standard 4-space indentation, correct snake_case and PascalCase naming conventions, and proper spacing around operators.

#### Lab 4: Interactive Code Debugging
* **Objective:** Find logical errors using Python's built-in debugger.
* **Tasks:**
  1. Create a script containing a loop that modifies list elements (e.g., adding 10 to each number in a list).
  2. Insert `breakpoint()` inside the loop body.
  3. Run the script and use debugger commands (like `p` to print variables and `c` to continue) to inspect variable states and values as the loop runs.

#### Lab 5: Branch and Feature Merge Simulation
* **Objective:** Practice creating and merging branches in Git.
* **Tasks:**
  1. Open the Git repository you created in Lab 2.
  2. Ensure you are on the `experimental-feature` branch.
  3. Modify `hello.py` to add a new function.
  4. Commit your changes.
  5. Switch back to the main branch and merge the changes from `experimental-feature` into it.
""",
        "insight": """
### Interview Q&A

#### Q1: Why are virtual environments critical for professional Python development?
* **Answer:** Virtual environments prevent version conflicts between dependencies of different projects on the same machine. This ensures each application has isolated access to the exact library versions it needs without affecting the system-wide Python installation.

#### Q2: What does the command 'git checkout -b feature-branch' accomplish?
* **Answer:** It is a shorthand command that performs two actions sequentially: first, it creates a new branch named `feature-branch`, and second, it switches your active working context to that branch.

#### Q3: What are the main benefits of PEP 8 styling conventions in engineering teams?
* **Answer:** PEP 8 standardizes code formatting across development teams. This consistent styling makes code easier to read and maintain, reduces onboarding time for new developers, and simplifies code reviews.

#### Q4: How do you resume normal execution or jump to the next line in the 'pdb' debugger?
* **Answer:** Inside the interactive debugger console, you can type `n` (next) to execute the current line and step to the next line in the function, or type `c` (continue) to resume normal execution until the program finishes or hits another breakpoint.

#### Q5: What does a '.gitignore' file do, and what files should be placed inside it?
* **Answer:** A `.gitignore` file specifies which local files and directories Git should ignore and not track in version control. It is commonly used to exclude sensitive credentials, virtual environment folders (like `venv/`), temporary files, and compiled bytecodes.

### Junior Assessment Focus
Be ready to create virtual environments, install dependencies using requirements.txt, explain PEP 8 naming and indentation rules, commit changes using Git, and debug code using the interactive debugger.
"""
    }
]
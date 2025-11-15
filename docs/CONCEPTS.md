# ES6 Classes & Data Manipulation - Concepts Guide

This guide provides a comprehensive reference for all concepts used in the Marketplace Manager activity.

---

## Table of Contents

1. [ES6 Classes](#es6-classes)
2. [Inheritance & Polymorphism](#inheritance--polymorphism)
3. [Array Methods](#array-methods)
4. [Object Destructuring](#object-destructuring)
5. [Static Methods](#static-methods)
6. [Date Handling](#date-handling)
7. [Caching Strategies](#caching-strategies)
8. [Best Practices](#best-practices)

---

## ES6 Classes

### What Are Classes?

Classes are blueprints for creating objects with predefined properties and methods. They provide a cleaner syntax for implementing object-oriented programming in JavaScript.

### Basic Syntax

```javascript
class ClassName {
  // Constructor - called when creating new instance
  constructor(param1, param2) {
    this.property1 = param1;
    this.property2 = param2;
  }

  // Instance method
  methodName() {
    return this.property1;
  }

  // Getter - access like a property
  get computedValue() {
    return this.property1 + this.property2;
  }

  // Setter - set like a property
  set property1(value) {
    this._property1 = value;
  }
}

// Creating an instance
const instance = new ClassName('value1', 'value2');
console.log(instance.methodName()); // 'value1'
console.log(instance.computedValue); // 'value1value2'
```

### Key Concepts

**Constructor:**
- Special method called automatically when you create a new instance
- Used to initialize object properties
- Only one constructor per class

```javascript
class Vendor {
  constructor(name, location) {
    this.name = name;
    this.location = location;
    this.revenue = 0; // Default value
    this.createdAt = new Date(); // Auto-generated
  }
}
```

**The `this` Keyword:**
- Refers to the current instance of the class
- Used to access properties and methods within the class

```javascript
class Product {
  constructor(name, price) {
    this.name = name;
    this.price = price;
  }

  displayInfo() {
    // 'this' refers to the current Product instance
    console.log(`${this.name}: RWF ${this.price}`);
  }
}
```

**Instance Properties vs Methods:**

```javascript
class Example {
  constructor() {
    // Instance property - data
    this.data = 'some value';
  }

  // Instance method - behavior
  doSomething() {
    return this.data.toUpperCase();
  }
}
```

### When to Use Classes

✅ **Use classes when you need:**
- Multiple objects with similar structure
- Encapsulation (grouping related data and behavior)
- Inheritance (sharing functionality between related objects)
- Clear object relationships

❌ **Don't use classes for:**
- Simple data containers (use plain objects)
- One-off functionality (use functions)
- Stateless utilities (use modules with functions)

### Common Patterns

**Validation in Constructor:**
```javascript
class Vendor {
  constructor(name, stallNumber) {
    if (!name || !stallNumber) {
      throw new Error('Name and stall number are required');
    }
    if (typeof stallNumber !== 'string') {
      throw new Error('Stall number must be a string');
    }
    this.name = name;
    this.stallNumber = stallNumber;
  }
}
```

**Default Values:**
```javascript
class Product {
  constructor(name, price, stock = 0) {
    this.name = name;
    this.price = price;
    this.stock = stock; // Defaults to 0 if not provided
  }
}
```

**Auto-generated Properties:**
```javascript
import { v4 as uuidv4 } from 'uuid';

class Sale {
  constructor(product, quantity) {
    this.id = uuidv4(); // Auto-generate unique ID
    this.timestamp = new Date(); // Auto-set current time
    this.product = product;
    this.quantity = quantity;
  }
}
```

---

## Inheritance & Polymorphism

### Inheritance Basics

Inheritance allows you to create a new class based on an existing class, inheriting its properties and methods.

```javascript
// Parent class
class Product {
  constructor(name, price, stock) {
    this.name = name;
    this.price = price;
    this.stock = stock;
  }

  isInStock() {
    return this.stock > 0;
  }

  getDetails() {
    return { name: this.name, price: this.price, stock: this.stock };
  }
}

// Child class
class PhysicalProduct extends Product {
  constructor(name, price, stock, weight, dimensions) {
    // Call parent constructor first
    super(name, price, stock);
    
    // Add child-specific properties
    this.weight = weight;
    this.dimensions = dimensions;
  }

  // Add child-specific method
  calculateShipping(distance) {
    return this.weight * distance * 500;
  }

  // Override parent method
  getDetails() {
    // Get parent details
    const details = super.getDetails();
    
    // Add child-specific details
    return {
      ...details,
      weight: this.weight,
      dimensions: this.dimensions
    };
  }
}
```

### The `extends` Keyword

Creates an inheritance relationship between classes.

```javascript
class Child extends Parent {
  // Child inherits all properties and methods from Parent
}
```

### The `super` Keyword

**In Constructor:**
```javascript
class Child extends Parent {
  constructor(parentParam, childParam) {
    // MUST call super() first
    super(parentParam);
    
    // Then initialize child properties
    this.childProperty = childParam;
  }
}
```

**Calling Parent Methods:**
```javascript
class Child extends Parent {
  parentMethod() {
    // Call parent's version first
    super.parentMethod();
    
    // Then add child-specific behavior
    console.log('Child-specific behavior');
  }
}
```

### Method Overriding

Child classes can replace parent methods with their own implementation.

```javascript
class DigitalProduct extends Product {
  // Override to always return true
  isInStock() {
    return true; // Digital products never run out
  }
}

const ebook = new DigitalProduct('Guide', 5000, 999);
console.log(ebook.isInStock()); // true, uses child's version
```

### Polymorphism

Different classes can be used interchangeably through a common interface.

```javascript
function displayProductInfo(product) {
  // Works with any Product subclass
  console.log(product.getDetails());
  console.log(`In stock: ${product.isInStock()}`);
}

const physical = new PhysicalProduct('Shirt', 15000, 50, 0.5, {});
const digital = new DigitalProduct('Ebook', 5000, 999);

displayProductInfo(physical); // Works!
displayProductInfo(digital);  // Works!
```

### Inheritance Hierarchy

```
        Product
       /       \
      /         \
PhysicalProduct  DigitalProduct
     |
     |
PerishableProduct
```

```javascript
class Product {
  constructor(name, price) {
    this.name = name;
    this.price = price;
  }
}

class PhysicalProduct extends Product {
  constructor(name, price, weight) {
    super(name, price);
    this.weight = weight;
  }
}

class PerishableProduct extends PhysicalProduct {
  constructor(name, price, weight, expiryDate) {
    super(name, price, weight);
    this.expiryDate = expiryDate;
  }

  isExpired() {
    return new Date() > this.expiryDate;
  }
}
```

### When to Use Inheritance

✅ **Use inheritance when:**
- There's a clear "is-a" relationship (DigitalProduct IS-A Product)
- Child classes share substantial common behavior
- You want to enforce a common interface

❌ **Consider alternatives when:**
- Relationship is "has-a" (use composition)
- Inheritance tree becomes too deep (>3 levels)
- Classes don't share much behavior

---

## Array Methods

### map() - Transform Elements

Creates a new array by transforming each element.

```javascript
// Basic transformation
const prices = [1000, 2000, 3000];
const withTax = prices.map(price => price * 1.18);
// [1180, 2360, 3540]

// Extracting properties
const products = [
  { name: 'Item A', price: 1000 },
  { name: 'Item B', price: 2000 }
];
const names = products.map(product => product.name);
// ['Item A', 'Item B']

// Complex transformation
const formatted = products.map(product => ({
  label: `${product.name} - RWF ${product.price.toLocaleString()}`,
  value: product.price
}));
// [
//   { label: 'Item A - RWF 1,000', value: 1000 },
//   { label: 'Item B - RWF 2,000', value: 2000 }
// ]
```

**Key Points:**
- Returns a NEW array (doesn't modify original)
- New array has same length as original
- Each element is transformed
- Use when you want to transform every item

### filter() - Select Elements

Creates a new array with elements that pass a test.

```javascript
// Simple filtering
const numbers = [1, 2, 3, 4, 5];
const evens = numbers.filter(n => n % 2 === 0);
// [2, 4]

// Complex conditions
const products = [
  { name: 'A', price: 5000, stock: 10 },
  { name: 'B', price: 15000, stock: 0 },
  { name: 'C', price: 8000, stock: 5 }
];

const affordable = products.filter(p => p.price < 10000);
// [{ name: 'A', ... }, { name: 'C', ... }]

const inStock = products.filter(p => p.stock > 0);
// [{ name: 'A', ... }, { name: 'C', ... }]

// Multiple conditions
const affordableInStock = products.filter(
  p => p.price < 10000 && p.stock > 0
);
// [{ name: 'A', ... }, { name: 'C', ... }]
```

**Key Points:**
- Returns a NEW array (doesn't modify original)
- New array may be shorter than original
- Only includes elements where test returns true
- Use when you want a subset of data

### reduce() - Combine Elements

Reduces an array to a single value.

```javascript
// Sum
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((total, num) => total + num, 0);
// 15

// Calculate total inventory value
const products = [
  { name: 'A', price: 1000, stock: 10 },
  { name: 'B', price: 2000, stock: 5 }
];
const totalValue = products.reduce(
  (sum, product) => sum + (product.price * product.stock),
  0
);
// 20000

// Find maximum
const prices = [1000, 5000, 3000, 8000, 2000];
const maxPrice = prices.reduce(
  (max, price) => price > max ? price : max,
  0
);
// 8000

// Group by category
const productList = [
  { name: 'A', category: 'Food' },
  { name: 'B', category: 'Clothing' },
  { name: 'C', category: 'Food' }
];
const grouped = productList.reduce((acc, product) => {
  const category = product.category;
  if (!acc[category]) {
    acc[category] = [];
  }
  acc[category].push(product);
  return acc;
}, {});
// {
//   Food: [{ name: 'A', ... }, { name: 'C', ... }],
//   Clothing: [{ name: 'B', ... }]
// }

// Count occurrences
const categories = ['Food', 'Clothing', 'Food', 'Food', 'Electronics'];
const counts = categories.reduce((acc, category) => {
  acc[category] = (acc[category] || 0) + 1;
  return acc;
}, {});
// { Food: 3, Clothing: 1, Electronics: 1 }
```

**Reduce Parameters:**
```javascript
array.reduce((accumulator, currentValue, currentIndex, array) => {
  // accumulator: the running total/result
  // currentValue: current element being processed
  // currentIndex: index of current element (optional)
  // array: the original array (optional)
  
  return accumulator; // This becomes the accumulator for next iteration
}, initialValue); // Starting value for accumulator
```

**Key Points:**
- Returns a SINGLE value (can be any type)
- Initial value is important (usually 0 for numbers, {} for objects, [] for arrays)
- Most powerful but most complex array method
- Use for aggregations, groupings, transformations to different types

### sort() - Reorder Elements

Sorts array in place (MUTATES original).

```javascript
// Numbers - ascending
const numbers = [3, 1, 4, 1, 5, 9, 2, 6];
numbers.sort((a, b) => a - b);
// [1, 1, 2, 3, 4, 5, 6, 9]

// Numbers - descending
numbers.sort((a, b) => b - a);
// [9, 6, 5, 4, 3, 2, 1, 1]

// Strings - alphabetical
const names = ['Charlie', 'Alice', 'Bob'];
names.sort((a, b) => a.localeCompare(b));
// ['Alice', 'Bob', 'Charlie']

// Objects - by property
const vendors = [
  { name: 'Alice', revenue: 50000 },
  { name: 'Bob', revenue: 30000 },
  { name: 'Charlie', revenue: 80000 }
];
vendors.sort((a, b) => b.revenue - a.revenue); // Highest first
// [{ name: 'Charlie', revenue: 80000 }, ...]

// Sort without mutating (create copy first)
const sorted = [...numbers].sort((a, b) => a - b);
// Original 'numbers' unchanged
```

**Sort Logic:**
```javascript
// Return negative: a comes before b
// Return positive: b comes before a
// Return 0: order unchanged

array.sort((a, b) => {
  if (a < b) return -1;  // a comes first
  if (a > b) return 1;   // b comes first
  return 0;              // equal
});

// Shorthand for numbers
array.sort((a, b) => a - b); // Ascending
array.sort((a, b) => b - a); // Descending
```

### Other Useful Methods

**find() - Get First Match:**
```javascript
const products = [
  { id: '1', name: 'A' },
  { id: '2', name: 'B' }
];
const found = products.find(p => p.id === '2');
// { id: '2', name: 'B' }
```

**some() - Test if ANY Match:**
```javascript
const hasExpensive = products.some(p => p.price > 50000);
// true if at least one product costs > 50000
```

**every() - Test if ALL Match:**
```javascript
const allInStock = products.every(p => p.stock > 0);
// true only if every product has stock > 0
```

**slice() - Extract Portion:**
```javascript
const top5 = vendors.slice(0, 5); // First 5 elements
const last3 = vendors.slice(-3);  // Last 3 elements
// Doesn't mutate original
```

### Method Chaining

Combine multiple methods for powerful data processing:

```javascript
const result = products
  .filter(p => p.stock > 0)                    // Only in-stock
  .map(p => ({                                 // Transform
    ...p,
    totalValue: p.price * p.stock
  }))
  .sort((a, b) => b.totalValue - a.totalValue) // Sort by value
  .slice(0, 10)                                // Top 10
  .map(p => p.name);                           // Just names

// Example: Top 10 in-stock products by total value
```

**Chaining Best Practices:**
- Order matters (filter before map to process fewer items)
- Each method returns a new array (except sort)
- Keep chains readable (break into multiple lines)
- Consider performance with large datasets

---

## Object Destructuring

### Basic Destructuring

Extract properties from objects into variables.

```javascript
// Without destructuring
const product = { name: 'Kitenge', price: 15000, stock: 50 };
const name = product.name;
const price = product.price;
const stock = product.stock;

// With destructuring
const { name, price, stock } = product;
console.log(name);  // 'Kitenge'
console.log(price); // 15000
console.log(stock); // 50
```

### Renaming Variables

```javascript
const product = { name: 'Kitenge', price: 15000 };

// Rename while destructuring
const { name: productName, price: productPrice } = product;
console.log(productName);  // 'Kitenge'
console.log(productPrice); // 15000
```

### Default Values

```javascript
const product = { name: 'Kitenge', price: 15000 };

// Provide defaults for missing properties
const { name, price, stock = 0, category = 'Uncategorized' } = product;
console.log(stock);    // 0 (default)
console.log(category); // 'Uncategorized' (default)
```

### Nested Destructuring

```javascript
const vendor = {
  name: 'Mama Rose',
  location: {
    market: 'Kimironko',
    city: 'Kigali',
    country: 'Rwanda'
  }
};

// Destructure nested object
const {
  name,
  location: { market, city }
} = vendor;

console.log(name);   // 'Mama Rose'
console.log(market); // 'Kimironko'
console.log(city);   // 'Kigali'
```

### Function Parameters

```javascript
// Without destructuring
function displayProduct(product) {
  console.log(product.name);
  console.log(product.price);
}

// With destructuring
function displayProduct({ name, price, stock = 0 }) {
  console.log(name);
  console.log(price);
  console.log(stock);
}

displayProduct({ name: 'Kitenge', price: 15000 });
// Works! stock defaults to 0
```

### Destructuring in Loops

```javascript
const products = [
  { name: 'A', price: 1000 },
  { name: 'B', price: 2000 }
];

// Destructure each product
for (const { name, price } of products) {
  console.log(`${name}: RWF ${price}`);
}

// With map
const names = products.map(({ name }) => name);
```

### Rest Properties

```javascript
const product = {
  name: 'Kitenge',
  price: 15000,
  stock: 50,
  category: 'Textiles',
  vendor: 'Mama Rose'
};

// Extract some, collect rest
const { name, price, ...otherInfo } = product;
console.log(name);      // 'Kitenge'
console.log(price);     // 15000
console.log(otherInfo); // { stock: 50, category: 'Textiles', vendor: 'Mama Rose' }
```

### Array Destructuring

```javascript
// Basic
const numbers = [1, 2, 3, 4, 5];
const [first, second] = numbers;
console.log(first);  // 1
console.log(second); // 2

// Skip elements
const [, , third] = numbers;
console.log(third); // 3

// Rest elements
const [head, ...tail] = numbers;
console.log(head); // 1
console.log(tail); // [2, 3, 4, 5]

// Swapping variables
let a = 1, b = 2;
[a, b] = [b, a];
console.log(a); // 2
console.log(b); // 1
```

---

## Static Methods

### What Are Static Methods?

Static methods belong to the class itself, not to instances. They're called on the class, not on objects created from the class.

```javascript
class MathHelper {
  static add(a, b) {
    return a + b;
  }

  static multiply(a, b) {
    return a * b;
  }
}

// Call on the CLASS
console.log(MathHelper.add(2, 3)); // 5

// NOT on instances
const helper = new MathHelper();
helper.add(2, 3); // ERROR: helper.add is not a function
```

### When to Use Static Methods

✅ **Use static methods for:**

**1. Factory Methods** (create instances):
```javascript
class Product {
  constructor(name, price) {
    this.name = name;
    this.price = price;
  }

  static fromCSV(csvLine) {
    const [name, price] = csvLine.split(',');
    return new Product(name, parseFloat(price));
  }

  static createDigital(name, price, url) {
    const product = new Product(name, price);
    product.downloadUrl = url;
    product.isDigital = true;
    return product;
  }
}

const product = Product.fromCSV('Kitenge,15000');
```

**2. Utility Functions** (operate on class data):
```javascript
class Sale {
  constructor(amount) {
    this.amount = amount;
  }

  static getTotalRevenue(sales) {
    return sales.reduce((sum, sale) => sum + sale.amount, 0);
  }

  static getAverageRevenue(sales) {
    const total = Sale.getTotalRevenue(sales);
    return total / sales.length;
  }
}

const sales = [new Sale(1000), new Sale(2000), new Sale(3000)];
console.log(Sale.getTotalRevenue(sales)); // 6000
```

**3. Validation Functions:**
```javascript
class Vendor {
  constructor(name, stallNumber) {
    if (!Vendor.isValidStallNumber(stallNumber)) {
      throw new Error('Invalid stall number');
    }
    this.name = name;
    this.stallNumber = stallNumber;
  }

  static isValidStallNumber(stallNumber) {
    return /^[A-Z]-\d{2}$/.test(stallNumber); // Format: A-12
  }

  static isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}
```

**4. Aggregate Operations:**
```javascript
class Product {
  static groupByCategory(products) {
    return products.reduce((acc, product) => {
      if (!acc[product.category]) {
        acc[product.category] = [];
      }
      acc[product.category].push(product);
      return acc;
    }, {});
  }

  static findCheapest(products) {
    return products.reduce((min, p) =>
      p.price < min.price ? p : min
    );
  }
}
```

### Static vs Instance Methods

```javascript
class Calculator {
  constructor(initialValue) {
    this.value = initialValue;
  }

  // Instance method - operates on specific instance
  add(number) {
    this.value += number;
    return this;
  }

  // Static method - utility function
  static add(a, b) {
    return a + b;
  }
}

// Instance method usage
const calc = new Calculator(10);
calc.add(5); // calc.value is now 15

// Static method usage
const sum = Calculator.add(10, 5); // 15
```

---

## Date Handling

### Creating Dates

```javascript
// Current date/time
const now = new Date();

// Specific date
const specific = new Date('2025-11-11');
const detailed = new Date(2025, 10, 11, 14, 30, 0); // Month is 0-indexed!

// From timestamp
const fromTimestamp = new Date(1699876543000);

// From ISO string
const fromISO = new Date('2025-11-11T14:30:00.000Z');
```

### Getting Date Components

```javascript
const date = new Date('2025-11-11T14:30:00');

date.getFullYear();     // 2025
date.getMonth();        // 10 (November, 0-indexed!)
date.getDate();         // 11 (day of month)
date.getDay();          // 2 (Tuesday, 0=Sunday)
date.getHours();        // 14
date.getMinutes();      // 30
date.getSeconds();      // 0
date.getTime();         // Timestamp in milliseconds
```

### Comparing Dates

```javascript
const date1 = new Date('2025-11-11');
const date2 = new Date('2025-11-15');

// Direct comparison
date1 < date2;  // true
date1 > date2;  // false
date1.getTime() === date2.getTime(); // false

// Difference in milliseconds
const diffMs = date2 - date1;

// Convert to days
const diffDays = diffMs / (1000 * 60 * 60 * 24); // 4 days

// Convert to hours
const diffHours = diffMs / (1000 * 60 * 60); // 96 hours
```

### Common Date Operations

**Check if date is today:**
```javascript
function isToday(date) {
  const today = new Date();
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear();
}
```

**Start/end of day:**
```javascript
// Start of today (00:00:00)
const startOfDay = new Date();
startOfDay.setHours(0, 0, 0, 0);

// End of today (23:59:59)
const endOfDay = new Date();
endOfDay.setHours(23, 59, 59, 999);
```

**Start/end of month:**
```javascript
// Start of current month
const startOfMonth = new Date();
startOfMonth.setDate(1);
startOfMonth.setHours(0, 0, 0, 0);

// End of current month
const endOfMonth = new Date();
endOfMonth.setMonth(endOfMonth.getMonth() + 1);
endOfMonth.setDate(0);
endOfMonth.setHours(23, 59, 59, 999);
```

**Days ago/from now:**
```javascript
// 7 days ago
const weekAgo = new Date();
weekAgo.setDate(weekAgo.getDate() - 7);

// 30 days from now
const monthFromNow = new Date();
monthFromNow.setDate(monthFromNow.getDate() + 30);
```

**Age calculation:**
```javascript
function getDaysAgo(date) {
  const now = new Date();
  const diffMs = now - date;
  return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}
```

### Formatting Dates

```javascript
const date = new Date('2025-11-11T14:30:00');

// ISO format
date.toISOString(); // '2025-11-11T14:30:00.000Z'

// Locale formats
date.toLocaleDateString('en-US'); // '11/11/2025'
date.toLocaleDateString('en-GB'); // '11/11/2025'
date.toLocaleDateString('fr-FR'); // '11/11/2025'

// With options
date.toLocaleDateString('en-US', {
  year: 'numeric',
  month: 'long',
  day: 'numeric'
}); // 'November 11, 2025'

date.toLocaleTimeString('en-US'); // '2:30:00 PM'
```

### Date Filtering in Arrays

```javascript
const sales = [
  { date: new Date('2025-11-10'), amount: 1000 },
  { date: new Date('2025-11-11'), amount: 2000 },
  { date: new Date('2025-11-12'), amount: 3000 }
];

// Get today's sales
const today = new Date();
today.setHours(0, 0, 0, 0);
const tomorrow = new Date(today);
tomorrow.setDate(tomorrow.getDate() + 1);

const todaySales = sales.filter(sale =>
  sale.date >= today && sale.date < tomorrow
);

// Get sales in date range
function getSalesInRange(sales, startDate, endDate) {
  return sales.filter(sale =>
    sale.date >= startDate && sale.date <= endDate
  );
}
```

---

## Caching Strategies

### Why Cache?

Caching stores frequently accessed data in fast-access storage (like Redis) to:
- Reduce database load
- Improve response times
- Handle higher traffic
- Reduce computation costs

### When to Cache

✅ **Good caching candidates:**
- Frequently accessed data (product catalogs)
- Expensive calculations (analytics, reports)
- Data that changes infrequently
- Data where slight staleness is acceptable

❌ **Don't cache:**
- Data that changes constantly
- User-specific sensitive data
- Data that must be real-time
- Large binary objects (usually)

### Cache-Aside Pattern

Most common caching strategy:

```javascript
async function getData(key) {
  // 1. Try cache first
  let data = await cache.get(key);
  
  if (data) {
    console.log('Cache hit!');
    return JSON.parse(data);
  }
  
  // 2. Cache miss - load from database
  console.log('Cache miss - loading from DB');
  data = await database.query(key);
  
  // 3. Store in cache for next time
  await cache.set(key, JSON.stringify(data), TTL);
  
  return data;
}
```

### Write-Through Pattern

Update cache when writing to database:

```javascript
async function saveData(key, data) {
  // 1. Write to database
  await database.save(key, data);
  
  // 2. Update cache
  await cache.set(key, JSON.stringify(data), TTL);
  
  return data;
}
```

### Cache Invalidation

Remove/update cache when data changes:

```javascript
async function updateProduct(productId, updates) {
  // 1. Update database
  const updated = await database.update(productId, updates);
  
  // 2. Invalidate cache
  await cache.delete(`product:${productId}`);
  
  // Also invalidate related caches
  await cache.delete('products:popular');
  await cache.delete(`products:category:${updated.category}`);
  
  return updated;
}
```

### TTL (Time To Live)

Set expiration times for cached data:

```javascript
// Short TTL for frequently changing data
await cache.set('products:popular', data, 1800); // 30 minutes

// Long TTL for stable data
await cache.set('categories', data, 86400); // 24 hours

// Very long TTL for rarely changing data
await cache.set('vendor:profile', data, 604800); // 7 days
```

### Cache Keys Best Practices

```javascript
// Use consistent, descriptive keys
'vendor:123'
'product:456'
'sales:daily:2025-11-11'
'analytics:vendor:123:revenue'

// Namespace related items
'marketplace:vendor:123'
'marketplace:product:456'

// Include version for cache busting
'dashboard:stats:v2'
```

---

## Best Practices

### General Coding

**1. Use Descriptive Names:**
```javascript
// Bad
const d = new Date();
const p = products.filter(x => x.s > 0);

// Good
const currentDate = new Date();
const inStockProducts = products.filter(product => product.stock > 0);
```

**2. Keep Functions Small:**
```javascript
// Each function should do one thing well
function calculateTotalRevenue(sales) {
  return sales.reduce((sum, sale) => sum + sale.amount, 0);
}

function filterSalesByDate(sales, startDate, endDate) {
  return sales.filter(sale =>
    sale.date >= startDate && sale.date <= endDate
  );
}

// Compose them
function getRevenueForPeriod(sales, startDate, endDate) {
  const periodSales = filterSalesByDate(sales, startDate, endDate);
  return calculateTotalRevenue(periodSales);
}
```

**3. Validate Input:**
```javascript
function createVendor(name, stallNumber) {
  if (!name) {
    throw new Error('Vendor name is required');
  }
  if (!stallNumber) {
    throw new Error('Stall number is required');
  }
  // Continue with valid input
}
```

**4. Handle Errors Gracefully:**
```javascript
async function getVendor(id) {
  try {
    const vendor = await database.findById(id);
    if (!vendor) {
      return null; // Not found
    }
    return vendor;
  } catch (error) {
    console.error('Error fetching vendor:', error);
    throw new Error('Failed to fetch vendor');
  }
}
```

### ES6 Specific

**1. Use const/let, never var:**
```javascript
const TAX_RATE = 0.18; // Won't change
let currentStock = 50;  // Will change
```

**2. Use Arrow Functions Appropriately:**
```javascript
// For callbacks
products.map(p => p.name);
products.filter(p => p.stock > 0);

// For object methods, use regular functions (to preserve 'this')
class Vendor {
  getName() {  // Not arrow function
    return this.name;
  }
}
```

**3. Prefer Template Literals:**
```javascript
// Bad
const message = 'Hello, ' + name + '! Total: RWF ' + amount;

// Good
const message = `Hello, ${name}! Total: RWF ${amount}`;
```

**4. Use Default Parameters:**
```javascript
function getProducts(limit = 10, offset = 0) {
  // ...
}
```

### Array Method Guidelines

**1. Chain Thoughtfully:**
```javascript
// Filter first to reduce subsequent operations
const result = products
  .filter(p => p.stock > 0)  // Reduce dataset first
  .map(p => p.name)          // Then transform
  .sort();                   // Then sort
```

**2. Don't Mutate Original Arrays:**
```javascript
// Bad - mutates original
const sorted = vendors.sort((a, b) => b.revenue - a.revenue);

// Good - creates copy
const sorted = [...vendors].sort((a, b) => b.revenue - a.revenue);
```

**3. Use Appropriate Method:**
```javascript
// Need one item? Use find(), not filter()[0]
const vendor = vendors.find(v => v.id === '123');

// Just checking existence? Use some(), not filter().length
const hasExpensive = products.some(p => p.price > 50000);
```

### Performance Tips

**1. Cache Expensive Operations:**
```javascript
class Analytics {
  constructor() {
    this._cachedStats = null;
    this._cacheTime = null;
  }

  getStats() {
    const now = Date.now();
    // Cache for 5 minutes
    if (this._cachedStats && (now - this._cacheTime) < 300000) {
      return this._cachedStats;
    }

    // Expensive calculation
    this._cachedStats = this.calculateStats();
    this._cacheTime = now;
    return this._cachedStats;
  }
}
```

**2. Avoid Nested Loops When Possible:**
```javascript
// Bad - O(n²)
for (const sale of sales) {
  for (const product of products) {
    if (sale.productId === product.id) {
      // ...
    }
  }
}

// Good - O(n)
const productMap = new Map(products.map(p => [p.id, p]));
for (const sale of sales) {
  const product = productMap.get(sale.productId);
  // ...
}
```

---

## Quick Reference

### Array Methods Cheat Sheet

| Method | Purpose | Returns | Mutates? |
|--------|---------|---------|----------|
| `map()` | Transform each element | New array | No |
| `filter()` | Select matching elements | New array | No |
| `reduce()` | Combine to single value | Any type | No |
| `find()` | Get first match | Element or undefined | No |
| `some()` | Test if any match | Boolean | No |
| `every()` | Test if all match | Boolean | No |
| `sort()` | Reorder elements | Same array | **Yes** |
| `slice()` | Extract portion | New array | No |

### Class Keywords Cheat Sheet

| Keyword | Purpose | Example |
|---------|---------|---------|
| `class` | Define class | `class Vendor {}` |
| `constructor` | Initialize instance | `constructor(name) { this.name = name; }` |
| `extends` | Inherit from parent | `class Child extends Parent {}` |
| `super()` | Call parent constructor | `super(parentArg)` |
| `super.method()` | Call parent method | `super.getDetails()` |
| `static` | Class-level method | `static getTotals(items) {}` |
| `get` | Getter method | `get fullName() { return ... }` |
| `set` | Setter method | `set name(value) { ... }` |

---

This concepts guide should serve as your reference throughout the activity. Bookmark it and refer back whenever you need clarification!
